import streamlit as st
from groq import Groq
import requests
import json
import time
from datetime import datetime

# ================== CONFIG ==================
st.set_page_config(page_title="ClyxessChat AI", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# YE KEYS IDHAR HI FINAL HAI. BAR ADD NA KARNA PADEGA
HIDDEN_GROQ_API_KEY = "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"
SUPABASE_URL = "https://ggcpqhmfjqibpleedlgg.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_9kgpcnkITeh-kTXyRFJg6A_qLLouJmn"
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

# ================== SESSION STATE ==================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = "guest@clyxess.ai"

# ================== CSS ==================
st.markdown("""
    <style>
  .stApp { background-color: #FFFFFF; color: #1a1a1a; }
    [data-testid="stSidebar"] { background-color: #F7F7F8; border-right: 1px solid #E5E5E5; padding: 16px; }
    [data-testid="stSidebar"] * { color: #1a1a1a; }
  .main-title { text-align: center; font-size: 48px; font-weight: 600; margin-top: 100px; margin-bottom: 40px; letter-spacing: -1px; }
  .input-container { max-width: 760px; margin: 0 auto; position: fixed; bottom: 30px; left: 0; right: 0; padding: 0 20px; }
  .stTextArea textarea { border: 1px solid #E5E5E5!important; border-radius: 16px!important; padding: 18px 20px!important; font-size: 16px; background: #FFFFFF!important; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
  .stTextArea textarea:focus { border: 1px solid #1a73e8!important; box-shadow: 0 0 0 3px rgba(26,115,232,0.1); }
  .stButton>button { border-radius: 12px; font-weight: 600; padding: 12px; }
  .chat-msg { padding: 16px; border-radius: 12px; margin: 12px auto; max-width: 800px; }
  .user-msg { background: #1a73e8; color: white; margin-left: 20%; }
  .ai-msg { background: #F7F7F8; border: 1px solid #E5E5E5; margin-right: 20%; }
    </style>
""", unsafe_allow_html=True)

# ================== SUPABASE FUNCTIONS ==================
def save_to_supabase(email, query, response, status):
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        payload = {
            "email": email,
            "user_query": query,
            "ai_response": response[:500], # 500 char tak save
            "status": status,
            "created_at": datetime.now().isoformat()
        }
        requests.post(f"{SUPABASE_URL}chat_logs", headers=headers, json=payload, timeout=5)
    except Exception as e:
        print("Supabase Error:", e)

def get_user_chats(email):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        res = requests.get(f"{SUPABASE_URL}chat_logs?email=eq.{email}&order=created_at.desc&limit=10", headers=headers, timeout=5)
        return res.json()
    except:
        return []

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("<h2 style='font-size:22px; font-weight:700; margin-bottom:20px;'>⚡ ClyxessChat</h2>", unsafe_allow_html=True)

    # NEW CHAT
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_history = []
        st.toast("New Chat Started", icon="✨")
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # SIDEBAR MENU - SAB KAAM KAREGA
    menu_items = {
        "Computer": "AI Agent mode",
        "Spaces": "Your workspaces",
        "Artifacts": "Generated files",
        "Customize": "Theme & Settings",
        "Connectors": "Connect Google, Notion",
        "Skills": "Specialized AI Skills",
        "Workflows": "Automate tasks"
    }
    for item, desc in menu_items.items():
        if st.button(f"📁 {item}", key=f"sidebar_{item}", use_container_width=True):
            st.toast(f"{item}: {desc}", icon="🚀")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**📜 History**")

    # Supabase se history load
    if st.session_state.logged_in:
        old_chats = get_user_chats(st.session_state.user_email)
        if len(old_chats) == 0:
            st.caption("No saved chats")
        else:
            for chat in old_chats[:5]:
                if st.button(chat['user_query'][:25]+"...", key=f"old_{chat['created_at']}", use_container_width=True):
                    st.toast("Loading old chat - Coming Soon")
    else:
        st.caption("Login to see history")

    st.markdown("<div style='position:absolute; bottom:20px; width:85%;'>", unsafe_allow_html=True)

    # LOGIN SYSTEM - FINAL
    if not st.session_state.logged_in:
        email_input = st.text_input("Email", placeholder="you@gmail.com", key="login_email")
        if st.button("👤 Sign In", use_container_width=True):
            if email_input:
                st.session_state.logged_in = True
                st.session_state.user_email = email_input
                st.toast(f"Welcome {email_input}", icon="✅")
                st.rerun()
            else:
                st.warning("Email daalo bhai")
    else:
        st.success(f"Logged in: {st.session_state.user_email}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = "guest@clyxess.ai"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ================== MAIN CHAT AREA ==================
if len(st.session_state.chat_history) == 0:
    st.markdown("<h1 class='main-title'>clyxesschat</h1>", unsafe_allow_html=True)

# DISPLAY CHAT
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-msg user-msg'><b>You:</b><br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-msg ai-msg'><b>⚡ Clyxess:</b><br>{msg}</div>", unsafe_allow_html=True)

# ================== INPUT BOX ==================
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
col_input, col_send = st.columns([8,1])
with col_input:
    user_query = st.text_area("Ask anything...", placeholder="Ask anything... Shift+Enter for new line", height=68, label_visibility="collapsed", key="main_input")
with col_send:
    send_btn = st.button("➤", use_container_width=True, key="send", type="primary", help="Send")
st.markdown("</div>", unsafe_allow_html=True)

# ================== PROCESS LOGIC ==================
if send_btn and user_query.strip():
    # User message add
    st.session_state.chat_history.append(("user", user_query))

    with st.spinner("Clyxess is thinking..."):
        try:
            client = Groq(api_key=HIDDEN_GROQ_API_KEY)

            # AI Response
            chat_comp = client.chat.completions.create(
                model=ACTIVE_GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are ClyxessChat AI, a helpful and intelligent assistant. Answer in the same language as user. Be concise and useful."},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=2048,
                stream=False
            )
            response = chat_comp.choices[0].message.content

            # AI message add
            st.session_state.chat_history.append(("assistant", response))

            # Supabase me save
            if st.session_state.logged_in:
                save_to_supabase(st.session_state.user_email, user_query, response, "SUCCESS")

        except Exception as e:
            error_msg = f"API Error: {str(e)}. Key ya billing check karo."
            st.error(error_msg)
            st.session_state.chat_history.append(("assistant", "Sorry, API me dikkat aa gayi. Thodi der baad try karo."))

    st.rerun()

# Footer
st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#999; font-size:12px;'>© 2026 ClyxessChat AI | Powered by Groq</p>", unsafe_allow_html=True)
