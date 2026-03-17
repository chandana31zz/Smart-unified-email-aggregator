import streamlit as st

def login_page():
    st.markdown("## 🔐 Login")
    st.caption("Smart Unified Email Aggregator")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username == "nie" and password == "nie123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")
