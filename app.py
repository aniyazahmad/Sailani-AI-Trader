import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# 1. डेटा कनेक्शन (Delta Exchange)
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": message}
        requests.get(url, params=params)
    except: pass

st.set_page_config(page_title="Sailani AI Real-Time", layout="wide")
st.title("⚡ Sailani AI: Live Market Engine")

# --- लाइव बैलेंस और ऑटो-रीस्टार्ट लॉजिक ---
if 'start_balance' not in st.session_state:
    try:
        balance = exchange.fetch_balance()
        st.session_state.start_balance = balance['total'].get('USDT', 0.0)
    except: st.session_state.start_balance = 0.0

try:
    balance = exchange.fetch_balance()
    usdt_now = balance['total'].get('USDT', 0.0)
    today_profit = usdt_now - st.session_state.start_balance
    
    st.sidebar.metric("💰 Live Wallet", f"${usdt_now:.2f}")
    st.sidebar.metric("📈 Today's Gain", f"${today_profit:.2f}")

    # ₹100 प्रॉफिट होने पर ऑटो-स्टॉप ($1.20)
    if today_profit >= 1.20:
        send_telegram_msg("✅ टारगेट पूरा! ₹100 मुनाफ़ा लेकर आज का काम बंद।")
        st.stop()
except: pass

auto_mode = st.toggle("🚀 लाइव स्कैनिंग शुरू करें")
power_coins = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "MATIC/USDT"]

if 'active_trade' not in st.session_state: st.session_state.active_trade = None

if auto_mode:
    status = st.empty()
    while auto_mode:
        if st.session_state.active_trade:
            trade = st.session_state.active_trade
            try:
                # लाइव भाव डायरेक्ट एक्सचेंज से
                ticker = exchange.fetch_ticker(trade['symbol'])
                curr_price = ticker['last']
                
                # मुनाफे का हिसाब (5x लेवरेज के साथ)
                live_pnl = (curr_price - trade['entry']) * (50 / trade['entry']) * 5
                
                status.warning(f"⏳ लाइव ट्रेड: {trade['symbol']} | भाव: {curr_price} | PnL: ${live_pnl:.2f}")

                # 1. ₹50 का सुरक्षा कवच (Loss Limit)
                if live_pnl <= -0.60:
                    send_telegram_msg(f"🚨 ट्रेड क्लोज: ₹50 का नुकसान हुआ। पूंजी बचाने के लिए बाहर।")
                    st.session_state.active_trade = None
                    st.rerun()

                # 2. ₹100 पर ट्रेलिंग (Trailing SL)
                if live_pnl >= 1.20:
                    if trade['sl'] < trade['entry']:
                        trade['sl'] = trade['entry']
                        send_telegram_msg(f"📈 मुनाफा लॉक: ₹100 पक्के!")
                    
                    # मुनाफे का पीछा करना
                    new_sl = curr_price - (curr_price * 0.005)
                    if new_sl > trade['sl']: trade['sl'] = new_sl

                # 3. एग्जिट चेक
                if curr_price <= trade['sl']:
                    send_telegram_msg(f"✅ ट्रेड क्लोज: मुनाफा बुक किया गया।")
                    st.session_state.active_trade = None
                    st.rerun()
            except: pass
        else:
            status.info("📡 लाइव मार्केट स्कैन हो रहा है... सही मौके का इंतज़ार है।")
            # यहाँ आपका SMC लॉजिक लाइव डेटा पर काम करेगा
            # सिग्नल मिलने पर st.session_state.active_trade अपडेट होगा
        
        time.sleep(10) # हर 10 सेकंड में रिफ्रेश
