# Bloom's Taxonomy & Course Outcome Analyzer

An **AI-powered Outcome-Based Education (OBE) Assessment Analyzer** designed to automate the evaluation of examination question papers using **Bloom's Taxonomy**, **Course Outcome (CO) mapping**, and **OBE assessment blueprint validation**.

The application employs a **hybrid Artificial Intelligence framework** that integrates **rule-based NLP**, **machine learning**, **action-verb analysis**, and **assessment analytics** to assist faculty in designing high-quality examinations aligned with NBA, NAAC, and OBE standards.

---

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://bloomsanalyzerfinalhackathoncode-kpskpcgdrrzswupec9jpw8.streamlit.app/)

### 🚀 Live Demo

👉 **Try the application online:**

https://bloomsanalyzerfinalhackathoncode-kpskpcgdrrzswupec9jpw8.streamlit.app/

---

An **AI-powered Outcome-Based Education (OBE) Assessment Analyzer** designed to automate the evaluation of examination question papers using **Bloom's Taxonomy**, **Course Outcome (CO) mapping**, and **OBE assessment blueprint validation**.

# Key Features

## Intelligent Question Paper Analysis

Supports multiple input formats:

* DOC
* DOCX
* PDF
* CSV
* XLSX
* TXT

The system automatically:

* Extracts questions from uploaded files
* Removes duplicate questions
* Eliminates OR-choice questions
* Detects question numbering
* Extracts marks automatically
* Identifies Course Outcomes (COs)
* Recognizes question types

Supported question categories include:

* Theory Questions
* Programming Questions
* Numerical Problems
* Mathematical Questions
* Case Study Questions
* Design-Oriented Questions
* Analytical Questions

---

# Hybrid Bloom's Taxonomy Classification

The proposed model combines multiple intelligent techniques for robust Bloom-level prediction.

### Rule-Based NLP Engine

* Action verb detection
* Bloom keyword matching
* Domain-specific heuristic rules

### Machine Learning Classifier

* TF-IDF Vectorization
* Logistic Regression Classification

### Mathematical Question Detector

Automatically detects:

* Formula-based questions
* Numerical computations
* Engineering calculations

### Marks-Based Difficulty Analyzer

Difficulty is estimated using:

* Marks allocation
* Question complexity
* Bloom hierarchy

---

# Supported Bloom's Taxonomy Levels

| Level | Bloom Category        |
| ----- | --------------------- |
| 1     | Remember & Understand |
| 2     | Apply                 |
| 3     | Analyze               |
| 4     | Evaluate              |
| 5     | Create                |

---

# Outcome-Based Education (OBE) Blueprint Validation

Faculty can define assessment blueprints including:

* Course Outcomes (COs)
* Target Bloom Level
* Required Action Verbs
* Target Marks
* Number of Questions
* Assessment Weightage

### Example Blueprint

| CO  | Target Bloom          | Required Action Verb | Marks |
| --- | --------------------- | -------------------- | ----- |
| CO1 | Remember & Understand | Explain              | 10    |
| CO2 | Apply                 | Apply, Implement     | 10    |
| CO3 | Analyze               | Analyze, Compare     | 10    |
| CO4 | Evaluate              | Evaluate, Justify    | 10    |
| CO5 | Create                | Design, Develop      | 10    |

The analyzer automatically validates whether the uploaded assessment satisfies the defined blueprint.

---

# Course Outcome Coverage Analysis

The application evaluates:

* CO coverage percentage
* Missing Course Outcomes
* CO-wise Bloom distribution
* CO-wise marks allocation
* CO achievement matrix
* Blueprint compliance

---

# Action Verb Verification

The system verifies whether each question uses the appropriate Bloom action verbs.

Example:

| Question        | Expected Bloom | Detected Verb | Status |
| --------------- | -------------- | ------------- | ------ |
| Explain NLP     | Remember       | Explain       | ✓      |
| Analyze CNN     | Analyze        | Analyze       | ✓      |
| Design Database | Create         | Design        | ✓      |

---

# Expert Validation Module

Faculty experts can manually validate Bloom classifications.

### Workflow

1. Upload question paper
2. Automatic Bloom prediction
3. Expert selects correct Bloom level
4. Performance metrics generated automatically

### Expert Dropdown

* Remember & Understand
* Apply
* Analyze
* Evaluate
* Create

---

# AI Confidence & Explainability

Each prediction includes:

* Confidence Score
* Detected Action Verb
* Rule-Based Score
* Machine Learning Probability
* Final Hybrid Decision

This improves transparency and assists faculty in reviewing uncertain predictions.

---

# Performance Evaluation

The application compares:

## Baseline Model

Rule-Based Bloom Classifier

## Proposed Model

Hybrid AI Bloom Classifier

Performance metrics include:

* Accuracy
* Precision
* Recall
* F1 Score
* Error Rate
* Cohen's Kappa
* Confusion Matrix
* Classification Report

---

# Robustness Analysis

Classification performance is evaluated under different conditions:

* Original Questions
* Typographical Errors
* Question Paraphrasing
* Mixed Action Verbs
* Combined Noise & Paraphrasing

This enables benchmarking for research publications.

---

# Assessment Quality Analytics

The system computes:

* Bloom Distribution
* Higher-Order Thinking Skills (HOTS) Percentage
* Lower-Order Thinking Skills (LOTS) Percentage
* Difficulty Index
* Assessment Quality Score
* Cognitive Balance Index
* CO Coverage Score
* Blueprint Compliance Score

---

# Interactive Dashboard

## Bloom Analytics

* Bloom Distribution Bar Chart
* Pie Chart
* Radar Chart
* Cognitive Level Comparison

## CO Analytics

* CO Coverage Matrix
* CO vs Bloom Heatmap
* CO Achievement Chart
* Marks Distribution

## Assessment Analytics

* Bloom Distribution
* Difficulty Analysis
* Question Type Distribution
* HOTS vs LOTS Analysis
* Quality Score

---

# Visual Reports

The application automatically generates:

* Bloom Distribution Report
* Course Outcome Report
* OBE Compliance Report
* Action Verb Compliance Report
* Assessment Blueprint Report
* Question Quality Report
* Expert Validation Report
* Confusion Matrix
* Robustness Analysis Report

All reports are downloadable in CSV format.

---

# Supported Input Formats

## DOC / DOCX

Expected format:

| S.No. | Question | Course Outcome | Bloom's Taxonomy Level | Marks |

---

## CSV / XLSX

Required columns:

* S.No.
* Question
* Course Outcome
* Bloom's Taxonomy Level
* Marks

---

## Expert Validation CSV

Example:

Question,Expert_Level

What is NLP?,Remember & Understand

Explain Stemming.,Apply

Analyze discourse structure.,Analyze

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/obe-bloom-analyzer.git

cd obe-bloom-analyzer
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running Locally

```bash
streamlit run app.py
```

---

# Running in Google Colab

Install dependencies:

```bash
!pip install -r requirements.txt
```

Run Streamlit:

```bash
!streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

Create a Cloudflare Tunnel:

```bash
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared

!chmod +x cloudflared

!./cloudflared tunnel --url http://localhost:8501
```

A public URL will be generated for remote access.

---

# Research Contributions

The proposed framework introduces several novel features:

* Hybrid AI-based Bloom Classification
* Outcome-Based Education (OBE) Blueprint Validation
* Course Outcome Coverage Analysis
* Action Verb Verification
* AI Confidence Scoring
* Explainable Bloom Classification
* Expert-in-the-Loop Validation
* Robustness Testing Framework
* Cognitive Balance Analysis
* Assessment Quality Index

---

# Applications

Suitable for:

* NBA Accreditation
* NAAC Documentation
* OBE Assessment Audits
* Internal Academic Audits
* Educational Data Mining
* Learning Analytics
* AI in Education Research
* Examination Quality Assurance

---

# Technology Stack

* Python
* Streamlit
* Scikit-learn
* Pandas
* Plotly
* NumPy
* OpenPyXL
* python-docx
* PyPDF

---

# Author

## Team Members

**Dr. S. Pitchumani Angayarkanni**

Professor

Department of Computer Science and Engineering

Aarupadai Veedu Institute of Technology (AVIT)

Vinayaka Mission's Research Foundation (Deemed to be University)

---

# License

This software is intended for **academic, research, and educational purposes**. It may be used for teaching, institutional quality assurance, accreditation support, and educational research. Commercial use requires prior permission from the authors.
