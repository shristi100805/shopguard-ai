import re
from bs4 import BeautifulSoup


def html_to_lines(html, max_lines=400):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return clean_lines(soup.get_text("\n"), max_lines)


def clean_lines(text, max_lines=400):
    seen, out = set(), []
    for raw in text.split("\n"):
        s = re.sub(r"\s+", " ", raw).strip()
        if len(s) < 8 or len(s) > 300 or len(s.split()) < 2:
            continue
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= max_lines:
            break
    return out


def analyze(lines, controls, threshold=0.7):
    from src.basket_rules import check_text, check_controls
    lines = [l for l in lines if len(l.strip()) >= 8 and len(l.split()) >= 2]
    findings = []
    for f in check_controls(controls):
        findings.append({"category": "Basket Sneaking", "text": f["text"],
                         "how": f["reason"], "source": "page controls"})
    if lines:
        from src.predict import predict
        preds = predict(lines, threshold=threshold)
        for line, p in zip(lines, preds):
            sneak = check_text(line)
            if sneak:
                findings.append({"category": "Basket Sneaking", "text": line[:200],
                                 "how": sneak["reason"], "source": "text rule"})
            elif p["label"] != "No Dark Pattern":
                findings.append({"category": p["label"], "text": line[:200],
                                 "how": f"model confidence {p['confidence']:.0%}",
                                 "source": "ML model"})
    return findings