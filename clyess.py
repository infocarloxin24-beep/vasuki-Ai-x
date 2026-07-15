import streamlit as st
import json
from groq import Groq
import time

st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

HIDDEN_GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

# CHATGPT JAISE CSS
st.markdown("""
<style>
.stApp {background-color: #212121;}
.main.block-container {max-width: 800px; padding-top: 2rem;}
.stChatInputContainer {background: transparent;}
div[data-testid="stChatInput"] {background:#2f2f2f; border-radius:24px; border:1px solid #444;}
div[data-testid="stChatInput"] input {background:transparent; color:white; border:none;}
/* Mic button ko input ke andar chipka diya */
div[data-testid="stChatInput"] button {position: absolute; right: 45px; bottom: 8px; background:transparent; border:none; font-size:20px;}
/* Send button */
div[data-testid="stChatInput"] button[kind="secondary"] {right: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("💬 ClyxessChat")
st.caption("Next-Gen Portable Multi-File Code Engine")

# CHAT HISTORY CENTER ME
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"], unsafe_allow_html=True)

# INPUT
prompt = st.chat_input("Message ClyxessChat AI...")

# MIC BUTTON - CHAT INPUT KE ANDAR
if st.button("🎙️", help="Voice Input", key="mic_btn"):
    st.toast("Voice ke liye streamlit-mic-recorder install karna padega")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    client = Groq(api_key=HIDDEN_GROQ_API_KEY)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Generating..."):

            # 1. PEHLE CHECK KARO CODE CHAHIYE YA CHAT
            router = client.chat.completions.create(
                model=ACTIVE_GROQ_MODEL,
                messages=[{"role":"user","content":f"User asked: {prompt}. If they want code/website/app reply CODE. Else CHAT. Reply ONLY one word."}],
                max_tokens=5, temperature=0
            )
            decision = router.choices[0].message.content.strip().upper()

            if "CHAT" in decision:
                res = client.chat.completions.create(
                    model=ACTIVE_GROQ_MODEL, 
                    messages=[{"role":"user","content":prompt}], 
                    max_tokens=2000
                )
                ans = res.choices[0].message.content
                st.write(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})

            else:
                # 2. CODE MODO - SAKHT PROMPT
                code_prompt = f"""
                You are a senior developer. Generate COMPLETE working code for: {prompt}
                CRITICAL RULES:
                1. Return ONLY valid JSON. No text, no ``` before or after.
                2. Format: {{"index.html": "full html code here", "style.css": "full css code here"}}
                3. Code must be complete and runnable.
                """
                res = client.chat.completions.create(
                    model=ACTIVE_GROQ_MODEL,
                    messages=[{"role":"user","content":code_prompt}],
                    max_tokens=8000,
                    temperature=0.0
                )
                raw = res.choices[0].message.content.strip()
                raw = raw.replace("```json","").replace("```","").strip()

                try:
                    files = json.loads(raw)
                    success_msg = ""
                    for name, code in files.items():
                        st.download_button(f"⬇️ Download {name}", code, name, key=f"dl_{name}_{time.time()}")
                        with st.expander(f"📄 View {name}"):
                            st.code(code, language=name.split(".")[-1])
                        success_msg += f"<b>{name}</b> ✅<br>"
                    
                    st.session_state.messages.append({"role": "assistant", "content": f"Code Generated:<br>{success_msg}"})

                except json.JSONDecodeError as e:
                    error_msg = f"<b>Error in code generation:</b><br>AI ne sahi JSON nahi diya<br><pre>{raw}</pre>"
                    st.error("Error in code generation")
                    st.code(raw, language="json")
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
