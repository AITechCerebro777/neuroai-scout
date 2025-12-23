import streamlit as st  # MUST BE LINE 1
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os

# --- 1. SECURITY GATE (Mobile-Friendly Login) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    st.markdown("<h2 style='text-align: center; color: #F59E0B;'>ScoutMD Secure Access</h2>", unsafe_allow_html=True)
    st.text_input("Enter Password", type="password", 
                 on_change=lambda: st.session_state.update(password_correct=st.session_state.password == st.secrets["APP_PASSWORD"]), 
                 key="password")
    return False

if not check_password():
    st.stop()

# --- 2. PREMIUM THEME & MOBILE RESPONSIVENESS ---
st.set_page_config(page_title="ScoutMD | NeuroAI", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    /* Mobile-first background */
    .stApp { background-color: #0F172A; font-family: 'Inter', sans-serif; color: #E2E8F0; }
    
    /* Emerald + Gold Card Design */
    .expert-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-left: 6px solid #10B981; /* Emerald border */
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    
    .expert-name { color: #F59E0B; font-size: 22px; font-weight: 700; margin-bottom: 2px; } /* Gold name */
    .expert-title { color: #94A3B8; font-size: 14px; margin-bottom: 12px; font-style: italic; }
    
    /* Button that works well on touchscreens */
    .link-button {
        background-color: #10B981;
        color: white !important;
        padding: 12px 20px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        text-align: center;
        margin-top: 15px;
        font-weight: 700;
    }
    
    .email-preview {
        background-color: #0F172A;
        border: 1px dashed #475569;
        padding: 15px;
        margin-top: 15px;
        border-radius: 8px;
        font-size: 13px;
        color: #CBD5E1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (Collapses on Mobile) ---
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B; text-align: center;'>ScoutMD 🧠</h1>", unsafe_allow_html=True)
    st.markdown("---")
    if 'raw_data' in st.session_state:
        st.download_button("📥 Save Shortlist", 
                          data=st.session_state.raw_data, 
                          file_name=f"NeuroScout_{datetime.now().strftime('%m%d')}.txt",
                          use_container_width=True)
    st.info("The Emerald + Gold Standard for Neurology Speaker Search.")

# --- 4. MAIN INTERFACE ---
st.title("NeuroAI Speaker Platform")
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Search input at the bottom (Standard for mobile apps)
query = st.chat_input("Ex: Find founders in Brain-Computer Interfaces...")

if query:
    with st.spinner("Searching medical databases..."):
        prompt = f"""
        Find 3 real-world neurology experts for: {query}.
        Use these exact labels for each expert:
        [NAME]
        [TITLE]
        [LINK]
        [BIO]
        [EMAIL]
        """
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        st.session_state.raw_data = response.text

    # Parse entries into cards
    expert_entries = response.text.split("[NAME]")[1:]
    
    for entry in expert_entries:
        try:
            name = entry.split("[TITLE]")[0].strip()
            title = entry.split("[TITLE]")[1].split("[LINK]")[0].strip()
            link = entry.split("[LINK]")[1].split("[BIO]")[0].strip()
            bio = entry.split("[BIO]")[1].split("[EMAIL]")[0].strip()
            email = entry.split("[EMAIL]")[1].strip()

            st.markdown(f"""
            <div class="expert-card">
                <div class="expert-name">{name}</div>
                <div class="expert-title">{title}</div>
                <p style="font-size: 14px;">{bio}</p>
                <a href="{link}" target="_blank" class="link-button">View Profile / Research</a>
                <div class="email-preview">
                    <strong style="color: #F59E0B;">✉️ Outreach Draft:</strong><br>{email}
                </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            continue
else:
    st.info("Enter a topic below to generate your expert list.")
