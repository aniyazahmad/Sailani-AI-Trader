import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. आपकी नई और सटीक Keys (Sailani_Final) ---
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

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": message})
    except: pass

st.set_page_config(page_title="Sailani AI Pro", layout="wide")

# --- 2. साइडबार बैलेंस (बड़े फॉन्ट में) ---
st.sidebar.markdown("## 💰 **MY WALLET**")
try:
    balance = exchange.fetch_balance()
    usdt_val = balance['total'].get('USDT', 0.0)
    # बैलेंस को बड़ा और चमकीला (Green) दिखाने के लिए
    st.sidebar.markdown(f"<h1 style='color: #00ff00;'>${usdt_val:.2f}</h1>", unsafe_allow_html=True)
    st.sidebar.success("✅ DELTA CONNECTED")
except:
    st.sidebar.error("❌ CONNECTION ERROR")
    st.sidebar.info("डेल्टा में जाकर चेक करें कि IP Whitelist खाली है या नहीं।")

st.title("🛡️ Sailani AI: Power 15 Master")

# --- 3. सिग्नल डिस्प्ले सेटिंग्स (Bold & Large) ---
if 'active_trades' not in st.session_state:
    st.session_state.active_trades = {}

power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 चालू करें: लाइव ऑटो-स्कैनिंग")

if auto_mode:
    display_area = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                current_price = df['close'].iloc[-1]

                # ट्रैकिंग चेक (Target/SL)
                if symbol in st.session_state.active_trades:
                    trade = st.session_state.active_trades[symbol]
                    if current_price >= trade['target'] or current_price <= trade['sl']:
                        result = "PROFIT ✅" if current_price >= trade['target'] else "LOSS 🚨"
                        send_telegram_msg(f"🏁 TRADE CLOSED: {symbol}\nResult: {result}")
                        del st.session_state.active_trades[symbol]
                    continue

                # सिग्नल लॉजिक
                ema = df['close'].ewm(span=20).mean().iloc[-1]
                
                # BUY सिग्नल
                if current_price > ema and current_price > df['high'].iloc[-2]:
                    entry = current_price
                    sl = df['low'].iloc[-3]
                    tp = entry + (entry - sl) * 2
                    
                    st.session_state.active_trades[symbol] = {'target': tp, 'sl': sl}
                    
                    # स्क्रीन पर बड़ा और बोल्ड दिखाना
                    msg_html = f"""
                    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00ff00;">
                        <h2 style="color: #00ff00; margin: 0;">🚀 SIGNAL: <span style="font-size: 50px;">BUY</span></h2>
                        <h1 style="font-size: 60px; color: white;">{symbol}</h1>
                        <p style="font-size: 30px; color: #00ff00;"><b>ENTRY: {entry:.4f}</b></p>
                        <p style="font-size: 25px; color: #ff4b4b;">SL: {sl:.4f} | TP: {tp:.4f}</p>
                    </div>
                    """
                    st.markdown(msg_html, unsafe_allow_html=True)
                    send_telegram_msg(f"🚀 BUY SIGNAL: {symbol}\nEntry: {entry}\nSL: {sl}\nTP: {tp}")

                # SHORT सिग्नल
                elif current_price < ema and current_price < df['low'].iloc[-2]:
                    entry = current_price
                    sl = df['high'].iloc[-3]
                    tp = entry - (sl - entry) * 2
                    
                    st.session_state.active_trades[symbol] = {'target': tp, 'sl': sl}
                    
                    msg_html = f"""
                    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #ff4b4b;">
                        <h2 style="color: #ff4b4b; margin: 0;">📉 SIGNAL: <span style="font-size: 50px;">SHORT</span></h2>
                        <h1 style="font-size: 60px; color: white;">{symbol}</h1>
                        <p style="font-size: 30px; color: #ff4b4b;"><b>ENTRY: {entry:.4f}</b></p>
                        <p style="font-size: 25px; color: #00ff00;">SL: {sl:.4f} | TP: {tp:.4f}</p>
                    </div>
                    """
                    st.markdown(msg_html, unsafe_allow_html=True)
                    send_telegram_msg(f"📉 SHORT SIGNAL: {symbol}\nEntry: {entry}\nSL: {sl}\nTP: {tp}")

                time.sleep(0.5)
            except: continue
        time.sleep(10)
