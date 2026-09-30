import json
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# 1. Page & Mobile Responsive Setup
st.set_page_config(
    page_title="SBI & IBPS Clerk AI Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for UX & Badges
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        overflow-x: auto;
        white-space: nowrap;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 12px !important;
        font-weight: 700;
        padding: 8px 10px !important;
        border-radius: 8px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066cc !important;
        color: white !important;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .user-badge {
        background-color: #1e88e5;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
        margin-right: 8px;
    }
    .day-badge {
        background-color: #2e7d32;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 13px;
        font-weight: bold;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# API Key Connection
api_key = st.secrets.get("GEMINI_API_KEY", None)

# --- SIDEBAR: USER PROFILE & NAVIGATION ---
with st.sidebar:
    st.header("👤 Student Profile & Settings")
    
    # 1. User Identification (Default: Aiswarya)
    user_name = st.text_input(
        "നിങ്ങളുടെ പേര് നൽകുക (Student Name):",
        value="Aiswarya",
        help="വേറൊരു ഡിവൈസിൽ തുറക്കുമ്പോൾ ഇവിടെ പുതിയ പേര് നൽകിയാൽ ക്ലാസ്സ് 1 മുതൽ ആരംഭിക്കും."
    ).strip()
    
    if not user_name:
        user_name = "Aiswarya"

    st.markdown("---")
    
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    else:
        st.success("⚡ Gemini 2.5 Flash Connected")
    
    st.markdown("---")
    
    # 2. Day Selector System (1 - 180 Days)
    st.subheader("📅 Class Navigation")
    
    # Reset or Track Current Day per user session
    day_session_key = f"current_day_{user_name}"
    if day_session_key not in st.session_state:
        st.session_state[day_session_key] = 1

    selected_day = st.number_input(
        f"{user_name}'s Class Day (1 - 180):",
        min_value=1,
        max_value=180,
        value=st.session_state[day_session_key],
        step=1,
        key=f"day_input_{user_name}"
    )
    st.session_state[day_session_key] = selected_day

    # Quick Day Navigation Buttons
    col_start, col_next = st.columns(2)
    with col_start:
        if st.button("🔄 Day 1-ലേക്ക് പോകുക"):
            st.session_state[day_session_key] = 1
            st.rerun()
    with col_next:
        if st.button("▶️ അടുത്ത ദിവസം"):
            if st.session_state[day_session_key] < 180:
                st.session_state[day_session_key] += 1
                st.rerun()

    st.markdown("---")
    exam_target = st.radio("Target Exam Focus:", ["SBI Clerk", "IBPS Clerk", "Combined SBI + IBPS"])

if not api_key:
    st.warning("⚠️ തുടരുവാൻ Sidebar തുറന്ന് Gemini API Key നൽകുക.")
    st.stop()

# --- DYNAMIC GEMINI MODEL CACHING ---
@st.cache_resource
def get_gemini_model(api_key: str, subject: str, exam: str, day: int, student_name: str):
    genai.configure(api_key=api_key)
    
    system_instruction = f"""
    You are {student_name}'s personal AI Super-Coach for SBI Clerk and IBPS Clerk Examinations.
    Student Name: {student_name}
    Current Progress: DAY {day} of 180 Days (6-Month Mastery Roadmap)
    Target Exam Focus: {exam}
    Active Subject: {subject}

    MANDATORY PEDAGOGICAL & TEACHING RULES:

    1. DAILY PSYCHOLOGICAL MINDSET BOOST (First Paragraph Always):
       - Begin warmly: "പ്രിയപ്പെട്ട {student_name},"
       - Remind {student_name}: "6 മാസത്തിനുള്ളിൽ ബാങ്ക് ഉദ്യോഗസ്ഥയായി മാറാനുള്ള യാത്രയിലെ Day {day} ക്ലാസ്സിലേക്ക് സ്വാഗതം!"
       - Offer 1-2 lines of personalized psychological motivation to eliminate fear and sharpen memory.

    2. REAL-LIFE ANALOGY TEACHING METHOD:
       - Explain complex concepts using simple everyday situations (Shopping discount, UPI payments, kitchen recipe proportions, seating arrangements in functions).
       - Provide 30-Second Super Shortcuts / Vedic tricks.
       - End with 1 interactive SBI/IBPS Clerk pattern question.

    3. LANGUAGE: Warm, highly structured, encouraging Malayalam / Manglish.
    """
    return genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)

# --- HEADER SECTION ---
st.title("🎓 SBI & IBPS AI Super-Coach")
st.markdown(
    f"<div class='user-badge'>👤 STUDENT: {user_name.upper()}</div>"
    f"<div class='day-badge'>📍 CURRENT CLASS: DAY {selected_day} / 180</div>",
    unsafe_allow_html=True
)

# Top Navigation Subject Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔥 Current Affairs", 
    "📊 Quant & Speed Math", 
    "🧩 Reasoning Puzzles", 
    "✍️ English Grammar", 
    "💻 Computer Aptitude",
    "🎯 Live Exam Practice"
])

subject_map = {
    0: "Current Affairs, Banking & Financial Awareness",
    1: "Quantitative Aptitude, Speed Math & Data Interpretation",
    2: "Reasoning Ability, Puzzles & Seating Arrangements",
    3: "General English, Cloze Test & Error Spotting",
    4: "Computer Knowledge & Digital Banking",
    5: "Live Exam Mock Test & Evaluation Mode"
}

with tab1: active_subject = subject_map[0]
with tab2: active_subject = subject_map[1]
with tab3: active_subject = subject_map[2]
with tab4: active_subject = subject_map[3]
with tab5: active_subject = subject_map[4]
with tab6: active_subject = subject_map[5]

# Load Cached Fast Model Instance for Student, Day & Subject
model = get_gemini_model(api_key, active_subject, exam_target, selected_day, user_name)

# Session Reset Management per User, Day, and Subject
session_key = f"messages_{user_name}_day_{selected_day}_{active_subject}"

if "current_session_key" not in st.session_state or st.session_state.current_session_key != session_key:
    st.session_state.current_session_key = session_key
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"പ്രിയപ്പെട്ട {user_name}, നമസ്കാരം! **Day {selected_day}** ക്ലാസ്സിലേക്ക് സ്വാഗതം.\n\nഇന്ന് നമ്മൾ **{active_subject}** വിഭാഗത്തിലെ പാഠഭാഗങ്ങളാണ് പഠിക്കാൻ പോകുന്നത്. തയ്യാറാണെങ്കിൽ 'Start' എന്ന് ടൈപ്പ് ചെയ്യൂ!"
    }]

# Display Active Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input Box
if prompt := st.chat_input(f"{user_name} - Day {selected_day} പഠനഭാഗത്തെ ചോദ്യങ്ങളും സംശയങ്ങളും ചോദിക്കൂ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{user_name} മോൾക്കായി ഉത്തരം തയാറാക്കുന്നു..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# Sidebar Download Option for Notes
with st.sidebar:
    st.markdown("---")
    chat_download_data = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button(
        label=f"📥 Download {user_name}'s Day {selected_day} Notes",
        data=chat_download_data,
        file_name=f"{user_name}_Day_{selected_day}_Notes.json",
        mime="application/json"
    )