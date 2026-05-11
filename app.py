import streamlit as st
from groq import Groq
import urllib.parse

# 1. Configuration de la page
st.set_page_config(page_title="Elisa AI - Neon", page_icon="🎨", layout="centered")

# 2. Design "Cyber-Elisa" (Rose Néon & Noir)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #FF007F; }
    header, footer {visibility: hidden;}
    
    /* Titre Néon */
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        color: #FF007F;
        text-shadow: 0 0 10px #FF007F, 0 0 20px #FF007F, 0 0 40px #FF007F;
    }

    /* Bulles de Chat */
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        margin-bottom: 1rem;
        background-color: #0f0f0f;
        border: 1px solid #FF007F;
        box-shadow: 0 0 10px rgba(255, 0, 127, 0.2);
    }

    /* Input Box */
    .stChatInput input {
        border: 2px solid #FF007F !important;
        background-color: #000 !important;
        color: #fff !important;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">ELISA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#FF007F; opacity:0.7; font-family:monospace;">INTERFACE_IMAGE_MULTIMODAL_V2</p>', unsafe_allow_html=True)

# 3. Initialisation Clé API
api_key = st.secrets.get("GROQ_API_KEY") or st.sidebar.text_input("🔑 Clé API Groq", type="password")

if not api_key:
    st.info("💖 Veuillez entrer votre clé API Groq pour réveiller Elisa.")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Fonction de détection d'image
def detect_image_intent(prompt):
    keywords = ["dessine", "image", "photo", "crée", "affiche", "imagine", "peins", "illustration"]
    return any(word in prompt.lower() for word in keywords)

# 5. Affichage de l'historique (Texte ou Image)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["content"].startswith("https://image.pollinations.ai"):
            st.image(message["content"], caption="🎨 Création d'Elisa", use_container_width=True)
        else:
            st.markdown(message["content"])

# 6. Logique de Chat
if prompt := st.chat_input("Demande une image ou discute avec Elisa..."):
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # CAS 1 : GÉNÉRATION D'IMAGE
        if detect_image_intent(prompt):
            with st.spinner("✨ Elisa prépare ses pinceaux néon..."):
                # Nettoyage et encodage du prompt pour l'URL
                clean_prompt = urllib.parse.quote(prompt)
                image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&nologo=true&seed={os.urandom(4).hex()}"
                
                st.image(image_url, caption="Voici ce que j'ai imaginé pour toi.")
                st.session_state.messages.append({"role": "assistant", "content": image_url})
        
        # CAS 2 : DISCUSSION TEXTE
        else:
            placeholder = st.empty()
            full_response = ""
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es Elisa, une IA au style cyberpunk, sarcastique et créative. Tu parles en rose néon. Si on te demande de créer une image, réponds brièvement avec enthousiasme."},
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
                st.error(f"Bug système : {e}")
