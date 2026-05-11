import streamlit as st
from groq import Groq
import os

# 1. Configuration de la page
st.set_page_config(page_title="Elisa AI", page_icon="🎨", layout="centered")

# 2. Style CSS Néon Rose & Noir
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FF007F; }
    header, footer {visibility: hidden;}
    .neon-title {
        font-size: 3rem; font-weight: bold; text-align: center; color: #FF007F;
        text-shadow: 0 0 10px #FF007F, 0 0 20px #FF007F;
    }
    [data-testid="stChatMessage"] {
        border-radius: 15px; margin-bottom: 1rem;
        background-color: #0f0f0f; border: 1px solid #FF007F;
    }
    .stChatInput input {
        border: 2px solid #FF007F !important; background-color: #000 !important; color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">ELISA AI</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#FF007F; opacity:0.8;">Génération de texte et d\'images</p>', unsafe_allow_html=True)

# 3. Clé API Groq
api_key = st.secrets.get("GROQ_API_KEY") or st.sidebar.text_input("🔑 Clé API Groq", type="password")

if not api_key:
    st.info("💖 Connecte ta clé API pour parler à Elisa.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Fonction pour détecter si l'utilisateur veut une image
def is_image_request(prompt):
    keywords = ["dessine", "génère une image", "crée une image", "fais un dessin", "imagine"]
    return any(word in prompt.lower() for word in keywords)

# 5. Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["content"].startswith("http"):
            st.image(message["content"], caption="Généré par Elisa")
        else:
            st.markdown(message["content"])

# 6. Logique de Chat et Image
if prompt := st.chat_input("Demande une image à Elisa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_image_request(prompt):
            # --- LOGIQUE GÉNÉRATION D'IMAGE ---
            with st.spinner("Elisa dessine..."):
                # On encode le prompt pour l'URL
                encoded_prompt = prompt.replace(" ", "%20")
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                
                st.image(image_url, caption="Voici ton image !")
                st.session_state.messages.append({"role": "assistant", "content": image_url})
        else:
            # --- LOGIQUE TEXTE CLASSIQUE ---
            placeholder = st.empty()
            full_response = ""
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es Elisa, une IA élégante, un peu sarcastique mais créative. Si on te demande de dessiner, réponds que tu t'en occupes."},
                        *st.session_state.messages
                    ],
                    temperature=0.8,
                    stream=True
                )
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        placeholder.markdown(f"<span style='color:#FF007F;'>{full_response}▊</span>", unsafe_allow_html=True)
                
                placeholder.markdown(f"<span style='color:#FF007F;'>{full_response}</span>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Erreur : {e}")
