import streamlit as st
from groq import Groq
import requests
import time
import uuid
from datetime import datetime

# ========== 1. CONFIG - YAHAN 3 KEY DAL DE ==========
GROQ_API_KEY = "gsk_yaha_teli_key_daal" # GROQ KEY
SUPABASE_URL = "https://ggcpqhmfjqibpleedlgg.supabase.co/rest/v1/" # SUPABASE URL
SUPABASE_KEY = "sb_publishable_9kgpcnkITeh-kTXyRFJg6A_qLLouJmn" # SUPABASE KEY
# ===================================================

# ========== 2. PAGE SETUP ==========
st.set_page_config(
    page_title="ClyxessChat AI Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 3. PROFESSIONAL CSS ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body {font-family: 'Inter';}
.stApp {background: #0F1117; color: #ECECF1;}
[data-testid="stSidebar"] {background: #171A21; border-right: 1px solid #2A2E38;}
h1 {text-align: center; font-size: 56px; font-weight: 700; margin-top: 40px; background: linear-gradient(90deg, #6366F1, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.stChatInput {border-radius: 16px!important; background: #171A21!important; border: 1px solid #2A2E38!important;}
.stButton>button {background: #6366F1!important; color: white!important; border-radius: 10px; border: none; font-weight: 600;}
.chat-bubble {padding: 15px; border-radius: 12px; margin: 10px 0;}
.user-bubble {background: #1E293B;}
.ai-bubble {background: #1A1F2E; border-left: 3px solid #6366F1;}
</style>
""", unsafe_allow_html=True)

# ========== 4. SESSION STATE ==========
if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "current_session_id" not in st.session_state: st.session_state.current_session_id = str(uuid.uuid4())
if "models" not in st.session_state: st.session_state.models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

def new_chat():
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.chat_sessions[st.session_state.current_session_id] = []

# ========== 5. SUPABASE FUNCTIONS ==========
def save_to_supabase(query, response):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        payload = {"user_query": query, "ai_response": response[:2000], "model": st.session_state.get('selected_model'), "timestamp": datetime.now().isoformat()}
        requests.post(f"{SUPABASE_URL}chat_logs", headers=headers, json=payload, timeout=5)
    except: pass

# ========== 6. SIDEBAR ==========
with st.sidebar:
    st.markdown("<h2>⚡ ClyxessChat Pro</h2>", unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True, on_click=new_chat):
        st.rerun()

    st.markdown("---")
    st.session_state.selected_model = st.selectbox("🧠 AI Model", st.session_state.models)
    st.session_state.temperature = st.slider("🌡️ Creativity", 0.0, 1.0, 0.7)

    st.markdown("---")
    st.markdown("**📜 Chat History**")
    for sid in list(st.session_state.chat_sessions.keys())[-10:]:
        if st.session_state.chat_sessions[sid]:
            first_msg = st.session_state.chat_sessions[sid][0]["content"][:30]
            if st.button(f"💬 {first_msg}...", key=sid):
                st.session_state.current_session_id = sid
                st.rerun()

# ========== 7. MAIN CHAT AREA ==========
st.title("ClyxessChat AI")

current_chat = st.session_state.chat_sessions.get(st.session_state.current_session_id, [])

if len(current_chat) == 0:
    st.markdown("<p style='text-align:center; color:#9CA3AF;'>Start a new conversation. Powered by Groq</p>", unsafe_allow_html=True)

# Chat display
for msg in current_chat:
    bubble_class = "user-bubble" if msg["role"] == "user" else "ai-bubble"
    avatar = "👤" if msg["role"] == "user" else "⚡"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(f"<div class='chat-bubble {bubble_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# ========== 8. CHAT INPUT + LOGIC ==========
if prompt := st.chat_input("Message Clyxess..."):
    # User msg save
    current_chat.append({"role": "user", "content": prompt})
    st.session_state.chat_sessions[st.session_state.current_session_id] = current_chat
    st.rerun()

    # AI response
    with st.chat_message("assistant", avatar="⚡"):
        msg_placeholder = st.empty()
        full_response = ""
        try:
            client = Groq(api_key=GROQ_API_KEY)
            stream = client.chat.completions.create(
                model=st.session_state.selected_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=st.session_state.temperature,
                max_tokens=4096,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    msg_placeholder.markdown(f"<div class='chat-bubble ai-bubble'>{full_response}▌</div>", unsafe_allow_html=True)
                    time.sleep(0.005)
            msg_placeholder.markdown(f"<div class='chat-bubble ai-bubble'>{full_response}</div>", unsafe_allow_html=True)

            current_chat.append({"role": "assistant", "content": full_response})
            st.session_state.chat_sessions[st.session_state.current_session_id] = current_chat
            save_to_supabase(prompt, full_response)

        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("<p style='text-align:center; color:#6B7280; font-size:12px;'>ClyxessChat
