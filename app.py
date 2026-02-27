import streamlit as st
import ccxt
import pandas as pd
import requests
import time

# --- 1. सेटिंग्स और Keys ---
API_KEY = 'Q6TjQC8gjDUf2hSM4HXXmDf26E8G6w'
SECRET_KEY = 'aZzfh9m1J2Y3n88QZapvhPYwmXNVKUuEgigwmnbmfwlubFlwfw5GgEjs0i67'
TELEGRAM_TOKEN = '8555372861:AAET5vyB0myBGqJc0P3jvqN0xcDoVTX2cO8'
CHAT_ID = '7863674359'

# रिस्क मैनेजमेंट (₹500 = $6)
RISK_PER_TRADE_USD = 6.0 

@st.cache_resource
def init_servers():
    delta = ccxt.delta({'apiKey': API_KEY, 'secret': SECRET_KEY, 'enableRateLimit': True})
    binance = ccxt.binance()
    return delta, binance

delta_ex, bn_ex = init_servers()

def send_telegram_msg(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": f"<b>{message}</b>", "parse_mode": "HTML"})
    except: pass

st.set_page_config(page_title="Sailani AI: SMC Master", layout="wide")

# --- 2. SMC याददाश्त (Memory) ---
if 'profit' not in st.session_state: st.session_state.profit = 0.0
if 'loss' not in st.session_state: st.session_state.loss = 0.0
if 'active_trades' not in st.session_state: st.session_state.active_trades = {}
if 'sent_keys' not in st.session_state: st.session_state.sent_keys = set()

# --- 3. प्रोफेशनल डैशबोर्ड ---
st.title("🛡️ Sailani AI: Smart Money Concepts (SMC)")
c1, c2, c3 = st.columns(3)
c1.metric("Active Trades", len(st.session_state.active_trades))
c2.markdown(f"<h2 style='color:#00FF00;'>Profit: +${st.session_state.profit:.2f}</h2>", unsafe_allow_html=True)
c3.markdown(f"<h2 style='color:#FF4B4B;'>Loss: -${st.session_state.loss:.2f}</h2>", unsafe_allow_html=True)
st.divider()

# --- 4. पावर 15 एनालिसिस ---
power_15 = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "BNB/USDT", 
            "AVAX/USDT", "MATIC/USDT", "LINK/USDT", "ADA/USDT", "NEAR/USDT", 
            "SUI/USDT", "OP/USDT", "ARB/USDT", "ORDI/USDT"]

auto_mode = st.toggle("🚀 ACTIVATE SMC AUTO-TRADING")

if auto_mode:
    status = st.empty()
    while True:
        for sym in power_15:
            try:
                # बाइनेंस से डेटा (SMC के लिए अधिक डेटा चाहिए)
                bars = bn_ex.fetch_ohlcv(sym, timeframe='5m', limit=100)
                df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
                price = float(df['c'].iloc[-1])
                
                # SMC Indicators
                high_20 = df['h'].iloc[-20:-1].max()
                low_20 = df['l'].iloc[-20:-1].min()
                ema_50 = df['c'].ewm(span=50).mean().iloc[-1]

                # --- A. ट्रेड एग्जिट चेक ---
                if sym in st.session_state.active_trades:
                    t = st.session_state.active_trades[sym]
                    if (t['type'] == 'BUY' and price >= t['tp']) or (t['type'] == 'SHORT' and price <= t['tp']):
                        st.session_state.profit += (RISK_PER_TRADE_USD * 2) # 1:2 Reward
                        send_telegram_msg(f"✅ <b>TARGET HIT (SMC): {sym}</b>\n💰 PROFIT: +$12.00\n📊 EXIT: {price:.4f}")
                        del st.session_state.active_trades[sym]
                    elif (t['type'] == 'BUY' and price <= t['sl']) or (t['type'] == 'SHORT' and price >= t['sl']):
                        st.session_state.loss += RISK_PER_TRADE_USD
                        send_telegram_msg(f"🛑 <b>STOP LOSS HIT: {sym}</b>\n📉 LOSS: -${RISK_PER_TRADE_USD}\n📊 EXIT: {price:.4f}")
                        del st.session_state.active_trades[sym]
                    continue

                # --- B. SMC लॉजिक (CHoCH + Liquidity Sweep) ---
                time_key = f"{sym}_{df['t'].iloc[-1]}"
                if time_key in st.session_state.sent_keys: continue

                # BULLISH CHoCH + Liquidity Sweep (BUY)
                if price > high_20 and df['c'].iloc[-2] < high_20:
                    sl = low_20
                    tp = price + (price - sl) * 2
                    # ₹500 रिस्क के हिसाब से क्वांटिटी
                    qty = RISK_PER_TRADE_USD / (price - sl) if (price - sl) > 0 else 1
                    
                    delta_ex.create_market_buy_order(sym, qty)
                    st.session_state.active_trades[sym] = {'type':'BUY', 'tp':tp, 'sl':sl}
                    st.session_state.sent_keys.add(time_key)
                    send_telegram_msg(f"🚀 <b>SMC BUY (CHoCH): {sym}</b>\n💎 Order Block Entry: {price:.4f}\n🛑 SL: {sl:.4f}\n🎯 TP: {tp:.4f}")

                # BEARISH CHoCH + Liquidity Sweep (SHORT)
                elif price < low_20 and df['c'].iloc[-2] > low_20:
                    sl = high_20
                    tp = price - (sl - price) * 2
                    qty = RISK_PER_TRADE_USD / (sl - price) if (sl - price) > 0 else 1
                    
                    delta_ex.create_market_sell_order(sym, qty)
                    st.session_state.active_trades[sym] = {'type':'SHORT', 'tp':tp, 'sl':sl}
                    st.session_state.sent_signals.add(time_key)
                    send_telegram_msg(f"📉 <b>SMC SHORT (CHoCH): {sym}</b>\n💎 Order Block Entry: {price:.4f}\n🛑 SL: {sl:.4f}\n🎯 TP: {tp:.4f}")

                status.info(f"📡 SMC Scanning: {sym} | Price: {price:.4f}")
                time.sleep(1)
            except: continue
        time.sleep(10)
