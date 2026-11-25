"""
Day-trading EMA support alert bot.
Alerts via Telegram when price pulls back from above to its 9 or 21 EMA
on an intraday chart (default: 5-minute bars).
"""
import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import yfinance as yf

# ---- CONFIG -----------------------------------------------------------
TICKERS = ["MU", "SPY", "^GSPC", "SOXS", "TSLA", "AVGO", "NVDA", "META"]  # ^GSPC = SPX
EMAS = [9, 21]                       # EMA periods treated as support
INTERVAL = "5m"                      # "1m", "2m", "5m", "15m", "30m", "60m"
TOLERANCE = 0.0015                   # alert when within 0.15% of the EMA
COOLDOWN_MINUTES = 15                # min gap between repeat alerts per ticker/EMA
CHECK_EVERY_SECONDS = 60
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# -----------------------------------------------------------------------

NY = ZoneInfo("America/New_York")
last_alert = {}  # (ticker, ema) -> datetime


def market_open() -> bool:
    now = datetime.now(NY)
    if now.weekday() >= 5:
        return False
    return now.replace(hour=9, minute=30, second=0) <= now <= now.replace(hour=16, minute=0, second=0)


def send(msg: str) -> None:
    print(msg, "\n")
    if not TOKEN or not CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=10,
        )
    except requests.RequestException as e:
        print("Telegram error:", e)


def check(ticker: str) -> None:
    # 5 days of intraday bars so the EMAs are fully "warmed up" at the open
    df = yf.Ticker(ticker).history(period="5d", interval=INTERVAL)
    if len(df) < max(EMAS) * 3:
        return

    close = df["Close"]
    price = float(close.iloc[-1])
    low = float(df["Low"].iloc[-1])
    prev_close = float(close.iloc[-2])
    now = datetime.now(NY)

    for n in EMAS:
        ema_series = close.ewm(span=n, adjust=False).mean()
        ema = float(ema_series.iloc[-1])
        prev_ema = float(ema_series.iloc[-2])

        was_above = prev_close > prev_ema        # pulling back from above
        touched = low <= ema * (1 + TOLERANCE)   # wick/close reached the EMA
        holding = price >= ema * (1 - TOLERANCE) # hasn't broken down through it
        if not (was_above and touched and holding):
            continue

        key = (ticker, n)
        if key in last_alert and now - last_alert[key] < timedelta(minutes=COOLDOWN_MINUTES):
            continue
        last_alert[key] = now

        dist = (price - ema) / ema * 100
        send(f"📍 {ticker} testing {n} EMA ({INTERVAL}) support\n"
             f"Price: ${price:.2f} | {n} EMA: ${ema:.2f} ({dist:+.2f}%)\n"
             f"Bar low: ${low:.2f}")


def main() -> None:
    send(f"EMA support bot started ({INTERVAL} chart). Watching: {', '.join(TICKERS)}")
    while True:
        if market_open():
            for t in TICKERS:
                try:
                    check(t)
                except Exception as e:
                    print(f"{t} error: {e}")
        time.sleep(CHECK_EVERY_SECONDS)


if __name__ == "__main__":
    main()
