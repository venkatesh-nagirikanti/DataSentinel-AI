# DataSentinel AI – Enterprise Data Incident Commander

DataSentinel AI is an autonomous, enterprise-grade Data Incident Management system designed to minimize "data downtime" in complex ETL and data analytics pipelines. Developed as a single Python Streamlit project, it automatically profiles data payloads, triages infrastructure execution logs, performs AI-driven Root Cause Analysis (RCA), generates code remediation patches (SQL, PySpark, AWS Glue), and compiles post-mortem incident reports (PDF and Markdown).

---

## 🚀 Key Value Prop & Hackathon Highlights
- **Drastically Reduced MTTR:** Truncates response cycles from hours of manual database checks and log indexing down to minutes of automated AI synthesis.
- **Demo-Ready Out-Of-The-Box:** The application features a robust demo-fallback system. If no Gemini API key is configured, the application serves detailed, pre-compiled schema validation drift mocks so judges can immediately evaluate execution paths.
- **Clean PDF Layout Generator:** Utilizes custom layout calculations to transform raw incident details into clean, business-ready PDF documentation.
- **Human-In-The-Loop Sandbox:** Provides editable code generation blocks allowing engineers to review, adjust, and export scripts before deployment.

---

## 🛠️ Technology Stack
* **Frontend UI Framework:** Streamlit (customized with premium styles)
* **Computation & Metrics Engine:** Pandas, NumPy
* **Visualizations:** Plotly Express & Plotly Graph Objects
* **Generative AI Orchestration:** Google Gemini 1.5 Flash (via `google-generativeai`)
* **Document Compilation:** FPDF2 (PDF generation)
* **Configuration:** Python-dotenv

---

## 📂 Project Architecture
```text
DataSentinel-AI/
├── app.py                      # Main Streamlit App Router & View Controller
├── requirements.txt            # Project Dependencies
├── .env.example                # Template configuration parameters
├── README.md                   # This project guide
├── samples/                    # Sample target files
│   ├── sample_logs.log         # Sample AWS Glue error log (Schema drift + OOM)
│   └── sample_data.csv         # Sample CSV file (anomalies, nulls, invalid dates)
└── utils/                      # Helper libraries
    ├── data_analyzer.py        # Custom data profiler & quality parser
    ├── gemini_client.py        # Gemini client prompt wrappers & Mock templates
    └── report_generator.py     # Custom markdown-to-PDF parser utilizing FPDF2
```

---

## ⚙️ Quick Start Installation

Follow these steps to run the application on your local machine:

### 1. Prerequisites
Ensure you have Python 3.9 or higher installed.

### 2. Clone the Repository & Navigate to Folder
```powershell
cd c:\Users\venka\OneDrive\Documents\DataSentinel-AI
```

### 3. Initialize & Activate Virtual Environment
```powershell
# Create Virtual Environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Set up the Environment Configuration
Copy the sample environment file:
```powershell
cp .env.example .env
```
Open `.env` in a text editor and update your `GEMINI_API_KEY`:
```text
GEMINI_API_KEY=AIzaSy...
```
*(Note: If you leave this field empty, the application will run in **Demo Mode**, utilizing high-quality mock data configurations).*

### 6. Run the Streamlit Application
```powershell
streamlit run app.py
```
The application will automatically launch in your default web browser at `http://localhost:8501`.

---

## 📋 Recommended Walkthrough Path for Judges

1. **Dashboard Overview:** Start on **Executive Dashboard** to view historical MTTD/MTTR analytics and review the active incidents queue.
2. **CSV Quality Upload:** Navigate to **CSV Quality Upload**, click the button **"Load Sample CSV Dataset"**, and then select **"Run Data Profiling"**.
3. **ETL Log Ingest:** Go to **ETL Log Ingest** and click **"Load Sample AWS Glue Error Log"** to load the stack trace.
4. **AI Root Cause Analysis (RCA):** Navigate to **AI Root Cause Analysis** and click **"Run Root Cause Analysis"** to see Gemini isolate the JVM memory limit issue and table schema mismatches.
5. **Data Quality Profile:** Explore **Data Quality Profile** to view missing values, distributions, and registered anomalies.
6. **SQL Schema Fixer:** Click **"Generate SQL Fix Script"** to fetch repair query statements.
7. **PySpark Pipeline Repair:** Click **"Generate PySpark Repair Code"** to build Spark transformation functions.
8. **AWS Glue Scaffolder:** Click **"Scaffold AWS Glue Job"** to wrap the PySpark fixes inside a complete Glue job context.
9. **Post-Mortem Report:** Go to **Post-Mortem Report** and click **"Generate Comprehensive Report"** to assemble a structured markdown review.
10. **Export & Download:** Select **Export Incident Center** to download the clean **PDF report**, raw **Markdown summary**, and repair script files.
