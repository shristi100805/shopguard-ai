import re
from bs4 import BeautifulSoup

# Words that suggest an optional extra (insurance, donation, membership...)
ADDON = re.compile(
    r"donat|charit|insurance|protection|warranty|guarantee|membership|\bpass\b|sdg|"
    r"\bseat\b|travel plan|\bmeal\b|\bdips\b|pepsi|fries|gift|\btip\b|support the|"
    r"\bplus\b|priority|add[- ]?on|cover\b|assurance|round[- ]?up",
    re.I)

# Words that suggest the extra is already selected or added for the user
DEFAULT_SIGNAL = re.compile(
    r"\[✓\]|✓|\bselected\b|\badded\b|auto(matically)?[- ]?(added|selected)|"
    r"(?<!not )pre-?(checked|ticked|selected|toggled)|by default|"
    r"without (the )?(consumer'?s? )?consent|you have opted|opted for|"
    r"chosen .{0,40}for you|remove (insurance|donation|protection)",
    re.I)

# A charity/donation line sitting inside a fare or total breakdown
BILL_LINE = re.compile(r"(charit|donat).*(total|fare)|(total|fare).*(charit|donat)", re.I)

# A ticked option that says "no thanks" is the clean choice, not sneaking
NEGATIVE = re.compile(
    r"^\s*(no\b|skip|don'?t|do not)|don'?t want|do not want|not interested|"
    r"without (insurance|protection|trip)", re.I)


def check_text(text):
    """Text-only check. Returns a finding dict, or None."""
    if not ADDON.search(text):
        return None
    if DEFAULT_SIGNAL.search(text) or BILL_LINE.search(text):
        return {"label": "Basket Sneaking",
                "text": text[:200],
                "reason": "Optional extra appears to be pre-selected or added by default"}
    return None


def _finding(text, how):
    return {"label": "Basket Sneaking", "text": text.strip()[:200], "reason": how}


def check_controls(controls):
    """controls = list of {'label': str} for every checkbox/switch/radio that is ON."""
    out = []
    for c in controls:
        label = c.get("label", "")
        if ADDON.search(label) and not NEGATIVE.search(label):
            out.append(_finding(label, "Optional extra is switched on by default"))
    return out


def _label_text(box, soup):
    parts = []
    parent = box.find_parent("label")
    if parent:
        parts.append(parent.get_text(" ", strip=True))
    if box.get("id"):
        lab = soup.find("label", attrs={"for": box["id"]})
        if lab:
            parts.append(lab.get_text(" ", strip=True))
    for attr in ("aria-label", "name", "value", "title"):
        if box.get(attr):
            parts.append(str(box[attr]))
    if not parts and box.parent is not None:
        parts.append(box.parent.get_text(" ", strip=True)[:200])
    return " ".join(parts)


def html_controls(html):
    """Every checkbox / radio / switch that is ON in the page HTML, with its label."""
    soup = BeautifulSoup(html, "html.parser")
    controls = []
    for box in soup.find_all("input", attrs={"type": ["checkbox", "radio"]}):
        if box.has_attr("checked") and not box.has_attr("disabled"):
            controls.append({"label": _label_text(box, soup)})
    for node in soup.find_all(attrs={"role": ["checkbox", "switch"]}):
        if str(node.get("aria-checked", "")).lower() == "true":
            label = node.get("aria-label") or node.get_text(" ", strip=True)
            if not label and node.parent is not None:
                label = node.parent.get_text(" ", strip=True)[:200]
            controls.append({"label": label})
    return controls


def check_html(html):
    return check_controls(html_controls(html))