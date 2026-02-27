import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. सेटिंग्स (No Cache Mode) ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# एक्सचेंज को नए सिरे से कनेक्ट करना
@st.cache_resource
def get_exchange():
    return ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})

exchange = get_exchange()

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"})
    except: pass

st.set_page_config(page_title="Sailani AI Stable", layout="wide")

# --- 2. परमानेंट मेमोरी फिक्स (सर्वर रीसेट प्रूफ) ---
if 'history' not in st.session_state: st.session_state.history = set() # भेजे गए मैसेज की लिस्ट
if 'profit' not in st.session_state: st.session_state.profit = 0.0
if 'loss' not in st.session_state: st.session_state.loss = 0.0
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}

# --- 3. डैशबोर्ड ---
st.sidebar.title("💰 WALLET")
try:
    # बिना कैश के ताज़ा बैलेंस उठाना
    bal = exchange.fetch_balance({'type': 'future'})
    usdt = bal['total'].get('USDT', 0.0)
    st.sidebar.header(f"${usdt:.2f}")
except: st.sidebar.error("सर्वर कनेक्ट नहीं हो रहा")

st.title("🛡️ Sailani AI: Master Scan 15")
c1, c2, c3 = st.columns(3)
c1.metric("Live Trades", len(st.session_state.active_trades))
c2.success(f"Profit: +${st.session_state.profit:.2f}")
c3.error(f"Loss: -${st.session_state.loss:.2f}")

# --- 4. 15 कॉइन्स की लिस्ट ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "BNB/USDT", 
            "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT", "NEAR/USDT", 
            "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto = st.toggle("🚀 चालू करें")

if auto:
    status = st.empty()
    while True:
        for sym in power_15:
            try:
                # ताज़ा डेटा खींचना
                ohlcv = exchange.fetch_ohlcv(sym, timeframe='5m', limit=20)
                df = pd.DataFrame(ohlcv, columns=['t', 'o', 'h', 'l', 'c', 'v'])
                price = df['c'].iloc[-1]
                ema = df['c'].ewm(span=20).mean().iloc[-1]

                # --- 1. टारगेट/SL चेक ---
                if sym in st.session_state.active_trades:
                    t = st.session_state.active_trades[sym]
                    if (t['type'] == 'BUY' and price >= t['tp']) or (t['type'] == 'SHORT' and price <= t['tp']):
                        st.session_state.profit += 1.2
                        send_telegram_msg(f"✅ TARGET HIT: {sym}\nEXIT: {price}")
                        del st.session_state.active_trades[sym]
                    elif (t['type'] == 'BUY' and price <= t['sl']) or (t['type'] == 'SHORT' and price >= t['sl']):
                        st.session_state.loss += 0.6
                        send_telegram_msg(f"🛑 SL HIT: {sym}\nEXIT: {price}")
                        del st.session_state.active_trades[sym]
                    continue

                # --- 2. नया सिग्नल (Memory Lock के साथ) ---
                sig_key = f"{sym}_{price}" # यूनिक आईडी ताकि रिपीट न हो
                if sig_key in st.session_state.history: continue

                if price > ema and price > df['h'].iloc[-2]: # BUY
                    sl, tp = round(price*0.997, 4), round(price*1.01, 4)
                    st.session_state.active_trades[sym] = {'type':'BUY', 'tp':tp, 'sl':sl}
                    st.session_state.history.add(sig_key)
                    send_telegram_msg(f"🚀 BUY: {sym}\nENTRY: {price}\nSL: {sl}\nTP: {tp}")

                elif price < ema and price < df['l'].iloc[-2]: # SHORT
                    sl, tp = round(price*1.003, 4), round(price*0.99, 4)
                    st.session_state.active_trades[sym] = {'type':'SHORT', 'tp':tp, 'sl':sl}
                    st.session_state.history.add(sig_key)
                    send_telegram_msg(f"📉 SHORT: {sym}\nENTRY: {price}\nSL: {sl}\nTP: {tp}")

                status.info(f"📡 स्कैनिंग: {sym} | भाव: {price}")
                time.sleep(0.5)
            except: continue
        time.sleep(5)
