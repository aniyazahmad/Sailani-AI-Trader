import streamlit as st
import requests

# यह कोड आपके क्लाउड सर्वर की असली IP पता लगाएगा
try:
    server_ip = requests.get('https://api.ipify.org').text
except:
    server_ip = "IP नहीं मिल पाई, इंटरनेट चेक करें"

st.set_page_config(page_title="Sailani AI: IP Finder")
st.title("🛡️ Sailani AI: Server IP Registration")

st.markdown("### 1️⃣ आपकी सर्वर IP यहाँ है:")
st.code(server_ip, language='text')

st.markdown("""
### 2️⃣ अगला कदम (डेल्टा एक्सचेंज में):
1. डेल्टा एक्सचेंज के **API Settings** में जाएँ।
2. पुरानी Keys हटाकर **New API Key** बनाएँ।
3. **Whitelisted IP** वाले बॉक्स में ऊपर दी गई IP पेस्ट करें।
4. **Permissions** में 'Read' और 'Trade' दोनों को टिक (Check) करें।
5. नई **API Key** और **Secret Key** मुझे यहाँ बताएँ।
""")

if st.button("🔄 IP फिर से चेक करें"):
    st.rerun()
