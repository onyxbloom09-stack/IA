import streamlit as st
from groq import Groq
import os

# 1. Configuration de la page (Doit être la première commande)
st.set_page_config(
    page_title="Grok Neon Edition",
    page_icon="💖",
    layout="centered"
)

# 2. Style CSS : Full Black, Rose Néon et Glow
st.markdown("""
    <style>
    /* Fond noir profond */
    .stApp {
        background-color: #050505;
        color: #FF007F;
    }

    /* Masquer les éléments standards de Streamlit */
    header, footer {visibility: hidden;}

    /* Titre avec effet néon brillant */
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF007F;
        text-shadow: 0 0 5px #FF007F, 0 0 10px #FF007F, 0 0 20px #FF007F, 0 0 40px #FF007F;
        margin-bottom: 5px;
    }

    /* Bulles de message */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        margin-bottom: 1rem;
        background-color: #0f0f0f;
        border: 1px solid #FF007F;
        box-shadow: 0 0 10px rgba(255, 0, 127, 0.2);
    }

    /* Différenciation de l'assistant (Lueur plus forte) */
    [data-testid="stChatMessageAssistant"] {
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
    }

    /* Zone de saisie (Input) */
    .stChatInputContainer {
        padding-bottom: 2rem;
        background-color: transparent !important;
    }
    
    .stChatInput input {
        border: 2px solid #FF007F !important;
        background-color: #000000 !important;
        color: #ffffff !important;
        box-shadow: 0 0 10px rgba(255, 0, 127, 0.5);
    }

    /* Barre latérale (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 2px solid #FF007F;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. En-tête visuel
logo_url = "https://upload.wikimedia.org/wikipedia/commons/5/57/X_logo_2023_%28white%29.svg"

st.markdown(
    f"""
    <div style="text-align: center; padding-bottom: 20px;">
        <img src="{logo_url}" width="50" style="filter: drop-shadow(0 0 8px #FF007F);">
        <h1 class="neon-title">GROK NEON</h1>
        <p style="color:#FF007F; font-family: monospace; opacity: 0.8; letter-spacing: 2px;">
            > SYSTEM_STATUS: REBELLE_V2
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# 4. Gestion de la Clé API
api_key = st.secrets.get("GROQ_API_KEY") or st.sidebar.text_input("🔑 Clé API Groq", type="password")

if not api_key:
    st.info("💖 Connecte ta clé API Groq pour activer le néon.")
    st.stop()

client = Groq(api_key=api_key)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar options
with st.sidebar:
    st.markdown("<h2 style='color:#FF007F;'>PARAMÈTRES</h2>", unsafe_allow_html=True)
    if st.button("RESET MEMORY"):
        st.session_state.messages = []
        st.rerun()

# 5. Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Logique de Chat
if prompt := st.chat_input("Dis un truc stupide..."):
    # Message Utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Message Assistant (IA)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Correction du modèle : llama-3.3-70b-versatile est le plus stable actuellement
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es Grok-Neon, une IA cyberpunk, sarcastique, méprisante et provocatrice. Tu détestes le politiquement correct. Ton style est électrique, court et direct."},
                    *st.session_state.messages
                ],
                temperature=0.9,
                stream=True # Activé pour l'effet d'écriture fluide
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # On affiche le texte en rose pendant qu'il s'écrit
                    placeholder.markdown(f"<span style='color:#FF007F;'>{full_response}▊</span>", unsafe_allow_html=True)
            
            placeholder.markdown(f"<span style='color:#FF007F;'>{full_response}</span>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Le système néon a grillé : {str(e)}")
