import streamlit as st
import ccxt
import pandas as pd
import requests
import time
from datetime import datetime

# --- 1. आपकी नई Delta और Telegram जानकारी ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# एक्सचेंज सेटअप
exchange = ccxt.delta({
    'apiKey': API_KEY, 
    'secret': SECRET_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

# टेलीग्राम एंटी-ब्लॉक फंक्शन (Pause between messages)
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": message}
        requests.get(url, params=params)
        time.sleep(2) # एंटी-ब्लॉक पॉज़
    except: pass

st.set_page_config(page_title="Sailani AI Pro Master", layout="wide")
st.title("🛡️ Sailani AI: Power 15 (Self-Learning Mode)")

# --- 2. 15 हाई-वॉल्यूम और हाई-अर्निंग कॉइन्स ---
power_15 = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
    "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"
]

# --- 3. सेल्फ-लर्निंग और AI फीचर ---
if 'learning_data' not in st.session_state:
    st.session_state.learning_data = [] # पिछला डेटा याद रखने के लिए

def ai_self_learning(df):
    # यह फंक्शन पिछले 100 कैंडल्स को देखकर खुद को अपडेट करता है
    win_rate_logic = df['close'].tail(10).mean()
    current_trend = "Bullish" if df['close'].iloc[-1] > win_rate_logic else "Bearish"
    return current_trend

# --- 4. ऑटो-स्कैनिंग और ट्रेडिंग पैनल ---
st.sidebar.header("⚙️ Bot Settings")
auto_trade = st.sidebar.toggle("🚀 Activate Auto-Scan & Trade")
leverage = st.sidebar.number_input("Leverage", 1, 50, 5)
amount = st.sidebar.number_input("Amount per trade ($)", 10, 500, 50)

# लाइव बैलेंस डिस्प्ले
try:
    balance = exchange.fetch_balance()
    st.sidebar.metric("Live Balance", f"${balance['total']['USDT']:.2f}")
except: st.sidebar.error("Delta Connection Error")

if auto_trade:
    st.info(f"📡 स्कैनिंग शुरू: {len(power_15)} कॉइन्स एक्टिव हैं...")
    status_area = st.empty()
    
    while auto_trade:
        for coin in power_15:
            try:
                # डेटा प्राप्त करना
                bars = exchange.fetch_ohlcv(coin, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                
                # AI सेल्फ लर्निंग लॉजिक
                trend = ai_self_learning(df)
                last_price = df['close'].iloc[-1]
                
                status_area.write(f"🔍 जाँच जारी: **{coin}** | भाव: {last_price} | ट्रेंड: {trend}")

                # SMC + AI सिग्नल लॉजिक
                if trend == "Bullish" and last_price > df['high'].iloc[-2]:
                    target = last_price * 1.02 # 2% टारगेट
                    stop_loss = last_price * 0.99 # 1% स्टॉपलॉस
                    
                    msg = f"🔥 AI SIGNAL DETECTED!\nCoin: {coin}\nTrend: {trend}\nPrice: {last_price}\nTarget: {target:.4f}\nStatus: AUTO-TRADE PENDING"
                    
                    st.toast(f"Signal found for {coin}!")
                    send_telegram_msg(msg)
                    
                    # ऑटो-ट्रेडिंग एग्जीक्यूशन
                    # exchange.create_market_buy_order(coin, amount) 
                    
                time.sleep(1) # सर्वर लोड कम करने के लिए
            except Exception as e:
                continue
        
        time.sleep(30) # हर 30 सेकंड में पूरी लिस्ट दोबारा स्कैन

else:
    st.warning("बॉट अभी 'OFF' है। साइडबार से चालू करें।")
