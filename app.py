import streamlit as st
import os
from final import KeyRacerAnalyzer, RoadmapAgent, CareerSuccessAgent, InterviewChatAgent

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="2026 Career AI", page_icon="🏎️", layout="wide")

# Custom CSS for a professional "Glassmorphism" look
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #00ffcc; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏎️ Keyracer: AI Career Architect")
st.markdown("---")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("🔑 API Configuration")
    g_key = st.text_input("Groq API Key", type="password")
    t_key = st.text_input("Tavily API Key", type="password")
    
    st.header("🎯 Target Goal")
    target_role = st.text_input("Target Job Role", value="AI Engineer")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

# --- SESSION STATE INITIALIZATION ---
if "report" not in st.session_state: st.session_state.report = None
if "roadmap" not in st.session_state: st.session_state.roadmap = None

# --- MAIN WORKFLOW ---
if uploaded_file and g_key and t_key:
    if st.button("🚀 Analyze & Generate Full Strategy"):
        with st.status("Processing Career Data...", expanded=True) as status:
            # Save PDF temporarily
            temp_path = "temp_resume.pdf"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Phase 1: Deep Analysis
            st.write("🔍 Extracting Skills & Gaps...")
            analyzer = KeyRacerAnalyzer(g_key)
            st.session_state.report = analyzer.analyze(temp_path, target_role)
            
            # Phase 2: Roadmap Generation
            st.write("🗺️ Generating 6-Month Roadmap...")
            roadmap_agent = RoadmapAgent(g_key, t_key)
            st.session_state.roadmap = roadmap_agent.run(st.session_state.report, target_role)
            
            status.update(label="Analysis Complete!", state="complete")
            os.remove(temp_path)

# --- DISPLAY TABS ---
if st.session_state.report:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Profile Analysis", "🗺️ Roadmap", "🔍 Job Search", "🤝 Mock Interview"])

    with tab1:
        st.subheader("Candidate Intelligence")
        c1, c2, c3 = st.columns(3)
        c1.metric("Experience Score", f"{st.session_state.report.experience_score}/100")
        c2.metric("Skills Found", len(st.session_state.report.technical_skills))
        c3.metric("Gaps Found", len(st.session_state.report.current_gaps))
        
        st.info(f"**Professional Summary:** {st.session_state.report.professional_summary}")
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.success("**Top Technical Skills**")
            st.write(st.session_state.report.technical_skills)
        with col_right:
            st.error("**Missing Critical Skills**")
            st.write(st.session_state.report.current_gaps)

    with tab2:
        st.subheader(f"6-Month Learning Path for {target_role}")
        st.markdown(st.session_state.roadmap)

    with tab3:
        st.subheader("Real-time Job Opportunities (2026)")
        if st.button("Find Matching Jobs"):
            success_agent = CareerSuccessAgent(g_key, t_key)
            with st.spinner("Searching market..."):
                jobs = success_agent.find_jobs(target_role, st.session_state.report.technical_skills)
                st.markdown(jobs)

    with tab4:
        st.subheader("Interactive Interview Simulation")
        if "interview_messages" not in st.session_state:
            st.session_state.interview_messages = []
            st.session_state.chat_agent = InterviewChatAgent(g_key, target_role, st.session_state.report)

        # Display Chat History
        for msg in st.session_state.interview_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Answer the interviewer..."):
            st.session_state.interview_messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"): st.markdown(chat_input)
            
            with st.chat_message("assistant"):
                response = st.session_state.chat_agent.chat(chat_input)
                st.markdown(response)
                st.session_state.interview_messages.append({"role": "assistant", "content": response})

else:
    st.info("Please upload your resume and enter API keys in the sidebar to begin.")