import streamlit as st
import joblib
import whisper
import os

# 1. Carregar modelos (use cache para não carregar toda hora)
@st.cache_resource
def load_models():
    model = joblib.load('sentiment_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    stt_model = whisper.load_model("base")
    return model, vectorizer, stt_model

clf, tfidf, stt = load_models()

st.title("Análise de Sentimento via Áudio 🎙️")

# 2. Input de Áudio
audio_file = st.audio_input("Grave seu comentário em inglês")

if audio_file:
    # Salvar temporariamente o áudio gravado
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.read())
    
    with st.spinner("Transcrevendo áudio..."):
        # 3. Transcrever
        result = stt.transcribe("temp_audio.wav")
        text = result["text"]
        st.write(f"**Texto detectado:** {text}")

    with st.spinner("Analisando sentimento..."):
        # 4. Pré-processar e Predizer (Lembre-se de usar as mesmas funções de limpeza do seu notebook)
        text_vectorized = tfidf.transform([text])
        prediction = clf.predict(text_vectorized)
        
        # 5. Exibir Resultado
        sentimento = "Positivo" if prediction[0] == 1 else "Negativo"
        st.subheader(f"Resultado: {sentimento}")