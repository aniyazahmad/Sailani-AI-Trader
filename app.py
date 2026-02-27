import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. सेटिंग्स ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"})
        time.sleep(3)
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. पक्की याददाश्त (ताकि Target/SL मिस न हो) ---
if 'total_profit' not in st.session_state: st.session_state.total_profit = 0.0
if 'total_loss' not in st.session_state: st.session_state.total_loss = 0.0
if 'signal_count' not in st.session_state: st.session_state.signal_count = 0
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}

# --- 3. डैशबोर्ड पैनल ---
st.sidebar.markdown("### 💰 WALLET")
try:
    balance = exchange.fetch_balance()
    usdt = balance['total'].get('USDT', 0.0)
    st.sidebar.markdown(f"<h2 style='color: #00FF00;'>${usdt:.2f}</h2>", unsafe_allow_html=True)
except: st.sidebar.error("Delta Error")

st.markdown("### 📊 **DASHBOARD (Power 15)**")
c1, c2, c3 = st.columns(3)
c1.metric("Signals", st.session_state.signal_count)
c2.markdown(f"<span style='color:#00FF00; font-size:24px;'>Profit: +${st.session_state.total_profit:.2f}</span>", unsafe_allow_html=True)
c3.markdown(f"<span style='color:#FF4B4B; font-size:24px;'>Loss: -${st.session_state.total_loss:.2f}</span>", unsafe_allow_html=True)
st.divider()

# --- 4. पूरे 15 कॉइन्स (Power 15 List) ---
power_15 = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
    "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
    "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"
]

auto_mode = st.toggle("🚀 चालू करें: लाइव ऑटो-स्कैनिंग")

if auto_mode:
    status = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                price = df['close'].iloc[-1]
                ema = df['close'].ewm(span=20).mean().iloc[-1]

                # --- TARGET/SL चेक (जब तक हिट न हो, नया सिग्नल नहीं) ---
                if symbol in st.session_state.active_trades:
                    trade = st.session_state.active_trades[symbol]
                    
                    # Target हिट हुआ
                    if (trade['type'] == 'BUY' and price >= trade['tp']) or (trade['type'] == 'SHORT' and price <= trade['tp']):
                        st.session_state.total_profit += 1.20
                        send_telegram_msg(f"✅ TARGET HIT: {symbol}\n📊 EXIT: {price:.4f}\nRESULT: PROFIT 💰")
                        del st.session_state.active_trades[symbol]
                        continue
                    
                    # Stop Loss हिट हुआ
                    elif (trade['type'] == 'BUY' and price <= trade['sl']) or (trade['type'] == 'SHORT' and price >= trade['sl']):
                        st.session_state.total_loss += 0.60
                        send_telegram_msg(f"🛑 STOP LOSS HIT: {symbol}\n📊 EXIT: {price:.4f}\nRESULT: LOSS 🚨")
                        del st.session_state.active_logs[symbol]
                        del st.session_state.active_trades[symbol]
                        continue
                    
                    # जब तक ट्रेड चल रहा है, नया सिग्नल मत दो
                    continue

                # --- नया सिग्नल जनरेशन ---
                if price > ema and price > df['high'].iloc[-2]: # BUY
                    sl = round(price * 0.996, 4) # थोड़ा बड़ा SL ताकि बार-बार हिट न हो
                    tp = round(price * 1.012, 4)
                    st.session_state.active_trades[symbol] = {'type': 'BUY', 'tp': tp, 'sl': sl}
                    st.session_state.signal_count += 1
                    send_telegram_msg(f"🚀 <b>BUY: {symbol}</b>\nENTRY: {price:.4f}\n🛑 SL: {sl:.4f}\n🎯 TARGET: {tp:.4f}")

                elif price < ema and price < df['low'].iloc[-2]: # SHORT
                    sl = round(price * 1.004, 4)
                    tp = round(price * 0.988, 4)
                    st.session_state.active_trades[symbol] = {'type': 'SHORT', 'tp': tp, 'sl': sl}
                    st.session_state.signal_count += 1
                    send_telegram_msg(f"📉 <b>SHORT: {symbol}</b>\nENTRY: {price:.4f}\n🛑 SL: {sl:.4f}\n🎯 TARGET: {tp:.4f}")

                status.info(f"📡 स्कैनिंग 15 कॉइन्स: {symbol} | भाव: {price}")
                time.sleep(0.5)
            except: continue
        time.sleep(10)
