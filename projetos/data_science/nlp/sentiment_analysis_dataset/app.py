import streamlit as st
import joblib
import whisper
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer

# Baixar recursos necessários do NLTK (essencial para rodar em novos ambientes)
nltk.download('stopwords')

# 1. Carregar modelos
@st.cache_resource
def load_models():
    # Certifique-se de que os nomes dos arquivos .pkl estão corretos
    model = joblib.load('sentiment_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    stt_model = whisper.load_model("base")
    return model, vectorizer, stt_model

clf, tfidf, stt = load_models()

# --- NOVA SEÇÃO: FUNÇÃO DE LIMPEZA (IDÊNTICA AO SEU TESTE) ---
def preprocessar_texto(texto):
    palavras_irrelevantes = stopwords.words('english')
    token_pontuacao = WordPunctTokenizer()
    stemmer = PorterStemmer()
    
    # Passo 1 & 2: Tokenização e Lowercase/Stopwords
    tokens = token_pontuacao.tokenize(texto.lower())
    # Passo 3 & 4: Remover stopwords e manter apenas letras
    frase_processada = [palavra for palavra in tokens if palavra not in palavras_irrelevantes and palavra.isalpha()]
    # Passo 5: Stemming
    frase_processada = [stemmer.stem(palavra) for palavra in frase_processada]
    
    return ' '.join(frase_processada)
# -----------------------------------------------------------

st.title("Análise de Sentimento via Áudio 🎙️")

audio_file = st.audio_input("Grave seu comentário em inglês")

if audio_file:
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.read())
    
    with st.spinner("Transcrevendo áudio..."):
        result = stt.transcribe("temp_audio.wav")
        text_raw = result["text"]
        st.write(f"**Texto detectado:** {text_raw}")

    with st.spinner("Analisando sentimento..."):
        # --- O AJUSTE ESTÁ AQUI ---
        # 4. Pré-processar (Limpar o texto antes da vetorização)
        text_cleaned = preprocessar_texto(text_raw)
        st.write(f"**Texto processado (como o modelo vê):** `{text_cleaned}`")
        
        # 5. Vetorizar o texto LIMPO
        text_vectorized = tfidf.transform([text_cleaned])
        prediction = clf.predict(text_vectorized)
        
        # 6. Exibir Resultado
        # Verifique se o seu modelo retorna 'positive'/'negative' ou 1/0
        # No seu notebook parece que as labels eram strings!
        sentimento = "Positivo" if prediction[0] in ['positive', 1] else "Negativo"
        
        if sentimento == "Positivo":
            st.success(f"Resultado: {sentimento} 😊")
        else:
            st.error(f"Resultado: {sentimento} 😞")