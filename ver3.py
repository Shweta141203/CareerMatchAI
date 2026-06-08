import streamlit as st
import PyPDF2
import re
import io
from collections import defaultdict
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1,h2,h3,h4 { font-family: 'Syne', sans-serif !important; }

.stApp { background-color: #0d0f14; color: #e8eaf0; }

.hero-title {
    font-family: 'Syne', sans-serif; font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(135deg, #7c6af7 0%, #5ec3f0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem; line-height: 1.1;
}
.hero-sub { color: #7a7e92; font-size: 1rem; margin-bottom: 2rem; }

.card {
    background: #161922; border: 1px solid #2a2d3a;
    border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
}
.card-title {
    font-family: 'Syne', sans-serif; font-size: 0.72rem;
    letter-spacing: 0.14em; text-transform: uppercase; color: #555b72;
    margin-bottom: 0.7rem;
}

/* ── SCORE NUMBER  ── */
.score-wrap {
    text-align: center; padding: 1.4rem 0 1rem 0;
}
.score-num {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1;
    display: block;
    /* colour set inline */
}
.score-pct {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 600;
    vertical-align: super;
    /* colour set inline */
}
.score-caption {
    font-size: 0.82rem; color: #7a7e92; margin-top: 0.3rem; letter-spacing: 0.06em;
}

.verdict-badge {
    display: inline-block; padding: 0.4rem 1.2rem;
    border-radius: 999px; font-family: 'Syne', sans-serif;
    font-size: 0.9rem; font-weight: 700; letter-spacing: 0.05em;
    margin-top: 0.7rem;
}
.badge-green  { background:#0f2e1e; color:#4ade80; border:1px solid #166534; }
.badge-yellow { background:#2b2000; color:#facc15; border:1px solid #854d0e; }
.badge-red    { background:#2d0a0a; color:#f87171; border:1px solid #7f1d1d; }

.skill-tag {
    display: inline-block; padding: 0.25rem 0.75rem;
    border-radius: 8px; font-size: 0.8rem; font-weight: 500; margin: 0.2rem;
}
.tag-matched { background:#0d2b1a; color:#4ade80; border:1px solid #166534; }
.tag-missing { background:#2d0a0a; color:#f87171; border:1px solid #7f1d1d; }
.tag-extra   { background:#1a1a2e; color:#818cf8; border:1px solid #3730a3; }

.progress-bg  { background:#1e2130; border-radius:999px; height:10px; margin:0.5rem 0 1rem 0; overflow:hidden; }
.progress-fill{ height:100%; border-radius:999px; background:linear-gradient(90deg,#7c6af7,#5ec3f0); }

.cat-header {
    font-family:'Syne',sans-serif; font-size:0.78rem; text-transform:uppercase;
    letter-spacing:0.1em; color:#7c6af7; margin:1rem 0 0.4rem 0;
    padding-bottom:0.3rem; border-bottom:1px solid #2a2d3a;
}

.analysis-block {
    background:#12141c; border-left:3px solid #7c6af7;
    border-radius:0 12px 12px 0; padding:0.9rem 1.1rem;
    margin:0.5rem 0; font-size:0.87rem; line-height:1.7; color:#c8cce0;
}

.roadmap-step {
    display:flex; gap:1rem; align-items:flex-start;
    background:#161922; border:1px solid #2a2d3a;
    border-radius:12px; padding:0.9rem 1.1rem; margin:0.5rem 0;
}
.step-num { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; color:#7c6af7; min-width:2rem; }
.step-body { font-size:0.86rem; line-height:1.65; color:#c8cce0; }
.step-title { font-weight:600; color:#e8eaf0; margin-bottom:0.25rem; }
.res-chip {
    display:inline-block; padding:0.18rem 0.55rem;
    background:#1a1a2e; border:1px solid #3730a3;
    border-radius:6px; font-size:0.74rem; color:#818cf8; margin:0.15rem;
}

div[data-testid="stFileUploader"]     { border:2px dashed #2a2d3a; border-radius:12px; background:#12141c; padding:0.5rem; }
div[data-testid="stTextArea"] textarea{ background:#12141c !important; border:1px solid #2a2d3a !important; border-radius:10px !important; color:#e8eaf0 !important; font-family:'DM Sans',sans-serif !important; }
div.stButton > button {
    background:linear-gradient(135deg,#7c6af7 0%,#5ec3f0 100%);
    color:white; border:none; border-radius:10px;
    font-family:'Syne',sans-serif; font-weight:700;
    letter-spacing:0.05em; padding:0.55rem 1.5rem;
}
div[data-testid="stCheckbox"] label { color:#aab0c8 !important; font-size:0.88rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SKILLS DATABASE
# ─────────────────────────────────────────────────────────────────────────────
SKILL_CATEGORIES = {
    "Programming Languages": [
        "python","java","c++","c#","javascript","typescript","ruby","go",
        "php","scala","kotlin","swift","rust","r","matlab",
    ],
    "Databases & SQL": [
        "sql","mysql","postgresql","oracle","mssql","sqlite","mongodb","cassandra",
        "redis","dynamodb","elasticsearch","azure sql","stored procedures","triggers",
        "views","indexing","query tuning","performance tuning","database optimization",
        "high availability","sharding","partitioning","database replication","backup and recovery",
    ],
    "Data Engineering / ETL": [
        "etl","data pipelines","data integration","data warehousing",
        "spark","hadoop","kafka","airflow","luigi","dbt","flink",
    ],
    "Data Analysis / Analytics": [
        "data analysis","data analytics","data visualization","tableau","power bi",
        "excel","pandas","numpy","matplotlib","seaborn","plotly","dashboard","reporting","looker",
    ],
    "Machine Learning / AI": [
        "machine learning","deep learning","nlp","computer vision","tensorflow","keras",
        "pytorch","scikit-learn","xgboost","lightgbm","reinforcement learning","clustering",
        "regression","classification","recommendation systems","feature engineering",
        "llm","generative ai","langchain","hugging face",
    ],
    "Web / Backend / Frontend": [
        "flask","django","fastapi","node.js","express","rest api","graphql","html","css",
        "react","angular","vue","next.js","microservices","backend development",
        "frontend development","full stack development","spring boot",
    ],
    "Cloud / DevOps": [
        "aws","azure","gcp","docker","kubernetes","terraform","ci/cd","jenkins","git",
        "linux","bash scripting","ansible","helm","serverless","monitoring","prometheus","grafana",
    ],
    "Security & QA": [
        "security","authentication","authorization","encryption","vulnerability assessment",
        "penetration testing","unit testing","integration testing","selenium","pytest","jest",
        "debugging","root cause analysis","troubleshooting",
    ],
    "Business / Domain": [
        "erp","crm","business intelligence","agile methodology","scrum","kanban",
        "project management","jira","stakeholder communication",
    ],
    "Soft Skills": [
        "collaboration","teamwork","problem solving","critical thinking",
        "communication skills","time management","documentation","presentation skills","leadership",
    ],
}

ALL_SKILLS = [s for cat in SKILL_CATEGORIES.values() for s in cat]

LEARNING_RESOURCES = {
    "python":           ["Python.org docs","CS50P (free)","Automate the Boring Stuff"],
    "sql":              ["SQLZoo (free)","Mode SQL Tutorial","LeetCode SQL"],
    "machine learning": ["fast.ai (free)","Andrew Ng Coursera","Hands-On ML book"],
    "deep learning":    ["fast.ai (free)","d2l.ai (free)","deeplearning.ai"],
    "aws":              ["AWS Free Tier + labs","A Cloud Guru","AWS Skill Builder (free)"],
    "azure":            ["Microsoft Learn (free)","AZ-900 cert path"],
    "docker":           ["Docker docs","Play-with-Docker (free)","TechWorld with Nana YT"],
    "kubernetes":       ["Kubernetes.io tutorials","KodeKloud","CKA cert prep"],
    "spark":            ["Databricks free courses","Learning Spark O'Reilly"],
    "kafka":            ["Confluent free courses","Kafka: The Definitive Guide (free)"],
    "react":            ["React docs (free)","Scrimba React","Full Stack Open (free)"],
    "typescript":       ["TypeScript handbook (free)","Total TypeScript"],
    "pandas":           ["Pandas docs (free)","Kaggle Python course (free)"],
    "tableau":          ["Tableau Public (free)","Tableau eLearning"],
    "power bi":         ["Microsoft Learn Power BI (free)","Guy in a Cube YT"],
    "tensorflow":       ["TensorFlow tutorials (free)","deeplearning.ai TF cert"],
    "pytorch":          ["PyTorch tutorials (free)","fast.ai"],
    "git":              ["Pro Git book (free)","Oh My Git! game (free)"],
    "linux":            ["Linux Journey (free)","The Linux Command Line (free)"],
    "postgresql":       ["PostgreSQL Tutorial (free)","pgExercises (free)"],
    "mongodb":          ["MongoDB University (free)","M001 course"],
    "django":           ["Django docs + DjangoGirls (free)","William Vincent books"],
    "flask":            ["Flask mega-tutorial (free)","Flask docs"],
    "fastapi":          ["FastAPI docs (free)","TestDriven.io"],
    "nlp":              ["HuggingFace NLP course (free)","Speech & Language Processing"],
    "dbt":              ["dbt Learn (free)","dbt docs"],
    "airflow":          ["Airflow docs","Marc Lamberti YT (free)"],
    "scrum":            ["Scrum.org free resources","PSM I certification"],
    "agile methodology":["Atlassian Agile Coach (free)","Scrum Alliance"],
    "java":             ["Java docs (free)","MOOC.fi Java (free)"],
    "c++":              ["learncpp.com (free)","C++ Primer book"],
}
DEFAULT_RESOURCES = ["Search Coursera / Udemy","YouTube tutorials","Official documentation"] 

SKILL_PRIORITY = {
    "python":9,"sql":9,"machine learning":9,"deep learning":9,"aws":8,"docker":8,
    "kubernetes":8,"spark":8,"kafka":7,"react":7,"node.js":7,"typescript":7,"java":8,
    "c++":7,"postgresql":7,"mongodb":6,"tensorflow":8,"pytorch":8,"git":9,"linux":8,
    "agile methodology":6,"scrum":6,"data analysis":7,"data visualization":7,
    "tableau":6,"power bi":6,"etl":7,"data pipelines":7,
}


# ─────────────────────────────────────────────────────────────────────────────
# CORE UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def extract_text_from_pdf(f) -> str:
    reader = PyPDF2.PdfReader(f)
    return " ".join(p.extract_text() or "" for p in reader.pages)

def clean_text(t: str) -> str:
    t = t.lower()
    t = re.sub(r'[^a-z0-9+#\.\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def extract_skills(text: str) -> list:
    return [s for s in ALL_SKILLS if re.search(r'\b' + re.escape(s) + r'\b', text)]

def categorise(skills: list) -> dict:
    result = defaultdict(list)
    for cat, cat_skills in SKILL_CATEGORIES.items():
        for s in skills:
            if s in cat_skills:
                result[cat].append(s)
    return dict(result)

def score_color(score: float) -> str:
    return "#4ade80" if score >= 75 else "#facc15" if score >= 40 else "#f87171"

def get_verdict(score: float):
    if score >= 75: return "Strong Fit", "badge-green"
    if score >= 40: return "Needs Improvement", "badge-yellow"
    return "Not a Fit", "badge-red"

def prioritise_missing(missing: list) -> list:
    return sorted(missing, key=lambda s: SKILL_PRIORITY.get(s, 5), reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def infer_role(jd: str) -> str:
    t = jd.lower()
    if any(w in t for w in ["machine learning","deep learning","pytorch","tensorflow","ml engineer"]): return "ML / AI Engineer"
    if any(w in t for w in ["data engineer","etl","spark","kafka","airflow","data pipeline"]):         return "Data Engineer"
    if any(w in t for w in ["data analyst","tableau","power bi","reporting","dashboards"]):            return "Data Analyst"
    if any(w in t for w in ["devops","kubernetes","docker","ci/cd","terraform"]):                      return "DevOps / Cloud Engineer"
    if any(w in t for w in ["full stack","fullstack"]):                                                return "Full Stack Developer"
    if any(w in t for w in ["backend","api","microservices","django","flask","fastapi","spring"]):     return "Backend Developer"
    if any(w in t for w in ["frontend","react","angular","vue","css"]):                                return "Frontend Developer"
    if any(w in t for w in ["database administrator","dba","oracle","postgresql"]):                    return "Database Administrator"
    if any(w in t for w in ["security","penetration","vulnerability"]):                                return "Security Engineer"
    return "Software / Tech Professional"

def generate_strengths(matched, resume_cats):
    out = []
    if len(matched) >= 10:
        out.append(f"Strong overall skill coverage — {len(matched)} matched skills show broad technical depth.")
    elif len(matched) >= 5:
        out.append(f"Solid foundational match with {len(matched)} relevant skills already present.")
    dominant = max(resume_cats, key=lambda c: len(resume_cats[c]), default=None)
    if dominant:
        out.append(f"Strongest area: **{dominant}** — deep coverage here ({len(resume_cats[dominant])} skills).")
    high_value = [s for s in matched if SKILL_PRIORITY.get(s,0) >= 8]
    if high_value:
        out.append(f"High-demand skills already on your resume: {', '.join(f'`{s}`' for s in high_value[:4])}.")
    if not out:
        out.append("Your resume shows some relevant experience — build on it with the missing skills below.")
    return out

def generate_gaps(missing, score, role):
    out = []
    pm = prioritise_missing(missing)
    if score < 40:   out.append(f"Significant skill gap for a **{role}** role — {len(missing)} required skills absent.")
    elif score < 75: out.append(f"Moderately aligned for **{role}** but {len(missing)} key skills are missing.")
    if pm: out.append(f"Most critical missing: {', '.join(f'`{s}`' for s in pm[:4])}.")
    cats = categorise(missing)
    if len(cats) >= 3:
        out.append(f"Gaps span {len(cats)} categories: {', '.join(list(cats.keys())[:3])} — consider structured upskilling.")
    elif cats:
        for cat in cats:
            out.append(f"**{cat}** gap: missing {', '.join(f'`{s}`' for s in cats[cat][:3])}.")
    return out

def generate_roadmap(missing):
    pm = prioritise_missing(missing)
    if not pm:
        return [{"title":"Polish your resume","detail":"You meet all requirements. Quantify achievements with numbers and tailor your summary to this JD.","timeline":"This week","resources":[]}]
    steps = []
    steps.append({"title":f"Learn `{pm[0]}` first","detail":f"Highest-priority missing skill for this role. 2–4 weeks of focused practice makes it resume-worthy.","timeline":"Week 1–4","resources":LEARNING_RESOURCES.get(pm[0], DEFAULT_RESOURCES)})
    if len(pm) > 1:
        nxt = pm[1:4]
        steps.append({"title":f"Add {', '.join(f'`{s}`' for s in nxt)} to your toolkit","detail":"Work through these in parallel — many have overlapping concepts. Build one small project combining them.","timeline":"Week 4–10","resources":LEARNING_RESOURCES.get(nxt[0], DEFAULT_RESOURCES)})
    steps.append({"title":"Build a portfolio project","detail":"Create a project using the skills above. Push it to GitHub. A working demo beats any certificate.","timeline":"Week 8–12","resources":["GitHub (free)","Streamlit Cloud (free deploy)","Kaggle datasets (free)"]})
    steps.append({"title":"Update resume & apply","detail":"Add a Projects section. Use exact JD keyword phrases. Quantify everything — accuracy %, time saved, dataset size.","timeline":"Week 12","resources":["Jobscan (keyword check)","LinkedIn resume review","Resume.io"]})
    return steps

def generate_tips(matched, missing, resume_text, jd_text):
    tips = []
    res_lower = resume_text.lower(); jd_lower = jd_text.lower()
    if len(resume_text.split()) < 300:
        tips.append("Resume seems short. Aim for 400–700 words — expand project descriptions with impact metrics.")
    if not any(w in res_lower for w in ["improved","reduced","increased","achieved","built","designed","led","launched"]):
        tips.append("Add action verbs + metrics: 'Reduced query time by 40%' beats 'Worked on database optimization'.")
    explicit = [s for s in missing if re.search(r'\b'+re.escape(s)+r'\b', jd_lower)]
    if explicit:
        tips.append(f"JD explicitly mentions skills you're missing: {', '.join(f'`{s}`' for s in explicit[:4])}. Add any even partial exposure.")
    if "github" not in res_lower and "portfolio" not in res_lower:
        tips.append("Add a GitHub link — 2–3 pinned projects significantly boost recruiter credibility.")
    if matched and not any(m in res_lower[:500] for m in matched[:3]):
        tips.append("Put your strongest matched skills near the top of your resume for faster ATS scanning.")
    if not tips:
        tips.append("Resume is well-structured. Tailor the summary paragraph to mirror language from this JD.")
    return tips


# ─────────────────────────────────────────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_skill_tags(skills, cls):
    if not skills:
        st.markdown("<span style='color:#555b72;font-size:0.85rem;'>None found</span>", unsafe_allow_html=True)
        return
    st.markdown("".join(f'<span class="skill-tag {cls}">{s}</span>' for s in sorted(skills)), unsafe_allow_html=True)

def render_cat_skills(skills, cls):
    cats = categorise(skills)
    if not cats:
        st.markdown("<span style='color:#555b72;font-size:0.85rem;'>None found</span>", unsafe_allow_html=True)
        return
    for cat, cs in cats.items():
        st.markdown(f'<div class="cat-header">{cat}</div>', unsafe_allow_html=True)
        render_skill_tags(cs, cls)


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def strip_md(text: str) -> str:
    """Remove markdown bold/italic/backtick for PDF plain text."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    return text

def generate_pdf(score, verdict, role, matched, missing, extra,
                 jd_skills, resume_skills, strengths, gaps, tips,
                 roadmap, include_roadmap: bool) -> bytes:

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=15*mm,  bottomMargin=15*mm,
    )

    # colours
    BG      = colors.HexColor("#0d0f14")
    CARD    = colors.HexColor("#161922")
    BORDER  = colors.HexColor("#2a2d3a")
    PURPLE  = colors.HexColor("#7c6af7")
    CYAN    = colors.HexColor("#5ec3f0")
    GREEN   = colors.HexColor("#4ade80")
    RED     = colors.HexColor("#f87171")
    INDIGO  = colors.HexColor("#818cf8")
    YELLOW  = colors.HexColor("#facc15")
    MUTED   = colors.HexColor("#7a7e92")
    FG      = colors.HexColor("#e8eaf0")
    FG2     = colors.HexColor("#c8cce0")

    vc = GREEN if score >= 75 else YELLOW if score >= 40 else RED

    def ps(name, **kw):
        defaults = dict(fontName="Helvetica", fontSize=9, textColor=FG2,
                        leading=14, spaceAfter=2, backColor=None)
        defaults.update(kw)
        return ParagraphStyle(name, **defaults)

    S = {
        "title":    ps("title",   fontSize=22, textColor=FG,    fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2),
        "subtitle": ps("sub",     fontSize=9,  textColor=MUTED, alignment=TA_CENTER, spaceAfter=6),
        "h2":       ps("h2",      fontSize=12, textColor=FG,    fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3),
        "h3":       ps("h3",      fontSize=9,  textColor=PURPLE,fontName="Helvetica-Bold", spaceAfter=2),
        "body":     ps("body",    fontSize=9,  textColor=FG2),
        "muted":    ps("muted",   fontSize=8,  textColor=MUTED),
        "bullet":   ps("bullet",  fontSize=9,  textColor=FG2,   leftIndent=10, leading=14),
        "tag_g":    ps("tag_g",   fontSize=8,  textColor=GREEN, fontName="Helvetica-Bold"),
        "tag_r":    ps("tag_r",   fontSize=8,  textColor=RED,   fontName="Helvetica-Bold"),
        "tag_i":    ps("tag_i",   fontSize=8,  textColor=INDIGO,fontName="Helvetica-Bold"),
        "score":    ps("score",   fontSize=52, textColor=vc,    fontName="Helvetica-Bold", alignment=TA_CENTER, leading=60),
        "verdict":  ps("verdict", fontSize=14, textColor=vc,    fontName="Helvetica-Bold", alignment=TA_CENTER),
        "center":   ps("center",  fontSize=9,  textColor=MUTED, alignment=TA_CENTER),
    }

    def hr(c=BORDER):
        return HRFlowable(width="100%", thickness=1, color=c, spaceAfter=6, spaceBefore=4)

    def card_wrap(rows, col_widths=None):
        t = Table(rows, colWidths=col_widths or [doc.width])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), CARD),
            ("BOX",           (0,0),(-1,-1), 1, BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
            ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ]))
        return t

    story = []

    # HEADER
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Smart Resume Analyzer", S["title"]))
    story.append(Paragraph("Automated Skill Match Report", S["subtitle"]))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %b %Y, %H:%M')}", S["subtitle"]))
    story.append(hr(PURPLE))

    # SCORE CARD
    readiness = "85-100% Ready" if score>=75 else "50-80% Ready" if score>=40 else "Below 50% Ready"
    shortlist  = "High"         if score>=75 else "Moderate"     if score>=40 else "Low"
    story.append(card_wrap([
        [Paragraph(f"{score}%", S["score"])],
        [Paragraph(verdict,     S["verdict"])],
        [Paragraph(f"Detected Role: {role}", S["center"])],
        [Paragraph(f"Readiness: {readiness}   |   Shortlist Chance: {shortlist}", S["center"])],
    ]))
    story.append(Spacer(1, 4*mm))

    # STATS
    def hex_str(c): return c.hexval()[2:]
    stats = Table([[
        Paragraph(f"<b><font color='#{hex_str(GREEN)}'>Matched</font></b><br/>{len(matched)}", S["body"]),
        Paragraph(f"<b><font color='#{hex_str(RED)}'>Missing</font></b><br/>{len(missing)}", S["body"]),
        Paragraph(f"<b><font color='#{hex_str(INDIGO)}'>Extra</font></b><br/>{len(extra)}", S["body"]),
        Paragraph(f"<b>JD Skills</b><br/>{len(jd_skills)}", S["body"]),
        Paragraph(f"<b>Resume Skills</b><br/>{len(resume_skills)}", S["body"]),
    ]], colWidths=[doc.width/5]*5)
    stats.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), CARD),
        ("BOX",           (0,0),(-1,-1), 1, BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, BORDER),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
    ]))
    story.append(stats)
    story.append(Spacer(1, 5*mm))

    # SKILLS
    def skill_section(heading, skills, style_key):
        story.append(Paragraph(heading, S["h2"]))
        if not skills:
            story.append(Paragraph("None found", S["muted"]))
        else:
            for cat, cs in categorise(skills).items():
                story.append(Paragraph(cat, S["h3"]))
                story.append(Paragraph("   ".join(cs), S[style_key]))
        story.append(Spacer(1, 2*mm))

    skill_section("Matched Skills", matched, "tag_g")
    story.append(hr())
    skill_section("Missing Skills", missing, "tag_r")
    story.append(hr())
    skill_section("Additional Skills on Resume", extra, "tag_i")
    story.append(hr())

    # ANALYSIS
    story.append(Paragraph("Your Strengths", S["h2"]))
    for s in strengths:
        story.append(Paragraph("• " + strip_md(s), S["bullet"]))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("Critical Gaps", S["h2"]))
    for g in (gaps or ["No critical gaps — you are well aligned!"]):
        story.append(Paragraph("• " + strip_md(g), S["bullet"]))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("Resume Tips", S["h2"]))
    for tip in tips:
        story.append(Paragraph("• " + strip_md(tip), S["bullet"]))
    story.append(Spacer(1, 2*mm))
    story.append(hr())

    # ROADMAP (conditional)
    if include_roadmap:
        story.append(Paragraph("30-Day Improvement Roadmap", S["h2"]))
        for i, step in enumerate(roadmap, 1):
            t_clean = strip_md(step["title"])
            d_clean = strip_md(step["detail"])
            res_str = "  |  ".join(step["resources"][:3])
            row = Table([
                [Paragraph(f"<b><font color='#{hex_str(PURPLE)}'>{i}.</font>  {t_clean}</b>",
                           S["body"]),
                 Paragraph(f"<font color='#{hex_str(MUTED)}'>{step['timeline']}</font>", S["muted"])],
                [Paragraph(d_clean, S["body"]), ""],
                [Paragraph(f"Resources: {res_str}", S["muted"]), ""],
            ], colWidths=[doc.width*0.75, doc.width*0.25])
            row.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), CARD),
                ("BOX",           (0,0),(-1,-1), 1, BORDER),
                ("SPAN",          (0,1),(1,1)),
                ("SPAN",          (0,2),(1,2)),
                ("LEFTPADDING",   (0,0),(-1,-1), 12),
                ("RIGHTPADDING",  (0,0),(-1,-1), 12),
                ("TOPPADDING",    (0,0),(-1,-1), 7),
                ("BOTTOMPADDING", (0,0),(-1,-1), 7),
                ("LINEBELOW",     (0,0),(-1,0), 0.5, BORDER),
                ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ]))
            story.append(KeepTogether([row, Spacer(1, 2*mm)]))
        story.append(hr())

    # TOP SKILLS TO LEARN
    if missing:
        story.append(Paragraph("Top Skills to Learn (with Resources)", S["h2"]))
        pm = prioritise_missing(missing)
        rows = []
        row = []
        for i, skill in enumerate(pm[:6]):
            res = LEARNING_RESOURCES.get(skill, DEFAULT_RESOURCES)
            res_lines = "<br/>".join(f"- {r}" for r in res[:3])
            row.append(Paragraph(
                f"<b><font color='#{hex_str(RED)}'>{skill}</font></b><br/>"
                f"<font color='#{hex_str(INDIGO)}'>{res_lines}</font>",
                S["body"]
            ))
            if len(row) == 3:
                rows.append(row); row = []
        if row:
            while len(row) < 3: row.append(Paragraph("", S["body"]))
            rows.append(row)
        tbl = Table(rows, colWidths=[doc.width/3]*3)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), CARD),
            ("BOX",           (0,0),(-1,-1), 1, BORDER),
            ("INNERGRID",     (0,0),(-1,-1), 0.5, BORDER),
            ("TOPPADDING",    (0,0),(-1,-1), 8),
            ("BOTTOMPADDING", (0,0),(-1,-1), 8),
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("RIGHTPADDING",  (0,0),(-1,-1), 10),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        story.append(tbl)

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("100% offline  ·  No data sent anywhere  ·  Smart Resume Analyzer", S["muted"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────────────────────────────────────
# APP UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🚀 Smart Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">100% offline · No API key needed · Instant match score + smart career analysis</div>', unsafe_allow_html=True)

col_l, col_r = st.columns([1,1], gap="large")
with col_l:
    st.markdown('<div class="card-title">📄 Resume (PDF)</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
with col_r:
    st.markdown('<div class="card-title">📋 Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area("", height=185, placeholder="Paste the full job description here…", label_visibility="collapsed")

analyze_btn = st.button("⚡ Analyze Resume", use_container_width=True)

if not (uploaded_file and jd_text.strip()):
    st.markdown('<div style="color:#555b72;text-align:center;padding:2rem 0;font-size:0.9rem;">Upload a resume PDF and paste a job description to get started.</div>', unsafe_allow_html=True)
    st.stop()

if not (analyze_btn or st.session_state.get("analyzed")):
    st.stop()

st.session_state["analyzed"] = True

# ── PROCESS ──────────────────────────────────────────────────────────────────
with st.spinner("Analyzing…"):
    resume_raw    = extract_text_from_pdf(uploaded_file)
    resume_clean  = clean_text(resume_raw)
    jd_clean      = clean_text(jd_text)
    resume_skills = extract_skills(resume_clean)
    jd_skills     = extract_skills(jd_clean)
    matched       = sorted(set(resume_skills) & set(jd_skills))
    missing       = sorted(set(jd_skills) - set(resume_skills))
    extra         = sorted(set(resume_skills) - set(jd_skills))
    score         = round(len(matched)/len(jd_skills)*100, 1) if jd_skills else 0.0
    verdict, badge_cls = get_verdict(score)
    role          = infer_role(jd_text)
    vc            = score_color(score)
    resume_cats   = categorise(resume_skills)
    strengths     = generate_strengths(matched, resume_cats)
    gaps          = generate_gaps(missing, score, role)
    roadmap       = generate_roadmap(missing)
    tips          = generate_tips(matched, missing, resume_raw, jd_text)

# ── SCORE ROW ─────────────────────────────────────────────────────────────────
st.markdown("---")
sc1, sc2, sc3 = st.columns([1, 1.8, 1], gap="large")

with sc1:
    st.markdown(f"""
    <div class="card">
      <div class="card-title">Match Score</div>
      <div class="score-wrap">
        <span class="score-num" style="color:{vc};">{int(score)}</span>
        <span class="score-pct" style="color:{vc};">%</span>
        <div class="score-caption">of JD skills matched</div>
        <div class="verdict-badge {badge_cls}">{verdict}</div>
      </div>
    </div>""", unsafe_allow_html=True)

with sc2:
    st.markdown(f"""
    <div class="card">
      <div class="card-title">Skill Coverage</div>
      <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#aab0c8;margin-bottom:0.25rem;">
        <span>✅ Matched: <b style="color:#4ade80">{len(matched)}</b></span>
        <span>❌ Missing: <b style="color:#f87171">{len(missing)}</b></span>
        <span>➕ Extra: <b style="color:#818cf8">{len(extra)}</b></span>
      </div>
      <div class="progress-bg"><div class="progress-fill" style="width:{int(score)}%;"></div></div>
      <div style="font-size:0.84rem;color:#7a7e92;">
        Detected role: <b style="color:#c8cce0;">{role}</b>
      </div>
    </div>""", unsafe_allow_html=True)

with sc3:
    readiness = "85–100% Ready" if score>=75 else "50–80% Ready" if score>=40 else "Below 50% Ready"
    shortlist  = "High"         if score>=75 else "Moderate"     if score>=40 else "Low"
    st.markdown(f"""
    <div class="card">
      <div class="card-title">Quick Stats</div>
      <div style="font-size:0.84rem;line-height:2.2;color:#aab0c8;">
        <div>📈 Readiness: <b style="color:{vc}">{readiness}</b></div>
        <div>🎯 Shortlist: <b style="color:{vc}">{shortlist}</b></div>
        <div>📚 JD Skills: <b>{len(jd_skills)}</b></div>
        <div>📄 Resume: <b>{len(resume_skills)}</b></div>
      </div>
    </div>""", unsafe_allow_html=True)

# ── SKILL BREAKDOWN ───────────────────────────────────────────────────────────
st.markdown("### 🔍 Skill Breakdown")
tab1, tab2, tab3 = st.tabs(["✅ Matched", "❌ Missing", "➕ Additional"])
with tab1: render_cat_skills(matched, "tag-matched")
with tab2:
    if missing: render_cat_skills(missing, "tag-missing")
    else: st.success("🎉 Your resume covers all skills in the JD!")
with tab3:
    st.markdown("<span style='color:#555b72;font-size:0.82rem;'>Skills on your resume not explicitly required by this JD.</span>", unsafe_allow_html=True)
    render_cat_skills(extra, "tag-extra")

# ── DEEP ANALYSIS ─────────────────────────────────────────────────────────────
st.markdown("### 🧠 Deep Analysis")
a1, a2 = st.columns(2, gap="large")

with a1:
    st.markdown("#### 💪 Strengths")
    for s in strengths:
        st.markdown(f'<div class="analysis-block">✦ {s}</div>', unsafe_allow_html=True)
    st.markdown("#### 📝 Resume Tips")
    for t in tips:
        st.markdown(f'<div class="analysis-block">💡 {t}</div>', unsafe_allow_html=True)

with a2:
    st.markdown("#### ⚠️ Critical Gaps")
    if gaps:
        for g in gaps:
            st.markdown(f'<div class="analysis-block">⚡ {g}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="analysis-block">✅ No critical gaps — you are well aligned!</div>', unsafe_allow_html=True)

# ── ROADMAP (collapsible) ─────────────────────────────────────────────────────
st.markdown("### 🗺️ Improvement Roadmap")
show_roadmap = st.toggle("Show 30-Day Roadmap", value=False)

if show_roadmap:
    for i, step in enumerate(roadmap, 1):
        res_html = "".join(f'<span class="res-chip">📌 {r}</span>' for r in step["resources"])
        st.markdown(f"""
        <div class="roadmap-step">
          <div class="step-num">{i}</div>
          <div class="step-body">
            <div class="step-title">{step["title"]} <span style="color:#555b72;font-size:0.73rem;font-weight:400;">— {step["timeline"]}</span></div>
            {step["detail"]}
            <div style="margin-top:0.4rem;">{res_html}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# ── TOP MISSING SKILLS ────────────────────────────────────────────────────────
if missing:
    st.markdown("### 📚 Top Skills to Learn")
    pm = prioritise_missing(missing)
    cols = st.columns(min(3, len(pm[:6])))
    for i, skill in enumerate(pm[:6]):
        with cols[i % 3]:
            res = LEARNING_RESOURCES.get(skill, DEFAULT_RESOURCES)
            res_html = "".join(f'<div style="font-size:0.77rem;color:#818cf8;padding:0.14rem 0;">📌 {r}</div>' for r in res[:3])
            st.markdown(f"""
            <div class="card">
              <div style="font-family:Syne,sans-serif;font-weight:700;color:#f87171;margin-bottom:0.5rem;">{skill}</div>
              {res_html}
            </div>""", unsafe_allow_html=True)

# ── PDF REPORT ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📥 Download PDF Report")

st.markdown("<div style='color:#7a7e92;font-size:0.85rem;margin-bottom:0.8rem;'>Choose what to include in the PDF:</div>", unsafe_allow_html=True)

inc_roadmap = st.checkbox("📍 Include 30-Day Improvement Roadmap in PDF", value=True)

if st.button("🖨️ Generate & Download PDF", use_container_width=True):
    with st.spinner("Building PDF…"):
        pdf_bytes = generate_pdf(
            score, verdict, role,
            matched, missing, extra,
            jd_skills, resume_skills,
            strengths, gaps, tips,
            roadmap, inc_roadmap,
        )
    st.download_button(
        label="⬇️ Click to Download PDF",
        data=pdf_bytes,
        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.markdown('<div style="text-align:center;color:#2a2d3a;font-size:0.75rem;padding:1.5rem 0;">100% offline · No data sent anywhere · Smart Resume Analyzer</div>', unsafe_allow_html=True)