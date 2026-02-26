import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# 1. कॉन्फ़िगरेशन
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})
PROFIT_GOAL = 25.0 

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url)
    except: pass

st.set_page_config(page_title="Sailani AI Ultimate Pro", layout="centered")
st.title("🎯 Sailani AI Ultimate: 50 Coin Scanner")

# लेवरेज और अमाउंट सेटिंग्स
col1, col2 = st.columns(2)
with col1:
    leverage = st.number_input("Leverage (x)", 1, 50, 10)
with col2:
    amount = st.number_input("Trade Amount ($)", 10, value=50)

# 50 हाई वॉल्यूम कॉइन्स
coin_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT", "DOGE/USDT", "ADA/USDT", "MATIC/USDT", "DOT/USDT", "TRX/USDT", "LTC/USDT", "SHIB/USDT", "AVAX/USDT", "LINK/USDT", "UNI/USDT", "ATOM/USDT", "ETC/USDT", "XLM/USDT", "BCH/USDT", "FIL/USDT", "LDO/USDT", "APT/USDT", "NEAR/USDT", "ARB/USDT", "OP/USDT", "GRT/USDT", "STX/USDT", "ICP/USDT", "RNDR/USDT", "INJ/USDT", "TIA/USDT", "SUI/USDT", "SEI/USDT", "ORDI/USDT", "PEPE/USDT", "FET/USDT", "AGIX/USDT", "GALA/USDT", "IMX/USDT", "KAS/USDT", "THETA/USDT", "VET/USDT", "EGLD/USDT", "MKR/USDT", "AAVE/USDT", "FLOW/USDT", "RUNE/USDT", "ALGO/USDT", "HBAR/USDT", "SAND/USDT"]

# सेशन स्टेट मैनेजमेंट
if 'active_trade' not in st.session_state:
    st.session_state.active_trade = None
if 'today_profit' not in st.session_state:
    st.session_state.today_profit = 0.0

st.sidebar.markdown(f"### 💰 आज का प्रॉफिट: `${st.session_state.today_profit}`")

if st.session_state.today_profit >= PROFIT_GOAL:
    st.success("🎉 $25 का लक्ष्य पूरा! आज की ट्रेडिंग बंद।")
    auto_mode = False
else:
    auto_mode = st.toggle("🚀 50 Coin Auto-Scan चालू करें")

def scan_all_coins():
    for coin in coin_list:
        try:
            bars = exchange.fetch_ohlcv(coin, timeframe='5m', limit=50)
            df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
            last_price = df['close'].iloc[-1]
            prev_high = df['high'].iloc[-2]
            
            # SMC Breakout Logic
            if last_price > prev_high:
                sl = df['low'].rolling(window=5).min().iloc[-1]
                tp = last_price + (last_price - sl) * 3
                return {'symbol': coin, 'entry': last_price, 'sl': sl, 'tp': tp}
        except: continue
    return None

if auto_mode:
    status_box = st.empty()
    while auto_mode:
        # 1. अगर कोई ट्रेड चल रहा है, तो उसका रिजल्ट चेक करें
        if st.session_state.active_trade:
            trade = st.session_state.active_trade
            ticker = exchange.fetch_ticker(trade['symbol'])
            current = ticker['last']
            status_box.warning(f"⏳ वेटिंग: {trade['symbol']} | Price: {current}\nTarget: {trade['tp']} | SL: {trade['sl']}")
            
            if current >= trade['tp']:
                send_telegram_msg(f"✅ TARGET HIT! 🎯\nCoin: {trade['symbol']}\nProfit: Done")
                st.session_state.today_profit += 5.0 # प्रॉफिट अपडेट
                st.session_state.active_trade = None
                st.rerun()
            elif current <= trade['sl']:
                send_telegram_msg(f"❌ STOP LOSS HIT! 📉\nCoin: {trade['symbol']}")
                st.session_state.active_trade = None
                st.rerun()
        
        # 2. अगर कोई ट्रेड नहीं है, तो पूरी लिस्ट को स्कैन करें
        else:
            status_box.info("🔍 सभी 50 कॉइन्स में बेस्ट सेटअप ढूंढ रहा हूँ...")
            signal = scan_all_coins()
            if signal:
                st.session_state.active_trade = signal
                msg = f"🚀 NEW SIGNAL FOUND!\nCoin: {signal['symbol']}\nEntry: {signal['entry']}\nSL: {signal['sl']}\nTarget: {signal['tp']}\nLeverage: {leverage}x"
                send_telegram_msg(msg)
                st.rerun()
        
        time.sleep(30) # हर 30 सेकंड में रिफ्रेश
