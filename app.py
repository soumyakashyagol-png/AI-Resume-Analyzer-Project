from flask import Flask, render_template, request
import PyPDF2
import matplotlib.pyplot as plt
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# ----------------------------
# SKILL DATABASE
# ----------------------------
SKILL_DB = [
    "python", "java", "c++", "sql", "machine learning",
    "deep learning", "flask", "django", "html", "css",
    "javascript", "react", "aws", "azure", "git",
    "communication", "problem solving", "excel"
]

# ----------------------------
# PDF TEXT EXTRACTION
# ----------------------------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""

    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()

    return text.lower()

# ----------------------------
# SKILL EXTRACTION
# ----------------------------
def extract_skills(text):
    found = []
    for skill in SKILL_DB:
        if skill in text:
            found.append(skill)
    return list(set(found))

# ----------------------------
# ATS SCORE
# ----------------------------
def calculate_ats(resume_skills, jd_skills):
    if not jd_skills:
        return 0

    match = len(set(resume_skills) & set(jd_skills))
    return int((match / len(jd_skills)) * 100)

# ----------------------------
# SUGGESTIONS
# ----------------------------
def generate_suggestions(missing_skills):
    suggestions = []

    if len(missing_skills) > 0:
        for skill in missing_skills:
            suggestions.append(f"Improve or learn {skill} to increase ATS score.")

        suggestions.append("Add real-world projects using missing skills.")
        suggestions.append("Add GitHub or portfolio link.")
    else:
        suggestions.append("Excellent match 👍")
        suggestions.append("Add certifications to stand out.")
        suggestions.append("Improve system design knowledge.")

    return suggestions

# ----------------------------
# GRAPH
# ----------------------------
def generate_graph(matching, missing):
    labels = ['Matching Skills', 'Missing Skills']
    values = [len(matching), len(missing)]

    plt.figure()
    plt.bar(labels, values, color=['green', 'red'])
    plt.title("Skill Match Analysis")

    path = os.path.join("static", "graph.png")
    plt.savefig(path)
    plt.close()

    return path

# ----------------------------
# PDF REPORT GENERATION
# ----------------------------
def generate_pdf(score, required, matching, missing, suggestions):

    file_path = os.path.join("static", "ATS_Report.pdf")
    doc = SimpleDocTemplate(file_path)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"<b>ATS SCORE: {score}%</b>", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Required Skills: " + ", ".join(required), styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Matching Skills: " + ", ".join(matching), styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Missing Skills: " + ", ".join(missing), styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Suggestions:", styles["Heading2"]))
    for s in suggestions:
        content.append(Paragraph("- " + s, styles["Normal"]))

    doc.build(content)

    return file_path

# ----------------------------
# MAIN ROUTE
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    ats_score = 0
    required_skills = []
    matching_skills = []
    missing_skills = []
    suggestions = []
    graph = None
    pdf_file = None

    if request.method == "POST":

        file = request.files["resume"]
        job_description = request.form["job_description"].lower()

        resume_text = extract_text_from_pdf(file)

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(job_description)

        required_skills = jd_skills
        matching_skills = list(set(resume_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))

        ats_score = calculate_ats(resume_skills, jd_skills)

        suggestions = generate_suggestions(missing_skills)

        graph = generate_graph(matching_skills, missing_skills)

        pdf_file = generate_pdf(
            ats_score,
            required_skills,
            matching_skills,
            missing_skills,
            suggestions
        )

    return render_template(
        "index.html",
        score=ats_score,
        required_skills=required_skills,
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        suggestions=suggestions,
        graph=graph,
        pdf_file=pdf_file
    )

# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)