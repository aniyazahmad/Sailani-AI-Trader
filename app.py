import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. नई चाबियाँ (अभी आपने जो जेनरेट की हैं) ---
API_KEY = 'dX1TLflRYcDYpT3nStONLYCnGMYGSp' 
SECRET_KEY = 'F0U6b7xsHryvmDoF6nCmVXhjV8nuYNcDlAAixu0PgniU5aHP5nP2vOZs69F0'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# रिस्क मैनेजमेंट (₹500 = $6)
RISK_PER_TRADE_USD = 6.0 

@st.cache_resource
def init_servers():
    # डेल्टा कनेक्शन (ट्रेडिंग के लिए)
    delta = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})
    # बाइनेंस (फ़ास्ट डेटा के लिए)
    binance = ccxt.binance()
    return delta, binance

delta_ex, bn_ex = init_servers()

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"})
    except: pass

st.set_page_config(page_title="Sailani AI: SMC Master", layout="wide")

# --- 2. बैलेंस और डेटा फिक्स ---
if 'profit' not in st.session_state: st.session_state.profit = 0.0
if 'loss' not in st.session_state: st.session_state.loss = 0.0
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}

# --- 3. रियल-टाइम बैलेंस डैशबोर्ड ---
st.title("🛡️ Sailani AI: SMC Master")
st.sidebar.markdown("### 💰 **LIVE BALANCE**")

try:
    # डेल्टा से असली बैलेंस खींचना
    balance_data = delta_ex.fetch_balance()
    wallet_bal = balance_data['total'].get('USDT', 0.0)
    st.sidebar.markdown(f"<h1 style='color: #00FF00;'>${wallet_bal:.2f}</h1>", unsafe_allow_True=True)
except Exception as e:
    st.sidebar.error("❌ डेल्टा से कनेक्ट नहीं हो पा रहा")

c1, c2, c3 = st.columns(3)
c1.metric("Active Trades", len(st.session_state.active_trades))
c2.markdown(f"<h2 style='color:#00FF00;'>Profit: +${st.session_state.profit:.2f}</h2>", unsafe_allow_html=True)
c3.markdown(f"<h2 style='color:#FF4B4B;'>Loss: -${st.session_state.loss:.2f}</h2>", unsafe_allow_html=True)

# --- 4. 15 कॉइन SMC स्कैनिंग ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "BNB/USDT", 
            "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT", "NEAR/USDT", 
            "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 ACTIVATE SMC AUTO-TRADING")

if auto_mode:
    status = st.empty()
    while True:
        for sym in power_15:
            try:
                # बाइनेंस से फ़ास्ट डेटा उठाना
                bars = bn_ex.fetch_ohlcv(sym, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
                price = float(df['c'].iloc[-1])
                
                # SMC लॉजिक (CHoCH और Liquidity)
                high_prev = df['h'].iloc[-20:-1].max()
                low_prev = df['l'].iloc[-20:-1].min()

                # टारगेट/SL चेक
                if sym in st.session_state.active_trades:
                    # (यहाँ पुराना टारगेट लॉजिक रहेगा)
                    continue

                # SMC एंट्री लॉजिक (₹500 रिस्क के साथ)
                if price > high_prev: # BULLISH CHoCH
                    sl = low_prev
                    qty = RISK_PER_TRADE_USD / (price - sl) if (price - sl) > 0 else 1
                    # डेल्टा पर असली ट्रेड
                    delta_ex.create_market_buy_order(sym, qty)
                    st.session_state.active_trades[sym] = {'type':'BUY', 'tp':price*1.02, 'sl':sl}
                    send_telegram_msg(f"🚀 <b>SMC BUY: {sym}</b>\n💎 Entry: {price}\n💰 Risk: ₹500")

                status.info(f"📡 SMC Scanning: {sym} | Price: {price:.4f}")
                time.sleep(1)
            except: continue
        time.sleep(10)
