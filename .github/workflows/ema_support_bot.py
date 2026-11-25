def main() -> None:
    send(f"Bot started ({INTERVAL}). Watching: {', '.join(TICKERS)}")
    while True:
        now = datetime.now(NY)
        if now.weekday() >= 5 or now.hour >= 16:
            break  # market closed, end the run
        if market_open():
            for t in TICKERS:
                try:
                    df = load(t)
                    if df is None:
                        continue
                    check_setups(t, df, now)
                    if LEVEL_ALERTS:
                        check_levels(t, df, now)
                except Exception as e:
                    print(f"{t} error: {e}")
        time.sleep(CHECK_EVERY_SECONDS)
