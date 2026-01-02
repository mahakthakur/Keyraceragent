import streamlit as st
import os
import base64
from final import KeyRacerAnalyzer, RoadmapAgent, CareerSuccessAgent, InterviewChatAgent

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Keyracer AI | Career Architect", page_icon="🏎️", layout="wide")

# --- CUSTOM THEMING & GLASSMORPHISM ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
    }

    /* Glassmorphism Containers */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #00ffcc !important;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 10px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00ffcc44 !important;
        border-bottom: 2px solid #00ffcc !important;
    }

    /* Modern Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: none;
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("keyracer_logo-removebg-preview.png", width=100) # Placeholder for a cool logo
with col2:
    st.title("Keyracer: AI Career Agent")
    st.caption("2026 Edition | Powered by Groq & Tavily")

st.markdown("---")

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("🔐 Access")
    g_key = st.text_input("Groq API Key", type="password", help="Enter your GroqCloud API Key")
    t_key = st.text_input("Tavily API Key", type="password", help="Enter your Search API Key")
    
    st.markdown("---")
    st.header("🎯 Career Focus")
    target_role = st.selectbox("Target Job Role", 
                               ["AI Engineer", "Data Scientist", "Fullstack Developer", "Product Manager", "Cloud Architect"])
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
    
    if uploaded_file:
        st.success("Resume Uploaded!")

# --- SESSION STATE ---
if "report" not in st.session_state: st.session_state.report = None
if "roadmap" not in st.session_state: st.session_state.roadmap = None

# --- PROCESSING LOGIC ---
if uploaded_file and g_key and t_key:
    if st.button("🚀 START AI ACCELERATION"):
        with st.status("Analyzing Professional DNA...", expanded=True) as status:
            temp_path = "temp_resume.pdf"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.write("🧠 Scanning Resume with LLM...")
            analyzer = KeyRacerAnalyzer(g_key)
            st.session_state.report = analyzer.analyze(temp_path, target_role)
            
            st.write("🌍 Scouring Market for Skill Gaps...")
            roadmap_agent = RoadmapAgent(g_key, t_key)
            st.session_state.roadmap = roadmap_agent.run(st.session_state.report, target_role)
            
            status.update(label="Analysis Complete!", state="complete")
            os.remove(temp_path)

# --- MAIN DASHBOARD ---
if st.session_state.report:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Candidate Intelligence", 
        "🗺️ Skill Roadmap", 
        "💼 Live Opportunities", 
        "🤖 Interview Coach"
    ])

    with tab1:
        st.markdown("### 🔍 Executive Summary")
        # Horizontal Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Experience Score", f"{st.session_state.report.experience_score}%", "Top 10%")
        with m2:
            st.metric("Tech Stack Match", f"{len(st.session_state.report.technical_skills)} Skills")
        with m3:
            st.metric("Critical Gaps", f"{len(st.session_state.report.current_gaps)}")

        st.markdown(f"> **AI Insight:** {st.session_state.report.professional_summary}")
        
        # Skill Breakdown
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("✅ Core Strengths")
            for skill in st.session_state.report.technical_skills:
                st.markdown(f"- `{skill}`")
        with c_right:
            st.subheader("⚠️ Priority Skill Gaps")
            for gap in st.session_state.report.current_gaps:
                st.markdown(f"- :red[{gap}]")

    with tab2:
        st.markdown("### 🗓️ 180-Day Acceleration Path")
        # Visual Divider for Roadmap
        st.markdown(st.session_state.roadmap)

    with tab3:
        st.markdown("### 🌏 2026 Market Openings")
        if st.button("Scan Real-time Job Postings"):
            success_agent = CareerSuccessAgent(g_key, t_key)
            with st.spinner("Accessing global job boards..."):
                jobs = success_agent.find_jobs(target_role, st.session_state.report.technical_skills)
                st.markdown(jobs)

    with tab4:
        st.markdown("### 💬 Mock Interview Simulation")
        # Sidebar-like chat interface within the tab
        if "interview_messages" not in st.session_state:
            st.session_state.interview_messages = [{"role": "assistant", "content": f"Hello! I am your {target_role} interviewer. Ready to begin?"}]
            st.session_state.chat_agent = InterviewChatAgent(g_key, target_role, st.session_state.report)

        # Chat Container
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.interview_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if chat_input := st.chat_input("Type your response here..."):
            st.session_state.interview_messages.append({"role": "user", "content": chat_input})
            with st.chat_message("user"): st.markdown(chat_input)
            
            with st.chat_message("assistant"):
                response = st.session_state.chat_agent.chat(chat_input)
                st.markdown(response)
                st.session_state.interview_messages.append({"role": "assistant", "content": response})

else:
    # Empty State
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2 style="color: #666;">Welcome to the Future of Career Growth</h2>
            <p>Please upload your resume in the sidebar to generate your AI-powered career strategy.</p>
        </div>
    """, unsafe_allow_html=True)