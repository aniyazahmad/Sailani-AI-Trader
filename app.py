import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. आपकी Keys और सेटिंग्स ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

exchange = ccxt.delta({
    'apiKey': API_KEY, 'secret': SECRET_KEY,
    'enableRateLimit': True, 'options': {'defaultType': 'future'}
})

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": message})
    except: pass

st.set_page_config(page_title="Sailani AI Pro Trader", layout="wide")
st.title("🛡️ Sailani AI Master: Entry/Exit System")

# --- 2. ट्रेड ट्रैकिंग सिस्टम (ताकि बार-बार सिग्नल न आए) ---
if 'active_trades' not in st.session_state:
    st.session_state.active_trades = {} # यहाँ चल रहे ट्रेड्स जमा होंगे

power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", 
            "BNB/USDT", "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT",
            "NEAR/USDT", "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 लाइव ऑटो-स्कैनिंग और ट्रेडिंग चालू करें")

if auto_mode:
    status_box = st.empty()
    while auto_mode:
        for symbol in power_15:
            try:
                # मार्केट डेटा फेच करना
                bars = exchange.fetch_ohlcv(symbol, timeframe='5m', limit=50)
                df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
                current_price = df['close'].iloc[-1]

                # अगर इस कॉइन में पहले से ट्रेड चल रहा है, तो उसका रिजल्ट चेक करें
                if symbol in st.session_state.active_trades:
                    trade = st.session_state.active_trades[symbol]
                    
                    # Target हिट हुआ?
                    if current_price >= trade['target']:
                        msg = f"✅ TARGET HIT: {symbol}\nProfit: {trade['target']}\nExit Price: {current_price}"
                        send_telegram_msg(msg)
                        del st.session_state.active_trades[symbol] # लिस्ट से हटाएं
                    
                    # Stop Loss हिट हुआ?
                    elif current_price <= trade['sl']:
                        msg = f"🚨 STOP LOSS HIT: {symbol}\nLoss at: {trade['sl']}\nExit Price: {current_price}"
                        send_telegram_msg(msg)
                        del st.session_state.active_trades[symbol] # लिस्ट से हटाएं
                    
                    continue # जब तक फैसला न हो, नया सिग्नल नहीं ढूंढना

                # --- 3. नया सिग्नल ढूंढने का लॉजिक (Entry/SL/TP) ---
                ema_20 = df['close'].ewm(span=20).mean().iloc[-1]
                
                if current_price > ema_20 and current_price > df['high'].iloc[-2]:
                    # एंट्री, एसएल और टारगेट कैलकुलेशन
                    entry_price = current_price
                    stop_loss = df['low'].iloc[-3] # पिछली 3 कैंडल का लो
                    target_price = entry_price + (entry_price - stop_loss) * 2 # 1:2 रिस्क रिवॉर्ड

                    # ट्रेड को रजिस्टर करें
                    st.session_state.active_trades[symbol] = {
                        'entry': entry_price, 'sl': stop_loss, 'target': target_price
                    }

                    # टेलीग्राम मैसेज
                    signal_msg = (f"🔥 NEW SIGNAL: {symbol}\n\n"
                                  f"➡️ Entry: {entry_price}\n"
                                  f"🛑 Stop Loss: {stop_loss}\n"
                                  f"🎯 Target: {target_price}")
                    send_telegram_msg(signal_msg)
                    st.success(f"Signal sent for {symbol}")

                status_box.info(f"📡 स्कैनिंग: {symbol} | भाव: {current_price} | एक्टिव ट्रेड्स: {len(st.session_state.active_trades)}")
                time.sleep(1)

            except: continue
        
        time.sleep(10) # पूरी लिस्ट स्कैन करने के बाद ब्रेक
