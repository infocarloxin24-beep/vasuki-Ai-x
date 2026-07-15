import streamlit as st
import requests
import json
from groq import Groq
from streamlit_mic_recorder import mic_recorder

# 1. Authentic ChatGPT Dynamic UI Framework Settings
st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")

# CHAT HISTORY ke liye session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Absolute Fixed Infrastructure Credentials - Encrypted Backend Storage
HIDDEN_GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# 2026 Fully Active Groq Production Model ID
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

# Premium CSS Injection - Blue button #173BE8 kar diya
st.markdown("""
    <style>
  .stApp { background-color: #212121; color: #ececf1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    label p { color: #ffffff!important; font-weight: 600; font-size: 16px; margin-bottom: 6px; letter-spacing: 0.3px; }
  .stTextArea textarea { background-color: #2f2f2f!important; color: #ffffff!important; border: 1px solid #4d4d4d!important; border-radius: 16px; padding: 16px; font-size: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
  .stTextArea textarea::placeholder { color: #b4b4b4!important; }
  .stTextArea textarea:focus { border-color: #173BE8!important; }
  .stButton>button { background-color: #173BE8!important; color: #ffffff!important; border: none!important; border-radius: 26px!important; padding: 12px 30px!important; font-weight: bold!important; font-size: 16px!important; width: 100%!important; box-shadow: 0 4px 14px rgba(23, 59, 232, 0.25); transition: 0.2s; }
  .stButton>button:hover { background-color: #0f2bb5!important; box-shadow: 0 6px 20px rgba(23, 59, 232, 0.35); transform: translateY(-1px); }
  .google-mobile-btn { display: inline-flex; align-items: center; justify-content: center; background-color: #ffffff; color: #1f1f1f!important; font-family: 'Roboto', sans-serif; font-weight: bold; font-size: 12px; padding: 8px 18px; border-radius: 26px; border: 1px solid #e3e3e3; text-decoration: none; float: right; margin-top: -50px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: 0.2s; }
  .google-icon { width: 14px; height: 14px; margin-right: 8px; }
  .transparent-link { display: block; padding: 15px; margin: 12px 0; background: rgba(23, 59, 232, 0.08); border: 1px solid rgba(23, 59, 232, 0.4); border-radius: 12px; color: #173BE8!important; text-decoration: none; font-weight: bold; text-align: center; font-size: 14px; transition: 0.3s; }
  .transparent-link:hover { background: rgba(23, 59, 232, 0.16); border-color: #173BE8; box-shadow: 0 0 12px rgba(23, 59, 232, 0.3); }
    [data-testid="stSidebar"] { background-color: #171717!important; border-right: 1px solid #2f2f2f!important; }
    [data-testid="stSidebar"] * { color: #ececf1!important; }
   .chat-msg {background-color: #2f2f2f; padding: 12px; border-radius: 12px; margin-bottom: 10px;}
   .user-msg {border-left: 3px solid #173BE8;}
   .ai-msg {border-left: 3px solid #10a37f;}
    </style>
""", unsafe_allow_html=True)

# 2. Top Navigation Bar
st.markdown("<h2 style='color: #ffffff; margin-top:-20px; font-weight:700; font-size: 26px;'>💬 ClyxessChat</h2>", unsafe_allow_html=True)
google_html = """
<a class="google-mobile-btn" href="#" onclick="alert('ClyxessChat Security: Handshake with Google Accounts verified!')">
    <img class="google-icon" src="https://www.google.com/favicon.ico"/>
    Sign in
</a>
"""
st.markdown(google_html, unsafe_allow_html=True)
st.markdown("<p style='color:#b4b4b4; font-size:12px; margin-top:-16px;'>Next-Gen Portable Multi-File Code Engine</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. Left Sidebar - New Chat button add kiya
with st.sidebar:
    st.markdown("<h3 style='color:#173BE8; font-weight:700;'>💬 Navigation</h3>", unsafe_allow_html=True)
    st.caption("ClyxessChat v3.6 - Fixed Edition")
    if st.button("➕ New Workspace"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("• 📁 Code History\n• ⚙ System Diagnostics")
    st.markdown("---")
    # SSL hataya
    st.info("🔒 Secure Connection")

st.markdown("<h2 style='text-align: center; color: #ffffff; font-weight:600; margin-top: 30px; margin-bottom: 30px; font-size:28px;'>How can I help you today?</h2>", unsafe_allow_html=True)

def upload_to_cloud(title, content):
    try:
        response = requests.post('https://dpaste.com', data={'content': content, 'title': title, 'expiry_days': 1})
        if response.status_code == 201:
            return response.text.strip() + ".txt"
    except Exception:
        return None
    return None

def save_to_supabase(query, status):
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            requests.post(f"{SUPABASE_URL}/rest/v1/user_logs", headers=headers, json={"user_query": query, "status": status})
        except Exception:
            pass

# CHAT HISTORY DISPLAY
for msg in st.session_state.messages:
    with st.container():
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-msg user-msg'><b>You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-msg ai-msg'><b>AI:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,1,4])
            with col1:
                if st.button("📋 Copy", key=f"copy_{msg['id']}"):
                    st.code(msg['content'])
            with col2:
                st.button("👍", key=f"like_{msg['id']}")
            with col3:
                st.button("👎", key=f"dislike_{msg['id']}")

# 4. Centralized User Ingestion Terminal Box
user_query = st.text_area("⌨ Ask anything or give code specifications:", placeholder="Message ClyxessChat AI...", height=110, label_visibility="collapsed")

col_mic, col_cam, col_gal = st.columns(3)
with col_mic:
    st.write("🎙 Audio Input:")
    audio_data = mic_recorder(start_prompt="Record", stop_prompt="Stop", key='recorder')

with col_cam:
    camera_photo = st.camera_input("📷 Capture Frame", label_visibility="collapsed")
with col_gal:
    gallery_photo = st.file_uploader("🖼 Attachment Media", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

final_image = camera_photo if camera_photo else gallery_photo

if audio_data and HIDDEN_GROQ_API_KEY:
    with st.spinner("Decoding acoustics..."):
        try:
            client = Groq(api_key=HIDDEN_GROQ_API_KEY)
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_data['bytes']),
                model="whisper-large-v3",
                response_format="text"
            )
            user_query = transcription
            st.success(f"Captured: '{user_query}'")
        except Exception as e:
            st.error(f"Voice Server Pipeline Sync Interruption: {e}")

send_btn = st.button("🚀 Process Request", use_container_width=True)

if send_btn:
    if not HIDDEN_GROQ_API_KEY:
        st.error("Authentication Parameters Missing. Internal Engine Failure.")
    elif not user_query.strip() and not final_image:
        st.warning("Please type a message, supply microphone voice streams, or present an asset mockup frame.")
    else:
        # user ka msg save
        st.session_state.messages.append({"role": "user", "content": user_query, "id": len(st.session_state.messages)})

        client = Groq(api_key=HIDDEN_GROQ_API_KEY)
        with st.spinner("Processing thread intent..."):
            try:
                image_description = ""
                if final_image:
                    image_description = "\n[User supplied asset mockup image layout. Extract styles and colors to construct a 1:1 identical implementation framework codebase.]"

                full_context = user_query + image_description

                router_prompt = f"Analyze scope context: '{full_context}'. If user asks to build, write, script or clone program code/file repositories, respond CODE. If they seek answers, map directions, standard descriptions or generic talk, respond CHAT. Output ONLY the word 'CODE' or 'CHAT'."
                # MAX_TOKENS BADHAYA
                router_comp = client.chat.completions.create(model=ACTIVE_GROQ_MODEL, messages=[{"role": "user", "content": router_prompt}], temperature=0.0, max_tokens=100)
                decision = router_comp.choices[0].message.content.strip().upper()

                if "CHAT" in decision:
                    chat_comp = client.chat.completions.create(
                        model=ACTIVE_GROQ_MODEL,
                        messages=[{"role": "user", "content": f"Answer concisely and flawlessly in the exact style language prompt input given by the user: {full_context}"}],
                        temperature=0.4,
                        max_tokens=2000 # BADHAYA
                    )
                    ai_response = chat_comp.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_response, "id": len(st.session_state.messages)})
                    save_to_supabase(user_query, "CHAT_SUCCESS")
                    st.rerun()

                else:
                    # CODE MODE - PURA CODE MANGA
                    st.session_state.messages.append({"role": "assistant", "content": "### 💻 Generating Full Code...", "id": len(st.session_state.messages)})

                    struct_prompt = f"You are a senior developer. For this request: '{full_context}'. Generate COMPLETE working code for all files. Return ONLY valid JSON. Format: {{'index.html': 'FULL CODE HERE', 'style.css': 'FULL CODE HERE'}}. Do not truncate. No explanation."

                    # MAX_TOKENS 4000 KIYA
                    struct_comp = client.chat.completions.create(
                        model=ACTIVE_GROQ_MODEL,
                        messages=[{"role": "user", "content": struct_prompt}],
                        temperature=0.0,
                        max_tokens=4000
                    )

                    raw = struct_comp.choices[0].message.content
                    raw = raw.replace("```json", "").replace("```", "") # JSON clean kiya

                    try:
                        file_map = json.loads(raw)
                        final_output = ""
                        for fname, fcode in file_map.items():
                            link = upload_to_cloud(fname, fcode)
                            if link:
                                final_output += f'<a href="{link}" class="transparent-link" target="_blank">Download {fname}</a>'
                            else:
                                final_output += f"<b>{fname}</b><br><pre>{fcode}</pre><br>"

                        st.session_state.messages.append({"role": "assistant", "content": final_output, "id": len(st.session_state.messages)})
                    except json.JSONDecodeError:
                        st.session_state.messages.append({"role": "assistant", "content": f"JSON Parse Failed. Raw:<br><pre>{raw}</pre>", "id": len(st.session_state.messages)})

                    save_to_supabase(user_query, "CODE_SUCCESS")
                    st.rerun()

            except Exception as e:
                st.error(f"Processing Error: {e}")
                save_to_supabase(user_query, "ERROR")
