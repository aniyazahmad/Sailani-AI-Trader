import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# 1. कॉन्फ़िगरेशन (Delta & Telegram)
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})

# मुनाफे का लक्ष्य
PROFIT_GOAL = 25.0 

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url)
    except:
        pass

st.set_page_config(page_title="Sailani AI Pro", layout="centered")
st.title("🤖 Sailani AI: Smart Money Trader")

# सेशन स्टेट में आज का प्रॉफिट ट्रैक करना
if 'today_profit' not in st.session_state:
    st.session_state.today_profit = 0.0

# साइडबार में जानकारी
st.sidebar.header("Daily Tracking")
st.sidebar.write(f"💰 आज का मुनाफा: ${st.session_state.today_profit}")
st.sidebar.write(f"🎯 लक्ष्य: ${PROFIT_GOAL}")

if st.session_state.today_profit >= PROFIT_GOAL:
    st.balloons()
    st.success("🎉 मुबारक हो! आज का $25 का लक्ष्य पूरा हुआ। ट्रेडिंग अब कल करेंगे।")
    auto_mode = False
else:
    auto_mode = st.toggle("🚀 Auto-Scan Mode चालू करें")

# सेटिंग्स
symbol = st.selectbox("🎯 कॉइन चुनें", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
leverage = st.slider("Leverage (x)", 1, 50, 10)
amount = st.number_input("Amount ($)", 10, value=50)

def analyze_market():
    # Multi-Timeframe Analysis
    bars_15m = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50)
    df_15m = pd.DataFrame(bars_15m, columns=['t', 'o', 'h', 'l', 'c', 'v'])
    
    bars_5m = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
    df_5m = pd.DataFrame(bars_5m, columns=['t', 'o', 'h', 'l', 'c', 'v'])
    
    trend_up = df_15m['c'].iloc[-1] > df_15m['c'].iloc[-15] # 15 मिनट का ट्रेंड
    choch = df_5m['c'].iloc[-1] > df_5m['h'].iloc[-2] # 5 मिनट का ब्रेकआउट
    
    if trend_up and choch:
        entry = df_5m['c'].iloc[-1]
        sl = df_5m['l'].rolling(window=5).min().iloc[-1]
        tp = entry + (entry - sl) * 3
        return True, entry, sl, tp
    return False, 0, 0, 0

# ऑटो-स्कैनिंग लॉजिक
if auto_mode:
    st.warning(f"⚠️ ऑटो-स्कैन चालू है। ${PROFIT_GOAL} तक पहुँचते ही यह रुक जाएगा।")
    placeholder = st.empty()
    
    while auto_mode:
        # अगर बीच में लक्ष्य पूरा हो जाए
        if st.session_state.today_profit >= PROFIT_GOAL:
            st.rerun()
            
        is_signal, entry, sl, tp = analyze_market()
        
        if is_signal:
            msg = f"✅ HIGH ACCURACY SIGNAL!\nCoin: {symbol}\nPrice: {entry}\nSL: {sl}\nTarget: {tp}"
            placeholder.success(msg)
            send_telegram_msg(msg)
            # 5 मिनट का ब्रेक (Anti-Block)
            time.sleep(300) 
        else:
            placeholder.info(f"[{time.strftime('%H:%M:%S')}] मार्केट स्कैन हो रहा है... सही मौके का इंतज़ार है।")
            time.sleep(30) # हर 30 सेकंड में चेक
else:
    if st.session_state.today_profit < PROFIT_GOAL:
        st.info("ऑटो-स्कैन बंद है।")
