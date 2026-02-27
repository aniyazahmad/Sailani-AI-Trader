import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. पक्की सेटिंग्स ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# दो सर्वर का इस्तेमाल: डेटा के लिए Binance, ट्रेडिंग के लिए Delta
@st.cache_resource
def init_exchanges():
    delta = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})
    binance = ccxt.binance() # फ्री और फ़ास्ट डेटा के लिए
    return delta, binance

delta_ex, bn_ex = init_exchanges()

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"})
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. फिक्स्ड मेमोरी (Reboot प्रूफ) ---
if 'profit' not in st.session_state: st.session_state.profit = 0.0
if 'loss' not in st.session_state: st.session_state.loss = 0.0
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}
if 'sent_keys' not in st.session_state: st.session_state.sent_keys = set()

# --- 3. डैशबोर्ड ---
st.title("🛡️ Sailani AI Master: Live 15")
c1, c2, c3 = st.columns(3)
c1.metric("Active Trades", len(st.session_state.active_trades))
c2.markdown(f"<h2 style='color:#00FF00;'>Profit: +${st.session_state.profit:.2f}</h2>", unsafe_allow_html=True)
c3.markdown(f"<h2 style='color:#FF4B4B;'>Loss: -${st.session_state.loss:.2f}</h2>", unsafe_allow_html=True)

# --- 4. 15 कॉइन्स की लिस्ट ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "BNB/USDT", 
            "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT", "NEAR/USDT", 
            "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 चालू करें")

if auto_mode:
    status = st.empty()
    while True:
        for sym in power_15:
            try:
                # बाइनेंस के सुपर-फ़ास्ट सर्वर से डेटा लेना
                bars = bn_ex.fetch_ohlcv(sym, timeframe='5m', limit=30)
                df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
                price = float(df['c'].iloc[-1])
                ema = df['c'].ewm(span=20).mean().iloc[-1]

                # --- टारगेट/SL चेक ---
                if sym in st.session_state.active_trades:
                    t = st.session_state.active_trades[sym]
                    if (t['type'] == 'BUY' and price >= t['tp']) or (t['type'] == 'SHORT' and price <= t['tp']):
                        st.session_state.profit += 1.2
                        send_telegram_msg(f"✅ TARGET HIT: {sym}\nEXIT: {price:.4f}")
                        del st.session_state.active_trades[sym]
                    elif (t['type'] == 'BUY' and price <= t['sl']) or (t['type'] == 'SHORT' and price >= t['sl']):
                        st.session_state.loss += 0.6
                        send_telegram_msg(f"🚨 SL HIT: {sym}\nEXIT: {price:.4f}")
                        del st.session_state.active_trades[sym]
                    continue

                # --- सटीक सिग्नल लॉजिक ---
                # एक कैंडल पर एक ही सिग्नल (Duplicate रोकने के लिए)
                time_key = f"{sym}_{df['t'].iloc[-1]}"
                if time_key in st.session_state.sent_keys: continue

                if price > ema and price > df['h'].iloc[-2]: # BUY
                    sl, tp = round(price*0.996, 4), round(price*1.01, 4)
                    st.session_state.active_trades[sym] = {'type':'BUY', 'tp':tp, 'sl':sl}
                    st.session_state.sent_keys.add(time_key)
                    send_telegram_msg(f"🚀 BUY: {sym}\nENTRY: {price:.4f}\nSL: {sl:.4f}\nTP: {tp:.4f}")

                elif price < ema and price < df['l'].iloc[-2]: # SHORT
                    sl, tp = round(price*1.004, 4), round(price*0.99, 4)
                    st.session_state.active_trades[sym] = {'type':'SHORT', 'tp':tp, 'sl':sl}
                    st.session_state.sent_keys.add(time_key)
                    send_telegram_msg(f"📉 SHORT: {sym}\nENTRY: {price:.4f}\nSL: {sl:.4f}\nTP: {tp:.4f}")

                status.info(f"📡 Scanning: {sym} | Price: {price:.4f}")
                time.sleep(1) # सर्वर पर बोझ कम करने के लिए
            except: continue
        time.sleep(10)
