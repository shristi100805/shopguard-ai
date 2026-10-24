import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from src.predict import predict

st.title("Text Check")
text = st.text_area("Paste text from a shopping website", height=120)

if st.button("Check"):
    if text.strip():
        with st.spinner("Checking..."):
            r = predict([text])[0]
        if r["label"] == "No Dark Pattern":
            st.success("No clear dark pattern found")
        else:
            st.error(f"Possible dark pattern: {r['label']}")
        st.write(f"Model confidence: {r['confidence']:.0%}")
    else:
        st.warning("Please paste some text first.")