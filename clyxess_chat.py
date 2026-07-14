import streamlit as st
from groq import Groq

st.set_page_config(page_title="ClyxessChat AI", page_icon="⚡", layout="wide")

# ===== KEY SECRET SE AAYEGI =====
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
MODEL = "llama-3.3-70b-versatile"

if "chat" not in st.session_state: st.session_state.chat = []

# ===== DARK PROFESSIONAL UI =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body {font-family: 'Inter';}
.stApp {background: #0F1117; color: #ECECF1;}
[data-testid="stSidebar"] {background: #171A21; border-right: 1px solid #2A2E38;}
.main-title {text-align: center; font-size: 56px; font-weight: 700; margin-top: 120px; color: #6366F1;}
.stChatInput {border-radius: 16px!important;}
.stButton>button {background: #6366F1!important; color: white!important; border-radius: 10px; border: none;}
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR CLEAN =====
with st.sidebar:
    st.markdown("<h2>⚡ ClyxessChat</h2>", unsafe_allow_html=True)
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat = []
        st.rerun()
    st.markdown("---")
    st.button("💻 Computer", disabled=True, use_container_width=True)
    st.button("📁 Spaces", disabled=True, use_container_width=True)
    st.button("📄 Artifacts", disabled=True, use_container_width=True)

# ===== MAIN =====
if len(st.session_state.chat) == 0:
    st.markdown("<h1 class='main-title'>ClyxessChat AI</h1>", unsafe_allow_html=True)

for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.write(msg)

# ===== SIRF 1 INPUT =====
if prompt := st.chat_input("Ask Clyxess anything..."):
    st.session_state.chat.append(("user", prompt))
    with st.chat_message("user"): st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            client = Groq(api_key=GROQ_API_KEY)
            res = client.chat.completions.create(model=MODEL, messages=[{"role":"user","content":prompt}])
            answer = res.choices[0].message.content
            st.write(answer)
            st.session_state.chat.append(("assistant", answer))
