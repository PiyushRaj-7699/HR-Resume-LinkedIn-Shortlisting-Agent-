"""
Main Streamlit web application for HR Resume & LinkedIn Shortlisting Agent.

This app provides a web UI for parsing job descriptions, ingesting candidate
resumes/profiles, scoring candidates, and generating ranked shortlists.
"""

import os
import tempfile
import logging
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from agent.jd_parser import JDParser
from agent.profile_parser import ProfileParser
from agent.scoring_engine import ScoringEngine
from agent.ranker import rank_candidates, filter_by_recommendation
from agent.report_generator import ReportGenerator
from utils.override_logger import log_override

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(page_title="HR Shortlisting Agent", page_icon="🤖", layout="wide")


def main():
    """Main Streamlit app entry point."""
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    
    api_key = st.sidebar.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Your Anthropic Claude API key",
    )
    
    model = st.sidebar.selectbox(
        "LLM Model",
        options=[
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-haiku-4-5-20251001",
        ],
        index=0,
        help="Select the Claude model to use for analysis",
    )
    
    report_format = st.sidebar.selectbox(
        "Report Format",
        options=["HTML", "PDF", "JSON", "All Formats"],
        index=3,
        help="Select the format(s) for the generated report",
    )
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Job Description", "👥 Candidates", "📊 Results & Report"])
    
    # Initialize session state
    if "jd_parsed" not in st.session_state:
        st.session_state["jd_parsed"] = None
    if "scored_results" not in st.session_state:
        st.session_state["scored_results"] = None
    
    # TAB 1: Job Description
    with tab1:
        st.header("📋 Job Description Parser")
        st.write("Paste the job description below. The AI will parse and extract key requirements.")
        
        jd_text = st.text_area(
            "Paste Job Description here",
            height=400,
            placeholder="Job Title: ...\nResponsibilities: ...\nRequirements: ...",
        )
        
        if st.button("Parse JD", key="parse_jd_btn"):
            if not jd_text.strip():
                st.error("Please paste a job description first.")
            elif not api_key:
                st.error("Please enter your Anthropic API Key in the sidebar.")
            else:
                with st.spinner("Parsing job description..."):
                    try:
                        parser = JDParser(api_key=api_key, model=model)
                        jd_parsed = parser.parse(jd_text)
                        st.session_state["jd_parsed"] = jd_parsed
                        
                        num_skills = len(jd_parsed.get("required_skills", []))
                        st.success(f"✅ JD parsed successfully — {num_skills} required skills identified.")
                        st.json(jd_parsed)
                    except Exception as e:
                        st.error(f"Failed to parse JD: {e}")
                        logger.exception("JD parsing error")
    
    # TAB 2: Candidates
    with tab2:
        st.header("👥 Candidate Upload & Scoring")
        st.write("Upload resumes and LinkedIn profiles, then score all candidates.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Resumes")
            resume_files = st.file_uploader(
                "Upload Resumes",
                type=["pdf", "docx"],
                accept_multiple_files=True,
                key="resume_uploader",
            )
        
        with col2:
            st.subheader("💼 LinkedIn Profiles")
            linkedin_files = st.file_uploader(
                "Upload LinkedIn JSON profiles",
                type=["json"],
                accept_multiple_files=True,
                key="linkedin_uploader",
            )
        
        if st.button("Parse & Score All Candidates", key="score_candidates_btn"):
            # Check JD is parsed
            if st.session_state["jd_parsed"] is None:
                st.error("❌ Please parse the JD first in Tab 1.")
            elif not resume_files and not linkedin_files:
                st.error("❌ Please upload at least one resume or LinkedIn profile.")
            elif not api_key:
                st.error("❌ Please enter your Anthropic API Key in the sidebar.")
            else:
                with st.spinner("Scoring candidates..."):
                    try:
                        # Initialize parsers and engine
                        profile_parser = ProfileParser(api_key=api_key, model=model)
                        scoring_engine = ScoringEngine(api_key=api_key, model=model)
                        jd_dict = st.session_state["jd_parsed"]
                        
                        candidate_profiles = []
                        
                        # Process resume files
                        for resume_file in resume_files:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.name).suffix) as tmp:
                                tmp.write(resume_file.getbuffer())
                                tmp_path = tmp.name
                            
                            try:
                                profile = profile_parser.parse_from_file(tmp_path)
                                candidate_profiles.append(profile)
                                st.write(f"✓ Parsed: {profile.get('name', 'Unknown')}")
                            except Exception as e:
                                st.warning(f"⚠ Failed to parse {resume_file.name}: {e}")
                            finally:
                                os.unlink(tmp_path)
                        
                        # Process LinkedIn files
                        for linkedin_file in linkedin_files:
                            try:
                                import json
                                linkedin_data = json.loads(linkedin_file.getvalue().decode())
                                profile = profile_parser.parse_from_linkedin(linkedin_data)
                                candidate_profiles.append(profile)
                                st.write(f"✓ Parsed: {profile.get('name', 'Unknown')}")
                            except Exception as e:
                                st.warning(f"⚠ Failed to parse {linkedin_file.name}: {e}")
                        
                        # Score all candidates
                        if candidate_profiles:
                            progress_bar = st.progress(0)
                            scored_results = []
                            
                            for i, profile in enumerate(candidate_profiles):
                                try:
                                    score_result = scoring_engine.score(jd_dict, profile)
                                    score_result["candidate"] = profile
                                    scored_results.append(score_result)
                                    progress_bar.progress((i + 1) / len(candidate_profiles))
                                except Exception as e:
                                    st.warning(f"⚠ Failed to score {profile.get('name', 'Unknown')}: {e}")
                            
                            st.session_state["scored_results"] = scored_results
                            st.success(f"✅ {len(scored_results)} candidates scored successfully.")
                        else:
                            st.error("No valid candidates to score.")
                    except Exception as e:
                        st.error(f"Scoring error: {e}")
                        logger.exception("Candidate scoring error")
    
    # TAB 3: Results & Report
    with tab3:
        st.header("📊 Results & Report")
        
        if st.session_state["scored_results"] is None or len(st.session_state["scored_results"]) == 0:
            st.info("No results yet. Please score candidates in the 'Candidates' tab.")
        else:
            # Rank candidates
            ranked_results = rank_candidates(st.session_state["scored_results"])
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Screened", len(ranked_results))
            with col2:
                hire_count = len(filter_by_recommendation(ranked_results, "Hire"))
                st.metric("Hire ✓", hire_count)
            with col3:
                maybe_count = len(filter_by_recommendation(ranked_results, "Maybe"))
                st.metric("Maybe ⚠", maybe_count)
            with col4:
                no_hire_count = len(filter_by_recommendation(ranked_results, "No Hire"))
                st.metric("No Hire ✗", no_hire_count)
            
            st.divider()
            
            # Results table
            st.subheader("📑 Ranked Candidates")
            
            table_data = []
            for result in ranked_results:
                rank = result.get("rank", "")
                candidate = result.get("candidate", {})
                name = candidate.get("name", "Unknown")
                skills = result.get("skills_match", {}).get("score", 0)
                experience = result.get("experience_relevance", {}).get("score", 0)
                education = result.get("education_certs", {}).get("score", 0)
                project = result.get("project_portfolio", {}).get("score", 0)
                comms = result.get("communication_quality", {}).get("score", 0)
                total_score = result.get("weighted_total", 0)
                recommendation = result.get("hire_recommendation", "N/A")
                
                table_data.append({
                    "Rank": rank,
                    "Name": name,
                    "Skills": skills,
                    "Experience": experience,
                    "Education": education,
                    "Projects": project,
                    "Comms": comms,
                    "Total": f"{total_score:.2f}",
                    "Recommendation": recommendation,
                })
            
            st.dataframe(table_data, use_container_width=True)
            
            st.divider()
            
            # Candidate details with overrides
            st.subheader("🔍 Candidate Details & Score Overrides")
            
            for result in ranked_results:
                rank = result.get("rank", "")
                candidate = result.get("candidate", {})
                name = candidate.get("name", "Unknown")
                total_score = result.get("weighted_total", 0)
                recommendation = result.get("hire_recommendation", "N/A")
                
                with st.expander(f"#{rank} — {name} | Score: {total_score:.2f} | {recommendation}"):
                    # Display all scores and justifications
                    col1, col2 = st.columns(2)
                    
                    dimensions = [
                        ("skills_match", "Skills Match", 0.30),
                        ("experience_relevance", "Experience Relevance", 0.25),
                        ("education_certs", "Education & Certs", 0.15),
                        ("project_portfolio", "Project Portfolio", 0.20),
                        ("communication_quality", "Communication Quality", 0.10),
                    ]
                    
                    for i, (key, label, weight) in enumerate(dimensions):
                        score = result.get(key, {}).get("score", 0)
                        justification = result.get(key, {}).get("justification", "")
                        if i % 2 == 0:
                            with col1:
                                st.write(f"**{label} (weight: {weight*100}%)**")
                                st.write(f"Score: **{score}/10**")
                                st.caption(justification)
                        else:
                            with col2:
                                st.write(f"**{label} (weight: {weight*100}%)**")
                                st.write(f"Score: **{score}/10**")
                                st.caption(justification)
                    
                    st.divider()
                    
                    # Override section
                    st.write("**Override Score (Optional)**")
                    override_dimension = st.selectbox(
                        "Select dimension to override",
                        options=[d[1] for d in dimensions],
                        key=f"override_dim_{rank}_{name}",
                    )
                    
                    original_score = None
                    for key, label, _ in dimensions:
                        if label == override_dimension:
                            original_score = result.get(key, {}).get("score", 0)
                            break
                    
                    new_score = st.number_input(
                        f"New score for {override_dimension}",
                        min_value=0,
                        max_value=10,
                        value=original_score or 5,
                        key=f"new_score_{rank}_{name}",
                    )
                    
                    override_reason = st.text_input(
                        "Reason for override",
                        key=f"override_reason_{rank}_{name}",
                    )
                    
                    if st.button(
                        "Log Override",
                        key=f"log_override_{rank}_{name}",
                    ):
                        if override_reason.strip():
                            log_override(
                                candidate_name=name,
                                dimension=override_dimension,
                                original_score=original_score or 0,
                                new_score=new_score,
                                reason=override_reason,
                                log_file="outputs/override_log.json",
                            )
                            st.success("✓ Override logged successfully.")
                        else:
                            st.error("Please provide a reason for the override.")
            
            st.divider()
            
            # Report generation
            st.subheader("📄 Generate Report")
            
            if st.button("Generate Report", key="generate_report_btn"):
                if st.session_state["jd_parsed"] is None:
                    st.error("JD data not available.")
                else:
                    with st.spinner("Generating report..."):
                        try:
                            output_dir = os.getenv("OUTPUT_DIR", "outputs/")
                            report_gen = ReportGenerator(output_dir=output_dir)
                            
                            generated_files = []
                            
                            if report_format in ["JSON", "All Formats"]:
                                json_path = report_gen.generate_json(ranked_results)
                                generated_files.append(("JSON", json_path))
                            
                            if report_format in ["HTML", "All Formats"]:
                                html_path = report_gen.generate_html(
                                    ranked_results,
                                    st.session_state["jd_parsed"],
                                )
                                generated_files.append(("HTML", html_path))
                            
                            if report_format in ["PDF", "All Formats"]:
                                pdf_path = report_gen.generate_pdf(
                                    ranked_results,
                                    st.session_state["jd_parsed"],
                                )
                                generated_files.append(("PDF", pdf_path))
                            
                            st.success("✅ Report generated successfully!")
                            
                            # Download buttons
                            for fmt, filepath in generated_files:
                                with open(filepath, "rb") as f:
                                    st.download_button(
                                        label=f"Download {fmt}",
                                        data=f.read(),
                                        file_name=os.path.basename(filepath),
                                        mime=get_mime_type(fmt),
                                    )
                        except Exception as e:
                            st.error(f"Report generation failed: {e}")
                            logger.exception("Report generation error")


def get_mime_type(fmt: str) -> str:
    """Get MIME type for file format."""
    mime_types = {
        "JSON": "application/json",
        "HTML": "text/html",
        "PDF": "application/pdf",
    }
    return mime_types.get(fmt, "application/octet-stream")


if __name__ == "__main__":
    main()
