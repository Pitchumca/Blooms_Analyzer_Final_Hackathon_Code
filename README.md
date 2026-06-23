README.md
OBE-Based Bloom’s Taxonomy & Course Outcome Analyzer

An advanced Streamlit application for Outcome-Based Education (OBE) assessment analysis. The system automatically extracts questions from DOC, DOCX, PDF, CSV, XLSX, and TXT files, predicts Bloom's Taxonomy levels using a hybrid AI model, validates Course Outcome (CO) coverage, verifies assessment blueprints, and generates publication-quality evaluation metrics.

Features
Question Paper Analysis
Upload DOC, DOCX, PDF, CSV, XLSX, or TXT question papers
Automatic question extraction
Removal of OR questions and duplicate questions
Detection of question types:
Theory
Programming
Numerical/Mathematical
Analytical
Design/System
Bloom's Taxonomy Classification

Hybrid classification using:

Rule-Based Action Verb Analyzer
Machine Learning Classifier (TF-IDF + Logistic Regression)
Mathematical/Numerical Question Heuristics
Marks-Based Difficulty Adjustment

Supported Bloom Levels:

Level	Bloom Category
1	Remember & Understand
2	Apply
3	Analyze
4	Evaluate
5	Create
OBE Assessment Blueprint Validation

The system allows faculty to define:

Course Outcomes (COs)
Target Bloom Level per CO
Target Marks
Target Questions
Required Action Verbs

Example:

CO	Target Bloom	Action Verb	Marks
CO1	Remember & Understand	Explain	10
CO2	Apply	Apply, Implement	10
CO3	Analyze	Analyze, Compare	10
CO4	Evaluate	Evaluate, Justify	10
CO5	Create	Design, Develop	10

The analyzer verifies whether the uploaded assessment satisfies the blueprint exactly.

Expert Validation Module

Faculty can validate Bloom classification manually.

Workflow:

Upload question CSV
System predicts Bloom level
Expert selects correct Bloom level from dropdown
Metrics are automatically generated

Dropdown options:

Remember & Understand
Apply
Analyze
Evaluate
Create
Performance Evaluation

The application computes:

Baseline Model

Rule-Based Bloom Classifier

Proposed Model

Hybrid AI Classifier

Metrics
Accuracy
Error Rate
Precision
Recall
F1 Score
Cohen Kappa
Confusion Matrix
Robustness Analysis

Tests classification performance under:

Original Questions
Typographical Noise
Question Paraphrasing
Combined Noise + Paraphrasing

Useful for research publications and benchmarking.

Visual Analytics Dashboard
Bloom Distribution
Bar Chart
Pie Chart
Radar Chart
CO Analytics
CO Coverage Matrix
CO vs Bloom Heatmap
CO Flow Analysis
Assessment Analytics
Marks Distribution
Bloom Distribution
Higher-Order Thinking Percentage
Difficulty Index
Quality Score
Input Formats
DOC/DOCX

Question paper format:

S.No.	Question	Course Outcome	Bloom’s Taxonomy Level	Marks
CSV/XLSX

Required Columns:

S.No.
Question
Course Outcome
Bloom’s Taxonomy Level
Marks
Expert Validation CSV
Question,Expert_Level
What is NLP?,Remember & Understand
Explain stemming,Apply
Analyze discourse structure,Analyze
Installation
Clone Repository
git clone https://github.com/yourusername/obe-bloom-analyzer.git
cd obe-bloom-analyzer
Install Dependencies
pip install -r requirements.txt
Running Locally
streamlit run app.py
Running in Google Colab
Install Dependencies
!pip install -r requirements.txt
Start Streamlit
!streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
Cloudflare Tunnel
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared
!chmod +x cloudflared
!./cloudflared tunnel --url http://localhost:8501
Open Generated URL

Cloudflare will generate a public URL similar to:

https://xxxx.trycloudflare.com
Research Contributions
Novel Features
OBE-driven assessment validation
Hybrid Bloom classification
Mathematical question detection
Action verb verification
CO–Bloom blueprint compliance
Expert-in-the-loop validation
Robustness testing framework
Suitable For
NBA Accreditation
NAAC Documentation
OBE Assessment Audits
Academic Quality Assurance
Educational Data Mining Research
Bloom's Taxonomy Research
Output Reports

Generated Reports:

Question-wise Analysis
Bloom Distribution Report
CO Coverage Report
OBE Compliance Report
Action Verb Compliance Report
Expert Validation Report
Accuracy Comparison Report
Confusion Matrix
Robustness Analysis Report

All reports can be downloaded as CSV files.

Technology Stack
Streamlit
Python
Scikit-Learn
Plotly
Pandas
Python-Docx
PyPDF
OpenPyXL
Author

Dr. S. Pitchumani Angayarkanni
Professor, Department of Computer Science and Engineering
Aarupadai Veedu Institute of Technology (AVIT)
Vinayaka Mission's Research Foundation (VMRF-DU)

License

This project is intended for academic and research use.
