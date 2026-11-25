# 9/21 EMA + VWAP Alert Bot

Telegram alerts for:
- BUY setup: 9 EMA crosses above 21 EMA, next candle closes above both (and above VWAP)
- SELL setup: 9 EMA crosses below 21 EMA, next candle closes below both (and below VWAP)
- Support/resistance touches at the 9 EMA, 21 EMA and VWAP

## Setup
1. pip install -r requirements.txt
2. Create a Telegram bot with @BotFather, get your chat ID from @userinfobot, and message your bot once.
3. export TELEGRAM_TOKEN="your-token"
   export TELEGRAM_CHAT_ID="your-chat-id"
4. python ema_support_bot.py

Edit the CONFIG section at the top of the script to change tickers, timeframe, or filters.
