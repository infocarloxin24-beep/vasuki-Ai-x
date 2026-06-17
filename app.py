import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Vasuki-X", page_icon="🔥")
st.title("Vasuki-X Live Hai Bhai 🔥")
st.write("Elon Musk style bot ready hai")

ist = pytz.timezone('Asia/Kolkata')
time_now = datetime.now(ist).strftime("%d-%m-%Y %I:%M %p")
st.write(f"*Time:* {time_now}")
st.success("Deploy successful! App chal raha hai.")

user_input = st.text_input("Kuch pucho Elon se:")
if user_input:
    st.write(f"Elon bolta hai: '{user_input}' - ye to Mars pe le jayenge 🚀")
