import streamlit as st
import joblib
import whisper
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer
import os

st.markdown("""
<style>
/* Reset básico */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Fundo geral com grid */
.stApp {
    background: #0a0a0a;
    color: #fff;
    overflow-x: hidden;
}
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

/* Títulos centralizados com degradê */
h1, h2, h3, .stText, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    text-align: center;
    background: linear-gradient(135deg, #fff 0%, #00ff88 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Boxes customizados */
.custom-box {
    background: rgba(20, 20, 20, 0.8);
    border: 1px solid #00ff88;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    color: #fff;
}

/* Textos normais justificados */
.stMarkdown p {
    text-align: justify;
    color: #ccc;
}

/* Captions */
.css-10trblm {
    text-align: center;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)



# ------------------ CONFIGURAÇÃO DA PÁGINA ------------------
st.set_page_config(
    page_title="Pop Artist Sentiment",
    page_icon="🎧",
    layout="centered"
)

st.title("🎧 Pop Artist Sentiment Analyzer")
st.caption("Record a short comment about a pop artist to see its sentiment.")

# ------------------ NLTK ------------------
nltk.download('stopwords')

# ------------------ CARREGAR MODELOS ------------------
# Caminho base do arquivo app.py
BASE_DIR = os.path.dirname(__file__)

# Carregar modelos
@st.cache_resource
def load_models():
    clf_model = joblib.load(os.path.join(BASE_DIR, 'sentiment_model.pkl'))
    vectorizer = joblib.load(os.path.join(BASE_DIR, 'vectorizer.pkl'))
    stt_model = whisper.load_model("base")
    return clf_model, vectorizer, stt_model

clf, tfidf, stt = load_models()

# ------------------ FUNÇÃO DE LIMPEZA ------------------
def preprocess_text(text):
    stop_words = stopwords.words('english')
    tokenizer = WordPunctTokenizer()
    stemmer = PorterStemmer()

    tokens = tokenizer.tokenize(text.lower())
    clean_tokens = [stemmer.stem(word) for word in tokens if word.isalpha() and word not in stop_words]
    return ' '.join(clean_tokens)

# ------------------ INPUT DO USUÁRIO ------------------
st.subheader("Step 1: Record your comment")
st.markdown("🎤 Click below to record a short comment (in English) about a pop artist.")

audio_file = st.audio_input("Record here:")

if audio_file:
    # Salvar áudio temporariamente
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.read())

    # ------------------ TRANSCRIÇÃO ------------------
    with st.spinner("Transcribing audio..."):
        result = stt.transcribe("temp_audio.wav")
        raw_text = result["text"]
    
    st.subheader("Step 2: Detected Text")
    st.info(raw_text)

    # ------------------ PROCESSAMENTO E ANÁLISE ------------------
    with st.spinner("Analyzing sentiment..."):
        processed_text = preprocess_text(raw_text)
        st.write(f"**Processed text:** `{processed_text}`")

        vectorized_text = tfidf.transform([processed_text])
        prediction = clf.predict(vectorized_text)

        sentiment = "Positive" if prediction[0] in ['positive', 1] else "Negative"

    # ------------------ RESULTADO ------------------
    st.subheader("Step 3: Sentiment Result")
    if sentiment == "Positive":
        st.success(f"{sentiment} 😊")
    else:
        st.error(f"{sentiment} 😞")
