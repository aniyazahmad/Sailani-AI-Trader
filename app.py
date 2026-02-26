import streamlit as st
import ccxt

# आपकी 'Sailani_Final' वाली नई चाबियाँ (बिना IP वाली)
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'

# एक्सचेंज सेटअप
exchange = ccxt.delta({
    'apiKey': API_KEY, 
    'secret': SECRET_KEY, 
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

st.sidebar.title("💰 My Delta Wallet")

# बैलेंस चेक करने की कोशिश
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    st.sidebar.metric("Live Balance", f"${usdt_val:.2f}")
    st.sidebar.success("✅ डेल्टा कनेक्टेड!")
except Exception as e:
    st.sidebar.error("कनेक्शन फेल: 5 मिनट इंतज़ार करें।")

st.title("🛡️ Sailani AI Master")
st.info("बैलेंस लोड होने में थोड़ा समय लग सकता है।")
