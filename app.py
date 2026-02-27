import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. आपकी सटीक Keys ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({
    'apiKey': API_KEY, 'secret': SECRET_KEY,
    'enableRateLimit': True, 'options': {'defaultType': 'future'}
})

# बोल्ड टेलीग्राम मैसेज फंक्शन
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        # HTML mode इस्तेमाल किया है ताकि मैसेज BOLD आए
        params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.get(url, params=params)
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. साइडबार में बड़ा और चमकीला बैलेंस ---
st.sidebar.markdown("## 💰 **MY LIVE WALLET**")
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    st.sidebar.markdown(f"<h1 style='color: #00FF00; font-size: 45px;'>${usdt_val:.2f}</h1>", unsafe_allow_html=True)
    st.sidebar.success("CONNECTED")
except:
    st.sidebar.error("ERROR: Check Keys/IP")

# --- 3. डुप्लीकेट सिग्नल रोकने के लिए मेमोरी ---
if 'processed_signals' not in st.session_state:
    st.session_state.processed_signals = {}

power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

st.title("🛡️ Sailani AI Power 15")
auto_mode = st.toggle("🚀 Start Auto-Scanning")

if auto_mode:
    status = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                price = df['close'].iloc[-1]
                ema = df['close'].ewm(span=20).mean().iloc[-1]

                # अगर ट्रेड पहले से चल रहा है, तो चेक करें
                if symbol in st.session_state.processed_signals:
                    trade = st.session_state.processed_signals[symbol]
                    if price >= trade['tp'] or price <= trade['sl']:
                        res = "PROFIT ✅" if price >= trade['tp'] else "LOSS 🚨"
                        send_telegram_msg(f"<b>🏁 TRADE CLOSED: {symbol}</b>\n<b>RESULT: {res}</b>")
                        del st.session_state.processed_signals[symbol]
                    continue

                # BUY SIGNAL LOGIC
                if price > ema and price > df['high'].iloc[-2]:
                    sl = df['low'].iloc[-3]
                    tp = price + (price - sl) * 2
                    st.session_state.processed_signals[symbol] = {'tp': tp, 'sl': sl}
                    
                    # Bold Telegram Alert
                    msg = f"<b>🚀 BUY SIGNAL: {symbol}</b>\n\n<b>ENTRY: {price}</b>\n<b>SL: {sl}</b>\n<b>TARGET: {tp}</b>"
                    send_telegram_msg(msg)
                    st.success(f"Sent: {symbol} BUY")

                # SHORT SIGNAL LOGIC
                elif price < ema and price < df['low'].iloc[-2]:
                    sl = df['high'].iloc[-3]
                    tp = price - (sl - price) * 2
                    st.session_state.processed_signals[symbol] = {'tp': tp, 'sl': sl}
                    
                    msg = f"<b>📉 SHORT SIGNAL: {symbol}</b>\n\n<b>ENTRY: {price}</b>\n<b>SL: {sl}</b>\n<b>TARGET: {tp}</b>"
                    send_telegram_msg(msg)
                    st.error(f"Sent: {symbol} SHORT")

                status.info(f"📡 Scanning: {symbol} | Price: {price}")
                time.sleep(1)
            except: continue
        time.sleep(10)
