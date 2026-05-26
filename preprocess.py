import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)  # keep letters + spaces
    text = re.sub(r"\s+", " ", text)         # normalize spaces
    return text.strip()