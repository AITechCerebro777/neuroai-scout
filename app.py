import streamlit as st  # MUST BE LINE 1
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os

# --- 1. SECURITY GATE ---
# This function creates the lock. It must run before any other visual commands.
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # This displays the login box
    st.text_input(
        "Enter Password to Access ScoutMD", 
        type="password", 
        on_change=lambda: st.session_state.update(password_correct=st.session_state.password == st.secrets["APP_PASSWORD"]), 
        key="password"
    )
    return False

# This line tells the app to STOP here if the password isn't correct
if not check_password():
    st.stop()

# --- 2. CONFIGURATION & DARK THEME ---
# This part ONLY runs if the password check above is successful.
st.set_page_config(page_title="NeuroAI Scout", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #0F172A;
        font-family: 'Inter', sans-serif;
        color: #E2E8F0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }

    .stTextInput > div > div > input {
        background-color: #1E293B;
        color: white;
        border: 1px solid #475569;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brain--v1.png", width=80)
    st.title("ScoutMD")
    st.markdown("---")
    st.info("The Emerald + Gold Standard for finding Neurology Experts.")

# --- 4. MAIN INTERFACE ---
st.title("NeuroAI Speaker Platform")
st.write("Secure Search Active 🔒")

# Initialize Gemini Client using the Secret Key
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Search input
query = st.chat_input("Ex: Find founders building Brain-Computer Interfaces...")

if query:
    with st.status("Searching Neurology Databases...", expanded=True) as status:
        st.write("Analyzing expert profiles...")
        
        # Call the AI model
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Provide a list of top neurology experts related to: {query}. Include their names, specialties, and notable achievements."
        )
        
        status.update(label="Search Complete!", state="complete", expanded=False)
    
    # Display the results
    st.markdown("### Search Results")
    st.write(response.text)

else:
    st.info("Enter a query below to begin your expert search.")
