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
PROFIT_GOAL = 25.0 

# टेलीग्राम मैसेज भेजने का फंक्शन
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": message}
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        st.error(f"Telegram Error: {e}")
        return None

st.set_page_config(page_title="Sailani AI Ultimate", layout="centered")
st.title("🎯 Sailani AI: 50 Coin Scanner")

# सेटिंग्स
col1, col2 = st.columns(2)
with col1:
    leverage = st.number_input("Leverage (x)", 1, 50, 10)
with col2:
    amount = st.number_input("Trade Amount ($)", 10, value=50)

# 50 हाई वॉल्यूम कॉइन्स की लिस्ट
coin_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT", "DOGE/USDT", "ADA/USDT", "MATIC/USDT", "DOT/USDT", "TRX/USDT", "LTC/USDT", "SHIB/USDT", "AVAX/USDT", "LINK/USDT", "UNI/USDT", "ATOM/USDT", "ETC/USDT", "XLM/USDT", "BCH/USDT", "FIL/USDT", "LDO/USDT", "APT/USDT", "NEAR/USDT", "ARB/USDT", "OP/USDT", "GRT/USDT", "STX/USDT", "ICP/USDT", "RNDR/USDT", "INJ/USDT", "TIA/USDT", "SUI/USDT", "SEI/USDT", "ORDI/USDT", "PEPE/USDT", "FET/USDT", "AGIX/USDT", "GALA/USDT", "IMX/USDT", "KAS/USDT", "THETA/USDT", "VET/USDT", "EGLD/USDT", "MKR/USDT", "AAVE/USDT", "FLOW/USDT", "RUNE/USDT", "ALGO/USDT", "HBAR/USDT", "SAND/USDT"]

if 'active_trade' not in st.session_state: st.session_state.active_trade = None
if 'today_profit' not in st.session_state: st.session_state.today_profit = 0.0

auto_mode = st.toggle("🚀 50 Coin Auto-Scan चालू करें")

def scan_all_coins():
    for coin in coin_list:
        try:
            bars = exchange.fetch_ohlcv(coin, timeframe='5m', limit=50)
            df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
            
            # सुधार: यहाँ वेरिएबल का नाम 'last_price' रखा गया है
            last_price = df['close'].iloc[-1]
            prev_high = df['high'].iloc[-2]
            
            # लाइन 29 का फिक्स: यहाँ 'last_price' ही इस्तेमाल होगा
            if last_price > prev_high:
                sl = df['low'].rolling(window=5).min().iloc[-1]
                tp = last_price + (last_price - sl) * 3
                return {'symbol': coin, 'entry': last_price, 'sl': sl, 'tp': tp}
        except: continue
    return None

if auto_mode:
    status_box = st.empty()
    while auto_mode:
        if st.session_state.active_trade:
            trade = st.session_state.active_trade
            ticker = exchange.fetch_ticker(trade['symbol'])
            current = ticker['last']
            status_box.warning(f"⏳ {trade['symbol']} ट्रेड चालू है... Price: {current}")
            
            if current >= trade['tp'] or current <= trade['sl']:
                res = "🎯 TARGET HIT" if current >= trade['tp'] else "❌ SL HIT"
                send_telegram_msg(f"{res}!\nCoin: {trade['symbol']}\nFinal Price: {current}")
                st.session_state.active_trade = None
                st.rerun()
        else:
            status_box.info("🔍 सभी 50 कॉइन्स में बेस्ट सेटअप ढूंढ रहा हूँ...")
            signal = scan_all_coins()
            if signal:
                st.session_state.active_trade = signal
                # टेलीग्राम पर मैसेज भेजना
                msg = f"🚀 NEW SIGNAL FOUND!\nCoin: {signal['symbol']}\nEntry: {signal['entry']}\nSL: {signal['sl']}\nTarget: {signal['tp']}\nLeverage: {leverage}x"
                send_telegram_msg(msg)
                st.success(f"सिग्नल मिला: {signal['symbol']} - टेलीग्राम पर मैसेज भेज दिया गया है!")
                st.rerun()
        
        time.sleep(30) # हर 30 सेकंड में ऑटो-चेक
