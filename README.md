# ShopGuard AI

Dark pattern detector for Indian e-commerce, based on India's CCPA Dark Patterns Guidelines 2023.

## How it works
- ML model (MiniLM embeddings + Logistic Regression) classifies page text into 6 CCPA categories plus "No Dark Pattern".
- Rule checker finds Basket Sneaking (pre-ticked add-ons) from HTML, live pages and text.
- Gemini reads screenshots, double-checks findings and explains them in plain words.

## Setup
pip install -r requirements.txt
python -m playwright install chromium
Create .env with GEMINI_API_KEY and GEMINI_MODEL
python -m src.train
streamlit run app/app.py

## Results (5-fold cross-validation)
All data: accuracy [..], macro F1 [..]. Indian rows only: accuracy [..], macro F1 [..].

## Limitations
- Small classes (14-21 examples) and about 50 handwritten "no dark pattern" examples.
- Princeton data dominates; scores drop on Indian-only rows.
- Text alone cannot show visual tricks or hidden pre-ticked boxes.
- Research prototype, not legal advice.

## Related work
Mathur et al. (Princeton dark patterns study); DarkLens (princevshetty-ui/DarkLens).

##Prepared By
Shristi & Manya Pasricha 
