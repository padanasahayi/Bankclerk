import json
import streamlit as st
import google.generativeai as genai

# Page Setup
st.set_page_config(
    page_title="SBI & IBPS AI Coach - Aiswarya",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🚀 FASTER LOADING: AI Model Caching Function
@st.cache_resource
def get_gemini_model(api_key: str, subject: str, exam: str):
    genai.configure(api_key=api_key)
    system_instruction = f"""
    You are Aiswarya's personal AI Super-Coach for SBI & IBPS Clerk Exams.
    Student Name: Aiswarya
    Goal: Bank Clerk within 6 months.
    Target Exam: {exam}
    Active Subject: {subject}
    
    Rules:
    1. Start with a warm 1-line psychological boost addressing Aiswarya.
    2. Explain concepts using real-life daily examples (shopping, recipes, UPI, family seating).
    3. Keep answers concise, structured, mobile-friendly, and in clear Malayalam/Manglish.
    """
    return genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)

# CSS for Fast & Lightweight Mobile UI
st.markdown("""
<style>
    .block-container { padding: 0.8rem 0.5rem !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; overflow-x: auto; }
    .stTabs [data-baseweb="tab"] { font-size: 12px !important; font-weight: bold; padding: 6px 10px !important; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 SBI & IBPS AI Coach")

# Retrieve API Key from Secrets
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    exam_target = st.radio("Target Exam Focus:", ["SBI Clerk", "IBPS Clerk", "Combined"])

if not api_key:
    st.warning("⚠️ തുടരുവാൻ Gemini API Key നൽകുക.")
    st.stop()

# Subject Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔥 Current Affairs", 
    "📊 Quant", 
    "🧩 Reasoning", 
    "✍️ English", 
    "💻 Computer"
])

subject_map = {
    0: "Current Affairs & Banking Awareness",
    1: "Quantitative Aptitude & Speed Math",
    2: "Reasoning Ability & Puzzles",
    3: "General English & Grammar",
    4: "Computer Knowledge & Digital Banking"
}

with tab1: active_subject = subject_map[0]
with tab2: active_subject = subject_map[1]
with tab3: active_subject = subject_map[2]
with tab4: active_subject = subject_map[3]
with tab5: active_subject = subject_map[4]

# Load Cached Fast Model Instance
model = get_gemini_model(api_key, active_subject, exam_target)

# Initialize Session Chat
if "messages" not in st.session_state or st.session_state.get("current_subject") != active_subject:
    st.session_state.current_subject = active_subject
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"പ്രിയപ്പെട്ട ഐശ്വര്യ, നമസ്കാരം! **{active_subject}** പാഠഭാഗങ്ങളിലേക്ക് സ്വാഗതം. പഠനം ആരംഭിക്കാൻ 'Start' എന്ന് ടൈപ്പ് ചെയ്യൂ!"
    }]

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യുക..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("ഉത്തരം തയാറാക്കുന്നു..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
