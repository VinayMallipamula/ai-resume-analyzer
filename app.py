import streamlit as st
from resume_analyzer import ResumeAnalyzer
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        background-color: #e3f2fd;
        border-radius: 15px;
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize analyzer
@st.cache_resource
def get_analyzer():
    return ResumeAnalyzer()


analyzer = get_analyzer()

# Header
st.markdown('<div class="main-header">📄 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown("Upload your resume and get instant insights on skills, keywords, and job fit!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Options")
    analysis_mode = st.radio(
        "Analysis Mode",
        ["Resume Only", "Resume + Job Description"]
    )

    st.markdown("---")
    st.markdown("### About")
    st.info(
        "This tool analyzes your resume using NLP techniques to:\n"
        "- Extract key information\n"
        "- Identify skills and keywords\n"
        "- Calculate job match percentage\n"
        "- Generate visual insights"
    )

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload your resume in PDF format"
    )

with col2:
    if analysis_mode == "Resume + Job Description":
        st.markdown("### 📋 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=200,
            help="Paste the job description you want to match against"
        )
    else:
        job_description = None

# Analyze button
if uploaded_file:
    if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
        with st.spinner("Analyzing your resume... Please wait."):
            try:
                # Perform analysis
                results = analyzer.analyze_resume(uploaded_file, job_description)

                # Store results in session state
                st.session_state['results'] = results
                st.success("✅ Analysis complete!")

            except Exception as e:
                st.error(f"❌ Error analyzing resume: {str(e)}")

# Display results
if 'results' in st.session_state:
    results = st.session_state['results']

    st.markdown("---")
    st.markdown('<div class="sub-header">📊 Analysis Results</div>', unsafe_allow_html=True)

    # Contact Information
    st.markdown("### 👤 Contact Information")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**📧 Email:** {results['email']}")
    with col2:
        st.markdown(f"**📱 Phone:** {results['phone']}")

    # Job Match Score (if available)
    if results['job_match']:
        st.markdown("---")
        st.markdown("### 🎯 Job Match Analysis")

        match_pct = results['job_match']['percentage']

        # Display match percentage with color coding
        if match_pct >= 70:
            color = "green"
            emoji = "🟢"
        elif match_pct >= 50:
            color = "orange"
            emoji = "🟡"
        else:
            color = "red"
            emoji = "🔴"

        st.markdown(f"## {emoji} Match Score: {match_pct:.1f}%")
        st.progress(match_pct / 100)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ Matching Keywords")
            matching = list(results['job_match']['matching_keywords'])[:20]
            if matching:
                for keyword in matching:
                    st.markdown(f'<span class="skill-badge">✓ {keyword}</span>',
                                unsafe_allow_html=True)
            else:
                st.warning("No matching keywords found")

        with col2:
            st.markdown("#### ❌ Missing Keywords")
            missing = list(results['job_match']['missing_keywords'])[:20]
            if missing:
                for keyword in missing:
                    st.markdown(f'<span class="skill-badge">✗ {keyword}</span>',
                                unsafe_allow_html=True)
            else:
                st.info("No missing keywords!")

    # Skills Analysis
    st.markdown("---")
    st.markdown("### 🛠️ Skills Detected")

    if results['skills']:
        for category, skills in results['skills'].items():
            with st.expander(f"{category.replace('_', ' ').title()} ({len(skills)} skills)", expanded=True):
                for skill in skills:
                    st.markdown(f'<span class="skill-badge">{skill}</span>',
                                unsafe_allow_html=True)
    else:
        st.warning("No predefined skills detected. Check the word cloud for other keywords.")

    # Word Frequency
    st.markdown("---")
    st.markdown("### 📈 Top Keywords")

    col1, col2 = st.columns([1, 1])

    with col1:
        # Bar chart
        word_freq_df = pd.DataFrame(
            list(results['word_frequency'].items()),
            columns=['Word', 'Frequency']
        )
        st.bar_chart(word_freq_df.set_index('Word'))

    with col2:
        # Table
        st.dataframe(
            word_freq_df,
            use_container_width=True,
            hide_index=True
        )

    # Word Cloud
    st.markdown("---")
    st.markdown("### ☁️ Word Cloud Visualization")
    st.image(results['wordcloud'], use_container_width=True)

    # Resume Text Preview
    with st.expander("📄 View Extracted Text"):
        st.text_area("Resume Text", results['text'], height=300)

    # Download Report
    st.markdown("---")
    st.download_button(
        label="📥 Download Analysis Report",
        data=f"""
AI RESUME ANALYZER - ANALYSIS REPORT
=====================================

Contact Information:
- Email: {results['email']}
- Phone: {results['phone']}

Skills Detected:
{chr(10).join([f"- {cat.replace('_', ' ').title()}: {', '.join(skills)}" for cat, skills in results['skills'].items()])}

Top Keywords:
{chr(10).join([f"- {word}: {freq}" for word, freq in list(results['word_frequency'].items())[:10]])}

{'Job Match: ' + str(round(results['job_match']['percentage'], 1)) + '%' if results['job_match'] else ''}
""",
        file_name="resume_analysis_report.txt",
        mime="text/plain"
    )

else:
    # Instructions when no file is uploaded
    st.info("👆 Upload a resume PDF to get started!")

    st.markdown("### 🚀 Features")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 📧 Contact Extraction
        Automatically extracts email and phone number
        """)

    with col2:
        st.markdown("""
        #### 🛠️ Skills Detection
        Identifies technical and soft skills
        """)

    with col3:
        st.markdown("""
        #### 🎯 Job Matching
        Calculates fit with job descriptions
        """)
