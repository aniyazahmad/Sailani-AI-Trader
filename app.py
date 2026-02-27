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

# एक्सचेंज सेटअप
exchange = ccxt.delta({
    'apiKey': API_KEY, 'secret': SECRET_KEY,
    'enableRateLimit': True, 'options': {'defaultType': 'future'}
})

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"}
        requests.get(url, params=params)
        time.sleep(4) # एंटी-ब्लॉक पॉज़ (ब्लॉक से सुरक्षा)
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. डैशबोर्ड याददाश्त (Memory Persistence Fix) ---
# यह हिस्सा पक्का करेगा कि डैशबोर्ड 0 न हो
if 'total_profit' not in st.session_state: st.session_state.total_profit = 0.0
if 'total_loss' not in st.session_state: st.session_state.total_loss = 0.0
if 'signal_count' not in st.session_state: st.session_state.signal_count = 0
if 'active_logs' not in st.session_state: st.session_state.active_logs = {}
if 'last_signal_time' not in st.session_state: st.session_state.last_signal_time = {}

# --- 3. छोटा और साफ़ डैशबोर्ड ---
st.sidebar.markdown("### 💰 **WALLET**")
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    st.sidebar.markdown(f"<h2 style='color: #00FF00;'>${usdt_val:.2f}</h2>", unsafe_allow_html=True)
except: st.sidebar.error("Connection Error")

st.markdown("### 📊 **DAILY DASHBOARD**")
d_col1, d_col2, d_col3 = st.columns(3)
with d_col1:
    st.metric("Total Signals", st.session_state.signal_count)
with d_col2:
    st.markdown(f"<span style='color: #00FF00;'>Profit: +${st.session_state.total_profit:.2f}</span>", unsafe_allow_html=True)
with d_col3:
    st.markdown(f"<span style='color: #FF4B4B;'>Loss: -${st.session_state.total_loss:.2f}</span>", unsafe_allow_html=True)

st.divider()

# --- 4. 15 पावर कॉइन्स ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 चालू करें: लाइव ऑटो-स्कैनिंग")

if auto_mode:
    status_box = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                # 5-मिनट चार्ट पर डेटा स्कैनिंग
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                price = df['close'].iloc[-1]
                ema = df['close'].ewm(span=20).mean().iloc[-1]

                # ट्रेड एग्जिट चेक
                if symbol in st.session_state.active_logs:
                    trade = st.session_state.active_logs[symbol]
                    if (trade['type'] == 'BUY' and price >= trade['tp']) or (trade['type'] == 'SHORT' and price <= trade['tp']):
                        st.session_state.total_profit += 1.20
                        send_telegram_msg(f"✅ TARGET HIT: {symbol}\n📊 EXIT: {price:.4f}\nRESULT: PROFIT 💰")
                        del st.session_state.active_logs[symbol]
                        continue
                    elif (trade['type'] == 'BUY' and price <= trade['sl']) or (trade['type'] == 'SHORT' and price >= trade['sl']):
                        st.session_state.total_loss += 0.60
                        send_telegram_msg(f"🛑 STOP LOSS HIT: {symbol}\n📊 EXIT: {price:.4f}\nRESULT: LOSS 🛑")
                        del st.session_state.active_logs[symbol]
                        continue
                    continue

                # --- नया सिग्नल लॉजिक (No-Repeat Fix) ---
                # समय की जाँच ताकि एक ही मिनट में 10 सिग्नल न आएं
                current_time = time.time()
                last_time = st.session_state.last_signal_time.get(symbol, 0)

                if current_time - last_time > 300: # 5 मिनट का गैप (Candle Close)
                    # BUY
                    if price > ema and price > df['high'].iloc[-2]:
                        sl = round(price * 0.995, 4)
                        tp = round(price * 1.01, 4)
                        st.session_state.active_logs[symbol] = {'type': 'BUY', 'entry': price, 'tp': tp, 'sl': sl}
                        st.session_state.signal_count += 1
                        st.session_state.last_signal_time[symbol] = current_time
                        send_telegram_msg(f"🚀 <b>BUY SIGNAL: {symbol}</b>\nENTRY: {price:.4f}\n🛑 SL: {sl:.4f}\n🎯 TARGET: {tp:.4f}")

                    # SHORT
                    elif price < ema and price < df['low'].iloc[-2]:
                        sl = round(price * 1.005, 4)
                        tp = round(price * 0.99, 4)
                        st.session_state.active_logs[symbol] = {'type': 'SHORT', 'entry': price, 'tp': tp, 'sl': sl}
                        st.session_state.signal_count += 1
                        st.session_state.last_signal_time[symbol] = current_time
                        send_telegram_msg(f"📉 <b>SHORT SIGNAL: {symbol}</b>\nENTRY: {price:.4f}\n🛑 SL: {sl:.4f}\n🎯 TARGET: {tp:.4f}")

                status_box.info(f"📡 स्कैनिंग: {symbol} | भाव: {price}")
                time.sleep(1)
            except: continue
        time.sleep(10)
