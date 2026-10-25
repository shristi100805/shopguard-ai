import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from src.predict import predict
from src.basket_rules import check_text
from src.explain import explain

st.title("Text Check")
text = st.text_area("Paste text from a shopping website", height=120)
use_ai = st.checkbox("Also explain with AI")

if st.button("Check"):
    if text.strip():
        with st.spinner("Checking..."):
            r = predict([text])[0]
        sneak = check_text(text)
        if sneak:
            category = "Basket Sneaking"
            st.error("Possible dark pattern: Basket Sneaking")
            st.write(sneak["reason"])
        elif r["label"] == "No Dark Pattern":
            category = None
            st.success("No clear dark pattern found")
        else:
            category = r["label"]
            st.error(f"Possible dark pattern: {category}")
            st.write(f"Model confidence: {r['confidence']:.0%}")
        if use_ai and category:
            with st.spinner("Asking AI..."):
                st.info(explain(text, category))
    else:
        st.warning("Please paste some text first.")