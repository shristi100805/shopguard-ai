import re

def clean_text(s):
    s = str(s).lower().strip()
    s = re.sub(r"\[.*?\]", " ", s)
    s = re.sub(r"\d+(?:[.,]\d+)*", "xxnum", s)
    s = re.sub(r"\s+", " ", s)
    return s