import json
import joblib
from sentence_transformers import SentenceTransformer
from src.preprocess import clean_text

_embedder = None
_clf = None

def _load():
    global _embedder, _clf
    if _clf is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        _clf = joblib.load("models/best_model.joblib")

def predict(texts, threshold=0.5):
    _load()
    cleaned = [clean_text(t) for t in texts]
    vecs = _embedder.encode(cleaned, show_progress_bar=False)
    probs = _clf.predict_proba(vecs)
    out = []
    for p in probs:
        i = int(p.argmax())
        label = str(_clf.classes_[i])
        conf = float(p[i])
        # not sure enough? don't flag it
        if label != "No Dark Pattern" and conf < threshold:
            label = "No Dark Pattern"
        out.append({"label": label, "confidence": conf})
    return out