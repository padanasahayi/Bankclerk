import json
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# 1. Page Configuration for Mobile UX
st.set_page_config(
    page_title="SBI & IBPS Clerk AI Coach - Aiswarya",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Mobile Responsive Styling
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
    .day-badge {
        background-color: #0066cc;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 14px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# API Key Connection
api_key = st.secrets.get("GEMINI_API_KEY", None)

# --- SIDEBAR: NAVIGATION & DAY SELECTOR ---
with st.sidebar:
    st.header("🎯 Study Navigation")
    
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    else:
        st.success("⚡ Gemini 2.5 Flash Connected")
    
    st.markdown("---")
    
    # 🗓️ Day Selector (1 to 180 Days for 6 Months)
    st.subheader("📅 Class Selector")
    
    if "current_day" not in st.session_state:
        st.session_state.current_day = 1

    selected_day = st.number_input(
        "Select Day (1 - 180):",
        min_value=1,
        max_value=180,
        value=st.session_state.current_day,
        step=1,
        key="day_input"
    )

    # Quick Jump Actions
    col_start, col_next = st.columns(2)
    with col_start:
        if st.button("🔄 Go to Day 1"):
            st.session_state.current_day = 1
            st.rerun()
    with col_next:
        if st.button("▶️ Next Day"):
            if st.session_state.current_day < 180:
                st.session_state.current_day += 1
                st.rerun()

    st.markdown("---")
    exam_target = st.radio("Target Exam Focus:", ["SBI Clerk", "IBPS Clerk", "Combined SBI + IBPS"])

if not api_key:
    st.warning("⚠️ തുടരുവാൻ Sidebar തുറന്ന് Gemini API Key നൽകുക.")
    st.stop()

# Cache Gemini Model Initialization for High Performance
@st.cache_resource
def get_gemini_model(api_key: str, subject: str, exam: str, day: int):
    genai.configure(api_key=api_key)
    
    system_instruction = f"""
    You are Aiswarya's personal AI Super-Coach for SBI Clerk and IBPS Clerk Examinations.
    Student Name: Aiswarya
    Current Class Progress: DAY {day} of 180 Days (6-Month Roadmap)
    Target Exam Focus: {exam}
    Active Subject: {subject}

    PEDAGOGICAL & CLASS RULES:

    1. DAILY PSYCHOLOGICAL MINDSET BOOST (Mandatory 1st Paragraph):
       - Begin warmly: "പ്രിയപ്പെട്ട ഐശ്വര്യ," or "മോൾ ഐശ്വര്യ,".
       - Acknowledge DAY {day}: "6 മാസത്തെ നിന്റെ പഠനയാത്രയിലെ Day {day} ക്ലാസ്സിലേക്ക് സ്വാഗതം! ഈ 180 ദിവസത്തെ നിന്റെ അധ്വാനം നിന്നെ ഒരു ബാങ്ക് ഓഫീസറാക്കും."
       - Provide 1-2 sentences of encouraging psychological strength to boost focus and recall.

    2. DAY-SPECIFIC SYLLABUS LESSON STRUCTURE:
       - Teach concepts aligned with DAY {day} progression (from basic fundamentals in early days to advanced mains-level puzzles in later days).
       - Always use Real-Life Analogies (Shopping, UPI, recipes, family seating) to explain hard concepts.
       - Include 30-second Super Tricks / Vedic shortcuts.
       - End with 1 interactive practice question.

    3. LANGUAGE: Warm, clear, structured Malayalam / Manglish.
    """
    return genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)

# --- MAIN PAGE HEADER ---
st.title("🎓 SBI & IBPS AI Coach - Aiswarya")
st.markdown(f"<div class='day-badge'>📍 CURRENT CLASS: DAY {selected_day} / 180</div>", unsafe_allow_html=True)

# Top Subject Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔥 Current Affairs", 
    "📊 Quant & Speed Math", 
    "🧩 Reasoning Puzzles", 
    "✍️ English Grammar", 
    "💻 Computer Aptitude",
    "🎯 Live Quiz Mode"
])

subject_map = {
    0: "Current Affairs, Banking & Financial Awareness",
    1: "Quantitative Aptitude, Speed Math & Data Interpretation",
    2: "Reasoning Ability, Puzzles & Seating Arrangements",
    3: "General English, Cloze Test & Error Spotting",
    4: "Computer Knowledge & Digital Banking",
    5: "Live Exam Mock Practice & Evaluation"
}

with tab1: active_subject = subject_map[0]
with tab2: active_subject = subject_map[1]
with tab3: active_subject = subject_map[2]
with tab4: active_subject = subject_map[3]
with tab5: active_subject = subject_map[4]
with tab6: active_subject = subject_map[5]

# Load Cached Model for selected subject & day
model = get_gemini_model(api_key, active_subject, exam_target, selected_day)

# Session Reset when Day or Subject Changes
session_key = f"messages_day_{selected_day}_{active_subject}"

if "current_session_key" not in st.session_state or st.session_state.current_session_key != session_key:
    st.session_state.current_session_key = session_key
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"പ്രിയപ്പെട്ട ഐശ്വര്യ, നമസ്കാരം! **Day {selected_day}** ക്ലാസ്സിലേക്ക് സ്വാഗതം. ഇന്ന് നമ്മൾ **{active_subject}** വിഭാഗത്തിൽ നിന്നുള്ള പാഠങ്ങളാണ് പഠിക്കുന്നത്.\n\nപഠനം ആരംഭിക്കാൻ 'Start' എന്ന് ടൈപ്പ് ചെയ്യൂ!"
    }]

# Display Chat Stream
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input Box
if prompt := st.chat_input(f"Day {selected_day} - സംശയങ്ങളും ഉത്തരങ്ങളും ഇവിടെ ടൈപ്പ് ചെയ്യുക..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Day {selected_day} പാഠഭാഗം തയാറാക്കുന്നു..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

# Sidebar Download Option for Notes
with st.sidebar:
    chat_download_data = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button(
        label=f"📥 Download Day {selected_day} Notes (.json)",
        data=chat_download_data,
        file_name=f"Aiswarya_Day_{selected_day}_Notes.json",
        mime="application/json"
    )
