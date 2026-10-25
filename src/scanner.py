import json
import sys
from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

JS_CONTROLS = """
() => {
  const out = [];
  const nodes = document.querySelectorAll(
    'input[type=checkbox], input[type=radio], [role=checkbox], [role=switch]');
  nodes.forEach(n => {
    const on = n.tagName === 'INPUT' ? n.checked : n.getAttribute('aria-checked') === 'true';
    if (!on || n.disabled) return;
    let label = '';
    if (n.labels && n.labels.length) label = Array.from(n.labels).map(l => l.innerText).join(' ');
    if (!label) label = n.getAttribute('aria-label') || '';
    if (!label) { const p = n.closest('label') || n.parentElement; label = p ? p.innerText : ''; }
    out.push({label: (label || '').replace(/\\s+/g, ' ').trim().slice(0, 200)});
  });
  return out;
}
"""


def scan(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA, locale="en-IN",
                                  viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(4000)
        controls = page.evaluate(JS_CONTROLS)
        text = page.inner_text("body")
        title = page.title()
        browser.close()
    return {"title": title, "controls": controls, "text": text}


if __name__ == "__main__":
    try:
        result = scan(sys.argv[1])
    except Exception as e:
        result = {"error": str(e)[:300]}
    print(json.dumps(result))