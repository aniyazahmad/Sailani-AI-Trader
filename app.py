import streamlit as st
import ccxt
import pandas as pd

# आपकी Delta Exchange की चाबियाँ
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'

st.title("🚀 Sailani AI Trader (SMC)")
exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})

symbol = st.selectbox("Market", ["BTC/USDT", "ETH/USDT"])

if st.button('Scan Market'):
    bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    
    # SMC Logic: Trend check
    if df['close'].iloc[-1] > df['high'].iloc[-2]:
        st.success("🔥 BUY SIGNAL DETECTED!")
    else:
        st.info("Scanning...")
    st.line_chart(df['close'])
  
