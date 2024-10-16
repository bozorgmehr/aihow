import streamlit as st
import yaml
from pathlib import Path
import subprocess
import pandas as pd
import json
from datetime import datetime

# Function to load application data from a JSON file
def load_application_data():
    log_file = Path("data_folder/applied_jobs.json")
    if log_file.exists():
        with open(log_file, "r") as f:
            data = json.load(f)
            return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["Job Title", "Company", "Link", "Location", "Date", "Time"])

# Function to save job applications
def save_application_data(job_title, company, link, location):
    log_file = Path("data_folder/applied_jobs.json")
    if log_file.exists():
        with open(log_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    application = {
        "Job Title": job_title,
        "Company": company,
        "Link": link,
        "Location": location,
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Time": datetime.now().strftime("%H:%M:%S")
    }
    data.append(application)

    with open(log_file, "w") as f:
        json.dump(data, f)

def main():
    st.sidebar.title("Auto Jobs Applier - Configuration")

    st.sidebar.header("Personal Information")
    name = st.sidebar.text_input("First Name")
    surname = st.sidebar.text_input("Last Name")
    email = st.sidebar.text_input("Email")
    phone = st.sidebar.text_input("Phone Number")
    linkedin = st.sidebar.text_input("LinkedIn Profile URL")
    github = st.sidebar.text_input("GitHub Profile URL", "https://github.com/bozorgmehr")

    st.sidebar.header("Job Search Preferences")
    remote = st.sidebar.checkbox("Include Remote Jobs", value=False)
    positions = st.sidebar.text_input("Positions (comma-separated)", "Software Engineer, AI Developer")
    locations = st.sidebar.text_input("Locations (comma-separated)", "Berlin, Hamburg, Remote")
    experience_levels = st.sidebar.multiselect(
        "Experience Levels",
        ["Internship", "Entry", "Associate", "Mid-Senior Level", "Director", "Executive"],
        default=["Entry", "Associate"]
    )
    job_types = st.sidebar.selectbox("Job Type", ["Full-time", "Contract"], index=0)
    date_posted = st.sidebar.selectbox("Date Posted", ["All Time", "Past Month", "Past Week", "Past 24 hours"], index=2)
    distance = st.sidebar.selectbox("Distance (miles)", [0, 5, 10, 25, 50, 100], index=5)
    company_blacklist = st.sidebar.text_input("Company Blacklist (comma-separated)")
    title_blacklist = st.sidebar.text_input("Title Blacklist (comma-separated)")

    st.sidebar.header("Resume")
    resume_file = st.sidebar.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    plain_text_resume_file = st.sidebar.file_uploader("Upload Plain Text Resume (YAML)", type=["yaml", "yml"])

    st.sidebar.header("LLM Configuration")
    llm_model_type = st.sidebar.selectbox("LLM Model Type", ["gemini", "openai", "ollama", "claude"])
    llm_model = st.sidebar.text_input("LLM Model", "flash-1.5")
    llm_api_key = st.sidebar.text_input("LLM API Key", type="password")
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
    top_p = st.sidebar.slider("Top P", 0.0, 1.0, 0.8)
    max_tokens = st.sidebar.number_input("Max Tokens", min_value=1, max_value=4096, value=4096)

    st.sidebar.header("Additional Settings")
    apply_once_at_company = st.sidebar.checkbox("Apply Only Once Per Company", value=True)
    min_applicants = st.sidebar.number_input("Minimum Applicants", min_value=0, value=0)
    max_applicants = st.sidebar.number_input("Maximum Applicants", min_value=0, value=50)

    if st.sidebar.button("Save Configuration"):
        config_data = {
            'remote': remote,
            'experienceLevel': {level.lower(): level in experience_levels for level in ["Internship", "Entry", "Associate", "Mid-Senior Level", "Director", "Executive"]},
            'jobTypes': {job_types.lower().replace("-", "_"): True},
            'date': {date_posted.lower(): True},
            'positions': [pos.strip() for pos in positions.split(",")],
            'locations': [loc.strip() for loc in locations.split(",")],
            'distance': distance,
            'company_blacklist': [comp.strip() for comp in company_blacklist.split(",") if comp.strip()],
            'title_blacklist': [title.strip() for title in title_blacklist.split(",") if title.strip()],
            'apply_once_at_company': apply_once_at_company,
            'job_applicants_threshold': {
                'min_applicants': min_applicants,
                'max_applicants': max_applicants
            },
            'llm_model_type': llm_model_type.lower(),
            'llm_model': llm_model,
        }

        secrets_data = {
            'llm_api_key': llm_api_key
        }

        personal_info = {
            'personal_information': {
                'name': name,
                'surname': surname,
                'email': email,
                'phone': phone,
                'linkedin': linkedin,
                'github': github
            }
        }

        data_folder = Path("data_folder")
        data_folder.mkdir(exist_ok=True)

        with open(data_folder / "config.yaml", "w") as file:
            yaml.dump(config_data, file)

        with open(data_folder / "secrets.yaml", "w") as file:
            yaml.dump(secrets_data, file)

        if plain_text_resume_file is not None:
            plain_text_resume_content = plain_text_resume_file.getvalue().decode("utf-8")
            with open(data_folder / "plain_text_resume.yaml", "w") as file:
                file.write(plain_text_resume_content)
        else:
            with open(data_folder / "plain_text_resume.yaml", "w") as file:
                yaml.dump(personal_info, file)

        if resume_file is not None:
            with open(data_folder / "resume.pdf", "wb") as f:
                f.write(resume_file.read())

        st.sidebar.success("Configuration saved successfully!")

    st.title("AIHawk Job Applications Tracker")

    tab1, tab2 = st.tabs(["Job Applications", "Job Monitoring"])

    with tab1:
        st.header("Applied Jobs")
        applied_jobs = load_application_data()
        if not applied_jobs.empty:
            st.dataframe(applied_jobs)
        else:
            st.write("No applications logged yet.")

    with tab2:
        st.header("Monitor Jobs")
        if st.button("Run AIHawk"):
            st.info("Running AIHawk...")
            result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.success("AIHawk has finished running.")
                st.text_area("Output", result.stdout)
            else:
                st.error("An error occurred while running AIHawk.")
                st.text_area("Error Output", result.stderr)

if __name__ == "__main__":
    main()
