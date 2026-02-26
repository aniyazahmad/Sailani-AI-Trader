import streamlit as st
import ccxt
import pandas as pd

# Delta Exchange API Details
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})

st.title("🛡️ Sailani Safe-Trade AI (With Leverage)")

# साइडबार में लेवरेज और रिस्क मैनेजमेंट
st.sidebar.header("Trading Settings")
leverage = st.sidebar.slider("Select Leverage", min_value=1, max_value=50, value=10) # लेवरेज सेट करें
amount = st.sidebar.number_input("Trade Amount ($)", min_value=10, value=50)
symbol = st.sidebar.selectbox("Select Coin", ["BTC/USDT", "ETH/USDT"])

if st.button('Scan Market for SMC Setup'):
    # डेटा और SMC लॉजिक
    bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    
    last_price = df['close'].iloc[-1]
    prev_high = df['high'].iloc[-2]
    sl_price = df['low'].rolling(window=5).min().iloc[-1]
    
    # SMC Signal Detection
    if last_close > prev_high:
        st.success(f"🔥 BUY SIGNAL DETECTED for {symbol}!")
        st.write(f"Leverage: {leverage}x | Entry: {last_price} | SL: {sl_price}")
        
        # कन्फर्मेशन बटन
        if st.button(f"✅ CONFIRM {leverage}x TRADE"):
            try:
                # 1. पहले लेवरेज सेट करना (Leverage Setting)
                exchange.private_post_settings_leverage({
                    'symbol': symbol.replace('/', ''),
                    'leverage': str(leverage)
                })
                
                # 2. फिर आर्डर प्लेस करना
                order = exchange.create_order(symbol, 'market', 'buy', amount)
                st.balloons()
                st.write(f"🚀 {leverage}x Trade Executed on Delta Exchange!")
            except Exception as e:
                st.error(f"Error: {e}")
