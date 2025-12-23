import streamlit as st  # MUST BE AT THE VERY TOP
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os

# --- SECURITY GATE ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.text_input(
        "Enter Password to Access ScoutMD", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False

if not check_password():
    st.stop()  # Stop the app here if password is not correct

# --- 1. CONFIGURATION & DARK THEME ---
st.set_page_config(page_title="NeuroAI Scout", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp { background-color: #0F172A; font-family: 'Inter', sans-serif; color: #E2E8F0; }
    [data-testid="stSidebar"] { background-color: #1E293B; border-right: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# ... (rest of your app code follows below)
