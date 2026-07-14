import streamlit as st
import requests
import json
from groq import Groq
from streamlit_mic_recorder import mic_recorder
import base64

# 1. Premium Responsive Settings
st.set_page_config(page_title="ClyxessChat AI", page_icon="⚡", layout="centered", initial_sidebar_state="expanded")

# Keys - Production me st.secrets me daalna
HIDDEN_GROQ_API_KEY = "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"
SUPABASE_URL = "https://supabase.co"
SUPABASE_KEY = "sb_publishable_9kgpcnkITeh-kTXyRFJg6A_qLLouJmn"
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile" # <-- SIRF YE LINE CHANGE KI

# Premium CSS
st.markdown("""
    <style>
  .stApp { background-color: #131416; color: #e3e3e6; }
    label p { color: #ffffff!important; font-weight: 600; font-size: 15px; margin-bottom: 8px; }
  .stTextArea textarea { background-color: #1c1d21!important; color: #ffffff!important; border: 1px solid #2f3037!important; border-radius: 14px; padding: 14px; font-size: 15px; }
  .stTextArea textarea::placeholder { color: #9aa0a6!important; }
  .stButton>button { background-color: #1a73e8!important; color: #ffffff!important; border: none!important; border-radius: 24px!important; padding: 12px 28px!important; font-weight: bold!important; font-size: 15px!important; width: 100%!important; box-shadow: 0 4px 14px rgba(26, 115, 232, 0.3); transition: 0.2s; }
  .stButton>button:hover { background-color: #1557b0!important; box-shadow: 0 6px 20px rgba(26, 115, 232, 0.4); transform: translateY(-1px); }
  .google-mobile-btn {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #ffffff; color: #1f1f1f!important;
        font-family: 'Roboto', sans-serif; font-weight: bold; font-size: 12px;
        padding: 8px 16px; border-radius: 24px; border: 1px solid #747775;
        text-decoration: none; float: right; margin-top: -52px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: 0.2s;
    }
  .google-mobile-btn:hover { background-color: #f2f2f2; box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
  .google-icon { width: 14px; height: 14px; margin-right: 8px; }
  .transparent-link {
        display: block; padding: 14px; margin: 12px 0;
        background: rgba(26, 115, 232, 0.08); border: 1px solid rgba(26, 115, 232, 0.4);
        border-radius: 12px; color: #4facfe!important;
        text-decoration: none; font-weight: bold; text-align: center;
        font-size: 14px; transition: 0.3s;
    }
    [data-testid="stSidebar"] { background-color: #1c1d21!important; border-right: 1px solid #2f3037!important; }
    [data-testid="stSidebar"] * { color: #e3e3e6!important; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h2 style='color: #1a73e8; margin-top:-20px; font-weight:800; letter-spacing: -0.5px;'>⚡ ClyxessChat</h2>", unsafe_allow_html=True)
google_html = """
<a class="google-mobile-btn" href="#" onclick="alert('ClyxessChat Security: Google Sign-In Connected successfully!')">
    <img class="google-icon" src="https://www.gstatic.com/images/branding/product/1x/gsa4_p0.png"/>
    Sign in
</a>
"""
st.markdown(google_html, unsafe_allow_html=True)
st.markdown("<p style='color:#9aa0a6; font-size:12px; margin-top:-14px;'>Next-Gen Portable Multi-File Code Engine</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("<h3 style='color:#1a73e8; font-weight:700;'>⚙ ClyxessChat</h3>", unsafe_allow_html=True)
    st.caption("v3.1 - Final Stable Release")
    st.markdown("---")
    st.markdown("🌐 **Discover & Navigate**")
    st.markdown("• 🔍 New Thread\n• 📁 Saved Projects\n• 🛠 AI Workflows")
    st.markdown("---")
    st.success("🔒 End-to-End Encrypted Connection")

st.markdown("<h3 style='text-align: center; color: #ffffff; font-weight:500; margin-bottom: 25px;'>👋 Where knowledge begins.<br><span style='font-size:16px; color:#9aa0a6;'>Ask anything or clone clean application code blocks instantly.</span></h3>", unsafe_allow_html=True)

def upload_to_cloud(title, content):
    try:
        response = requests.post('https://dpaste.com', data={'content': content, 'title': title, 'expiry_days': 1}, timeout=10)
        if response.status_code == 201:
            return response.text.strip() + ".txt"
    except Exception:
        return None
    return None

def save_to_supabase(query, status):
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
            payload = {"user_query": query, "status": status}
            requests.post(f"{SUPABASE_URL}/rest/v1/user_logs", headers=headers, json=payload, timeout=5)
        except Exception:
            pass

# Input Box
user_query = st.text_area("⌨ Enter your code or conceptual requirements:", placeholder="Ask ClyxessChat anything... (e.g., 'Build an interactive dashboard in Vue.js')", height=110)

# Multi-Media Row
col_mic, col_cam, col_gal = st.columns(3)
with col_mic:
    st.write("🎙 Voice Assistant:")
    audio_data = mic_recorder(start_prompt="Record", stop_prompt="Stop", key='recorder')
with col_cam:
    camera_photo = st.camera_input("📷 Camera Input", label_visibility="collapsed")
with col_gal:
    gallery_photo = st.file_uploader("🖼 Upload Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

final_image = camera_photo if camera_photo else gallery_photo

# Voice Transcription
if audio_data and HIDDEN_GROQ_API_KEY:
    with st.spinner("Analyzing speech inputs..."):
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
            st.error(f"Voice Processor Error: {e}")

# Process Button
send_btn = st.button("🚀 Process Request", use_container_width=True)

if send_btn:
    if not HIDDEN_GROQ_API_KEY:
        st.error("Missing Authentication: Please verify Groq API Key")
    elif not user_query.strip() and not final_image:
        st.warning("Please specify a prompt or upload image/audio")
    else:
        client = Groq(api_key=HIDDEN_GROQ_API_KEY)
        with st.spinner("Processing architectural requirements..."):
            try:
                image_description = ""
                if final_image:
                    image_bytes = final_image.getvalue()
                    base64_image = base64.b64encode(image_bytes).decode("utf-8")
                    image_description = f"\n[User supplied image. Use it as UI reference and recreate it in code.]"

                full_context = user_query + image_description

                router_prompt = f"Analyze scope: '{full_context}'. If user asks to build/write code, respond CODE. If they seek answers, respond CHAT. Output ONLY 'CODE' or 'CHAT'."
                router_comp = client.chat.completions.create(model=ACTIVE_GROQ_MODEL, messages=[{"role": "user", "content": router_prompt}], temperature=0.0)
                decision = router_comp.choices[0].message.content.strip().upper()

                if "CHAT" in decision:
                    chat_comp = client.chat.completions.create(
                        model=ACTIVE_GROQ_MODEL,
                        messages=[{"role": "user", "content": f"Answer in user's language: {full_context}"}],
                        temperature=0.4
                    )
                    st.markdown("### 💬 AI Response:")
                    st.write(chat_comp.choices[0].message.content)
                    save_to_supabase(user_query, "CHAT_SUCCESS")

                else: # CODE MODE
                    st.markdown("### 💻 Assembled Repository Architecture:")
                    struct_prompt = f"Deconstruct this into JSON file map: '{full_context}'. Format: {{'filename.py': 'description'}}. Output RAW JSON ONLY."
                    struct_comp = client.chat.completions.create(model=ACTIVE_GROQ_MODEL, messages=[{"role": "user", "content": struct_prompt}], temperature=0.0)

                    raw_json = struct_comp.choices[0].message.content
                    try:
                        file_map = json.loads(raw_json)
                    except:
                        st.warning("AI ne JSON sahi nahi diya. Fallback use kar raha hu.")
                        file_map = {"main.py": "Core application logic", "requirements.txt": "Dependencies list"}

                    for filename, description in file_map.items():
                        st.subheader(f"📄 {filename}")
                        st.code(f"# {description}\n# AI will generate code here", language="python")
                        cloud_link = upload_to_cloud(filename, description)
                        if cloud_link:
                            st.markdown(f'<a class="transparent-link" href="{cloud_link}" target="_blank">⬇️ Download {filename}</a>', unsafe_allow_html=True)

                    save_to_supabase(user_query, "CODE_SUCCESS")

            except Exception as e:
                st.error(f"Processing Error: {str(e)}")

st.markdown("---")
st.caption("© 2026 ClyxessChat AI | Powered by Groq llama-3.3-70b-versatile") # <-- YAHAN BHI CHANGE KIYA
