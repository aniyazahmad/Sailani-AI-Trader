import streamlit as st
import ccxt
import pandas as pd
import requests

# 1. आपकी Delta Exchange और Telegram की जानकारी
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})

# टेलीग्राम पर मैसेज भेजने का फंक्शन
def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        requests.get(url)
    except:
        pass

st.set_page_config(page_title="Sailani AI Trader", layout="centered")
st.title("🚀 Sailani AI: Smart Money Trader")

# कॉइन्स की लिस्ट और सेटिंग्स
coin_list = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"]
symbol = st.selectbox("🎯 ट्रेड के लिए कॉइन चुनें", coin_list)

col1, col2 = st.columns(2)
with col1:
    leverage = st.number_input("Leverage (x)", 1, 50, 10)
with col2:
    amount = st.number_input("Amount ($)", 10, value=50)

if st.button('🔥 SCAN MARKET NOW'):
    bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    
    last_price = df['close'].iloc[-1]
    prev_high = df['high'].iloc[-2]
    sl_price = df['low'].rolling(window=5).min().iloc[-1]
    tp_price = last_price + (last_price - sl_price) * 3

    if last_price > prev_high:
        msg = f"🚀 SAILANI AI SIGNAL:\n\nCoin: {symbol}\nAction: BUY\nPrice: {last_price}\nSL: {sl_price}\nTarget: {tp_price}\nLeverage: {leverage}x"
        st.success("🔥 BUY SIGNAL DETECTED!")
        st.write(msg)
        
        # टेलीग्राम पर अलर्ट भेजें
        send_telegram_msg(msg)
        
        if st.button(f"✅ CONFIRM {leverage}x TRADE"):
            try:
                exchange.private_post_settings_leverage({'symbol': symbol.replace('/', ''), 'leverage': str(leverage)})
                order = exchange.create_order(symbol, 'market', 'buy', amount)
                st.balloons()
                st.write("✅ Order Success!")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Scanning... Market structure is not ready for 90% accuracy yet.")
    
    st.line_chart(df['close'])
