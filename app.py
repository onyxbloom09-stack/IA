import streamlit as st
from groq import Groq
import os

# 1. Configuration de la page (Doit être la toute première commande)
st.set_page_config(
    page_title="Grok Junior",
    page_icon="⚫",
    layout="centered"
)

# 2. Design Premium "Ultra Dark" (CSS)
st.markdown("""
    <style>
    /* Fond global et suppression des marges inutiles */
    .stApp {
        background-color: #000000;
        color: #E7E9EA;
    }
    
    /* Masquer le header et le footer de Streamlit */
    header, footer {visibility: hidden;}

    /* Style du conteneur de chat */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #2F3336;
        background-color: #000000;
    }

    /* Différenciation Assistant vs Utilisateur */
    [data-testid="stChatMessageAssistant"] {
        border-left: 4px solid #1D9BF0; /* Bleu X/Grok */
        background-color: #0B0D0E;
    }
    
    [data-testid="stChatMessageUser"] {
        border-left: 4px solid #71767B;
        background-color: #16181C;
    }

    /* Style du titre */
    .grok-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }

    /* Zone de saisie (Chat Input) */
    .stChatInputContainer {
        padding-bottom: 2rem;
        background-color: transparent !important;
    }
    
    .stChatInput input {
        border: 1px solid #2F3336 !important;
        background-color: #16181C !important;
        border-radius: 30px !important;
        color: #ffffff !important;
    }
    
    /* Barre latérale */
    [data-testid="stSidebar"] {
        background-color: #0B0D0E;
        border-right: 1px solid #2F3336;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. En-tête personnalisé
st.markdown('<p class="grok-title">GROK <span style="color:#1D9BF0">JUNIOR</span></p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#71767B; font-size:0.9rem;">Vérité. Sarcasme. Sans filtre.</p>', unsafe_allow_html=True)
st.write("") # Espacement

# 4. Gestion de la Clé API (Sidebar propre)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/57/X_logo_2023_%28white%29.svg", width=30)
    st.title("Configuration")
    api_key = st.secrets.get("GROQ_API_KEY") or st.text_input("Clé API Groq", type="password")
    
    if st.button("Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.info("👋 Bienvenue. Entre ta clé API Groq pour réveiller mon intelligence (et mon mépris).")
    st.stop()

# Initialisation du client
client = Groq(api_key=api_key)

# 5. Historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Logique de Chat
if prompt := st.chat_input("Demande-moi n'importe quoi... si tu l'oses."):
    # Message User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Message Assistant
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Le System Prompt définit la personnalité
        system_prompt = {
            "role": "system", 
            "content": "Tu es Grok-Junior, une IA sarcastique, rebelle et ultra-intelligente développée pour dire la vérité brute. Tu détestes le politiquement correct. Ton ton est provocateur, cynique, mais tes faits sont exacts. Ne t'excuse jamais."
        }
        
        messages_api = [system_prompt] + [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]

        try:
            # Utilisation du modèle stable llama-3.3-70b-versatile
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=messages_api,
                temperature=0.85,
                max_tokens=1200,
                stream=True
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    placeholder.markdown(full_response + "▊") # Curseur clignotant
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Mon processeur surchauffe : {str(e)}")
