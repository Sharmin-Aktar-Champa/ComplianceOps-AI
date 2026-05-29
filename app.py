import streamlit as st
import requests

st.title("🛡️ ComplianceOps AI")
user_query = st.text_input("Enter query")

if st.button("Check Compliance"):
    if user_query:
        url = "http://127.0.0.1:8000/query"
        payload = {"query": user_query}
        response = requests.post(url, json = payload)
        if response.status_code == 200:
            data = response.json()
            st.write(f"🎯 Route: {data['route']}")
            st.write(f"⏱️ Time: {data['time']} sec")
            st.info(data['answer'])
        


