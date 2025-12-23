import streamlit as st  # MUST BE LINE 1
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os
from io import BytesIO

# --- 1. SECURITY GATE ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    st.text_input("Enter Password to Access ScoutMD", type="password", 
                 on_change=lambda: st.session_state.update(password_correct=st.session_state.password == st.secrets["APP_PASSWORD"]), 
                 key="password")
    return False

if not check_password():
    st.stop()

# --- 2. CONFIGURATION & DARK THEME ---
st.set_page_config(page_title="NeuroAI Scout", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #E2E8F0; }
    .expert-card { background-color: #1E293B; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 15px; }
    .email-box { background-color: #334155; padding: 15px; border-radius: 5px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR & TOOLS ---
with st.sidebar:
    st.title("ScoutMD 🧠")
    st.markdown("---")
    if 'last_results' in st.session_state:
        st.subheader("Export Tools")
        # Download PDF Simulation (Using Text File for compatibility)
        st.download_button(label="📥 Download Results (TXT)", 
                          data=st.session_state.last_results, 
                          file_name=f"Neuro_Scout_{datetime.now().strftime('%Y%m%d')}.txt")

# --- 4. MAIN ENGINE ---
st.title("NeuroAI Speaker Platform")
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

query = st.chat_input("Ex: Find founders building Brain-Computer Interfaces...")

if query:
    with st.status("Gathering Expert Data & Generating Outreach...", expanded=True):
        # AI prompt designed to force links and email drafts
        prompt = f"""
        Find neurology experts for: {query}.
        For each expert provide:
        1. Full Name and Title
        2. Direct Link to Research or Profile (simulated URL if necessary)
        3. A professional 3-sentence email invitation draft to speak at a conference.
        Format as clear sections.
        """
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        st.session_state.last_results = response.text

    st.markdown("### ⚡ Expert Shortlist & Outreach Drafts")
    st.markdown(response.text)
    
    # Email Writer Tool
    with st.expander("✉️ Open Email Writer Tool"):
        st.write("Copy the drafted emails from the results above into your mail client.")
        st.info("Tip: You can now click the 'Download' button in the sidebar to save this list.")

else:
    st.info("Ready for your next search. Type a query at the bottom.")
