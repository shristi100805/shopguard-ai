import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import streamlit as st
from src.explain import read_screenshot, review
from src.report import analyze

st.title("Screenshot Check")
st.caption("AI reads the screenshot, the detector flags lines, then AI double-checks each flag.")
thr = st.slider("Detection threshold (lower = flags more)", 0.3, 0.9, 0.5)
img = st.file_uploader("Screenshot", type=["png", "jpg", "jpeg", "webp"])

if img is not None:
    st.image(img)
    if st.button("Analyze"):
        with st.spinner("Reading the screenshot..."):
            try:
                lines, controls = read_screenshot(img.getvalue(), img.type)
            except Exception as e:
                st.error(f"Could not read the screenshot: {str(e)[:200]}")
                st.stop()

        with st.expander("What the AI read from the image"):
            st.write(lines)
            st.write(controls)

        findings = analyze(lines, controls, threshold=thr)
        with st.spinner("AI is double-checking the findings..."):
            verdicts = review(findings) if findings else {}

        kept, dismissed = [], []
        for i, f in enumerate(findings):
            v = verdicts.get(i, {})
            f["ai_check"] = v.get("why", "")
            if v.get("is_dark_pattern") is False and f["source"] != "page controls":
                dismissed.append(f)
            else:
                kept.append(f)

        if not kept:
            st.success("No dark patterns found")
        else:
            st.error(f"{len(kept)} dark pattern(s) confirmed")
            st.dataframe(pd.DataFrame(kept)[["category", "text", "source", "ai_check"]])
            st.bar_chart(pd.DataFrame(kept)["category"].value_counts())

        if dismissed:
            with st.expander(f"{len(dismissed)} flagged lines the AI dismissed as harmless"):
                st.dataframe(pd.DataFrame(dismissed)[["category", "text", "ai_check"]])