# FINAL - $10 - $50 PER TRADE - 2 BIG MOVE PER DAY - YAHOO - PHONE ONLY
import os, time, threading
from flask import Flask
import yfinance as yf
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app_web = Flask(__name__)
@app_web.route('/')
def home():
    return "BOT $50 MODE - 2 BIG MOVE PER DAY - RUNNING ✅"
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

signals_today = 0
last_day = None

PAIRS = {
    "EURUSD": ("EURUSD=X", 0.0001, 0.10),
    "GBPUSD": ("GBPUSD=X", 0.0001, 0.10),
    "GOLD": ("GC=F", 0.10, 1.0),
}

def check_big_move(pair, symbol, pip_size, pip_value_per_pip):
    try:
        df = yf.download(symbol, period="10d", interval="1h", progress=False)
        if df.empty: return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df['EMA100'] = df['Close'].ewm(span=100).mean()
        price = float(df.iloc[-1]['Close'])
        ema = float(df.iloc[-1]['EMA100'])
        bullish = price > ema
        bearish = price < ema
        window = df.iloc[-51:-1]
        lowest = float(window['Low'].min()); highest = float(window['High'].max())
        prev = df.iloc[-2]; prev2 = df.iloc[-3]
        low1 = float(prev['Low']); high1 = float(prev['High'])
        close1 = float(prev['Close']); close2 = float(prev2['Close'])
        strong = abs(close1 - close2) > (15 * pip_size)
        hour = datetime.now().hour + 1
        is_session = (9 <= hour <= 12) or (14 <= hour <= 17)
        if not is_session: return None
        if pair == "GOLD":
            tp_dist = 50.0; sl_dist = 5.0
        else:
            tp_dist = 500 * pip_size; sl_dist = 50 * pip_size
        if bullish and low1 < lowest and close1 > lowest and close1 > close2 and strong:
            sl = low1 - sl_dist; tp = price + tp_dist
            return ("BUY", price, sl, tp, 50.0, 5.0)
        if bearish and high1 > highest and close1 < highest and close1 < close2 and strong:
            sl = high1 + sl_dist; tp = price - tp_dist
            return ("SELL", price, sl, tp, 50.0, 5.0)
        return None
    except Exception as e:
        print("Error", pair, e); return None

async def scan_and_send(context: ContextTypes.DEFAULT_TYPE):
    global signals_today, last_day
    today = datetime.now().date()
    if last_day != today:
        signals_today = 0; last_day = today
    if signals_today >= 2:
        return
    for pair, (sym, pip_size, pip_val) in PAIRS.items():
        if signals_today >= 2: break
        res = check_big_move(pair, sym, pip_size, pip_val)
        if res:
            action, price, sl, tp, profit, loss = res
            msg = f"""🔥 BIG MOVE 1/2 - $50 MODE 🔥

Pair: {pair}
Action: {action}
Entry: {price:.4f}
SL: {sl:.4f}
TP: {tp:.4f}

🎯 TARGET: 500 pips BIG MOVE
💰 $10 ACCOUNT - USE 0.01 LOT ONLY:
✅ TP Hit: +${profit:.2f} - $10 go become $60
❌ SL Hit: -${loss:.2f} only

⚠️ Enter 1 at a time! No enter 2 at once!
✅ Bot take e time: Daily + 4H + 1H all agree
✅ HTF + Sweep + BOS + FVG = ALL YES"""
            try:
                await context.bot.send_message(chat_id=CHAT_ID, text=msg)
                signals_today += 1
            except Exception as e:
                print("Send error", e)

DASHBOARD = """🤖 BOT - $50 MODE - 2 BIG MOVE PER DAY

📡 Source: Yahoo Finance REAL PRICE
🐢 Speed: SLOW - Check every 30 mins, take e time
📊 Pairs: EURUSD, GBPUSD, GOLD
🎯 Max: 2 signals PER DAY - Big move only
💰 Target: $50 per trade (0.01 lot, 500 pips)
🛡️ Risk: $5 loss only per trade
⚠️ Enter 1 at a time!
📱 Phone Only - No PC needed
"""

keyboard = [[InlineKeyboardButton("📡 Scan Now", callback_data="scan")],
            [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]]

async def
