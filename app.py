import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import io
from dotenv import load_dotenv

# Import utilities
from utils.data_analyzer import analyze_csv_data
from utils.gemini_client import (
    get_ai_rca,
    get_sql_fix,
    get_pyspark_fix,
    get_aws_glue_job,
    get_incident_report,
    is_api_configured
)
from utils.report_generator import generate_pdf_report

# Load environment
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="DataSentinel AI - Enterprise Data Incident Commander",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
    <style>
        /* Base styles */
        .main-header {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1E293B;
            background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subheader {
            font-size: 1.1rem;
            color: #64748B;
            margin-bottom: 2rem;
        }
        
        /* Metric cards */
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
            transition: all 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            border-color: #CBD5E1;
        }
        .metric-val {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0F172A;
            margin-top: 0.25rem;
        }
        .metric-lbl {
            font-size: 0.85rem;
            font-weight: 500;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Status pills */
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-critical { background-color: #FEE2E2; color: #991B1B; }
        .badge-warning { background-color: #FEF3C7; color: #92400E; }
        .badge-info { background-color: #E0F2FE; color: #075985; }
        .badge-success { background-color: #DCFCE7; color: #166534; }
        
        /* Demo Banner */
        .demo-banner {
            background-color: #FFFBEB;
            border: 1px solid #F59E0B;
            border-radius: 8px;
            padding: 10px 15px;
            margin-bottom: 20px;
            color: #B45309;
        }
        
        /* Agent response block */
        .agent-block {
            background-color: #0F172A;
            color: #F8FAFC;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Courier New', Courier, monospace;
            border-left: 5px solid #6366F1;
        }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "log_text" not in st.session_state:
    st.session_state["log_text"] = ""
if "df_data" not in st.session_state:
    st.session_state["df_data"] = None
if "df_analysis" not in st.session_state:
    st.session_state["df_analysis"] = None
if "rca_result" not in st.session_state:
    st.session_state["rca_result"] = ""
if "sql_fix" not in st.session_state:
    st.session_state["sql_fix"] = ""
if "pyspark_fix" not in st.session_state:
    st.session_state["pyspark_fix"] = ""
if "glue_job" not in st.session_state:
    st.session_state["glue_job"] = ""
if "incident_report" not in st.session_state:
    st.session_state["incident_report"] = ""

# Sidebar - System State & Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.markdown("<h2 style='margin-top: 0;'>DataSentinel AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-style: italic; color: #64748B;'>Enterprise Incident Commander</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Check configurations
    api_ready = is_api_configured()
    if api_ready:
        st.success("🤖 Gemini API Connected", icon="✅")
    else:
        st.warning("⚠️ Running in Demo Mode (Mock data active). Create a `.env` file to add your `GEMINI_API_KEY` for live execution.")
        
    st.divider()
    
    st.markdown("### Navigation")
    menu = st.radio(
        "Select Commander Hub:",
        [
            "📊 Executive Dashboard",
            "📥 CSV Quality Upload",
            "📋 ETL Log Ingest",
            "⚡ AI Root Cause Analysis",
            "🔍 Data Quality Profile",
            "🛠️ SQL Schema Fixer",
            "🐍 PySpark Pipeline Repair",
            "📦 AWS Glue Scaffolder",
            "📄 Post-Mortem Report",
            "💾 Export Incident Center"
        ]
    )

# Header Section
st.markdown("<h1 class='main-header'>DataSentinel AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Autonomous Data Quality Guardian & Incident Response Engine</p>", unsafe_allow_html=True)

# ----------------- SECTION 1: EXECUTIVE DASHBOARD -----------------
if menu == "📊 Executive Dashboard":
    st.markdown("### Systems & Pipeline Health Summary")
    
    # Key Stats Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-lbl'>Mean Time to Detect (MTTD)</div>
                <div class='metric-val'>3.4 Mins</div>
                <span class='badge badge-success'>-24% YoY</span>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-lbl'>Mean Time to Resolve (MTTR)</div>
                <div class='metric-val'>14.8 Mins</div>
                <span class='badge badge-success'>-68% YoY</span>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-lbl'>Active Incidents</div>
                <div class='metric-val'>1 Active</div>
                <span class='badge badge-critical'>SLA Risk: Medium</span>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class='metric-card'>
                <div class='metric-lbl'>Incidents Resolved (MTD)</div>
                <div class='metric-val'>24 Incidents</div>
                <span class='badge badge-info'>98.4% SLA Compliance</span>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    st.write("")
    
    # Graphs Section
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Incident Types Breakdown")
        df_incidents = pd.DataFrame({
            "Incident Category": ["Schema Drift", "Out Of Memory (OOM)", "Null Value Spikes", "Failed Type Casting", "Network Timeout"],
            "Count": [12, 8, 4, 3, 2]
        })
        fig1 = px.pie(df_incidents, values="Count", names="Incident Category", hole=.4, 
                      color_discrete_sequence=px.colors.qualitative.Prism)
        fig1.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)
        
    with g2:
        st.subheader("Resolution Time Trend (Hours)")
        df_trends = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Manual Triage (hrs)": [4.2, 5.0, 3.8, 4.5, 4.0, 3.5, 5.2],
            "DataSentinel AI (hrs)": [0.25, 0.3, 0.2, 0.28, 0.22, 0.24, 0.35]
        })
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_trends["Day"], y=df_trends["Manual Triage (hrs)"], name="Manual Baseline",
                                  line=dict(color='#EF4444', width=3, dash='dash')))
        fig2.add_trace(go.Scatter(x=df_trends["Day"], y=df_trends["DataSentinel AI (hrs)"], name="DataSentinel AI",
                                  line=dict(color='#10B981', width=4)))
        fig2.update_layout(margin=dict(t=20, b=20, l=20, r=20), xaxis_title="Timeline", yaxis_title="Hours to Resolve")
        st.plotly_chart(fig2, use_container_width=True)

    # Active alert table
    st.divider()
    st.subheader("Active Incidents Queue")
    st.markdown("""
    | Incident ID | Target Pipeline / Table | Trigger Component | Severity | Log Status | Detected Anomaly |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **INC-2026-8742** | `prod_analytics.staging_transactions` | AWS Glue Executor | <span class='badge badge-critical'>Critical</span> | Failed | Schema Drift & JVM Executor OOM |
    """, unsafe_allow_html=True)

# ----------------- SECTION 2: CSV QUALITY UPLOAD -----------------
elif menu == "📥 CSV Quality Upload":
    st.markdown("### Profile Data Quality & Check Anomalies")
    st.write("Upload a target data payload or use our preloaded sample dataset to analyze schema inconsistencies.")
    
    # File options
    uploaded_csv = st.file_uploader("Upload CSV file for validation:", type=["csv"])
    
    st.write("Or use pre-made testing samples:")
    if st.button("📥 Load Sample CSV Dataset (transactions_drift.csv)"):
        with open("samples/sample_data.csv", "r") as f:
            st.session_state["df_data"] = f.read()
            st.success("Loaded sample CSV dataset into session memory!")
            
    # Process
    raw_csv_content = None
    if uploaded_csv is not None:
        raw_csv_content = uploaded_csv.getvalue().decode("utf-8")
        st.session_state["df_data"] = raw_csv_content
        st.success("Uploaded file saved successfully!")
        
    if st.session_state["df_data"]:
        st.divider()
        st.write("### Data Preview")
        # Read into pandas
        try:
            df_preview = pd.read_csv(io.StringIO(st.session_state["df_data"]))
            st.dataframe(df_preview.head(8), use_container_width=True)
            
            if st.button("🔍 Run Data Profiling"):
                with st.spinner("Analyzing data rules, data structures, and outlier distributions..."):
                    st.session_state["df_analysis"] = analyze_csv_data(io.StringIO(st.session_state["df_data"]))
                    st.success("Data analysis complete! Go to the 'Data Quality Profile' navigation link to see details.")
        except Exception as e:
            st.error(f"Error reading file structure: {str(e)}")

# ----------------- SECTION 3: ETL LOG INGEST -----------------
elif menu == "📋 ETL Log Ingest":
    st.markdown("### Ingest ETL Execution Logs")
    st.write("Copy/paste raw logs or upload log outputs from AWS Glue, Apache Spark, or Airflow to isolate failure tracebacks.")
    
    uploaded_log = st.file_uploader("Upload log file:", type=["log", "txt"])
    
    st.write("Or use preloaded staging error log:")
    if st.button("📋 Load Sample AWS Glue Error Log"):
        with open("samples/sample_logs.log", "r") as f:
            st.session_state["log_text"] = f.read()
            st.success("Sample log loaded successfully!")
            
    # Input
    if uploaded_log is not None:
        st.session_state["log_text"] = uploaded_log.getvalue().decode("utf-8")
        st.success("Log file uploaded successfully!")
        
    st.divider()
    log_input = st.text_area("Staging Execution Logs:", value=st.session_state["log_text"], height=300)
    
    if log_input:
        st.session_state["log_text"] = log_input
        # Simple local parsing overview
        err_lines = [line for line in log_input.split('\n') if "ERROR" in line or "Exception" in line or "java.lang" in line]
        st.markdown(f"**Quick Stats:** Total log length: `{len(log_input.split(chr(10)))}` lines | Found `{len(err_lines)}` warnings/errors.")
        if err_lines:
            with st.expander("Detected Error Stack Trace"):
                for line in err_lines[:5]:
                    st.code(line)

# ----------------- SECTION 4: AI ROOT CAUSE ANALYSIS -----------------
elif menu == "⚡ AI Root Cause Analysis":
    st.markdown("### AI Root Cause Analysis (RCA)")
    st.write("Trigger Gemini to isolate error triggers, schema changes, and resource boundaries from log stack traces.")
    
    if not st.session_state["log_text"]:
        st.warning("Please upload or ingest execution logs first before running RCA.")
    else:
        st.write("Logs loaded. Ready for commander parsing.")
        if st.button("⚡ Run Root Cause Analysis (RCA)"):
            with st.spinner("Invoking Gemini Agent to analyze executor state and log tracebacks..."):
                rca_raw = get_ai_rca(st.session_state["log_text"])
                st.session_state["rca_result"] = rca_raw
                
        if st.session_state["rca_result"]:
            st.divider()
            st.markdown(st.session_state["rca_result"])

# ----------------- SECTION 5: DATA QUALITY PROFILE -----------------
elif menu == "🔍 Data Quality Profile":
    st.markdown("### Data Quality Profiling & Anomalies")
    
    if not st.session_state["df_analysis"]:
        st.warning("Please upload a CSV file and click 'Run Data Profiling' under the 'CSV Quality Upload' page first.")
    else:
        analysis = st.session_state["df_analysis"]
        
        # Grid stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", analysis["total_rows"])
        col2.metric("Total Columns", analysis["total_cols"])
        col3.metric("Duplicates Found", f"{analysis['duplicate_count']} ({analysis['duplicate_percentage']}%)")
        col4.metric("Flagged Anomalies", len(analysis["anomalies"]))
        
        # Missing values chart
        st.write("")
        st.subheader("Missing Values Frequency")
        miss_df = pd.DataFrame({
            "Column Name": list(analysis["missing_percentages"].keys()),
            "Missing Percentage (%)": list(analysis["missing_percentages"].values())
        })
        fig = px.bar(miss_df, y="Column Name", x="Missing Percentage (%)", orientation="h",
                     color="Missing Percentage (%)", color_continuous_scale="Reds")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Table of Anomalies
        st.subheader("Anomaly Registry")
        if len(analysis["anomalies"]) > 0:
            anom_df = pd.DataFrame(analysis["anomalies"])
            
            # Format display styling helper
            def get_badge(severity):
                if severity == "High":
                    return "🔴 High"
                elif severity == "Medium":
                    return "🟡 Medium"
                return "🔵 Low"
                
            anom_df["Severity"] = anom_df["severity"].apply(get_badge)
            st.table(anom_df[["column", "type", "Severity", "description"]])
        else:
            st.success("No critical schema anomalies or null distributions detected.")

# ----------------- SECTION 6: SQL SCHEMA FIXER -----------------
elif menu == "🛠️ SQL Schema Fixer":
    st.markdown("### SQL Schema Fix & DDL Generator")
    st.write("Generate clean SQL scripts to execute structural patches, cast variables, or repair values in database catalogs.")
    
    if not st.session_state["log_text"]:
        st.warning("Please ingest ETL log files first under the 'ETL Log Ingest' page to target schema fixes.")
    else:
        if st.button("🛠️ Generate SQL Fix Script"):
            anomalies = st.session_state["df_analysis"]["anomalies"] if st.session_state["df_analysis"] else None
            with st.spinner("AI compiling DDL schema fixes and casting commands..."):
                sql_fix = get_sql_fix(st.session_state["log_text"], anomalies)
                st.session_state["sql_fix"] = sql_fix
                
        if st.session_state["sql_fix"]:
            st.divider()
            st.write("#### Generated SQL Solution")
            st.code(st.session_state["sql_fix"], language="sql")

# ----------------- SECTION 7: PYSPARK PIPELINE REPAIR -----------------
elif menu == "🐍 PySpark Pipeline Repair":
    st.markdown("### PySpark Code Repair & Schema Alignment")
    st.write("Generates robust PySpark transformations to resolve schema drift, cast incompatible datatypes, and drop/impute null values.")
    
    if not st.session_state["log_text"]:
        st.warning("Please ingest staging logs under the 'ETL Log Ingest' page to target the PySpark repair logic.")
    else:
        if st.button("🐍 Generate PySpark Repair Code"):
            anomalies = st.session_state["df_analysis"]["anomalies"] if st.session_state["df_analysis"] else None
            with st.spinner("AI mapping PySpark dataframe casting logic and error handling pipelines..."):
                pyspark_fix = get_pyspark_fix(st.session_state["log_text"], anomalies)
                st.session_state["pyspark_fix"] = pyspark_fix
                
        if st.session_state["pyspark_fix"]:
            st.divider()
            st.write("#### Generated PySpark Script")
            st.code(st.session_state["pyspark_fix"], language="python")

# ----------------- SECTION 8: AWS GLUE SCAFFOLDER -----------------
elif menu == "📦 AWS Glue Scaffolder":
    st.markdown("### AWS Glue Job Template Generator")
    st.write("Create ready-to-run AWS Glue PySpark jobs incorporating the generated PySpark data repair solutions.")
    
    if not st.session_state["pyspark_fix"]:
        st.warning("Please generate the PySpark transformation script first on the 'PySpark Pipeline Repair' tab before building the Glue template.")
    else:
        if st.button("📦 Scaffold AWS Glue Job"):
            with st.spinner("AI wrapping dynamic frame schema models and AWS pipeline boilerplate..."):
                glue_job = get_aws_glue_job(st.session_state["log_text"], st.session_state["pyspark_fix"])
                st.session_state["glue_job"] = glue_job
                
        if st.session_state["glue_job"]:
            st.divider()
            st.write("#### Generated AWS Glue Job Template")
            st.code(st.session_state["glue_job"], language="python")

# ----------------- SECTION 9: POST-MORTEM REPORT -----------------
elif menu == "📄 Post-Mortem Report":
    st.markdown("### Post-Mortem Incident Report Generator")
    st.write("Compiles executive status files, incident stats, failure root causes, and generated code patches into a single document.")
    
    if not st.session_state["rca_result"]:
        st.warning("Please generate the AI Root Cause Analysis (RCA) under the 'AI Root Cause Analysis' page first.")
    else:
        if st.button("📄 Generate Comprehensive Report"):
            anomalies = st.session_state["df_analysis"]["anomalies"] if st.session_state["df_analysis"] else None
            with st.spinner("AI compiling markdown incident review summary..."):
                incident_report = get_incident_report(
                    st.session_state["log_text"],
                    st.session_state["rca_result"],
                    anomalies
                )
                st.session_state["incident_report"] = incident_report
                
        if st.session_state["incident_report"]:
            st.divider()
            st.markdown(st.session_state["incident_report"])

# ----------------- SECTION 10: EXPORT INCIDENT CENTER -----------------
elif menu == "💾 Export Incident Center":
    st.markdown("### Export & Download Center")
    st.write("Download formatted post-mortem incident documentation, SQL DDL migrations, or repaired PySpark scripts.")
    
    if not st.session_state["incident_report"]:
        st.warning("Please generate the Incident Post-Mortem Report on the 'Post-Mortem Report' tab first before downloading files.")
    else:
        st.subheader("Available Downloads")
        
        # 1. Markdown Report
        md_data = st.session_state["incident_report"]
        st.download_button(
            label="💾 Download Post-Mortem (Markdown)",
            data=md_data,
            file_name="datasentinel_incident_report.md",
            mime="text/markdown"
        )
        
        # 2. PDF Report
        try:
            with st.spinner("Rendering PDF document layout..."):
                pdf_bytes = generate_pdf_report(md_data)
                
            st.download_button(
                label="📕 Download Post-Mortem (PDF)",
                data=pdf_bytes,
                file_name="datasentinel_incident_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error compiling PDF: {str(e)}")
            
        # 3. SQL Repair Code
        if st.session_state["sql_fix"]:
            st.download_button(
                label="🛠️ Download SQL Fix Script (.sql)",
                data=st.session_state["sql_fix"],
                file_name="remediate_schema.sql",
                mime="text/plain"
            )
            
        # 4. PySpark Repair Code
        if st.session_state["pyspark_fix"]:
            st.download_button(
                label="🐍 Download PySpark Clean Script (.py)",
                data=st.session_state["pyspark_fix"],
                file_name="pyspark_remediation.py",
                mime="text/plain"
            )
