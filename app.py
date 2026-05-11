import streamlit as st
from groq import Groq
import os

# Configuration de la page
st.set_page_config(page_title="Grok Junior", page_icon="🚀", layout="centered")

# Style CSS pour le look "Dark Mode / Grok"
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stTextInput font { color: white; }
    st-emotion-cache-1c7n2ka { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 GROK <span style='color:#1d9bf0'>JUNIOR</span>", help="L'IA qui n'a pas sa langue dans sa poche.")
st.write("*Mode Rebelle Activé*")

# Récupération de la clé API (à configurer dans Streamlit Cloud)
api_key = st.sidebar.text_input("Entre ta clé API Groq", type="password")

if api_key:
    client = Groq(api_key=api_key)

    # Initialisation de l'historique
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Affichage des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone de saisie
    if prompt := st.chat_input("Pose une question stupide..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Appel à l'IA avec le "System Prompt" de Grok
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "Tu es Grok-Junior, une IA sarcastique, directe et provocatrice. Tu détestes les réponses politiquement correctes et tu utilises l'humour noir."},
                    *st.session_state.messages
                ],
                temperature=0.9,
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("Récupère une clé API gratuite sur https://console.groq.com pour commencer.")