import streamlit as st
import random

def show_login_gate():
    # CSS - Photo wala design
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);}
    [data-testid="stForm"] {border: 1px solid #334155; border-radius: 16px; padding: 30px; background: #1e293b; max-width: 500px; margin: auto;}
    .stTextInput>div>div>input {background-color: #334155; color: #e2e8f0; border-radius: 10px; border: 1px solid #475569; padding: 12px;}
    .stButton>button {width: 100%; background: #475569; color: white; border-radius: 10px; border: none; padding: 12px; font-weight: 600;}
    .stButton>button:hover {background: #64748b;}
    h3 {color: #f8fafc !important; font-weight: 700;}
    label {color: #cbd5e1 !important; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

    # Puzzle generate karna
    if "puzzle_num1" not in st.session_state:
        st.session_state.puzzle_num1 = random.randint(1, 9)
        st.session_state.puzzle_num2 = random.randint(1, 9)
    
    correct_answer = st.session_state.puzzle_num1 + st.session_state.puzzle_num2

    with st.form("login_form"):
        st.radio("Mode:", ["Login", "Sign Up"], horizontal=True)
        st.markdown("### 📧 Login with Email")
        
        email = st.text_input("Email:", placeholder="admin@humbotix.ai")
        password = st.text_input("Password:", type="password", placeholder="Humbo@2026")
        
        # PUZZLE SECTION
        st.markdown(f"### 🧩 Puzzle: {st.session_state.puzzle_num1} + {st.session_state.puzzle_num2} = ?")
        puzzle_ans = st.text_input("Puzzle Answer:", placeholder="Answer likho")
        
        # Login + Refresh button
        col1, col2 = st.columns([5,1])
        with col1:
            submitted = st.form_submit_button("Login", use_container_width=True)
        with col2:
            refresh = st.form_submit_button("🔄", help="New Puzzle")

    st.markdown("---")
    st.markdown("### 🚀 Social Login")
    col1, col2 = st.columns(2)
    col1.button("G Google", use_container_width=True, disabled=True)
    col2.button("💻 GitHub", use_container_width=True, disabled=True)

    # Refresh dabane pe naya puzzle
    if refresh:
        st.session_state.puzzle_num1 = random.randint(1, 9)
        st.session_state.puzzle_num2 = random.randint(1, 9)
        st.rerun()

    # Login logic
    if submitted:
        if not puzzle_ans.isdigit():
            st.error("Pehle Puzzle solve karo")
        elif int(puzzle_ans) != correct_answer:
            st.error("Puzzle Galat hai. 🔄 se naya try karo")
        elif email == "admin@humbotix.ai" and password == "Humbo@2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Galat Email ya Password")
