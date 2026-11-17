import asyncio, json, os, re
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright

BASE = Path(__file__).parent
DATA = BASE / "data.json"
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "300"))
SITES = {
    "District": "https://www.district.in/movies/avengers-doomsday-movie-tickets-MV176735",
    "BookMyShow": "https://in.bookmyshow.com/movies/chennai/avengers-doomsday/ET00439706",
}
app = FastAPI(title="Avengers Chennai Tracker")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

def read_data():
    if DATA.exists():
        try: return json.loads(DATA.read_text(encoding="utf-8"))
        except Exception: pass
    return {"updated_at": None, "sources": {}, "events": [], "status": "Not checked yet"}

def write_data(d):
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_lines(body):
    lines = []
    for raw in body.splitlines():
        s = re.sub(r"\s+", " ", raw).strip()
        if len(s) > 2 and len(s) < 180:
            if re.search(r"(\b(?:1[0-2]|0?[1-9])(?::[0-5]\d)?\s?(?:am|pm)\b|book tickets|filling fast|available|sold out|imax|4dx|3d|dec(?:ember)?\s+\d{1,2})", s, re.I):
                lines.append(s)
    return list(dict.fromkeys(lines))[:250]

async def scan():
    data = read_data()
    now = datetime.now(timezone.utc).isoformat()
    found_any = False
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for site, url in SITES.items():
            page = await browser.new_page(viewport={"width": 1365, "height": 900})
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(7000)
                body = await page.locator("body").inner_text(timeout=15000)
                lines = extract_lines(body)
                old = set(data.get("sources", {}).get(site, {}).get("lines", []))
                new = [x for x in lines if x not in old]
                # First scan is a baseline, not a false-positive alert.
                if site in data.get("sources", {}):
                    for line in new:
                        data.setdefault("events", []).insert(0, {
                            "site": site, "text": line, "detected_at": now, "url": url
                        })
                        found_any = True
                data.setdefault("sources", {})[site] = {
                    "url": url, "lines": lines, "checked_at": now,
                    "page_title": await page.title(), "error": None
                }
            except Exception as e:
                errors.append(f"{site}: {str(e)[:220]}")
                data.setdefault("sources", {}).setdefault(site, {})["error"] = str(e)[:300]
                data["sources"][site]["checked_at"] = now
                data["sources"][site]["url"] = url
            finally:
                await page.close()
        await browser.close()
    data["events"] = data.get("events", [])[:100]
    data["updated_at"] = now
    data["status"] = "New page text detected" if found_any else ("Check completed" if not errors else "Some sources could not be checked")
    data["errors"] = errors
    write_data(data)
    return data

@app.get("/")
async def home():
    return FileResponse(BASE / "static" / "index.html")

@app.get("/api/status")
async def status():
    return read_data()

@app.post("/api/check")
async def check():
    return await scan()

@app.on_event("startup")
async def startup():
    async def loop():
        while True:
            try: await scan()
            except Exception: pass
            await asyncio.sleep(POLL_SECONDS)
    asyncio.create_task(loop())
