import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import requests
import re
import unicodedata

#  Replace with your actual API keys
HUGGINGFACE_API_KEY = "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"
GOOGLE_API_KEY = "AIzaSyBI08d9uUrZCvirOQDM02hJYOn3BiRg7Bg"

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Use the latest Gemini model
MODEL_NAME = "gemini-1.5-pro"

# Function to remove AI-generated comments from the output
def clean_resume_text(resume_text):
    """Removes AI-generated comments and suggestions from the resume output."""
    resume_text = re.sub(r"\*Note:\*.*", "", resume_text, flags=re.DOTALL)
    resume_text = re.sub(r"This resume has been tailored.*", "", resume_text, flags=re.DOTALL)
    resume_text = re.sub(r"Further details regarding.*", "", resume_text, flags=re.DOTALL)
    resume_text = re.sub(r"Quantifiable achievements.*", "", resume_text, flags=re.DOTALL)
    return resume_text.strip()

# Function to generate AI-powered resume content using Hugging Face
def generate_resume_huggingface(prompt):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {"inputs": prompt}

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return clean_resume_text(data[0]['summary_text']) if isinstance(data, list) else "Error generating resume."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to generate AI-powered resume content using Google Generative AI
def generate_resume_gemini(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return clean_resume_text(response.text) if response else "Error: Could not generate resume content."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to clean text before saving to PDF
def clean_text(text):
    """Convert special characters to normal ASCII characters."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

# Function to generate a PDF resume
def save_resume_as_pdf(resume_text, filename="Generated_Resume.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, "Generated Resume", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, clean_text(resume_text))

    pdf.output(filename)
    return filename

# Streamlit UI
st.title("🚀 AI-Powered Resume Generator")

# Personal Information
name = st.text_input("Full Name")
age = st.number_input("Age", min_value=18, max_value=99)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
email = st.text_input("Email")
phone = st.text_input("Phone Number")
linkedin = st.text_input("LinkedIn URL")
github = st.text_input("GitHub URL")

# Education
graduation = st.text_input("Graduation Degree & Specialization")
grad_cgpa = st.text_input("Graduation CGPA")
post_graduation = st.text_input("Post-Graduation Degree & Specialization (if any)")
post_grad_cgpa = st.text_input("Post-Graduation CGPA (if any)")

# Internships
internship_title = st.text_input("Internship Title")
internship_company = st.text_input("Internship Company")
internship_location = st.text_input("Internship Location (City, State)")
internship_start = st.date_input("Internship Start Date")
internship_end = st.date_input("Internship End Date")
internship_description = st.text_area("Internship Responsibilities & Achievements")

# Work Experience
job_title = st.text_input("Professional Job Title")
company_name = st.text_input("Company Name")
work_start = st.date_input("Job Start Date")
work_end = st.date_input("Job End Date")
work_achievements = st.text_area("Job Responsibilities & Achievements")

# Projects
project_title = st.text_input("Project Title")
project_tech = st.text_input("Technologies/Languages Used")
project_description = st.text_area("Project Functionality & Key Features")

# Other Sections
skills = st.text_area("Skills (comma-separated)")
hobbies = st.text_area("Hobbies")
job_description = st.text_area("Paste the Job Description (For AI Customization)")

ai_choice = st.selectbox("Choose AI Model", ["Hugging Face", "Google Gemini"])

if st.button("Generate Resume"):
    if all([name, email, phone, linkedin, github, graduation, skills, job_description]):
        st.info("⏳ Generating resume using AI... Please wait.")

        prompt = f"""
        Generate a professional, ATS-optimized resume in plain text format.
        Do NOT include comments, suggestions, or additional notes.

        Candidate Information:
        Name: {name}, Age: {age}, Gender: {gender}
        Email: {email}, Phone: {phone}
        LinkedIn: {linkedin}, GitHub: {github}

        Education:
        Graduation: {graduation} (CGPA: {grad_cgpa})
        Post-Graduation: {post_graduation} (CGPA: {post_grad_cgpa})

        Internships:
        {internship_title} at {internship_company}, {internship_location}
        {internship_start} - {internship_end}
        {internship_description}

        Work Experience:
        {job_title} at {company_name}
        {work_start} - {work_end}
        {work_achievements}

        Projects:
        {project_title} - Technologies: {project_tech}
        {project_description}

        Skills:
        {skills}

        Hobbies:
        {hobbies}

        Customize for job description: {job_description}
        """

        resume_content = generate_resume_huggingface(prompt) if ai_choice == "Hugging Face" else generate_resume_gemini(prompt)

        st.subheader("Generated Resume Content:")
        st.text_area("", resume_content, height=300)

        pdf_filename = save_resume_as_pdf(resume_content)
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(label="📥 Download Resume as PDF", data=pdf_file, file_name="Generated_Resume.pdf", mime="application/pdf")

        st.success("✅ Resume Generated Successfully!")
    else:
        st.error("⚠️ Please fill in all fields before generating the resume.")
