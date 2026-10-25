import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

import pandas as pd
import streamlit as st
from src.report import analyze, clean_lines, html_to_lines
from src.basket_rules import html_controls

st.title("Page Scanner")
mode = st.radio("Input", ["Paste page HTML", "Live URL"], horizontal=True)
findings = None

if mode == "Paste page HTML":
    html = st.text_area("Paste the page HTML", height=200)
    up = st.file_uploader("...or upload a saved .html file", type=["html", "htm"])
    if up is not None:
        html = up.read().decode("utf-8", errors="ignore")
    if st.button("Scan") and html.strip():
        with st.spinner("Scanning..."):
            findings = analyze(html_to_lines(html), html_controls(html))
else:
    url = st.text_input("Page URL (https://...)")
    if st.button("Scan") and url.strip():
        with st.spinner("Opening the page in a headless browser (up to 2 minutes)..."):
            try:
                res = subprocess.run(
                    [sys.executable, "-m", "src.scanner", url.strip()],
                    capture_output=True, text=True, encoding="utf-8",
                    cwd=ROOT, timeout=120)
                data = json.loads(res.stdout.strip().splitlines()[-1])
            except subprocess.TimeoutExpired:
                data = {"error": "The page took too long to load."}
            except Exception:
                data = {"error": "Scanner failed: " + (res.stderr or "no output")[-300:]}
        if "error" in data:
            st.error(data["error"])
        else:
            st.caption(f"Scanned: {data.get('title', '')}")
            findings = analyze(clean_lines(data["text"]), data["controls"])

if findings is not None:
    if not findings:
        st.success("No dark patterns found on this page")
    else:
        df = pd.DataFrame(findings)
        st.error(f"{len(df)} possible dark pattern(s) found")
        st.dataframe(df)
        st.bar_chart(df["category"].value_counts())