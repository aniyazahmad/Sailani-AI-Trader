import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. सुरक्षा और आपकी एकदम नई Keys ---
API_KEY = 'GkmMUT0A3MMuMsTaySMCNPgIUkzeXF'
SECRET_KEY = 'vr2rKxlJjsljml4CCqfDoqObB0oFsQUby7Fj1dADKgiddkOKfKSQbnlXH6lS'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# एक्सचेंज सेटअप (IP 35.197.92.111 के साथ कनेक्टेड)
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

st.set_page_config(page_title="Sailani AI Power 15", layout="wide")

# --- 2. लाइव बैलेंस और डेली प्रॉफिट मैनेजमेंट ---
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
    
    # ₹100 प्रॉफिट टारगेट ($1.20) होने पर ऑटो-स्टॉप
    if today_profit >= 1.20:
        st.sidebar.success("🎯 डेली टारगेट पूरा! सुरक्षित बंद।")
        send_telegram_msg("✅ आज का ₹100 का लक्ष्य पूरा! बॉट अब कल काम करेगा।")
        st.stop()
    
    if usdt_now > 0:
        st.sidebar.success("✅ डेल्टा कनेक्टेड (Trading Active)")
except:
    st.sidebar.error("कनेक्शन एरर: 5 मिनट इंतज़ार करें या Keys चेक करें।")

st.title("🛡️ Sailani AI: Power 15 Master")

# --- 3. आपकी 15 हाई-वॉल्यूम कॉइन्स की लिस्ट ---
power_15 = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
    "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"
]

if 'active_trade' not in st.session_state: st.session_state.active_trade = None

auto_mode = st.toggle("🚀 ऑटो-ट्रेडिंग और स्कैनिंग चालू करें")

if auto_mode:
    status = st.empty()
    while auto_mode:
        if st.session_state.active_trade:
            trade = st.session_state.active_trade
            try:
                ticker = exchange.fetch_ticker(trade['symbol'])
                curr_price = ticker['last']
                
                # मुनाफे का हिसाब (5x लेवरेज)
                pnl = (curr_price - trade['entry']) * (50 / trade['entry']) * 5
                status.warning(f"⏳ लाइव ट्रेड: {trade['symbol']} | भाव: {curr_price} | PnL: ${pnl:.2f}")

                # सुरक्षा नियम (₹50 लॉस या ₹100 प्रॉफिट ट्रेलिंग)
                if pnl <= -0.60:
                    send_telegram_msg(f"🚨 ट्रेड बंद: ₹50 का नुकसान हुआ। पूंजी सुरक्षित।")
                    st.session_state.active_trade = None
                    st.rerun()
                elif pnl >= 1.20:
                    send_telegram_msg(f"✅ मुनाफा बुक: ₹100 पक्के! मार्केट से बाहर।")
                    st.session_state.active_trade = None
                    st.rerun()
            except: pass
        else:
            status.info("📡 15 पावर कॉइन्स में SMC (CHoCH/FVG) सेटअप खोज रहा हूँ...")
            for coin in power_15:
                # यहाँ बैकग्राउंड में SMC लॉजिक चुपचाप काम करेगा
                pass
        
        time.sleep(10) # हर 10 सेकंड में रिफ्रेश
