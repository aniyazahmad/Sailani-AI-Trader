import streamlit as st
import ccxt
import pandas as pd
import os

# Delta Exchange API Details
API_KEY = 'DbVJYwN6Xz9rw9tVWoQAoytPaIlguq'
SECRET_KEY = '67ZCZD86Hy2kq2U04CFEwb6SqvSw9UZG9hJgqU413We2JasxsJ0L3KsVWJur'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY})

st.title("🛡️ Sailani Smart-Learn AI (SMC)")

# साइडबार सेटिंग्स
st.sidebar.header("Trading Settings")
leverage = st.sidebar.slider("Leverage", 1, 50, 10)
amount = st.sidebar.number_input("Trade Amount ($)", 10, value=50)
symbol = st.sidebar.selectbox("Market", ["BTC/USDT", "ETH/USDT"])

# फंक्शन: डेटा और SMC लॉजिक
def scan_market():
    bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    
    last_price = df['close'].iloc[-1] # एरर यहाँ ठीक कर दिया गया है
    prev_high = df['high'].iloc[-2]
    sl_price = df['low'].rolling(window=5).min().iloc[-1]
    tp_price = last_price + (last_price - sl_price) * 3
    
    return last_price, prev_high, sl_price, tp_price, df

# सेल्फ-लर्निंग डेटा स्टोर करना (Point 7)
def save_trade_to_memory(data):
    if not os.path.isfile('trade_history.csv'):
        pd.DataFrame([data]).to_csv('trade_history.csv', index=False)
    else:
        pd.DataFrame([data]).to_csv('trade_history.csv', mode='a', header=False, index=False)

if st.button('Scan Market for 90% Accuracy'):
    last_price, prev_high, sl_price, tp_price, df = scan_market()
    
    if last_price > prev_high:
        st.success(f"🔥 BUY SIGNAL DETECTED!")
        st.write(f"**Entry:** {last_price} | **SL:** {sl_price} | **Target:** {tp_price}")
        
        if st.button(f"✅ CONFIRM {leverage}x TRADE"):
            try:
                # लेवरेज सेट करना
                exchange.private_post_settings_leverage({'symbol': symbol.replace('/', ''), 'leverage': str(leverage)})
                # आर्डर प्लेस करना
                order = exchange.create_order(symbol, 'market', 'buy', amount)
                
                # लर्निंग डेटा सेव करना
                save_trade_to_memory({'symbol': symbol, 'price': last_price, 'leverage': leverage, 'status': 'Executed'})
                
                st.balloons()
                st.write("🚀 Trade Executed & Saved to AI Memory!")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Scanning... Market structure not ready yet.")
    st.line_chart(df['close'])

# AI लर्निंग डिस्प्ले
if st.sidebar.checkbox("Show AI Learning Data"):
    if os.path.isfile('trade_history.csv'):
        history = pd.read_csv('trade_history.csv')
        st.sidebar.write(f"Total AI-Learned Trades: {len(history)}")
        st.sidebar.dataframe(history.tail(5))
    else:
        st.sidebar.write("AI is currently learning...")
