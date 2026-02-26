import streamlit as st
import ccxt
import time

# --- आपकी नई लाइव Keys (100% सटीक) ---
API_KEY = 'PGGavj1fLP94pGaWixOmLzYB5pqvz2'
SECRET_KEY = 'YrbuAPll5UVtR2vS3mG2RtqrHlGyKpkbfjrFeldkBvqTAVyXqdLJhHJrTVMy'

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
    if usdt_val >= 0:
        st.sidebar.metric("Live Balance", f"${usdt_val:.2f}")
        st.sidebar.success("✅ डेल्टा कनेक्टेड (Trading Active)")
except Exception as e:
    st.sidebar.error("कनेक्शन एरर: 10 मिनट इंतज़ार करें या IP चेक करें।")

st.title("🛡️ Sailani AI: Power 15 Master")

# आपकी 15 कॉइन्स की लिस्ट
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 ऑटो-ट्रेडिंग और स्कैनिंग शुरू करें")

if auto_mode:
    status = st.empty()
    while auto_mode:
        for coin in power_15:
            try:
                ticker = exchange.fetch_ticker(coin)
                status.info(f"📡 लाइव स्कैनिंग: {coin} | भाव: {ticker['last']}")
            except: continue
        time.sleep(10)
