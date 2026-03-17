# classifiers.py
import joblib

# Load trained spam-ham model
vectorizer = joblib.load("spam_vectorizer.pkl")
model = joblib.load("spam_ham_model.pkl")

# Keywords for ham split
PROMO_KW = ["sale", "discount", "offer", "promo", "newsletter"]
IMPORTANT_KW = ["deadline", "exam", "interview", "invoice", "fee", "urgent","immediate"]
PERSONAL_KW = ["hi", "hello", "dear","love"]

def predict_email(email_obj):
    subject = email_obj.get("subject", "")
    body = email_obj.get("body", "")
    sender = email_obj.get("sender", "")

    text = f"{subject} {body}".lower()

    # ---------- Stage 1: Spam vs Ham ----------
    X = vectorizer.transform([text])
    probs = model.predict_proba(X)[0]
    pred = model.classes_[probs.argmax()]
    confidence = probs.max()

    if pred == "spam":
        return {
            "raw_label": "spam",
            "category": "spam",
            "priority": "low",
            "priority_score": 0.0,
            "confidence": 0.0,
        }

    # ---------- Stage 2: Ham → sub-category ----------
    if any(k in text for k in IMPORTANT_KW) or "hr@" in sender.lower():
        label = "important"
        conf = 0.95
    elif any(k in text for k in PROMO_KW):
        label = "promotion"
        conf = 0.75
    elif any(k in text for k in PERSONAL_KW):
        label = "personal"
        conf = 0.85
    else:
        label = "personal"  # default ham
        conf = 0.77

    priority = "high" if label == "important" else "normal"

    return {
        "raw_label": label,
        "category": label,
        "priority": priority,
        "priority_score": conf * 100,
        "confidence": float(conf),
    }
