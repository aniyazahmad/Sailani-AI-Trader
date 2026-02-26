import streamlit as st
import requests

# यह लाइन आपके सॉफ्टवेयर का सर्वर IP बताएगी
try:
    server_ip = requests.get('https://api.ipify.org').text
    st.title("🌐 आपके बॉट का IP एड्रेस")
    st.code(server_ip)
    st.info("ऊपर दिए गए नंबर को कॉपी करें और डेल्टा में डालें।")
except:
    st.error("IP नहीं मिल पाया")
