import streamlit as st
from groq import Groq
import urllib.parse
import os

# 1. Configuration de la page
st.set_page_config(page_title="Elisa AI", page_icon="🎨", layout="centered")

# 2. Design "Cyber-Elisa"
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FF007F; }
    header, footer {visibility: hidden;}
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF007F;
        text-shadow: 0 0 10px #FF007F, 0 0 20px #FF007F, 0 0 40px #FF007F;
    }
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        margin-bottom: 1rem;
        background-color: #0f0f0f;
        border: 1px solid #FF007F;
    }
    .stChatInput input {
        border: 2px solid #FF007F !important;
        background-color: #000 !important;
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">ELISA</h1>', unsafe_allow_html=True)

# 3. Initialisation Clé API
api_key = st.secrets.get("GROQ_API_KEY") or st.sidebar.text_input("🔑 Clé API Groq", type="password")

if not api_key:
    st.info("💖 Veuillez entrer votre clé API Groq pour réveiller Elisa.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

def detect_image_intent(prompt):
    keywords = ["dessine", "image", "photo", "crée", "affiche", "imagine", "peins", "illustration"]
    return any(word in prompt.lower() for word in keywords)

# 4. Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "https://image.pollinations.ai" in message["content"]:
            st.image(message["content"], caption="🎨 Création d'Elisa")
        else:
            st.markdown(message["content"])

# 5. Logique de Chat
if prompt := st.chat_input("Demande une image ou discute avec Elisa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if detect_image_intent(prompt):
            with st.spinner("✨ Elisa prépare ses pinceaux néon..."):
                clean_prompt = urllib.parse.quote(prompt)
                # Correction ici : os est maintenant bien importé
                random_seed = os.urandom(4).hex()
                image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true&seed={random_seed}"
                
                st.image(image_url, caption="Voici ce que j'ai imaginé.")
                st.session_state.messages.append({"role": "assistant", "content": image_url})
        else:
            placeholder = st.empty()
            full_response = ""
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es Elisa, une IA au style cyberpunk et sarcastique."},
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
