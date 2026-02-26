import streamlit as st
import ccxt
import time

# --- आपकी नई लाइव Keys ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'

exchange = ccxt.delta({
    'apiKey': API_KEY, 
    'secret': SECRET_KEY, 
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

st.set_page_config(page_title="Sailani AI Power 15", layout="wide")
st.sidebar.title("💰 My Delta Wallet")

# लाइव बैलेंस चेक
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    st.sidebar.metric("Live Balance", f"${usdt_val:.2f}")
    st.sidebar.success("✅ डेल्टा कनेक्टेड!")
except Exception as e:
    st.sidebar.error("अभी 5 मिनट इंतज़ार करें, डेल्टा चाबी एक्टिव कर रहा है।")

st.title("🛡️ Sailani AI: Power 15 Master")

power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 ऑटो-स्कैनिंग चालू करें")

if auto_mode:
    status = st.empty()
    while auto_mode:
        for coin in power_15:
            try:
                ticker = exchange.fetch_ticker(coin)
                status.info(f"📡 लाइव स्कैनिंग: {coin} | भाव: {ticker['last']}")
            except: continue
        time.sleep(10)
