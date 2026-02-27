import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. आपकी सेटिंग्स ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({
    'apiKey': API_KEY, 'secret': SECRET_KEY,
    'enableRateLimit': True, 'options': {'defaultType': 'future'}
})

# --- ANTI-BLOCK टेलीग्राम फंक्शन (Ultra-Bold) ---
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        # HTML का उपयोग करके मैसेज को और भी बोल्ड बनाया गया है
        params = {
            "chat_id": CHAT_ID, 
            "text": f"<b>{message}</b>", 
            "parse_mode": "HTML"
        }
        requests.get(url, params=params)
        time.sleep(3) # एंटी-ब्लॉक सुरक्षा: हर मैसेज के बाद 3 सेकंड का ब्रेक
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. डैशबोर्ड याददाश्त ---
if 'total_profit' not in st.session_state: st.session_state.total_profit = 0.0
if 'total_loss' not in st.session_state: st.session_state.total_loss = 0.0
if 'signal_count' not in st.session_state: st.session_state.signal_count = 0
if 'active_logs' not in st.session_state: st.session_state.active_logs = {}

# --- 3. साइडबार में बड़ा बैलेंस ---
st.sidebar.markdown("## 💰 **MY WALLET**")
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    st.sidebar.markdown(f"<h1 style='color: #00FF00; font-size: 55px;'>${usdt_val:.2f}</h1>", unsafe_allow_html=True)
except:
    st.sidebar.error("❌ CONNECTION ERROR")

# --- 4. अल्ट्रा-बोल्ड डैशबोर्ड ---
st.title("🛡️ SAILANI AI: PRO DASHBOARD")
d_col1, d_col2, d_col3 = st.columns(3)
with d_col1:
    st.markdown("### 📢 TOTAL SIGNALS")
    st.markdown(f"## {st.session_state.signal_count}")
with d_col2:
    st.markdown("### 🟢 PROFIT")
    st.markdown(f"<h2 style='color: #00FF00;'>+${st.session_state.total_profit:.2f}</h2>", unsafe_allow_html=True)
with d_col3:
    st.markdown("### 🔴 LOSS")
    st.markdown(f"<h2 style='color: #FF4B4B;'>-${st.session_state.total_loss:.2f}</h2>", unsafe_allow_html=True)

st.divider()

# --- 5. 15 पावर कॉइन्स लिस्ट ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 चालू करें: लाइव ऑटो-स्कैनिंग")

if auto_mode:
    status = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                price = df['close'].iloc[-1]
                ema = df['close'].ewm(span=20).mean().iloc[-1]

                # ट्रेड एग्जिट चेक
                if symbol in st.session_state.active_logs:
                    trade = st.session_state.active_logs[symbol]
                    if (trade['type'] == 'BUY' and price >= trade['tp']) or (trade['type'] == 'SHORT' and price <= trade['tp']):
                        st.session_state.total_profit += 1.2
                        msg = f"🟢 TARGET HIT: {symbol}\n💰 PROFIT: +$1.20\n📊 EXIT: {price}"
                        send_telegram_msg(msg)
                        del st.session_state.active_logs[symbol]
                        continue
                    elif (trade['type'] == 'BUY' and price <= trade['sl']) or (trade['type'] == 'SHORT' and price >= trade['sl']):
                        st.session_state.total_loss += 0.6
                        msg = f"🔴 STOP LOSS HIT: {symbol}\n📉 LOSS: -$0.60\n📊 EXIT: {price}"
                        send_telegram_msg(msg)
                        del st.session_state.active_logs[symbol]
                        continue
                    continue

                # नया अल्ट्रा-बोल्ड सिग्नल लॉजिक
                if price > ema and price > df['high'].iloc[-2]:
                    sl = df['low'].iloc[-3]
                    tp = price + (price - sl) * 2
                    st.session_state.active_logs[symbol] = {'type': 'BUY', 'entry': price, 'tp': tp, 'sl': sl}
                    st.session_state.signal_count += 1
                    
                    signal = f"🚀 BUY SIGNAL: {symbol}\n━━━━━━━━━━━━━━\n➡️ ENTRY: {price}\n🛑 SL: {sl}\n🎯 TARGET: {tp}"
                    send_telegram_msg(signal)

                elif price < ema and price < df['low'].iloc[-2]:
                    sl = df['high'].iloc[-3]
                    tp = price - (sl - price) * 2
                    st.session_state.active_logs[symbol] = {'type': 'SHORT', 'entry': price, 'tp': tp, 'sl': sl}
                    st.session_state.signal_count += 1
                    
                    signal = f"📉 SHORT SIGNAL: {symbol}\n━━━━━━━━━━━━━━\n➡️ ENTRY: {price}\n🛑 SL: {sl}\n🎯 TARGET: {tp}"
                    send_telegram_msg(signal)

                status.info(f"📡 स्कैनिंग: {symbol} | भाव: {price}")
                time.sleep(0.5)
            except: continue
        time.sleep(10)
