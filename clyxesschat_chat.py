import streamlit as st
from groq import Groq
import requests
from datetime import datetime
import base64

st.set_page_config(page_title="ClyxessChat AI", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ===== KEYS =====
HIDDEN_GROQ_API_KEY = "gsk_TERI_NAYI_KEY_YAHA_DAALO" 
SUPABASE_URL = "https://ggcpqhmfjqibpleedlgg.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_9kgpcnkITeh-kTXyRFJg6A_qLLouJmn"
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = "guest@clyxess.ai"

# ===== LOGO KO BASE64 ME CONVERT =====
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_b64 = get_base64_image("An_awHticOwWVVmpZfE7QC59GzLXFCtIBtYbTe5TYqpRVMir3o5JbQJ7S_9hetCIbjtZL99VTjDe8yLl_th8KLpbZWB5tMLGUg8qkQRueP8heDy6j-LgZciL")

# ===== PROFESSIONAL DARK CSS =====
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
  .stApp {{ background-color: #0F1117; color: #ECECF1; }}
    [data-testid="stSidebar"] {{ background-color: #171A21; border-right: 1px solid #2A2E38; }}
  .sidebar-logo {{ text-align: center; padding: 20px 0; }}
  .sidebar-logo img {{ width: 80px; }}
  .sidebar-title {{ text-align: center; font-size: 18px; font-weight: 700; color: #6366F1; margin-bottom: 20px; }}
  .main-title {{ text-align: center; font-size: 52px; font-weight: 700; margin-top: 80px; margin-bottom: 20px; }}
  .main-title span {{ color: #6366F1; }}
  .input-container {{ max-width: 800px; margin: 0 auto; position: fixed; bottom: 40px; left: 0; right: 0; padding: 0 20px; }}
  .stTextArea textarea {{ border: 1px solid #2A2E38!important; border-radius: 16px!important; padding: 20px 24px!important; font-size: 16px; background: #171A21!important; color: #ECECF1!important; }}
  .stButton>button {{ border-radius: 12px; font-weight: 600; background: #6366F1!important; color: white!important; border: none; }}
  .chat-msg {{ padding: 16px 20px; border-radius: 12px; margin: 16px auto; max-width: 800px; line-height: 1.6; }}
  .user-msg {{ background: #6366F1; color: white; margin-left: 15%; }}
  .ai-msg {{ background: #171A21; border: 1px solid #2A2E38; margin-right: 15%; }}
    </style>
""", unsafe_allow_html=True)

def save_to_supabase(email, query, response, status):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        payload = {"email": email, "user_query": query, "ai_response": response[:1000], "status": status, "created_at": datetime.now().isoformat()}
        requests.post(f"{SUPABASE_URL}chat_logs", headers=headers, json=payload, timeout=5)
    except: pass

# ===== SIDEBAR WITH REAL LOGO =====
with st.sidebar:
    st.markdown(f"""
        <div class='sidebar-logo'>
            <img src="data:image/png;base64,{logo_b64}">
        </div>
        <div class='sidebar-title'>ClyxessChat AI</div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    
    # SIRF KAAM KE 4 BUTTON
    if st.button("💻 Computer", use_container_width=True): st.toast("AI Agent Mode - Coming Soon")
    if st.button("📁 Spaces", use_container_width=True): st.toast("Workspaces - Coming Soon")
    if st.button("📄 Artifacts", use_container_width=True): st.toast("Generated Files - Coming Soon")
    if st.button("⚙️ Settings", use_container_width=True): st.toast("Settings - Coming Soon")
    
    st.markdown("---")
    st.markdown("**📜 History**")
    st.caption("Login to save chats")

    st.markdown("<div style='position:absolute; bottom:20px; width:85%;'>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        email_input = st.text_input("Email", placeholder="you@gmail.com", key="login_email", label_visibility="collapsed")
        if st.button("👤 Sign In", use_container_width=True):
            if email_input:
                st.session_state.logged_in = True
                st.session_state.user_email = email_input
                st.rerun()
    else:
        st.success(f"{st.session_state.user_email}")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ===== MAIN AREA =====
if len(st.session_state.chat_history) == 0:
    st.markdown(f"""
        <div style='text-align:center; margin-top:60px;'>
            <img src="data:image/png;base64,{logo_b64}" width="120">
            <h1 class='main-title'><span>Clyxess</span>Chat AI</h1>
        </div>
    """, unsafe_allow_html=True)

for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-msg user-msg'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-msg ai-msg'>⚡ {msg}</div>", unsafe_allow_html=True)

# ===== SIRF 1 INPUT BOX =====
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
col_input, col_send = st.columns([9,1])
with col_input:
    user_query = st.text_area("Ask", placeholder="Ask Clyxess anything...", height=65, label_visibility="collapsed", key="main_input")
with col_send:
    send_btn = st.button("➤", use_container_width=True, key="send", type="primary")
st.markdown("</div>", unsafe_allow_html=True)

# ===== LOGIC =====
if send_btn and user_query.strip():
    st.session_state.chat_history.append(("user", user_query))
    with st.spinner("Thinking..."):
        try:
            client = Groq(api_key=HIDDEN_GROQ_API_KEY)
            chat_comp = client.chat.completions.create(
                model=ACTIVE_GROQ_MODEL,
                messages=[{"role": "user", "content": user_query}],
                temperature=0.7, max_tokens=2048
            )
            response = chat_comp.choices[0].message.content
            st.session_state.chat_history.append(("assistant", response))
            if st.session_state.logged_in:
                save_to_supabase(st.session_state.user_email, user_query, response, "SUCCESS")
        except Exception as e:
            st.error("API Error: Key/Billing check karo")
            st.session_state.chat_history.append(("assistant", "Sorry, API me dikkat hai."))
    st.rerun()
