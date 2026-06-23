import logging
logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)

import streamlit as st
import pandas as pd
import re
import io
import os
import tempfile
import subprocess
from docx import Document
from pypdf import PdfReader
import plotly.express as px
import plotly.graph_objects as go

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, cohen_kappa_score

st.set_page_config(page_title="Advanced Bloom Analyzer", layout="wide")

BLOOM_LEVELS = ["Remember & Understand", "Apply", "Analyze", "Evaluate", "Create"]

BLOOM_ORDER = {
    "Remember & Understand": 1,
    "Apply": 2,
    "Analyze": 3,
    "Evaluate": 4,
    "Create": 5
}

NUMERIC_BLOOM_MAP = {
    "1": "Remember & Understand",
    "2": "Apply",
    "3": "Analyze",
    "4": "Evaluate",
    "5": "Create",
    "6": "Create"
}

TARGET_DISTRIBUTION = {
    "Remember & Understand": 30,
    "Apply": 25,
    "Analyze": 25,
    "Evaluate": 10,
    "Create": 10
}

BLOOM_VERBS = {
    "Remember & Understand": [
        "define", "list", "name", "identify", "recall", "state", "recognize",
        "label", "select", "match", "enumerate", "describe", "summarize",
        "outline", "interpret", "illustrate", "explain", "classify",
        "categorize", "discuss", "what", "which", "who", "when", "where"
    ],
    "Apply": [
        "apply", "solve", "calculate", "compute", "demonstrate", "implement",
        "use", "show", "prepare", "execute", "perform", "determine",
        "estimate", "predict", "simulate", "convert", "derive", "obtain",
        "find", "draw", "sketch", "plot", "evaluate expression"
    ],
    "Analyze": [
        "analyze", "analyse", "compare", "contrast", "differentiate",
        "distinguish", "examine", "infer", "inspect", "investigate",
        "break down", "decompose", "correlate", "diagnose", "interpret results"
    ],
    "Evaluate": [
        "evaluate", "justify", "assess", "criticize", "critique", "validate",
        "defend", "recommend", "review", "argue", "judge", "verify",
        "prioritize", "rank", "measure", "appraise", "prove", "disprove"
    ],
    "Create": [
        "design", "develop", "construct", "create", "formulate", "propose",
        "build", "generate", "compose", "invent", "plan", "produce",
        "architect", "synthesize", "integrate", "write algorithm",
        "develop framework", "construct model", "design architecture"
    ]
}

MATH_KEYWORDS = [
    "calculate", "compute", "solve", "find", "determine", "derive", "integrate",
    "differentiate", "evaluate", "simplify", "obtain", "prove", "verify",
    "matrix", "vector", "equation", "probability", "statistics", "mean",
    "median", "variance", "standard deviation", "limit", "derivative",
    "integral", "laplace", "fourier", "graph", "tree", "algorithm",
    "complexity", "big o", "polynomial", "logarithm", "eigenvalue"
]

DISCIPLINES = [
    "CSE", "CSE-AIML", "CSE-CS", "CSE-DS", "IT", "ECE", "EEE",
    "MECH", "CIVIL", "CHEMICAL", "BIOTECH", "MATHS", "PHYSICS",
    "CHEMISTRY", "MBA", "MCA"
]

def clean_text(x):
    x = "" if x is None else str(x)
    x = x.replace("\xa0", " ").replace("\n", " ").replace("\t", " ")
    return re.sub(r"\s+", " ", x).strip()

def normalize_bloom(value):
    value = clean_text(value)
    if value in NUMERIC_BLOOM_MAP:
        return NUMERIC_BLOOM_MAP[value]
    v = value.lower()
    if any(k in v for k in ["remember", "understand", "k1", "l1", "bt1", "b1"]):
        return "Remember & Understand"
    if any(k in v for k in ["apply", "k2", "l2", "bt2", "b2"]):
        return "Apply"
    if any(k in v for k in ["analyze", "analyse", "k3", "l3", "bt3", "b3"]):
        return "Analyze"
    if any(k in v for k in ["evaluate", "k4", "l4", "bt4", "b4"]):
        return "Evaluate"
    if any(k in v for k in ["create", "k5", "l5", "bt5", "b5", "k6", "l6"]):
        return "Create"
    return "Not Provided"

def is_number(x):
    return bool(re.fullmatch(r"\d+(\.\d+)?", clean_text(x)))

def safe_int(x, default=0):
    try:
        return int(float(clean_text(x)))
    except Exception:
        return default

def remove_mcq_options(question):
    question = clean_text(question)
    question = re.split(r"\bA\.\s+", question)[0]
    question = re.split(r"\ba\.\s+", question)[0]
    question = re.split(r"\b\(A\)\s+", question)[0]
    return clean_text(question)

def is_or_row(row):
    parts = [clean_text(x).lower().replace("|", "") for x in row if clean_text(x)]
    return (not parts) or all(x == "or" for x in parts)

def is_valid_sno(sno):
    sno = clean_text(sno)
    return bool(re.fullmatch(r"\d+|\d+\([a-zA-Z]\)|\([a-zA-Z]\)|[a-zA-Z]\)|[a-zA-Z]", sno))

def normalize_sno_value(sno, last_main_no):
    sno = clean_text(sno)
    if re.fullmatch(r"\d+", sno):
        return sno
    if re.fullmatch(r"\d+\([a-zA-Z]\)", sno):
        return sno
    if re.fullmatch(r"\([a-zA-Z]\)", sno) and last_main_no:
        return f"{last_main_no}{sno}"
    if re.fullmatch(r"[a-zA-Z]\)", sno) and last_main_no:
        return f"{last_main_no}({sno[0]})"
    if re.fullmatch(r"[a-zA-Z]", sno) and last_main_no:
        return f"{last_main_no}({sno})"
    return sno

def convert_doc_to_docx(file_bytes):
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = os.path.join(tmpdir, "input.doc")
        with open(doc_path, "wb") as f:
            f.write(file_bytes)
        try:
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "docx", "--outdir", tmpdir, doc_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            docx_path = os.path.join(tmpdir, "input.docx")
            if os.path.exists(docx_path):
                return open(docx_path, "rb").read()
        except Exception:
            return None
    return None

def extract_docx_rows(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    rows = []
    for table in doc.tables:
        for row in table.rows:
            rows.append([clean_text(cell.text) for cell in row.cells])
    return rows

def is_header_row(row):
    joined = " ".join([clean_text(x).lower() for x in row])
    return (
        ("s.no" in joined or "s no" in joined or "sno" in joined)
        and "question" in joined
        and ("course outcome" in joined or "co" in joined)
        and "bloom" in joined
        and "marks" in joined
    )

def extract_questions_from_docx_rows(rows):
    extracted = []
    inside_question_table = False
    last_main_no = None

    for row in rows:
        row = [clean_text(x) for x in row]
        if is_header_row(row):
            inside_question_table = True
            continue
        if not inside_question_table or is_or_row(row) or len(row) < 2:
            continue

        sno = clean_text(row[0])
        question = clean_text(row[1])

        if not is_valid_sno(sno) or not question or question.lower() in ["question", "or"]:
            continue

        if re.match(r"^\d+", sno):
            last_main_no = re.match(r"^\d+", sno).group()

        sno = normalize_sno_value(sno, last_main_no)
        numeric_cells = [clean_text(x) for x in row if is_number(x)]

        if len(numeric_cells) >= 3:
            co = numeric_cells[-3]
            bloom = numeric_cells[-2]
            marks = numeric_cells[-1]
        else:
            continue

        extracted.append({
            "S.No.": sno,
            "Question": remove_mcq_options(question),
            "Full Question with Options": question,
            "Course Outcome": co,
            "Bloom’s Taxonomy Level": bloom,
            "Bloom Level in Paper": normalize_bloom(bloom),
            "Marks": marks
        })

    df = pd.DataFrame(extracted)
    if df.empty:
        return df

    df = df[df["Question"].str.lower() != "or"]
    df = df[df["S.No."].str.lower() != "or"]
    df = df.drop_duplicates(subset=["S.No.", "Question"])
    return df.reset_index(drop=True)

def extract_questions_from_doc_or_docx(file_bytes, file_name):
    if file_name.lower().endswith(".doc"):
        converted = convert_doc_to_docx(file_bytes)
        if converted is None:
            return pd.DataFrame()
        file_bytes = converted
    return extract_questions_from_docx_rows(extract_docx_rows(file_bytes))

def extract_text_from_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def extract_questions_from_plain_text(text):
    lines = [clean_text(x) for x in text.splitlines() if clean_text(x)]
    rows = []
    header_seen = False
    last_main_no = None
    i = 0

    while i < len(lines):
        line = lines[i].lower()

        if (
            ("s.no" in line or "s no" in line or "sno" in line)
            and "question" in line
            and ("course outcome" in line or "co" in line)
            and "bloom" in line
            and "marks" in line
        ):
            header_seen = True
            i += 1
            continue

        if not header_seen:
            i += 1
            continue

        if lines[i].lower() == "or":
            i += 1
            continue

        if is_valid_sno(lines[i]):
            sno_raw = lines[i]
            if re.match(r"^\d+", sno_raw):
                last_main_no = re.match(r"^\d+", sno_raw).group()

            sno = normalize_sno_value(sno_raw, last_main_no)
            question_parts = []
            i += 1

            while i < len(lines):
                current = lines[i]

                if current.lower() == "or":
                    i += 1
                    break

                if is_valid_sno(current) and question_parts:
                    break

                if is_number(current) and i + 2 < len(lines) and is_number(lines[i + 1]) and is_number(lines[i + 2]):
                    co = current
                    bloom = lines[i + 1]
                    marks = lines[i + 2]
                    rows.append({
                        "S.No.": sno,
                        "Question": remove_mcq_options(" ".join(question_parts)),
                        "Full Question with Options": " ".join(question_parts),
                        "Course Outcome": co,
                        "Bloom’s Taxonomy Level": bloom,
                        "Bloom Level in Paper": normalize_bloom(bloom),
                        "Marks": marks
                    })
                    i += 3
                    break

                question_parts.append(current)
                i += 1
        else:
            i += 1

    return pd.DataFrame(rows)

def detect_math_question(question):
    q = clean_text(question).lower()
    score = 0
    patterns = [
        r"\d+", r"\+", r"\-", r"\*", r"\/", r"=", r"\^", r"\(", r"\)",
        r"\bmatrix\b", r"\bvector\b", r"\bequation\b", r"\bintegral\b",
        r"\bderivative\b", r"\bprobability\b", r"\bvariance\b",
        r"\bstandard deviation\b", r"\bmean\b", r"\bmedian\b",
        r"\blog\b", r"\blimit\b", r"\bgraph\b", r"\bcomplexity\b",
        r"\bo\(", r"\bpolynomial\b"
    ]
    for p in patterns:
        if re.search(p, q):
            score += 1
    for kw in MATH_KEYWORDS:
        if kw in q:
            score += 1
    return score >= 2

def infer_question_type(question):
    q = clean_text(question).lower()
    if detect_math_question(q):
        return "Maths/Numerical"
    if any(x in q for x in ["program", "algorithm", "code", "implement", "python", "java", "c program"]):
        return "Programming"
    if any(x in q for x in ["design", "architecture", "framework", "system", "model"]):
        return "Design/System"
    if any(x in q for x in ["compare", "differentiate", "analyze", "analyse", "examine"]):
        return "Analytical"
    return "Theory"

def create_training_data():
    data = []
    remember = [
        "Define artificial intelligence.", "List the components of a computer system.",
        "State Bayes theorem.", "What is a database management system?",
        "Define data mining.", "Name the types of operating systems.",
        "Recall the syntax of a for loop in C.", "Identify the layers of OSI model.",
        "Define normalization in DBMS.", "List the basic data types in Java.",
        "What is a vector in mathematics?", "Define matrix.", "State Ohm's law.",
        "Define stress and strain.", "What is entropy in thermodynamics?",
        "List the phases of compiler design.", "Define tokenization in NLP.",
        "Describe cloud computing.", "Explain supervised learning.",
        "Describe the purpose of a constructor in Java.", "Summarize the need for cyber security.",
        "Classify machine learning techniques.", "Explain the concept of inheritance.",
        "Describe the working of a diode.", "Outline the steps in software development life cycle."
    ]
    apply = [
        "Apply Bayes theorem to solve the probability problem.",
        "Calculate the mean and variance for the given dataset.",
        "Compute the determinant of the given matrix.",
        "Solve the system of linear equations.",
        "Find the shortest path using Dijkstra algorithm.",
        "Use K-means algorithm for the given data points.",
        "Implement a stack using arrays.",
        "Write a Java program to implement inheritance.",
        "Execute the SQL query to retrieve employee records.",
        "Demonstrate the use of recursion with factorial program.",
        "Calculate the current using Ohm's law.",
        "Find the bending moment for the given beam.",
        "Compute the efficiency of the heat engine.",
        "Apply Laplace transform to solve the differential equation.",
        "Determine the time complexity of the given loop.",
        "Use NLTK to perform stemming.",
        "Apply convolution operation on the given image matrix.",
        "Simulate a queue using linked list.",
        "Plot the graph for the given function.",
        "Evaluate the postfix expression.",
        "Convert infix expression into postfix expression.",
        "Derive the output of the given C program.",
        "Perform normalization for the given database table.",
        "Estimate the power consumption of the circuit.",
        "Compute TF-IDF score for the given text."
    ]
    analyze = [
        "Analyze the performance of quick sort and merge sort.",
        "Compare TCP and UDP protocols.",
        "Differentiate supervised and unsupervised learning.",
        "Examine the ambiguity in the given sentence.",
        "Analyze the output of the given Java program.",
        "Inspect the given ER diagram and identify anomalies.",
        "Compare relational and non-relational databases.",
        "Analyze the complexity of the recursive algorithm.",
        "Differentiate between overloading and overriding.",
        "Investigate the causes of packet loss in the network.",
        "Analyze the trend in the given statistical dataset.",
        "Compare BFS and DFS traversal techniques.",
        "Examine the effect of learning rate in neural networks.",
        "Analyze the confusion matrix of the classification model.",
        "Differentiate combinational and sequential circuits.",
        "Break down the compiler phases for the given program.",
        "Interpret the result of regression analysis.",
        "Analyze the stability of the control system.",
        "Compare different clustering algorithms.",
        "Diagnose the error in the given Python code.",
        "Analyze the relationship between voltage and current.",
        "Examine the limitations of classical image processing.",
        "Distinguish between process and thread.",
        "Analyze the architecture of transformer model.",
        "Compare public cloud and private cloud deployment."
    ]
    evaluate = [
        "Evaluate the performance of the machine learning model.",
        "Justify the use of normalization in database design.",
        "Assess the security risks in the given network architecture.",
        "Critique the limitations of rule-based NLP systems.",
        "Validate the output of the given algorithm.",
        "Recommend the best sorting algorithm for large datasets.",
        "Judge the suitability of cloud deployment for the organization.",
        "Verify the correctness of the mathematical proof.",
        "Evaluate the efficiency of the proposed circuit.",
        "Defend the use of CNN for image classification.",
        "Rank the given models based on accuracy and complexity.",
        "Assess the effectiveness of the energy-saving strategy.",
        "Compare alternatives and choose the best database model.",
        "Evaluate the reliability of the classification report.",
        "Justify the use of blockchain in healthcare data security.",
        "Review the limitations of the given software design.",
        "Measure the performance improvement after optimization.",
        "Appraise the impact of AI in medical diagnosis.",
        "Evaluate whether the given grammar is ambiguous.",
        "Critique the design of the user interface.",
        "Assess the suitability of Random Forest for the dataset.",
        "Verify whether the given matrix is invertible.",
        "Evaluate the robustness of the segmentation method.",
        "Recommend a suitable protocol for IoT communication.",
        "Judge the correctness of the SQL transaction schedule."
    ]
    create = [
        "Design a database schema for hospital management system.",
        "Develop a chatbot for student support services.",
        "Construct a decision tree for the given dataset.",
        "Create a machine learning pipeline for cancer prediction.",
        "Formulate an algorithm for shortest path computation.",
        "Propose a secure authentication framework.",
        "Build a web application using Streamlit.",
        "Generate a data visualization dashboard.",
        "Compose a program to implement linked list operations.",
        "Design an IoT-based smart irrigation system.",
        "Develop an NLP pipeline for sentiment analysis.",
        "Construct an ER diagram for university management system.",
        "Create a regression model for sales prediction.",
        "Formulate a mathematical model for population growth.",
        "Design a controller for the given system.",
        "Architect a cloud-based attendance management system.",
        "Synthesize a solution for reducing network congestion.",
        "Integrate image processing and machine learning for colony counting.",
        "Write an algorithm for detecting fake profiles.",
        "Develop a recommender system for online learning.",
        "Design a neural network for handwritten digit recognition.",
        "Propose an energy audit and savings advisor.",
        "Build a cyber security threat detection framework.",
        "Create a blockchain-based medical record system.",
        "Develop a full-stack application for question paper analysis."
    ]
    for q in remember:
        data.append((q, "Remember & Understand"))
    for q in apply:
        data.append((q, "Apply"))
    for q in analyze:
        data.append((q, "Analyze"))
    for q in evaluate:
        data.append((q, "Evaluate"))
    for q in create:
        data.append((q, "Create"))
    return pd.DataFrame(data, columns=["Question", "Bloom_Level"])

@st.cache_resource
def train_model():
    df = create_training_data()
    model = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 3), min_df=1)),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced"))
    ])
    model.fit(df["Question"], df["Bloom_Level"])
    return model, df

model, training_df = train_model()

def rule_based_classifier(question, marks=0):
    q_original = remove_mcq_options(question)
    q = q_original.lower()
    q_clean = re.sub(r"[^a-z0-9\s\+\-\*\/\=\^\(\)]", " ", q)
    q_clean = re.sub(r"\s+", " ", q_clean).strip()

    scores = {level: 0 for level in BLOOM_LEVELS}
    matched = []

    for level, verbs in BLOOM_VERBS.items():
        for verb in verbs:
            pattern = r"\b" + re.escape(verb.lower()) + r"\b"
            if re.search(pattern, q_clean):
                scores[level] += BLOOM_ORDER[level]
                matched.append(f"{verb} → {level}")

    is_math = detect_math_question(q_original)

    if is_math:
        if any(v in q for v in ["solve", "calculate", "compute", "find", "determine", "obtain", "simplify"]):
            scores["Apply"] += 3
        if any(v in q for v in ["prove", "verify", "justify", "evaluate"]):
            scores["Evaluate"] += 4
        if any(v in q for v in ["derive", "formulate", "model", "construct"]):
            scores["Create"] += 4

    if marks >= 10:
        if any(v in q for v in ["design", "develop", "propose", "create", "formulate", "construct"]):
            scores["Create"] += 5
        elif any(v in q for v in ["evaluate", "justify", "assess", "verify"]):
            scores["Evaluate"] += 4
        elif any(v in q for v in ["analyze", "analyse", "compare", "differentiate", "examine"]):
            scores["Analyze"] += 3

    max_score = max(scores.values())

    if max_score == 0:
        if is_math:
            return "Apply", "Maths/numerical detected; defaulted to Apply", "Numerical pattern"
        return "Remember & Understand", "No clear verb found", ""

    best = [level for level, score in scores.items() if score == max_score]
    selected = max(best, key=lambda x: BLOOM_ORDER[x])
    remark = "Keyword / rule matched" if len(best) == 1 else "Mixed verbs found; higher Bloom level selected"

    return selected, remark, ", ".join(matched)

def hybrid_classifier(question, paper_bloom, marks=0):
    rule_level, rule_remark, matched_verbs = rule_based_classifier(question, marks)
    nlp_level = model.predict([remove_mcq_options(question)])[0]
    is_math = detect_math_question(question)

    if paper_bloom != "Not Provided":
        final_level = paper_bloom
        status = "Final level taken from question paper table"
    elif rule_level == nlp_level:
        final_level = rule_level
        status = "Rule and NLP agree"
    else:
        candidate_levels = [rule_level, nlp_level]
        if is_math and marks <= 5:
            candidate_levels.append("Apply")
        elif is_math and marks >= 10 and any(v in question.lower() for v in ["prove", "verify", "justify", "derive", "formulate"]):
            candidate_levels.append("Evaluate")
        final_level = max(candidate_levels, key=lambda x: BLOOM_ORDER[x])
        status = "Hybrid decision: rule + NLP + maths/marks heuristic"

    return rule_level, nlp_level, final_level, status, rule_remark, matched_verbs, is_math

def generate_balance_report(df):
    total = len(df)
    if total == 0:
        return pd.DataFrame(), [], 0, 0, 0, 0

    counts = df["Final Bloom Level"].value_counts().reindex(BLOOM_LEVELS, fill_value=0)
    actual = (counts / total * 100).round(2)

    report = pd.DataFrame({
        "Bloom Level": BLOOM_LEVELS,
        "Question Count": counts.values,
        "Actual %": actual.values,
        "Recommended %": [TARGET_DISTRIBUTION[x] for x in BLOOM_LEVELS]
    })
    report["Difference %"] = report["Actual %"] - report["Recommended %"]

    lower = report[report["Bloom Level"] == "Remember & Understand"]["Actual %"].sum()
    higher = report[report["Bloom Level"].isin(["Apply", "Analyze", "Evaluate", "Create"])]["Actual %"].sum()

    weights = {"Remember & Understand": 1, "Apply": 2, "Analyze": 3, "Evaluate": 4, "Create": 5}
    complexity_score = (df["Final Bloom Level"].map(weights).sum() / (len(df) * 5)) * 100

    distribution_score = max(0, 100 - report["Difference %"].abs().sum() / 2)
    higher_order_score = min(100, higher * 1.5)
    quality_score = distribution_score * 0.6 + higher_order_score * 0.4

    suggestions = []
    for _, row in report.iterrows():
        if row["Difference %"] > 10:
            suggestions.append(f"Reduce {row['Bloom Level']} questions by about {row['Difference %']:.1f}%.")
        elif row["Difference %"] < -10:
            suggestions.append(f"Increase {row['Bloom Level']} questions by about {abs(row['Difference %']):.1f}%.")

    if higher < 50:
        suggestions.append("Higher-order thinking is low. Add more Apply, Analyze, Evaluate and Create questions.")
    if report.loc[report["Bloom Level"] == "Evaluate", "Question Count"].iloc[0] == 0:
        suggestions.append("No Evaluate-level question found.")
    if report.loc[report["Bloom Level"] == "Create", "Question Count"].iloc[0] == 0:
        suggestions.append("No Create-level question found.")
    if not suggestions:
        suggestions.append("The question paper has a balanced Bloom distribution.")

    return report, suggestions, lower, higher, complexity_score, quality_score

def validate_against_expert(expert_df):
    if not {"Question", "Expert_Level"}.issubset(expert_df.columns):
        return None, "CSV must contain Question and Expert_Level columns."

    expert_df = expert_df.copy()
    expert_df["Expert_Level"] = expert_df["Expert_Level"].apply(normalize_bloom)
    expert_df["Predicted_Level"] = [
        hybrid_classifier(q, "Not Provided", 0)[2] for q in expert_df["Question"]
    ]

    metrics = {
        "Accuracy": accuracy_score(expert_df["Expert_Level"], expert_df["Predicted_Level"]),
        "Cohen Kappa": cohen_kappa_score(expert_df["Expert_Level"], expert_df["Predicted_Level"])
    }

    report = classification_report(
        expert_df["Expert_Level"],
        expert_df["Predicted_Level"],
        labels=BLOOM_LEVELS,
        output_dict=True,
        zero_division=0
    )

    cm = confusion_matrix(
        expert_df["Expert_Level"],
        expert_df["Predicted_Level"],
        labels=BLOOM_LEVELS
    )

    return {
        "data": expert_df,
        "metrics": metrics,
        "classification_report": pd.DataFrame(report).transpose(),
        "confusion_matrix": pd.DataFrame(cm, index=BLOOM_LEVELS, columns=BLOOM_LEVELS)
    }, None

def show_visual_dashboard(result_df, report, key_prefix="dash"):
    st.subheader("Visual Analytics Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.bar(report, x="Bloom Level", y="Actual %", text="Actual %", title="Bloom-Level Distribution")
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_bar, width="stretch", key=f"{key_prefix}_bloom_bar")

    with col2:
        fig_pie = px.pie(report, names="Bloom Level", values="Question Count", title="Question Count by Bloom Level", hole=0.35)
        st.plotly_chart(fig_pie, width="stretch", key=f"{key_prefix}_bloom_pie")

    col3, col4 = st.columns(2)

    with col3:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=report["Actual %"], theta=report["Bloom Level"], fill="toself", name="Actual %"))
        fig_radar.add_trace(go.Scatterpolar(r=report["Recommended %"], theta=report["Bloom Level"], fill="toself", name="Recommended %"))
        fig_radar.update_layout(title="Actual vs Recommended Bloom Radar", polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
        st.plotly_chart(fig_radar, width="stretch", key=f"{key_prefix}_radar")

    with col4:
        marks_df = result_df.copy()
        marks_df["Marks"] = marks_df["Marks"].apply(safe_int)
        marks_group = marks_df.groupby("Final Bloom Level")["Marks"].sum().reindex(BLOOM_LEVELS, fill_value=0).reset_index()
        fig_marks = px.bar(marks_group, x="Final Bloom Level", y="Marks", text="Marks", title="Marks Distribution by Bloom Level")
        fig_marks.update_traces(textposition="outside")
        st.plotly_chart(fig_marks, width="stretch", key=f"{key_prefix}_marks")

    if "Course Outcome" in result_df.columns:
        st.subheader("CO-wise Bloom Analytics")
        heatmap_data = pd.crosstab(result_df["Course Outcome"], result_df["Final Bloom Level"]).reindex(columns=BLOOM_LEVELS, fill_value=0)
        fig_heat = px.imshow(heatmap_data, text_auto=True, title="CO vs Bloom Heatmap", aspect="auto")
        st.plotly_chart(fig_heat, width="stretch", key=f"{key_prefix}_co_heatmap")

        fig_parallel = px.parallel_categories(result_df, dimensions=["Course Outcome", "Final Bloom Level"], title="CO to Bloom Flow")
        st.plotly_chart(fig_parallel, width="stretch", key=f"{key_prefix}_parallel")

    if "Question Type" in result_df.columns:
        fig_sun = px.sunburst(result_df, path=["Question Type", "Final Bloom Level"], title="Question Type to Bloom Sunburst")
        st.plotly_chart(fig_sun, width="stretch", key=f"{key_prefix}_sunburst")

    fig_dev = px.bar(report, x="Bloom Level", y="Difference %", text="Difference %", title="Deviation from Recommended Bloom Distribution")
    fig_dev.update_traces(textposition="outside")
    st.plotly_chart(fig_dev, width="stretch", key=f"{key_prefix}_deviation")

st.title("Advanced Question-Paper Bloom's Taxonomy Analyzer")
st.caption("Colab-ready Streamlit app with unique Plotly keys, advanced Bloom verbs, maths/numerical training and visual analytics.")

with st.sidebar:
    st.header("Course Details")
    course_title = st.text_input("Course Title", value="Natural Language Processing")
    department = st.selectbox("Offering Department", DISCIPLINES)
    regulation = st.text_input("Regulation / Batch", value="")
    exam_name = st.text_input("Exam Name", value="IAT / Model / Semester")
    use_paper_bloom = st.checkbox("Use Bloom level already given in question paper", value=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Analyze Question Paper",
    "Visual Dashboard",
    "Expert Validation",
    "Training Data"
])

if "result_df" not in st.session_state:
    st.session_state.result_df = pd.DataFrame()
if "report_df" not in st.session_state:
    st.session_state.report_df = pd.DataFrame()

with tab1:
    st.subheader("Upload DOC/DOCX/PDF/TXT/CSV/XLSX Question Paper")

    uploaded_file = st.file_uploader("Upload Question Paper", type=["doc", "docx", "pdf", "txt", "csv", "xlsx"])
    manual_text = st.text_area("Or paste question paper text", height=250)
    question_df = pd.DataFrame()

    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".doc") or file_name.endswith(".docx"):
            question_df = extract_questions_from_doc_or_docx(file_bytes, file_name)
            if question_df.empty:
                st.warning("No valid DOC/DOCX question table found.")
        elif file_name.endswith(".pdf"):
            question_df = extract_questions_from_plain_text(extract_text_from_pdf(file_bytes))
        elif file_name.endswith(".txt"):
            question_df = extract_questions_from_plain_text(file_bytes.decode("utf-8", errors="ignore"))
        elif file_name.endswith(".csv"):
            question_df = pd.read_csv(io.BytesIO(file_bytes))
        elif file_name.endswith(".xlsx"):
            question_df = pd.read_excel(io.BytesIO(file_bytes))
    elif manual_text.strip():
        question_df = extract_questions_from_plain_text(manual_text)

    if not question_df.empty:
        st.subheader("Extracted Table")
        st.dataframe(question_df, width="stretch")
        st.info(f"Extracted {len(question_df)} valid question rows. OR rows removed.")

    if st.button("Analyze Bloom Balance", type="primary"):
        if question_df.empty:
            st.error("No table extracted. Ensure columns: S.No., Question, Course Outcome, Bloom’s Taxonomy Level, Marks.")
        else:
            results = []

            for _, row in question_df.iterrows():
                sno = clean_text(row.get("S.No.", ""))
                question = clean_text(row.get("Question", ""))
                full_question = clean_text(row.get("Full Question with Options", question))
                co = clean_text(row.get("Course Outcome", ""))
                bloom_raw = clean_text(row.get("Bloom’s Taxonomy Level", ""))
                marks = clean_text(row.get("Marks", ""))

                if not question or question.lower() == "or":
                    continue

                marks_int = safe_int(marks)
                paper_bloom = normalize_bloom(bloom_raw)
                if not use_paper_bloom:
                    paper_bloom = "Not Provided"

                rule, nlp, final, status, remark, verbs, is_math = hybrid_classifier(question, paper_bloom, marks_int)

                results.append({
                    "Course Title": course_title,
                    "Offering Department": department,
                    "Exam Name": exam_name,
                    "S.No.": sno,
                    "Question": question,
                    "Full Question with Options": full_question,
                    "Course Outcome": co,
                    "Bloom’s Taxonomy Level": bloom_raw,
                    "Bloom Level in Paper": normalize_bloom(bloom_raw),
                    "Marks": marks,
                    "Question Type": infer_question_type(question),
                    "Maths/Numerical Detected": "Yes" if is_math else "No",
                    "Rule-Based Baseline": rule,
                    "NLP Classifier": nlp,
                    "Final Bloom Level": final,
                    "Robustness Status": status,
                    "Rule Remark": remark,
                    "Matched Verbs": verbs
                })

            result_df = pd.DataFrame(results)
            st.session_state.result_df = result_df

            report, suggestions, lower, higher, complexity_score, quality_score = generate_balance_report(result_df)
            st.session_state.report_df = report

            st.success(f"{len(result_df)} questions analyzed successfully.")

            st.subheader("Question-wise Bloom Analysis")
            st.dataframe(result_df, width="stretch")

            st.subheader("Summary Metrics")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Questions", len(result_df))
            m2.metric("Remember & Understand", f"{lower:.1f}%")
            m3.metric("Higher Order Thinking", f"{higher:.1f}%")
            m4.metric("Cognitive Complexity", f"{complexity_score:.1f}%")
            m5.metric("Quality Score", f"{quality_score:.1f}/100")

            st.subheader("Bloom Balance Report")
            st.dataframe(report, width="stretch")

            st.subheader("Decision Output / Recommendations")
            for s in suggestions:
                st.info(s)

            show_visual_dashboard(result_df, report, key_prefix="tab1")

            st.download_button("Download Question-wise Report CSV", result_df.to_csv(index=False).encode("utf-8"), "bloom_questionwise_report.csv", "text/csv")
            st.download_button("Download Balance Report CSV", report.to_csv(index=False).encode("utf-8"), "bloom_balance_report.csv", "text/csv")

with tab2:
    if st.session_state.result_df.empty or st.session_state.report_df.empty:
        st.warning("Analyze a question paper first.")
    else:
        show_visual_dashboard(st.session_state.result_df, st.session_state.report_df, key_prefix="tab2")

with tab3:
    st.subheader("Expert Validation")
    expert_file = st.file_uploader("Upload CSV with Question and Expert_Level columns", type=["csv"], key="expert")

    if expert_file:
        expert_df = pd.read_csv(expert_file)
        validation, error = validate_against_expert(expert_df)

        if error:
            st.error(error)
        else:
            col1, col2 = st.columns(2)
            col1.metric("Accuracy", f"{validation['metrics']['Accuracy'] * 100:.2f}%")
            col2.metric("Cohen Kappa", f"{validation['metrics']['Cohen Kappa']:.2f}")

            st.subheader("Validation Table")
            st.dataframe(validation["data"], width="stretch")

            st.subheader("Per-Level Report")
            st.dataframe(validation["classification_report"], width="stretch")

            st.subheader("Confusion Matrix")
            st.dataframe(validation["confusion_matrix"], width="stretch")

            fig_cm = px.imshow(validation["confusion_matrix"], text_auto=True, title="Confusion Matrix Heatmap", aspect="auto")
            st.plotly_chart(fig_cm, width="stretch", key="expert_confusion_matrix")

with tab4:
    st.subheader("Training Data Used for Model")
    st.info("Training set covers CSE, AI, NLP, Data Mining, Java, Maths, Statistics, EEE, Mechanical, Civil and engineering questions.")
    st.dataframe(training_df, width="stretch")

    fig_train = px.histogram(training_df, x="Bloom_Level", title="Training Data Distribution", category_orders={"Bloom_Level": BLOOM_LEVELS})
    st.plotly_chart(fig_train, width="stretch", key="training_distribution")

    st.download_button("Download Training Dataset CSV", training_df.to_csv(index=False).encode("utf-8"), "bloom_training_dataset.csv", "text/csv")

# Expert validation dropdown patch could not locate tab4 automatically.
