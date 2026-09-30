import json
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# 1. Page & Mobile Responsive Setup
st.set_page_config(
    page_title="SBI & IBPS Clerk AI Coach - Aiswarya",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for Mobile UX & Top Navigation
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
        padding: 8px 12px !important;
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
</style>
""", unsafe_allow_html=True)

# 2. IndexedDB Script for Auto Local Revision Storage
INDEXED_DB_JS = """
<script>
const DB_NAME = 'AiswaryaBankCoachDB';
const DB_VERSION = 1;
const STORE_NAME = 'bank_lessons';

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
            }
        };
        request.onsuccess = (event) => resolve(event.target.result);
        request.onerror = (event) => reject(event.target.error);
    });
}

async function saveToLocalDB(exam, subject, role, text) {
    try {
        const db = await openDB();
        const tx = db.transaction(STORE_NAME, 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.add({
            exam_type: exam,
            subject: subject,
            role: role,
            content: text,
            date: new Date().toLocaleString()
        });
    } catch (err) { console.error("IndexedDB Save Error:", err); }
}
</script>
"""
components.html(INDEXED_DB_JS, height=0)

# Application Header
st.title("🎓 SBI & IBPS Clerk AI Super-Coach")
st.caption("Aiswarya's 6-Month Bank Officer Mission | Powered by Gemini 2.5 Flash")

# API Key Connection (Streamlit Secrets or Sidebar)
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.sidebar:
    st.header("⚙️ Exam & System Config")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    else:
        st.success("⚡ Gemini 2.5 Flash Connected")
    
    st.markdown("---")
    exam_target = st.radio("Target Exam Focus:", ["SBI Clerk (CRPD)", "IBPS Clerk (CRP)", "Combined SBI + IBPS"])
    st.markdown("---")

if not api_key:
    st.warning("⚠️ തുടരുവാൻ Sidebar തുറന്ന് Gemini API Key നൽകുക.")
    st.stop()

genai.configure(api_key=api_key)

# Top Navigation Tabs covering Complete Syllabus
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔥 Current Affairs", 
    "📊 Quant & Speed Math", 
    "🧩 Reasoning Puzzles", 
    "✍️ English Grammar", 
    "💻 Computer Aptitude",
    "🎯 Live Quiz & Evaluator"
])

subject_map = {
    0: "Current Affairs, Banking & Financial Awareness",
    1: "Quantitative Aptitude, Speed Math & Data Interpretation",
    2: "Reasoning Ability, Puzzles & Seating Arrangements",
    3: "General English, Cloze Test & Error Spotting",
    4: "Computer Knowledge & Digital Banking",
    5: "SBI & IBPS Clerk Live Mock Exam & AI Evaluation"
}

with tab1: active_subject = subject_map[0]
with tab2: active_subject = subject_map[1]
with tab3: active_subject = subject_map[2]
with tab4: active_subject = subject_map[3]
with tab5: active_subject = subject_map[4]
with tab6: active_subject = subject_map[5]

# Master Prompting Engine
SYSTEM_INSTRUCTION = f"""
You are Aiswarya's personal AI Super-Coach for SBI Clerk and IBPS Clerk Examinations.
Student Name: Aiswarya
Target Goal: Secure a Bank Clerk Job within 6 Months.
Selected Focus: {exam_target}
Active Subject: {active_subject}

CORE PEDAGOGICAL INSTRUCTIONS:

1. DAILY PSYCHOLOGICAL MINDSET BOOST (First Paragraph Always):
   - Start warmly addressing her: "പ്രിയപ്പെട്ട ഐശ്വര്യ," or "മോൾ ഐശ്വര്യ,".
   - Remind her: "6 മാസത്തിനുള്ളിൽ ബാങ്ക് ക്ലർക്ക് എന്ന നിന്റെ ലക്ഷ്യത്തിലേക്കുള്ള വളരെ പ്രധാനപ്പെട്ട പടിയാണിത്."
   - Give 1-2 lines of psychological motivation to remove exam stress and boost recall power.

2. REAL-LIFE ANALOGY TEACHING METHOD (Nithya Jeevitha Examples):
   - Do NOT teach using dry rules or formulas alone.
   - Always connect concepts to real-world everyday life:
     * Quant/Maths -> Shopping discounts, kitchen recipes, budgeting, bus/train timings.
     * Reasoning Puzzles -> Family seating at functions, apartment building floor arrangements.
     * Banking Awareness -> Daily GooglePay/UPI transactions, ATM operations, fixed deposits.
     * English -> Common daily chat mistakes and news reading habits.

3. LESSON STRUCTURE:
   - Part 1: Psychological Mindset Boost.
   - Part 2: Simplified Concept using a Daily Life Story/Example.
   - Part 3: 30-Second Vedic Trick / Exam Shortcut.
   - Part 4: 1 or 2 SBI/IBPS Clerk Level Practice Questions.
   - Part 5: Evaluate her answers with marks (+1 for correct, -0.25 for wrong) and encouraging explanation.

4. LANGUAGE: Simple, warm, structured Malayalam / Manglish.
"""

# Initialize Session State
if "messages" not in st.session_state or st.session_state.get("current_subject") != active_subject:
    st.session_state.current_subject = active_subject
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
    st.session_state.chat = model.start_chat(history=[])
    
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"പ്രിയപ്പെട്ട ഐശ്വര്യ, നമസ്കാരം! അടുത്ത 6 മാസത്തിനുള്ളിൽ ബാങ്ക് ഉദ്യോഗസ്ഥയായി മാറാനുള്ള നിന്റെ യാത്രയിൽ **{exam_target}** സിലബസ് അടിസ്ഥാനമാക്കിയുള്ള പഠനം നമ്മൾ ആരംഭിക്കുകയാണ്.\n\nഇന്ന് നമ്മൾ **{active_subject}** ആണ് പഠിക്കാൻ പോകുന്നത്. തയ്യാറാണെങ്കിൽ 'Start' എന്ന് അയക്കൂ, വളരെ ലളിതമായി മനസ്സിലാക്കി പഠിച്ചു തുടങ്ങാം!"
        }
    ]

# Action Bar: Quick Question Generator
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🎲 Get Exam Question"):
        prompt = f"Give me 1 SBI/IBPS Clerk pattern practice question from {active_subject} with options."
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = st.session_state.chat.send_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input Box
if prompt := st.chat_input("ഉത്തരം അല്ലെങ്കിൽ സംശയങ്ങൾ ചോദിക്കൂ..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("ഐശ്വര്യയ്ക്കായി ഉത്തരം തയാറാക്കുന്നു..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

            # Save to IndexedDB
            save_js = f"""
            <script>
                if (window.parent.saveToLocalDB) {{
                    window.parent.saveToLocalDB('{exam_target}', '{active_subject}', 'assistant', `{response.text.replace('`', '')}`);
                }}
            </script>
            """
            components.html(save_js, height=0)

# Sidebar Download Option
with st.sidebar:
    chat_download_data = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Download Class Notes (.json)",
        data=chat_download_data,
        file_name="Aiswarya_Bank_Exam_Notes.json",
        mime="application/json"
    )
