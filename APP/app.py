# import libraries
import streamlit as st
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('stopwords')
nltk.download('wordnet')
# Load Model & Vectorizer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

vectorizer_path = os.path.join(BASE_DIR, "models", "vectorizer.pkl")
vectorizer = pickle.load(open(vectorizer_path, "rb"))

model_path = os.path.join(BASE_DIR, "models", "model.pkl")
model = pickle.load(open(model_path, "rb"))

# Text Preprocessing Function
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return " ".join(words)

# UI Design
st.title("📰 Fake News Detection System")
st.write("Enter a news article below to check whether it is REAL or FAKE")

# Session state to control reset
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "result" not in st.session_state:
    st.session_state.result = None
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Input Box
user_input = st.text_area("Enter News Text", value=st.session_state.input_text, key="news_input")

# Predict Button
if st.button("Predict"):
    if user_input.strip() == "":
        st.warning("Please enter some news text first.")
    else:
        cleaned = clean_text(user_input)
        vector = vectorizer.transform([cleaned])
        prediction = model.predict(vector)
        st.session_state.result = int(prediction[0])
        st.session_state.show_result = True
        st.session_state.input_text = user_input

# Show result + reset button
if st.session_state.show_result:
    if st.session_state.result == 1:
        st.success("🟢 Real News")
    else:
        st.error("🔴 Fake News")

    if st.button("🔄 Reset"):
        st.session_state.show_result = False
        st.session_state.result = None
        st.session_state.input_text = ""
        st.rerun()