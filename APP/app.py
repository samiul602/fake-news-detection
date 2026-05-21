import streamlit as st
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os
import time

# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

# Page Configuration
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* Gradient background */
    .stApp {
         background: linear-gradient(90deg, rgba(99, 0, 0, 1) 0%, rgba(9, 9, 121, 1) 52%, rgba(0, 212, 255, 1) 100%);

    }

    .main {
        background: transparent !important;
    }

    /* REMOVE the empty white box at top 
    .stApp > header {
        display: none !important;
    }*/

    .stApp [data-testid="stHeader"] {
        display: none !important;
    }

    .stApp [data-testid="stToolbar"] {
        display: none !important;
    }

    /* Main card container - glassmorphism */
    .glass-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 48px 40px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 40px auto;
        max-width: 800px;
    }

    /* Title - BOLD WHITE with dark shadow for readability on gradient */
    .title-text {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), 0 2px 4px rgba(0, 0, 0, 0.3);
        }

    /* Subtitle - white with shadow */
    .subtitle-text {
        text-align: center;
        color: #e2e8f0;
        font-size: 1.15rem;
        margin-bottom: 40px;
        font-weight: 400;
        line-height: 1.6;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    /* Info badges */
    .info-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        border-radius: 50px;
        font-size: 0.9rem;
        color: #ffffff;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    /* Section label */
    .section-label {
        font-size: 2.15rem;
        font-weight: 600;
        color: #93a2b8;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Text area styling */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 20px !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        transition: all 0.2s ease !important;
        background: #ffffff !important;
        color: #1e293b !important;
        min-height: 180px !important;
    }

    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }

    .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
    }

    /* Word count */
    .word-count {
        text-align: right;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 8px;
        font-weight: 500;
    }

    /* Primary button */
    .stButton button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 40px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin-top: 20px !important;
        letter-spacing: 0.01em;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }

    .stButton button:active {
        transform: translateY(0) !important;
    }

    .stButton button:disabled {
        background: #cbd5e1 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Result containers */
    .result-container {
        border-radius: 20px;
        padding: 40px 30px;
        margin-top: 30px;
        text-align: center;
        animation: slideUp 0.5s ease-out;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .real-news {
        background: #f0fdf4;
        border: 2px solid #22c55e;
    }

    .real-news .result-icon {
        font-size: 3.5rem;
        margin-bottom: 16px;
    }

    .real-news .result-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #15803d;
        margin-bottom: 8px;
    }

    .real-news .result-desc {
        font-size: 1.05rem;
        color: #166534;
        font-weight: 500;
    }

    .fake-news {
        background: #fef2f2;
        border: 2px solid #ef4444;
    }

    .fake-news .result-icon {
        font-size: 3.5rem;
        margin-bottom: 16px;
    }

    .fake-news .result-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #b91c1c;
        margin-bottom: 8px;
    }

    .fake-news .result-desc {
        font-size: 1.05rem;
        color: #991b1b;
        font-weight: 500;
    }

    /* Reset button */
    .reset-btn button {
        background: #ffffff !important;
        color: #475569 !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        width: auto !important;
        transition: all 0.2s ease !important;
    }

    .reset-btn button:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        color: #334155 !important;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        border-radius: 10px !important;
    }

    .stProgress > div {
        background: #e2e8f0 !important;
        border-radius: 10px !important;
        height: 8px !important;
    }

    /* Status text */
    .status-text {
        text-align: center;
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 12px;
        font-weight: 500;
    }

    /* Warning message */
    .stWarning {
        background: #fffbeb !important;
        border: 1px solid #fbbf24 !important;
        border-radius: 12px !important;
        color: #92400e !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 40px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        padding-bottom: 40px;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }

    .footer p {
        margin: 4px 0;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Divider line */
    .divider {
        height: 1px;
        background: #e2e8f0;
        margin: 32px 0;
    }

    /* Remove top padding from main container */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Load Model & Vectorizer
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

# Session state initialization
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "result" not in st.session_state:
    st.session_state.result = None
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "is_analyzing" not in st.session_state:
    st.session_state.is_analyzing = False

# Main Container
#st.markdown('<div class="glass-container">', unsafe_allow_html=True)

# Header Section
st.markdown('<div class="title-text">🔍 Fake News Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Enter any news article below and our AI will analyze its authenticity in seconds</div>', unsafe_allow_html=True)

# Info badges row
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div style="text-align: center;"><span class="info-badge">⚡ Instant</span></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div style="text-align: center;"><span class="info-badge">🤖 AI Powered</span></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div style="text-align: center;"><span class="info-badge">🎯 Accurate</span></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Input Section
st.markdown('<div class="section-label">📰 Enter News Article</div>', unsafe_allow_html=True)

user_input = st.text_area(
    "",
    value=st.session_state.input_text,
    height=200,
    placeholder="Paste the news article or text you want to verify here...",
    key="news_input",
    label_visibility="collapsed"
)

# Word count
word_count = len(user_input.split()) if user_input else 0
st.markdown(f'<div class="word-count">{word_count} words</div>', unsafe_allow_html=True)

# Predict Button
if st.button("🔍 Analyze News", disabled=st.session_state.is_analyzing):
    if user_input.strip() == "":
        st.warning("⚠️ Please enter some news text to analyze.")
    else:
        st.session_state.is_analyzing = True
        st.session_state.input_text = user_input

        # Show progress
        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        steps = [
            (20, "🧹 Cleaning and preprocessing text..."),
            (50, "🔢 Converting to numerical features..."),
            (80, "🤖 Running AI model prediction..."),
            (100, "✅ Analysis complete!")
        ]

        for target, message in steps:
            progress_bar.progress(target)
            status_placeholder.markdown(f'<div class="status-text">{message}</div>', unsafe_allow_html=True)
            time.sleep(0.4)

        # Make prediction
        cleaned = clean_text(user_input)
        vector = vectorizer.transform([cleaned])
        prediction = model.predict(vector)

        # Clear progress
        progress_bar.empty()
        status_placeholder.empty()

        st.session_state.result = int(prediction[0])
        st.session_state.show_result = True
        st.session_state.is_analyzing = False
        st.rerun()

# Show Result
if st.session_state.show_result and not st.session_state.is_analyzing:
    if st.session_state.result == 1:
        st.markdown("""
        <div class="result-container real-news">
            <div class="result-icon">✅</div>
            <div class="result-title">Real News Detected</div>
            <div class="result-desc">This article appears to be authentic and trustworthy based on our analysis.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="result-container fake-news">
            <div class="result-icon">⚠️</div>
            <div class="result-title">Fake News Detected</div>
            <div class="result-desc">This article shows signs of misinformation. Please verify from trusted sources before sharing.</div>
        </div>
        """, unsafe_allow_html=True)

    # Reset Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Analyze Another Article", key="reset"):
            st.session_state.show_result = False
            st.session_state.result = None
            st.session_state.input_text = ""
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>🔒 Your text is processed locally and never stored</p>
    <p style="font-size: 0.8rem; margin-top: 8px;">Powered by Machine Learning · Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)