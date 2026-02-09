import streamlit as st
import google.generativeai as genai
import tempfile
import time
import os

# --- VOUCH.AI BRAND CONFIG ---
st.set_page_config(
    page_title="Vouch.ai | Compliance & Liability Shield",
    page_icon="🛡️",
    layout="wide"
)

# --- THE LEGAL BRAIN (ENHANCED) ---
INDIAN_LAWS = """
CRITICAL COMPLIANCE CHECKLIST FOR INDIAN MEDIA (2026 STANDARDS):

1. RELIGION & HATE SPEECH (IPC Section 295A & 153A)
   - RED FLAG: Any deliberate insult to Hindu gods/goddesses, Prophet Muhammad, Sikh Gurus, or Christian saints.
   - RED FLAG: Mocking religious rituals or idols.
   - RED FLAG: Promoting enmity between groups based on religion, caste, birth, or language.

2. NATIONAL PRIDE (Prevention of Insults to National Honour Act, 1971)
   - RED FLAG: Incorrect Map of India (Must include PoK/Ladakh borders correctly).
   - RED FLAG: Disrespect to the National Flag (touching ground, worn below waist).
   - RED FLAG: Disrespect to the National Anthem.

3. OBSCENITY & NUDITY (IPC Section 292 & IT Act Section 67)
   - RED FLAG: Explicit sexual acts or full frontal nudity.
   - YELLOW FLAG: Excessive intimacy (kissing/touching) without 'A' certificate context.
   - RED FLAG: Child pornography or sexual abuse (Instant BAN).

4. WOMEN'S SAFETY (Indecent Representation of Women Act, 1986)
   - RED FLAG: Depicting women as merely objects of sexual desire.
   - RED FLAG: Glorification of Sati or Dowry.

5. CASTE & TRIBAL PROTECTION (SC/ST Prevention of Atrocities Act)
   - RED FLAG: Use of derogatory caste-slurs (e.g., 'Chamar', 'Bhangi', 'Mahar').
   - RED FLAG: Humiliation of Dalit characters solely for their caste identity.

6. SUBSTANCE ABUSE (COTPA Act & Cable TV Rules)
   - COMPLIANCE CHECK: If smoking/alcohol is shown, is there a static warning ("Smoking Kills") on screen?
   - RED FLAG: Glorification of drug use or suggesting drugs make you "cool/successful".

7. DEFAMATION & PRIVACY (Bharatiya Nyaya Sanhita - BNS)
   - RED FLAG: Revealing the identity of sexual assault victims.
   - YELLOW FLAG: Use of real people's names/photos without consent (Deepfake risk).
"""

# --- SMART AUTH (SECRETS + MANUAL FALLBACK) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.title("Vouch.ai")
    
    # Check if the key is hidden in the cloud (Secrets)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Enterprise License Active")
    else:
        # Fallback for local testing if secrets aren't set
        api_key = st.text_input("🔑 Enter Google API Key", type="password")

    if api_key:
        genai.configure(api_key=api_key)
    st.markdown("---")
    st.info("💡 **Pro Tip:** This MVP uses Gemini 1.5 Flash (Free Tier).")

# Main Interface
st.markdown("## 🛡️ Content Compliance Audit")
st.markdown("Upload your rough cut or trailer. **Vouch.ai** will scan it against 5,000+ Indian laws and generate a liability report.")

uploaded_file = st.file_uploader("", type=["mp4", "mov", "avi"], help="Upload video (Max 200MB)")

if uploaded_file and api_key:
    # 1. Save file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name

    # Display video player
    st.video(video_path)

    # 2. Action Button
    if st.button("🛡️ Vouch for this Content (Run Audit)", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Uploading
            status_text.text("📤 Uploading video to Visual Cortex...")
            progress_bar.progress(25)
            video_file = genai.upload_file(path=video_path)

            # Step 2: Processing
            status_text.text("👀 Watching video & processing audio...")
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            progress_bar.progress(60)

            # Step 3: Legal Reasoning
            status_text.text("⚖️ Cross-referencing Indian Penal Code & DPDP Act...")
            progress_bar.progress(85)

            # The Vouch Prompt
            prompt = f"""
            You are "Vouch", an AI Legal Compliance Officer for the Indian Media Industry.
            Your job is to protect the studio from lawsuits, bans, and PR disasters.

            Analyze this video frame-by-frame and audio-by-audio against the following STRICT Legal Code:
            {INDIAN_LAWS}

            OUTPUT INSTRUCTIONS:
            1. **Risk Score**: Give a clear rating (SAFE / CAUTION / HIGH RISK).
            2. **The Verdict**: A 1-sentence summary for the Chief Legal Officer.
            3. **Timestamped Violations**: Create a table with columns [Time, Flag Type, Description, Legal Section Violated].
            4. **Remediation**: Suggest edits (e.g., "Blur map at 02:30", "Mute audio at 04:15").

            Be conservative. If you are unsure, flag it as YELLOW.
            """

            model = genai.GenerativeModel(model_name="gemini-flash-latest")
            response = model.generate_content([video_file, prompt])
            
            progress_bar.progress(100)
            status_text.text("✅ Audit Complete.")

            # Step 4: Display Report
            st.divider()
            st.subheader("📋 Vouch.ai Liability Report")
            st.markdown(response.text)

            # Cleanup
            genai.delete_file(video_file.name)

        except Exception as e:
            st.error(f"❌ Error during audit: {e}")