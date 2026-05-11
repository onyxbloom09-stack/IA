import streamlit as st
from groq import Groq
import os

# 1. Configuration de la page (Doit être la première commande Streamlit)
st.set_page_config(
    page_title="Grok Junior",
    page_icon="🚀",
    layout="centered"
)

# 2. Design "Dark Grok"
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stTextInput input { background-color: #111; color: white; border-radius: 20px; }
    [data-testid="stChatMessage"] { background-color: #111; border-radius: 15px; margin-bottom: 10px; border: 1px solid #333; }
    .stChatInputContainer { padding-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 GROK <span style='color:#1d9bf0'>JUNIOR</span>", help="L'IA rebelle")
st.write("---")

# 3. Gestion de la Clé API (Priorité aux Secrets Streamlit, sinon Input)
api_key = st.secrets.get("GROQ_API_KEY") or st.sidebar.text_input("Clé API Groq", type="password")

if not api_key:
    st.warning("⚠️ Ajoute ta clé API Groq (gsk_...) dans la barre latérale ou les Secrets pour commencer.")
    st.stop()

# Initialisation du client Groq
client = Groq(api_key=api_key)

# 4. Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Zone de saisie et Logique
if prompt := st.chat_input("Dis-moi quelque chose de brillant... ou de stupide."):
    # Ajouter le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Préparation des messages pour l'API
    # On définit le caractère "Grok" ici
    system_prompt = {
        "role": "system", 
        "content": "Tu es Grok-Junior, une IA sarcastique, rebelle et ultra-intelligente. Tu détestes la langue de bois et le politiquement correct. Réponds avec humour noir et sarcasme, mais reste factuellement précis."
    }
    
    messages_api = [system_prompt] + [
        {"role": m["role"], "content": m["content"]} 
        for m in st.session_state.messages
    ]

    # Appel à l'API avec gestion d'erreurs
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Utilisation du modèle Llama-3.3-70b (le plus performant et stable actuellement)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-specdec", 
                messages=messages_api,
                temperature=0.8,
                max_tokens=1024,
                top_p=1,
                stream=True # Streaming pour un effet "frappe au clavier"
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_msg = f"Erreur critique : {str(e)}"
            st.error(error_msg)
            if "model_not_found" in str(e):
                st.info("💡 Essaye de changer le modèle par 'llama-3.1-70b-versatile' dans le code.")
