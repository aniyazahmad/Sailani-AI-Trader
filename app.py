import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. आपकी नई लाइव Keys (जो आपने अभी बनाई) ---
API_KEY = 'GkmMUT0A3MMuMsTaySMCNPgIUkzeXF'
SECRET_KEY = 'vr2rKxlJjsljml4CCqfDoqObB0oFsQUby7Fj1dADKgiddkOKfKSQbnlXH6lS'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# एक्सचेंज सेटअप (IP 2409:40c2... के लिए तैयार)
exchange = ccxt.delta({
    'apiKey': API_KEY, 
    'secret': SECRET_KEY, 
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": message}
        requests.get(url, params=params)
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. लाइव बैलेंस और प्रॉफिट ट्रैकिंग ---
if 'start_balance' not in st.session_state:
    try:
        balance = exchange.fetch_balance()
        st.session_state.start_balance = balance['total'].get('USDT', 0.0)
    except: st.session_state.start_balance = 0.0

st.sidebar.title("💰 My Delta Wallet")
try:
    balance = exchange.fetch_balance()
    usdt_now = balance['total'].get('USDT', 0.0)
    today_profit = usdt_now - st.session_state.start_balance
    
    st.sidebar.metric("Live Balance", f"${usdt_now:.2f}")
    st.sidebar.metric("Today's Profit", f"${today_profit:.2f}")
    
    if usdt_now > 0:
        st.sidebar.success("✅ डेल्टा कनेक्टेड (Trading Active)")
    else:
        st.sidebar.warning("Wallet में फंड चेक करें।")
except:
    st.sidebar.error("कनेक्शन एरर: Keys या IP चेक करें।")

st.title("🛡️ Sailani AI: Power 15 Master")

# --- 3. Power 15 स्कैनिंग और ऑटो-ट्रेडिंग ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 ऑटो-ट्रेडिंग और स्कैनिंग चालू करें")

if auto_mode:
    status = st.empty()
    while auto_mode:
        for coin in power_15:
            try:
                ticker = exchange.fetch_ticker(coin)
                live_price = ticker['last']
                status.info(f"📡 लाइव स्कैनिंग: {coin} | भाव: {live_price}")
            except: continue
        time.sleep(10)
