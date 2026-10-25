import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

GUIDE = (
    "You explain dark patterns on Indian shopping websites to students and shoppers. "
    "Base your answer on India's CCPA Guidelines for Prevention and Regulation of "
    "Dark Patterns, 2023. Use simple English in 2-3 short sentences: why the text is "
    "manipulative and what the shopper can do. Do not quote clause numbers and do not "
    "give legal advice. If the text looks harmless, say so."
)


_CLIENT = None


def _client():
    global _CLIENT
    if _CLIENT is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
        _CLIENT = genai.Client(api_key=key)
    return _CLIENT


def explain(text, category):
    try:
        r = _client().models.generate_content(
            model=MODEL,
            contents=f"Category found by our detector: {category}\n"
                     f"Text on the page: {text}\nExplain.",
            config=types.GenerateContentConfig(system_instruction=GUIDE),
        )
        return (r.text or "").strip()
    except Exception as e:
        return f"(AI explanation unavailable: {str(e)[:150]})"


def read_screenshot(image_bytes, mime_type="image/png"):
    """Returns (lines, controls) read from a screenshot."""
    prompt = (
        "Read this screenshot of a shopping page. Return JSON with two lists. "
        '"lines": every distinct piece of visible text a shopper would see '
        "(banners, timers, buttons, prices, fine print), copied exactly. "
        '"ticked_options": for every checkbox, toggle or radio button that is '
        "ALREADY ticked or switched on, the text next to it. Do not guess. "
        "Return only JSON."
    )
    r = _client().models.generate_content(
        model=MODEL,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime_type), prompt],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    data = json.loads(r.text)
    lines = [str(x) for x in data.get("lines", [])]
    controls = [{"label": str(x)} for x in data.get("ticked_options", [])]
    return lines, controls

def review(findings):
    """One AI call: confirm or dismiss every finding. Returns {index: verdict}."""
    items = [{"i": i, "category": f["category"], "text": f["text"]}
             for i, f in enumerate(findings)]
    prompt = (
        "A detector flagged these texts from an Indian shopping page as possible "
        "dark patterns (India CCPA Dark Patterns Guidelines 2023). For each item, "
        "decide if it really is that dark pattern. Menu labels, product names, "
        "image placeholders and ordinary prices are NOT dark patterns. "
        'Return a JSON list of {"i": number, "is_dark_pattern": true or false, '
        '"why": "one simple sentence"}.\n' + json.dumps(items, ensure_ascii=False)
    )
    try:
        r = _client().models.generate_content(
            model=MODEL, contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"))
        return {int(x["i"]): x for x in json.loads(r.text)}
    except Exception:
        return {}   # if the AI fails, keep every finding