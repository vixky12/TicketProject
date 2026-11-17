# Avengers Chennai Tracker (phone-friendly PWA)

This project provides a mobile dashboard and a small server-side checker for the public District and BookMyShow Avengers: Doomsday Chennai pages.

## Important limitations
- The research confirmed the movie pages and release date, but did **not** establish a stable, permitted public showtime API or validated page selectors.
- The checker compares relevant visible page text. Dynamic pages, bot protection, or layout changes can prevent extraction. A scan error is not proof that no shows exist.
- It does not bypass logins, CAPTCHAs, anti-bot controls, or private endpoints.
- The server must stay online for automatic 5-minute checks. Browser notifications are foreground-only in this starter build; true background push needs a push subscription service and VAPID keys.

## Run on your computer
1. Install Python 3.11+.
2. In this folder run:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Start:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```
4. On your phone connected to the same Wi-Fi, open `http://YOUR-COMPUTER-LAN-IP:8000`.

## Put it online for phone access anywhere
1. Create a GitHub repository and upload all files in this folder.
2. In Render, create a new **Web Service** from that repository.
3. Render can use `render.yaml`; build and start commands are included.
4. After deployment, open the Render URL on your Android phone in Chrome.
5. Use Chrome menu → **Add to Home screen** / **Install app**.

A free hosting tier may sleep or restart; continuous polling requires an always-on service. Check the host's current pricing and sleep policy.

## Pages monitored
- District: https://www.district.in/movies/avengers-doomsday-movie-tickets-MV176735
- BookMyShow: https://in.bookmyshow.com/movies/chennai/avengers-doomsday/ET00439706

## Configuration
Set `POLL_SECONDS` to change the polling interval (default 300 seconds / 5 minutes).
