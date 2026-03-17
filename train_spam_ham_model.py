import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load dataset
df = pd.read_csv("spam.csv", encoding="latin-1")

texts = df["text"].astype(str).tolist()
labels = df["label"].map({"ham": 0, "spam": 1}).tolist()

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=6000,
    ngram_range=(1, 2)
)

X = vectorizer.fit_transform(texts)

# Logistic Regression model
model = LogisticRegression(max_iter=300)
model.fit(X, labels)

# Save model and vectorizer
joblib.dump(vectorizer, "spam_vectorizer.pkl")
joblib.dump(model, "spam_ham_model.pkl")

print("✅ Spam–Ham model trained successfully")
