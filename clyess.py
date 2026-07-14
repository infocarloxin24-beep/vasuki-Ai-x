import streamlit as st
import requests
import json
from groq import Groq
from streamlit_mic_recorder import mic_recorder

# =============== [तेरी सीक्रेट कीज यहाँ] ===============
HIDDEN_GROQ_API_KEY = "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"
SUPABASE_URL = "https://ggcpqhmfjqibpleedlgg.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_publishable_9kgpcnkITeh-kTXyRFJg6A_qLLouJmn"
# =========================================================

# 1. CHATGPT JAISE PAGE CONFIG + DARK THEME
st.set_page_config(page_title="ClyxessChat AI Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
   .stApp { background-color: #212121; color: #e5e7eb; }
    [data-testid="stSidebar"] {background-color: #171717;}
   .stTextArea textarea { background-color: #303030!important; color: white!important; border: 1px solid #555!important; border-radius: 12px; }
   .stChatInput {border-radius: 20px;}
   .transparent-link {
        display: block; padding: 14px; margin: 10px 0;
        background: rgba(33, 150, 243, 0.08); border: 1px solid rgba(33, 150, 243, 0.35);
        border-radius: 10px; color: #4facfe!important;
        text-decoration: none; font-weight: bold; text-align: center;
        font-size: 13px; transition: 0.2s;
    }
   .transparent-link:hover {
        background: rgba(33, 150, 243, 0.15); border-color: #2196F3;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CHATGPT JAISE SIDEBAR
with st.sidebar:
    st.title("⚡ ClyxessChat Pro")
    if st.button("+ New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("AI Model")
    model_select = st.selectbox("", ["qwen-2.5-coder-32b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"])

    st.subheader("Settings")
    st.success("🔒 API Key Hidden")
    st.caption("v2.0 - ChatGPT UI + Voice + Image")

# 3. MAIN CHAT AREA - CHATGPT JAISE
st.title("What's on your mind today?")

# Suggested prompts
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("💻 HTML Login Page Banao", use_container_width=True):
        st.session_state.prompt = "एक सुंदर HTML लॉगिन पेज बनाओ"
with col2:
    if st.button("🗺️ Map Link Chahiye", use_container_width=True):
        st.session_state.prompt = "रायपुर रेलवे स्टेशन का गूगल मैप लिंक दो"
with col3:
    if st.button("📷 Photo se Code", use_container_width=True):
        st.session_state.prompt = "इस फोटो जैसा UI बना दो"

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. INPUT + MIC + CAMERA + GALLERY
prompt_input = st.chat_input("⌨️ पूछें या नीचे टूल्स का उपयोग करें:")

col_mic, col_cam, col_gal = st.columns(3)
with col_mic:
    audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='recorder')
with col_cam:
    camera_photo = st.camera_input("📷", label_visibility="collapsed")
with col_gal:
    gallery_photo = st.file_input("🖼️", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

final_image = camera_photo if camera_photo else gallery_photo

if "prompt" in st.session_state:
    prompt_input = st.session_state.prompt
    del st.session_state.prompt

# VOICE TO TEXT
user_query = prompt_input
if audio_data and HIDDEN_GROQ_API_KEY!= "YOUR_SECRET_GROQ_API_KEY_HERE":
    with st.spinner("🔊 आवाज़ पहचानी जा रही है..."):
        try:
            client = Groq(api_key=HIDDEN_GROQ_API_KEY)
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_data['bytes']),
                model="whisper-large-v3",
                response_format="text"
            )
            user_query = transcription
            st.success(f"🗣️ पहचाना गया: '{user_query}'")
        except Exception as e:
            st.error(f"वॉइस एरर: {e}")

def upload_to_cloud(title, content):
    try:
        response = requests.post('https://dpaste.com', data={'content': content, 'title': title, 'expiry_days': 1})
        if response.status_code == 201:
            return response.text.strip() + ".txt"
    except Exception:
        return None
    return None

# 5. MAIN LOGIC
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    if HIDDEN_GROQ_API_KEY == "YOUR_SECRET_GROQ_API_KEY_HERE":
        st.error("कृपया पहले लाइन 9 में अपनी असली Groq API Key डालें!")
    else:
        client = Groq(api_key=HIDDEN_GROQ_API_KEY)
        with st.chat_message("assistant"):
            msg_placeholder = st.empty()
            with st.spinner("🧠 Clyxess प्रोसेस कर रहा है..."):
                try:
                    image_description = ""
                    if final_image:
                        image_description = "\n[User attached a UI photo. Analyze and clone it perfectly.]"

                    full_context = user_query + image_description

                    router_prompt = f"Analyze: '{full_context}'. If user asks for general info, map links, website links, or casual chat, answer CHAT. If they ask to generate programming code/files, answer CODE. One word only: 'CODE' or 'CHAT'."
                    router_comp = client.chat.completions.create(model=model_select, messages=[{"role": "user", "content": router_prompt}], temperature=0.0)
                    decision = router_comp.choices[0].message.content.strip().upper()

                    full_response = ""
                    # CASE 1: CHAT
                    if "CHAT" in decision:
                        chat_comp = client.chat.completions.create(
                            model=model_select,
                            messages=[{"role": "user", "content": f"Respond natively in the user's language. Provide direct clickable markdown links if they asked for any website or map location: {full_context}"}],
                            temperature=0.4,
                            stream=True
                        )
                        for chunk in chat_comp:
                            if chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                                msg_placeholder.write(full_response + "▌")

                    # CASE 2: CODE
                    else:
                        struct_prompt = f"Plan architecture JSON for code request: '{full_context}'. Format: {{ 'PART 1: Name.ext': 'desc' }}. JSON ONLY."
                        struct_comp = client.chat.completions.create(model=model_select, messages=[{"role": "user", "content": struct_prompt}], temperature=0.0)

                        try:
                            file_map = json.loads(struct_comp.choices[0].message.content)
                        except Exception:
                            file_map = {"PART 1: Full Implementation.py": "Code compilation"}

                        full_response = "### 💻 पारदर्शी लिंक्स जनरेट हो गए:\n"
                        for file_name, file_desc in file_map.items():
                            code_prompt = f"Write full code for '{file_name}'. Context: {file_desc}. Target: {full_context}. No placeholders. Code only."
                            code_comp = client.chat.completions.create(model=model_select, messages=[{"role": "user", "content": code_prompt}], temperature=0.0)

                            cloud_link = upload_to_cloud(file_name, code_comp.choices[0].message.content)
                            if cloud_link:
                                full_response += f"<a href='{cloud_link}' target='_blank' class='transparent-link'>🔗 {file_name} (ओपन करें)</a>\n"
                        full_response += "\n🎉 कार्य सफलतापूर्वक पूर्ण हुआ!"
                        msg_placeholder.markdown(full_response, unsafe_allow_html=True)

                    msg_placeholder.markdown(full_response, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"एरर: {e}")
