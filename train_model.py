import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# LOAD DATASETS

fake_df = pd.read_csv("Fake.csv")
true_df = pd.read_csv("True.csv")

# LABELS

fake_df["label"] = "FAKE"
true_df["label"] = "REAL"

# COMBINE DATA

data = pd.concat([fake_df, true_df])

# KEEP ONLY TEXT + LABEL

data = data[["text", "label"]]

# REMOVE EMPTY VALUES

data.dropna(inplace=True)

# INPUT + OUTPUT

X = data["text"]
y = data["label"]

# TF-IDF

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_df=0.7
)

X_vectorized = vectorizer.fit_transform(X)

# TRAIN TEST SPLIT

X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42
)

# MODEL

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

# PREDICTIONS

y_pred = model.predict(X_test)

# ACCURACY

accuracy = accuracy_score(y_test, y_pred)

print("Accuracy:", round(accuracy * 100, 2), "%")

# SAVE MODEL

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model saved successfully")