import streamlit as st
import requests
import json
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import time

st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

HIDDEN_GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

# CSS - ChatGPT wala clean design + chote icon
st.markdown("""
    <style>
.stApp { background-color: #212121; color: #ececf1; }
 [data-testid="stTextInput"] input { background-color: #2f2f2f!important; color: #ffffff!important; border-radius: 24px; padding: 12px 20px; border: 1px solid #444; }
.stButton>button { background-color: #173BE8!important; color: #ffffff!important; border-radius: 24px!important; border: none; font-weight: 600; }
.icon-btn { background: transparent!important; border: none!important; box-shadow: none!important; padding: 8px!important; width: 40px!important; height: 40px!important; font-size: 20px; }
.icon-btn:hover { background: #2f2f2f!important; border-radius: 50%!important; }
.input-row { display: flex; align-items: center; gap: 8px; }
.file-box {background:#2f2f2f; padding:15px; border-radius:12px; margin:10px 0; border:1px solid #444;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color: #ffffff; text-align:center;'>💬 ClyxessChat</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#b4b4b4; font-size:12px; text-align:center;'>Next-Gen Portable Multi-File Code Engine</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h3 style='color:#173BE8;'>💬 Navigation</h3>", unsafe_allow_html=True)
    if st.button("➕ New Workspace"):
        st.session_state.messages = []
        st.session_state.show_camera = False
    st.info("🔒 Secure Connection")

# CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# INPUT AREA - ChatGPT style
col1, col2, col3, col4 = st.columns([1,1,1,6])

with col1:
    # MIC - chota button
    if st.button("🎙️", key="mic", help="Record Audio", use_container_width=True):
        st.session_state.show_camera = False

with col2:
    # CAMERA - chota button, click pe hi khulega
    if st.button("📷", key="cam", help="Take Photo", use_container_width=True):
        st.session_state.show_camera = not st.session_state.show_camera

with col3:
    # UPLOAD - chota button
    uploaded_file = st.file_uploader("📎", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

with col4:
    # TEXT INPUT
    user_query = st.chat_input("Message ClyxessChat AI...")

# CAMERA SIRF CLICK PE KHOLEGA
if st.session_state.show_camera:
    camera_photo = st.camera_input("Take Photo", label_visibility="collapsed")
else:
    camera_photo = None

# MIC RECORDING
if HIDDEN_GROQ_API_KEY and st.session_state.get('mic_clicked', False):
    audio_data = mic_recorder(start_prompt="🔴", stop_prompt="⏹️", key='recorder')
    if audio_data:
        with st.spinner("Decoding..."):
            client = Groq(api_key=HIDDEN_GROQ_API_KEY)
            transcription = client.audio.transcriptions.create(file=("audio.wav", audio_data['bytes']), model="whisper-large-v3", response_format="text")
            user_query = transcription

final_image = camera_photo if camera_photo else uploaded_file

# JAB SEND HOGA
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.show_camera = False # camera band

    client = Groq(api_key=HIDDEN_GROQ_API_KEY)

    with st.chat_message("assistant"):
        with st.spinner("Generating..."):
            router_prompt = f"Analyze: '{user_query}'. If code request respond CODE. Else CHAT. Output ONLY 'CODE' or 'CHAT'."
            router_comp = client.chat.completions.create(model=ACTIVE_GROQ_MODEL, messages=[{"role": "user", "content": router_prompt}], temperature=0.0, max_tokens=10)
            decision = router_comp.choices[0].message.content.strip().upper()

            if "CHAT" in decision:
                chat_comp = client.chat.completions.create(model=ACTIVE_GROQ_MODEL, messages=[{"role": "user", "content": user_query}], temperature=0.4, max_tokens=2000)
                ai_response = chat_comp.choices[0].message.content
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

            else:
                struct_prompt = f"""You are a senior developer. User request: '{user_query}'
                Generate COMPLETE working code. Return ONLY valid JSON.
                Format: {{"index.html": "full code", "style.css": "full code", "script.js": "full code"}}"""

                struct_comp = client.chat.completions.create(model=ACTIVE_GROQ_MODEL, messages=[{"role": "user", "content": struct_prompt}], temperature=0.0, max_tokens=4000)
                raw = struct_comp.choices[0].message.content.replace("```json", "").replace("```", "").strip()

                try:
                    file_map = json.loads(raw)
                    for fname, fcode in file_map.items():
                        st.download_button(label=f"⬇️ Download {fname}", data=fcode, file_name=fname, mime="text/plain", key=f"{fname}_{time.time()}")
                        with st.expander(f"📄 {fname}"):
                            st.code(fcode, language=fname.split('.')[-1])
                    st.session_state.messages.append({"role": "assistant", "content": "✅ Code Generated. Download upar hai."})
                except:
                    st.error("Error in code generation")
                    st.session_state.messages.append({"role": "assistant", "content": "Code generation failed"})
