# Stock Drop Notifier — Build Guide

Sends a push notification to your phone when a stock drops 2%+ from its opening price that day.

---

## What You'll Need

- Python 3.8+
- The `ntfy` app on your phone (free, no account required): https://ntfy.sh/
- Two Python libraries: `yfinance` and `requests`

---

## Step 1 — Set Up ntfy (Phone Notifications)

1. Install the **ntfy** app on your iPhone or Android (search "ntfy" in the App Store / Play Store)
2. Open the app and subscribe to a topic — pick any unique name, e.g. `jason-stock-alerts-7842`
   - The more unique the name, the less likely a stranger is also subscribed to the same topic
   - You'll use this same topic name in your Python script
3. That's it — no login, no account

---

## Step 2 — Project Structure

Create these files inside this folder:

```
stockNotifs/
├── stocks.py       ← your stock list and settings
├── checker.py      ← fetches prices and checks the 2% rule
├── notifier.py     ← sends the push notification via ntfy
├── main.py         ← checks all stocks once and exits
└── requirements.txt
```

---

## Step 3 — Set Up a Virtual Environment (Recommended)

**Use a virtual environment, not your global Python.** When running scripts automatically via cron (see Step 7), the system may use a different Python than you expect, and globally installed packages can conflict across projects or break after system updates. A venv keeps everything self-contained and makes the cron job reliable.

```bash
cd ~/Coding/stockNotifs
python3 -m venv venv
source venv/bin/activate
```

Your prompt will change to show `(venv)` — you're now inside the environment.

Install dependencies into the venv:

```bash
pip install yfinance requests
```

Or using a `requirements.txt`:

```
yfinance
requests
```

```bash
pip install -r requirements.txt
```

To deactivate the venv when you're done working manually:

```bash
deactivate
```

> **Note:** When running via cron (Step 7), you don't activate the venv — instead you call the venv's Python binary directly using its full path (e.g. `~/Coding/stockNotifs/venv/bin/python`). This is shown in the cron setup below.

---

## Step 4 — Write Each File

### `stocks.py`

This is where you configure everything. Edit `STOCKS` to add/remove tickers anytime.

```python
STOCKS = ["AAPL", "TSLA", "NVDA", "MSFT"]  # add your tickers here
NTFY_TOPIC = "jason-stock-alerts-7842"       # must match what you subscribed to in the app
ALERT_THRESHOLD = -0.02                       # -2% triggers a notification
```

---

### `checker.py`

Fetches the current price and opening price, then checks if the drop threshold is met.

```python
import yfinance as yf

def get_pct_change(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.fast_info
    open_price = info.get("open")
    last_price = info.get("last_price")

    if not open_price or not last_price:
        return None, None, None

    pct_change = (last_price - open_price) / open_price
    return pct_change, open_price, last_price
```

---

### `notifier.py`

Sends a push notification to your phone via ntfy.sh.

```python
import requests

def send_alert(topic, symbol, pct_change, current_price):
    message = f"{symbol} is down {abs(pct_change) * 100:.1f}% today (${current_price:.2f})"
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message,
        headers={"Title": f"Stock Alert: {symbol}"}
    )
    print(f"[ALERT SENT] {message}")
```

---

### `main.py`

Runs once, checks every stock, sends alerts for any that are down 2%+, then exits.
Cron handles the scheduling (see Step 7).

```python
from stocks import STOCKS, NTFY_TOPIC, ALERT_THRESHOLD
from checker import get_pct_change
from notifier import send_alert


def run():
    print("Checking stocks:", STOCKS)

    for symbol in STOCKS:
        pct_change, open_price, last_price = get_pct_change(symbol)

        if pct_change is None:
            print(f"[WARN] Could not fetch data for {symbol}")
            continue

        print(f"{symbol}: {pct_change * 100:.2f}% from open")

        if pct_change <= ALERT_THRESHOLD:
            send_alert(NTFY_TOPIC, symbol, pct_change, last_price)

    print("Done.")


if __name__ == "__main__":
    run()
```

---

## Step 5 — Run It Manually

```bash
cd ~/Coding/stockNotifs
source venv/bin/activate
python main.py
```

The script checks each stock once and exits — no need to keep a terminal open.

---

## Step 6 — Test It Works

Temporarily change the threshold in `stocks.py` to `0.0` (fires on any movement), run the script manually during market hours, and you should get a phone notification within seconds. Then set it back to `-0.02`.

---

## Step 7 — Run It Automatically Every Weekday (cron)

Use **cron** to run the script at 1:30pm CT every weekday. Since the script runs once and exits, cron handles all the scheduling — no loop needed.

### Set up the cron job

Open your crontab:

```bash
crontab -e
```

Add this line at the bottom (adjust the path to match where your project lives):

```
30 13 * * 1-5 cd ~/Coding/stockNotifs && ~/Coding/stockNotifs/venv/bin/python main.py >> ~/Coding/stockNotifs/stock_alerts.log 2>&1
```

What this does:
- `30 13 * * 1-5` — runs at 1:30pm every Monday–Friday (in your machine's local time, CT)
- Uses the venv's Python directly — no need to activate first
- Logs all output to `stock_alerts.log`

Save and exit. Verify it was saved with:

```bash
crontab -l
```

Check the log after it runs:

```bash
cat ~/Coding/stockNotifs/stock_alerts.log
```

### One catch: your machine needs to be on

Cron only runs if your computer is awake at 1:30pm. If it's asleep, the job won't fire. A few ways to handle this:

- **Leave your machine on** — simplest option
- **Set a wake alarm** — on macOS, go to System Settings → Battery → Schedule and set a wake time before 1:30pm on weekdays
- **Run on an always-on machine** — a Raspberry Pi, a home server, or a cheap cloud VM (e.g. a $4/month DigitalOcean droplet) works great for this

---

## Notes

- `yfinance` data has a small delay (~15 minutes). Running at 1:30pm CT means you're seeing prices from ~1:15pm, which is fine for catching a 2%+ drop.
- If a stock has already bounced back by 1:30pm you won't catch it — this is a single daily snapshot, not continuous monitoring.
- You can add as many tickers as you want to `STOCKS` in `stocks.py`.
- For more reliable data (real-time, no delay), look into **Polygon.io** or **Finnhub** — both have free tiers.
