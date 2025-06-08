import streamlit as st
from credentials import CREDENTIALS

def login():
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == CREDENTIALS["username"] and password == CREDENTIALS["password"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials ❌")
