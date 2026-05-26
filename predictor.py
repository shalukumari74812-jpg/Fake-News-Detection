import pickle

# LOAD MODEL
model = pickle.load(open("model.pkl", "rb"))

# LOAD VECTORIZER
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))


def predict_news(text):

    # VECTORIZE
    vectorized_text = vectorizer.transform([text])

    # PREDICT
    prediction = model.predict(vectorized_text)[0]

    # CONFIDENCE
    probabilities = model.predict_proba(vectorized_text)[0]

    confidence = round(max(probabilities) * 100, 2)

    # RESULT
    if prediction == "FAKE":

        result = "Fake News"

    else:

        result = "Real News"

    return result, confidence