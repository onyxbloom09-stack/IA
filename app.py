import streamlit as st
from groq import Groq
import urllib.parse
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Elisa AI | Creative Intelligence",
    page_icon="✨",
    layout="wide" # Passage en mode large pour plus de propreté
)

# --- 2. DESIGN PRO & CLEAN (CSS) ---
st.markdown("""
    <style>
    /* Importation d'une police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
    }

    .stApp { background-color: #000000; }

    /* Masquage des éléments Streamlit */
    header, footer {visibility: hidden;}

    /* Conteneur principal centré */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }

    /* Titre Minimaliste Pro */
    .main-title {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 2.2rem;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #FF007F;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 3rem;
        opacity: 0.8;
    }

    /* Bulles de Chat Style "Glassmorphism" */
    [data-testid="stChatMessage"] {
        background-color: #0A0A0A !important;
        border: 1px solid #1A1A1A !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
        transition: all 0.3s ease;
    }

    [data-testid="stChatMessage"]:hover {
        border: 1px solid #FF007F55 !important;
    }

    /* Barre de saisie élégante */
    .stChatInput {
        padding: 1rem;
    }
    
    .stChatInput input {
        background-color: #0A0A0A !important;
        border: 1px solid #1A1A1A !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    /* Sidebar élégante */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #1A1A1A;
    }

    /* Scrollbar invisible */
    ::-webkit-scrollbar { width: 0px; background: transparent; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE DE L'INTERFACE ---

st.markdown('<h1 class="main-title">ELISA <span style="color:#FF007F">AI</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Intelligence Multimodale</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h3 style='color:white;'>Paramètres</h3>", unsafe_allow_html=True)
    api_key = st.secrets.get("GROQ_API_KEY") or st.text_input("Clé API Groq", type="password")
    if st.button("Nouvelle Session"):
        st.session_state.messages = []
        st.rerun()

if not api_key:
    st.warning("Veuillez configurer votre clé API dans la barre latérale.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. FONCTIONS CŒUR ---

def detect_image_intent(prompt):
    # Liste étendue pour une meilleure détection pro
    keywords = ["dessine", "image", "photo", "crée", "affiche", "imagine", "peins", "illustration", "rendu", "visualise"]
    return any(word in prompt.lower() for word in keywords)

# --- 5. AFFICHAGE DES MESSAGES ---

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "https://image.pollinations.ai" in message["content"]:
            st.image(message["content"], use_container_width=True)
        else:
            st.markdown(message["content"])

# --- 6. GESTION DU CHAT ---

if prompt := st.chat_input("Décrivez votre idée ou posez une question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if detect_image_intent(prompt):
            with st.spinner("Génération du visuel en cours..."):
                # On ajoute des tags de qualité "pro" automatiquement
                enhanced_prompt = urllib.parse.quote(f"{prompt}, professional photography, 8k, highly detailed, clean composition")
                random_seed = os.urandom(4).hex()
                image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt}?width=1280&height=720&nologo=true&seed={random_seed}"
                
                st.image(image_url)
                st.session_state.messages.append({"role": "assistant", "content": image_url})
        else:
            placeholder = st.empty()
            full_response = ""
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es Elisa, une IA sophistiquée, concise et intelligente. Ton style est minimaliste et efficace. Tu réponds de manière élégante."},
                        *st.session_state.messages
                    ],
                    temperature=0.7, # Légèrement baissée pour plus de sérieux/précision
                    stream=True
                )
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        placeholder.markdown(full_response + "▊")
                
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
