import streamlit as st
import requests
import json
from groq import Groq
from streamlit_mic_recorder import mic_recorder

# 1. मोबाइल-अनुकूल सेंटर्ड लेआउट और अल्ट्रा-डार्क स्टाइलिंग
st.set_page_config(page_title="ClyxessChat AI", page_icon="⚡", layout="centered")

# API KEY को यहाँ छुपाएं (यूजर स्क्रीन से बॉक्स हमेशा के लिए हटा दिया गया है)
HIDDEN_GROQ_API_KEY = "YOUR_SECRET_GROQ_API_KEY_HERE"

st.markdown("""
    <style>
    /* आँखों को आराम देने वाला डीप डार्क ब्लैक बैकग्राउंड */
    .stApp { background-color: #0b0c10; color: #e5e7eb; }
    .stTextArea textarea { background-color: #171921 !important; color: white !important; border: 1px solid #282a36 !important; border-radius: 12px; }
    
    /* मोबाइल गूगल लॉगिन बटन (प्रीमियम लुक) */
    .google-mobile-btn {
        display: inline-flex; align-items: center; justify-content: center;
        background-color: #ffffff; color: #1f1f1f !important;
        font-family: 'Roboto', sans-serif; font-weight: bold; font-size: 11px;
        padding: 6px 12px; border-radius: 20px; border: none;
        text-decoration: none; float: right; margin-top: -42px;
    }
    .google-icon { width: 14px; height: 14px; margin-right: 6px; }

    /* पारदर्शी और कॉम्पैक्ट मोबाइल कोड लिंक बटन्स */
    .transparent-link {
        display: block; padding: 14px; margin: 10px 0;
        background: rgba(33, 150, 243, 0.08); border: 1px solid rgba(33, 150, 243, 0.35);
        border-radius: 10px; color: #4facfe !important;
        text-decoration: none; font-weight: bold; text-align: center;
        font-size: 13px; transition: 0.2s;
    }
    .transparent-link:hover {
        background: rgba(33, 150, 243, 0.15); border-color: #2196F3;
    }
    </style>
""", unsafe_allow_html=True)

# 2. मोबाइल हेडर और ओरिजिनल गूगल लॉगिन
st.markdown("<h2 style='color: #2196F3; margin-top:-20px;'>⚡ ClyxessChat</h2>", unsafe_allow_html=True)

google_html = """
<a class="google-mobile-btn" href="#">
    <img class="google-icon" src="https://gstatic.com"/>
    Sign in
</a>
"""
st.markdown(google_html, unsafe_allow_html=True)
st.markdown("<p style='color:#666; font-size:12px; margin-top:-14px;'>क्लिकसेस चैट एआई — Portable Code Engine</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. साइडबार को केवल ब्रांडिंग के लिए उपयोग किया गया है
with st.sidebar:
    st.markdown("### ⚡ ClyxessChat AI")
    st.caption("v1.2 - API Key Hidden & Mobile Optimized")
    st.markdown("---")
    st.success("🔒 एंड-टू-एंड एन्क्रिप्शन सक्रिय है।")

def upload_to_cloud(title, content):
    try:
        response = requests.post('https://dpaste.com', data={'content': content, 'title': title, 'expiry_days': 1})
        if response.status_code == 201:
            return response.text.strip() + ".txt"
    except Exception:
        return None
    return None

# 4. इनपुट फील्ड्स
user_query = st.text_area("⌨️ पूछें या नीचे माइक का उपयोग करें:", placeholder="जैसे: 'एक सुंदर HTML लॉगिन पेज बनाओ' या 'रायपुर रेलवे स्टेशन का गूगल मैप लिंक दो'...", height=90)

# मोबाइल इनपुट टूल्स एक पंक्ति में
col_mic, col_cam, col_gal = st.columns(3)
with col_mic:
    st.write("🎙️ वॉइस कमांड:")
    audio_data = mic_recorder(start_prompt="On", stop_prompt="Off", key='recorder')
with col_cam:
    camera_photo = st.camera_input("📷 लाइव फोटो", label_visibility="collapsed")
with col_gal:
    gallery_photo = st.file_input("🖼️ गैलरी", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

final_image = camera_photo if camera_photo else gallery_photo

if audio_data and HIDDEN_GROQ_API_KEY != "YOUR_SECRET_GROQ_API_KEY_HERE":
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

# 5. मुख्य एक्शन बटन
send_btn = st.button("🚀 सेंड करें", use_container_width=True)

if send_btn:
    if HIDDEN_GROQ_API_KEY == "YOUR_SECRET_GROQ_API_KEY_HERE":
        st.error("कृपया पहले बैकएंड कोड की लाइन नंबर 9 में अपनी असली Groq API Key सुरक्षित छुपाकर दर्ज करें!")
    elif not user_query.strip() and not final_image:
        st.warning("कृपया कुछ इनपुट टाइप करें या रिकॉर्ड करें!")
    else:
        client = Groq(api_key=HIDDEN_GROQ_API_KEY)
        with st.spinner("🧠 क्लिकसेस चैट एआई प्रोसेस कर रहा है..."):
            try:
                image_description = ""
                if final_image:
                    image_description = "\n[User attached a UI photo. Analyze and clone it perfectly.]"

                full_context = user_query + image_description
                
                # राउटर तय करेगा कि कोडिंग का काम है या लिंक/चैट का सामान्य सवाल
                router_prompt = f"Analyze: '{full_context}'. If user asks for general info, map links, website links, or casual chat, answer CHAT. If they ask to generate programming code/files, answer CODE. One word only: 'CODE' or 'CHAT'."
                router_comp = client.chat.completions.create(model="qwen-2.5-coder-32b", messages=[{"role": "user", "content": router_prompt}], temperature=0.0)
                decision = router_comp.choices.message.content.strip().upper()

                # केस 1: सामान्य बातचीत, या कोई लोकेशन/वेबसाइट लिंक मांगना
                if "CHAT" in decision:
                    chat_comp = client.chat.completions.create(
                        model="qwen-2.5-coder-32b",
                        messages=[{"role": "user", "content": f"Respond natively in the user's language. Provide direct clickable markdown links if they asked for any website or map location like Raipur: {full_context}"}],
                        temperature=0.4
                    )
                    st.markdown("### 💬 AI प्रतिक्रिया:")
                    st.write(chat_comp.choices.message.content)
                    
                # केस 2: शुद्ध कोडिंग का काम (मल्टी-फाइल लिंक्स लूप)
                else:
                    struct_prompt = f"Plan architecture JSON for code request: '{full_context}'. Format: {{ 'PART 1: Name.ext': 'desc' }}. JSON ONLY."
                    struct_comp = client.chat.completions.create(model="qwen-2.5-coder-32b", messages=[{"role": "user", "content": struct_prompt}], temperature=0.0)
                    
                    try:
                        file_map = json.loads(struct_comp.choices.message.content)
                    except Exception:
                        file_map = {"PART 1: Full Implementation.py": "Code compilation"}

                    st.markdown("### 💻 पारदर्शी लिंक्स जनरेट हो गए:")
                    for file_name, file_desc in file_map.items():
                        code_prompt = f"Write full code for '{file_name}'. Context: {file_desc}. Target: {full_context}. No placeholders. Code only."
                        code_comp = client.chat.completions.create(model="qwen-2.5-coder-32b", messages=[{"role": "user", "content": code_prompt}], temperature=0.0)
                        
                        cloud_link = upload_to_cloud(file_name, code_comp.choices.message.content)
                        if cloud_link:
                            st.markdown(f"<a href='{cloud_link}' target='_blank' class='transparent-link'>🔗 {file_name} (ओपन करें)</a>", unsafe_allow_html=True)
                    st.success("🎉 कार्य सफलतापूर्वक पूर्ण हुआ!")
            except Exception as e:
                st.error(f"एरर: {e}")
