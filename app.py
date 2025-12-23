import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os

# --- 1. CONFIGURATION & DARK THEME ---
st.set_page_config(page_title="NeuroAI Scout", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .stApp { background-color: #0F172A; font-family: 'Inter', sans-serif; color: #E2E8F0; }
    [data-testid="stSidebar"] { background-color: #1E293B; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #F8FAFC !important; }
    
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: #1E293B !important; padding: 24px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); border: 1px solid #334155; margin-bottom: 20px;
    }

    h1, h2, h3, h4, h5, h6, strong { color: #FFFFFF !important; font-weight: 700; }
    p, li, span { color: #CBD5E1; line-height: 1.6; }

    .badge-researcher { background-color: rgba(14, 165, 233, 0.2); color: #38BDF8; padding: 6px 16px; border-radius: 20px; border: 1px solid #0EA5E9; display: inline-block; margin-bottom: 12px; font-weight: 700; font-size: 0.8rem; }
    .badge-entrepreneur { background-color: rgba(34, 197, 94, 0.2); color: #4ADE80; padding: 6px 16px; border-radius: 20px; border: 1px solid #22C55E; display: inline-block; margin-bottom: 12px; font-weight: 700; font-size: 0.8rem; }
    .badge-tech { background-color: rgba(168, 85, 247, 0.2); color: #C084FC; padding: 6px 16px; border-radius: 20px; border: 1px solid #A855F7; display: inline-block; margin-bottom: 12px; font-weight: 700; font-size: 0.8rem; }

    a { color: #38BDF8 !important; text-decoration: none; font-weight: 600; }
    a:hover { color: #60A5FA !important; text-decoration: underline; }

    .stButton>button { background: linear-gradient(135deg, #2563EB 0%, #0EA5E9 100%); color: white; border-radius: 8px; border: none; padding: 0.6rem 1.2rem; font-weight: 600; width: 100%; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
    </style>
""", unsafe_allow_html=True)

# --- 2. HYBRID AUTHENTICATION (Works in Cloud Shell & Public Web) ---
@st.cache_resource
def get_client():
    # 1. Try to find a Public API Key (For Streamlit Cloud)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return genai.Client(api_key=st.secrets["GEMINI_API_KEY"], http_options={'api_version':'v1alpha'})
    except:
        pass
    
    # 2. Fallback to Internal Google Cloud Auth (For your current Preview)
    return genai.Client(vertexai=True, project="neuroaispeakerplatform", location="us-central1")

client = get_client()
MODEL_ID = "gemini-2.0-flash-exp" # Using Flash for speed

if "messages" not in st.session_state: st.session_state.messages = []
if "database" not in st.session_state: st.session_state.database = [] 

# --- 3. DATA LOGIC ---
def parse_and_save(text_content, search_query):
    try:
        lines = [l for l in text_content.split('\n') if l.strip()]
        name = "Unknown Expert"
        for line in lines:
            if "###" in line:
                name = line.replace("###", "").strip()
                break
        
        upper_text = text_content.upper()
        category = "Researcher"
        if "ENTREPRENEUR" in upper_text or "FOUNDER" in upper_text: category = "Entrepreneur"
        elif "TECH_INNOVATOR" in upper_text: category = "Tech Innovator"

        def extract(pattern, text, default="N/A"):
            match = re.search(pattern, text)
            return match.group(1).strip() if match else default

        affiliation = extract(r'\*\*🏥 Affiliation:\*\*\s*(.*)', text_content)
        innovation = extract(r'\*\*🧬 Innovation \(Emerald\):\*\*\s*>\s*(.*)', text_content)
        prestige = extract(r'\*\*🏆 Prestige \(Gold\):\*\*\s*>\s*(.*)', text_content)
        proof_link = extract(r'🔗 \*\*Proof:\*\*\s*(http[^\s]*)', text_content)
        linkedin_link = extract(r'💼 \*\*LinkedIn:\*\*\s*(http[^\s]*)', text_content)

        if not any(d['Name'] == name for d in st.session_state.database):
            st.session_state.database.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Search Query": search_query,
                "Name": name,
                "Type": category,
                "Affiliation": affiliation,
                "Innovation": innovation,
                "Prestige": prestige,
                "Proof Link": proof_link,
                "LinkedIn": linkedin_link,
                "Raw Data": text_content
            })
    except: pass

def create_classified_card(text_content, search_query):
    parse_and_save(text_content, search_query)
    border_color, badge_html, icon_url = "#475569", "", "https://cdn-icons-png.flaticon.com/512/387/387561.png"
    upper_text = text_content.upper()
    
    if "ENTREPRENEUR" in upper_text or "FOUNDER" in upper_text: 
        border_color, badge_html, icon_url = "#22c55e", '<span class="badge-entrepreneur">🚀 FOUNDER / CEO</span>', "https://cdn-icons-png.flaticon.com/512/4127/4127281.png"
    elif "TECH_INNOVATOR" in upper_text or "DEVICE CREATOR" in upper_text:
        border_color, badge_html, icon_url = "#a855f7", '<span class="badge-tech">🛠️ DEVICE CREATOR / PhD</span>', "https://cdn-icons-png.flaticon.com/512/2083/2083213.png"
    elif "RESEARCHER" in upper_text:
        border_color, badge_html, icon_url = "#0ea5e9", '<span class="badge-researcher">🎓 CLINICAL RESEARCHER</span>', "https://cdn-icons-png.flaticon.com/512/387/387561.png"

    clean_text = re.sub(r'(?i)(🚀|🎓|🛠️)?\s*TYPE:.*', '', text_content)

    with st.container():
        st.markdown(f'<div style="border-left: 4px solid {border_color}; background-color: #1E293B; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px;">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 6])
        with col1: st.image(icon_url, width=70)
        with col2:
            if badge_html: st.markdown(badge_html, unsafe_allow_html=True)
            st.markdown(clean_text)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=60) 
    st.title("ScoutMD")
    st.caption("v11.0 | Deploy Ready")
    st.markdown("---")
    
    df = pd.DataFrame(st.session_state.database)
    if not df.empty:
        st.write(f"**📝 Database ({len(df)})**")
        st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "neuroai_scout.csv", "text/csv")
        st.markdown("---")
        
        st.subheader("✉️ Invitation Writer")
        candidate_list = df['Name'].tolist()
        if candidate_list:
            selected_candidate = st.selectbox("Select Candidate:", candidate_list)
            if st.button("Generate Invite Draft"):
                candidate_data = df[df['Name'] == selected_candidate].iloc[0]
                email_prompt = f"Write a VIP invite to {candidate_data['Name']}. Mention innovation: '{candidate_data['Innovation']}' and prestige: '{candidate_data['Prestige']}'. Tone: Executive, Professional."
                with st.spinner("Writing..."):
                    try:
                        resp = client.models.generate_content(model=MODEL_ID, contents=email_prompt)
                        st.text_area("Draft:", resp.text, height=300)
                    except Exception as e: st.error(f"Error: {e}")
    
    st.markdown("---")
    if st.button("Clear Session"):
        st.session_state.messages = []
        st.session_state.database = []
        st.rerun()

# --- 5. MAIN PAGE ---
col_logo, col_header = st.columns([1, 10])
with col_logo: st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg", width=50)
with col_header:
    st.title("NeuroAI Speaker Platform")
    st.markdown("<h4 style='color: #94A3B8; margin-top: -15px;'>The Emerald + Gold Standard Search Engine</h4>", unsafe_allow_html=True)
st.markdown("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

if prompt := st.chat_input("Ex: Find founders building Brain-Computer Interfaces..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        hist = ""
        for msg in st.session_state.messages[-4:]: hist += f"{msg['role'].upper()}: {msg['content']}\n"
        full_prompt = f"""
        HISTORY: {hist}\nREQUEST: {prompt}
        MANDATE: Headhunter for AI & Healthcare Congress.
        1. CLASSIFY: "RESEARCHER" (Papers), "ENTREPRENEUR" (Startups), "TECH_INNOVATOR" (Devices).
        2. FORMAT: Separate with "|||". Include "TYPE: [CLASS]".
        VISUAL TEMPLATE:
        ### [Name]
        TYPE: [INSERT CLASS HERE]
        **🏥 Affiliation:** [Company/University]
        ---
        **🧬 Innovation (Emerald):** > [Work]
        **🏆 Prestige (Gold):** > [Awards]
        **🌐 Connect & Verify:**
        * 🔗 **Proof:** https://www.google.com/search?q=[Name]+[Work]+Research
        * 🏫 **Profile:** https://www.google.com/search?q=[Name]+[Affiliation]+Profile
        * 💼 **LinkedIn:** https://www.google.com/search?q=[Name]+LinkedIn
        """
        try:
            resp = client.models.generate_content(model=MODEL_ID, contents=full_prompt, config=types.GenerateContentConfig(temperature=0.4, tools=[types.Tool(google_search=types.GoogleSearch())]))
            if "|||" in resp.text:
                for cand in resp.text.split("|||"): 
                    if len(cand.strip()) > 10: create_classified_card(cand, prompt)
            elif "###" in resp.text: create_classified_card(resp.text, prompt)
            else: st.markdown(resp.text)
            st.session_state.messages.append({"role": "assistant", "content": resp.text})
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")
