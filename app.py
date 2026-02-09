import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION (Must be first) ---
st.set_page_config(
    page_title="Vouch.ai | Enterprise Compliance",
    page_icon="⚖️",
    layout="centered"
)

# --- 2. CSS HACK (Hide Streamlit Branding & Watermarks) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. SIDEBAR & AUTH ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.title("Vouch.ai")
    st.caption("v1.0.4 Enterprise Build")
    
    # Check if key is in Secrets (Cloud) or Manual (Local)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ License Active")
        genai.configure(api_key=api_key)
    else:
        api_key = st.text_input("🔑 API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)

# --- 4. MAIN INTERFACE ---
st.title("⚖️ Vouch.ai")
st.markdown("### Automated Legal & Compliance Audit")
st.markdown("---")

# --- 5. SAFETY SHIELD (Disclaimer) ---
with st.expander("⚠️ LEGAL DISCLAIMER (READ FIRST)", expanded=True):
    st.warning(
        """
        **CONFIDENTIALITY NOTICE:**
        1. This is an automated AI assessment tool for **preliminary screening**.
        2. It is **NOT** a substitute for professional legal counsel. 
        3. **DO NOT** upload sensitive or unreleased client assets to this server.
        4. Vouch.ai assumes no liability for missed violations.
        """
    )
    # The "Lock" - User must check this to proceed
    legal_agreement = st.checkbox("I acknowledge this is an automated draft analysis.")

# --- 6. FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Media Asset (MP4, MOV)", type=['mp4', 'mov', 'avi'])

if uploaded_file and api_key:
    # Display the video player
    st.video(uploaded_file)
    
    # Button is disabled until agreement is checked
    if st.button("🚀 Run Compliance Audit", disabled=not legal_agreement):
        
        with st.spinner("🕵️‍♂️ Analyzing visual & audio vectors..."):
            try:
                # A. Save file temporarily
                temp_filename = "temp_video.mp4"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.read())
                
                # B. Upload to "The Vault" (Gemini)
                video_file = genai.upload_file(path=temp_filename)
                
                # C. Wait for processing
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Error: Video processing failed. Please try a different format.")
                else:
                    # D. The "Lawyer" Prompt (Strict)
                    prompt = """
                    Act as a Senior Compliance Officer for the Indian Censor Board (CBFC). 
                    Analyze this video for legal risks under Indian Law.
                    
                    Focus on these specific statutes:
                    1. IPC 295A & BNS 299 (Religious Sentiments).
                    2. IPC 153A & BNS 196 (Promoting Enmity).
                    3. The Cinematograph Act (Certification Rules).
                    4. COTPA 2003 (Tobacco Disclaimers).
                    5. Criminal Law Amendment Act 1961 (Map accuracy).

                    Output a structured audit report:
                    - **Timestamp**: [MM:SS]
                    - **Risk Category**: [e.g., Hate Speech, Visual Compliance, Defamation]
                    - **Severity**: [High/Medium/Low]
                    - **Observation**: [Description of the flag]
                    - **Legal Reference**: [Cite the Act/Section if applicable]
                    - **Remediation**: [How to fix it]
                    
                    If the video is safe, explicitly state "No Compliance Violations Detected."
                    """
                    
                    # E. Select Model (Backend only - user doesn't see this)
                    # We use 1.5 Flash for speed and cost
                    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

                    # F. Generate
                    response = model.generate_content([prompt, video_file])
                    
                    # G. Display Report
                    st.success("✅ Audit Complete")
                    st.markdown("### 📋 Executive Summary")
                    st.write(response.text)
                    
                    # H. The "Professional" Footer
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    audit_id = int(time.time())
                    st.markdown("---")
                    st.markdown(
                        f"""
                        <div style="text-align: center; color: #888; font-size: 12px; font-family: sans-serif;">
                            <b>CONFIDENTIAL REPORT</b><br>
                            Generated by Vouch.ai Compliance Engine v1.0<br>
                            Timestamp: {timestamp} IST • Audit ID: #V{audit_id}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Cleanup: Delete the temp file to save space
                    try:
                        os.remove("temp_video.mp4") 
                    except:
                        pass

            except Exception as e:
                st.error(f"System Error: {str(e)}")

elif not api_key:
    st.info("👈 Initialize via Sidebar System Settings")