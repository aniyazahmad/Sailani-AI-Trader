import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. सुरक्षा और Keys (Q6TjQC... वाली) ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({
    'apiKey': API_KEY, 'secret': SECRET_KEY,
    'enableRateLimit': True, 'options': {'defaultType': 'future'}
})

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"}
        requests.get(url, params=params)
        time.sleep(2) # एंटी-ब्लॉक पॉज़
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. डैशबोर्ड याददाश्त (Memory Fix) ---
if 'total_profit' not in st.session_state: st.session_state.total_profit = 0.0
if 'total_loss' not in st.session_state: st.session_state.total_loss = 0.0
if 'signal_count' not in st.session_state: st.session_state.signal_count = 0
if 'active_logs' not in st.session_state: st.session_state.active_logs = {}

# --- 3. साइडबार में बड़ा वॉलेट बैलेंस ---
st.sidebar.markdown("## 💰 **MY WALLET**")
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    st.sidebar.markdown(f"<h1 style='color: #00FF00; font-size: 50px;'>${usdt_val:.2f}</h1>", unsafe_allow_html=True)
except: st.sidebar.error("❌ CONNECTION ERROR")

# --- 4. अल्ट्रा-बोल्ड डैशबोर्ड (Dashboard Fix) ---
st.title("🛡️ SAILANI AI: PRO DASHBOARD")
d_col1, d_col2, d_col3 = st.columns(3)
with d_col1:
    st.markdown("### 📢 TOTAL SIGNALS")
    st.markdown(f"<h1 style='font-size: 60px;'>{st.session_state.signal_count}</h1>", unsafe_allow_html=True)
with d_col2:
    st.markdown("### 🟢 PROFIT")
    st.markdown(f"<h1 style='color: #00FF00; font-size: 60px;'>+${st.session_state.total_profit:.2f}</h1>", unsafe_allow_html=True)
with d_col3:
    st.markdown("### 🔴 LOSS")
    st.markdown(f"<h1 style='color: #FF4B4B; font-size: 60px;'>-${st.session_state.total_loss:.2f}</h1>", unsafe_allow_html=True)

st.divider()

# --- 5. ऑटो-स्कैनिंग और सही SL/TP लॉजिक ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 चालू करें: लाइव ऑटो-स्कैनिंग")

if auto_mode:
    status_box = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                price = df['close'].iloc[-1]
                ema = df['close'].ewm(span=20).mean().iloc[-1]

                # ट्रेड क्लोज चेक (Memory Fix)
                if symbol in st.session_state.active_logs:
                    trade = st.session_state.active_logs[symbol]
                    if (trade['type'] == 'BUY' and price >= trade['tp']) or (trade['type'] == 'SHORT' and price <= trade['tp']):
                        st.session_state.total_profit += 1.20
                        send_telegram_msg(f"✅ TARGET HIT: {symbol}\n💰 PROFIT: +$1.20\n📊 EXIT: {price}")
                        del st.session_state.active_logs[symbol]
                        continue
                    elif (trade['type'] == 'BUY' and price <= trade['sl']) or (trade['type'] == 'SHORT' and price >= trade['sl']):
                        st.session_state.total_loss += 0.60
                        send_telegram_msg(f"🛑 STOP LOSS HIT: {symbol}\n📉 LOSS: -$0.60\n📊 EXIT: {price}")
                        del st.session_state.active_logs[symbol]
                        continue
                    continue

                # --- नया सिग्नल लॉजिक (SL/TP Calculation Fix) ---
                if price > ema and price > df['high'].iloc[-2]: # BUY
                    sl = round(price * 0.995, 4) # 0.5% नीचे
                    tp = round(price * 1.01, 4)  # 1% ऊपर
                    st.session_state.active_logs[symbol] = {'type': 'BUY', 'entry': price, 'tp': tp, 'sl': sl}
                    st.session_state.signal_count += 1
                    send_telegram_msg(f"🚀 BUY SIGNAL: {symbol}\nENTRY: {price}\n🛑 SL: {sl}\n🎯 TARGET: {tp}")

                elif price < ema and price < df['low'].iloc[-2]: # SHORT
                    sl = round(price * 1.005, 4) # 0.5% ऊपर
                    tp = round(price * 0.99, 4)  # 1% नीचे
                    st.session_state.active_logs[symbol] = {'type': 'SHORT', 'entry': price, 'tp': tp, 'sl': sl}
                    st.session_state.signal_count += 1
                    send_telegram_msg(f"📉 SHORT SIGNAL: {symbol}\nENTRY: {price}\n🛑 SL: {sl}\n🎯 TARGET: {tp}")

                status_box.info(f"📡 स्कैनिंग: {symbol} | भाव: {price}")
                time.sleep(1)
            except: continue
        time.sleep(10)
