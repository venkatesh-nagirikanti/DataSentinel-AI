import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize GenAI if key is present
def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        return None

def is_api_configured():
    return os.getenv("GEMINI_API_KEY") is not None and os.getenv("GEMINI_API_KEY") != ""

# Pre-canned mock responses for out-of-box demo validation
MOCK_RCA = """### 🚨 Incident Root Cause Analysis (RCA)

**Incident ID:** INC-2026-8742  
**Timestamp:** 2026-06-28 14:32:36 UTC  
**Primary Impact:** Critical failure on ETL pipeline task execution.  
**Severity:** Critical (P0)

---

#### 1. Executive Summary
During the execution of the transaction ingestion job, the system encountered a schema mismatch exception when writing out to the target table `prod_analytics.staging_transactions`. Almost simultaneously, the Spark executor threw a JVM OutOfMemoryError (OOM) due to memory exhaustion during aggregation calculations. The process crashed, yielding an exit code of 1.

#### 2. Root Cause Breakdown
1. **Schema Drift (Primary Blocker):**
   - **Target Catalog Expectation:** Column `amount` as `Decimal(10,2)` and column `device_type` as `StringType`.
   - **Source Dataset Payload:** Column `amount` was mapped as `DoubleType` and column `device_type` was completely missing.
   - **Failure Point:** Spark's `TableOutputResolver` raised a structural `AnalysisException` during output validation as it cannot implicitly downcast `DoubleType` to `Decimal(10,2)` without risk of precision loss, nor can it populate a table when a non-nullable required field is absent.
2. **Resource Exhaustion (Secondary Blocker):**
   - **Error Details:** `java.lang.OutOfMemoryError: Java heap space` on Spark Executor `0.0` at stage `3.0`.
   - **Failure Point:** The exception was raised inside `ObjectAggregationIterator.processInputs` during sorting. This points to a skewed data distribution or memory starvation on the worker instance which was unable to hold the unsorted keys in execution memory.

#### 3. Immediate Recommendations
* **Schema Mitigation:** Alter target table properties to support optional types, or implement explicit casting in the Glue script. Use a schema mapping layer to inject missing columns (`device_type` as null string).
* **Resource Scaling:** Scale the worker type from `G.1X` to `G.2X` or enable dynamic allocation and adjust `spark.executor.memory` configuration parameters.
"""

MOCK_SQL = """-- =====================================================================
-- DataSentinel AI - SQL Schema Repair & DDL Migration Script
-- Incident Context: Schema Drift Resolved on staging_transactions
-- Target Table: prod_analytics.staging_transactions
-- =====================================================================

-- Step 1: Evolve Schema to handle the missing 'device_type' column
ALTER TABLE prod_analytics.staging_transactions 
ADD COLUMN IF NOT EXISTS device_type VARCHAR(255) DEFAULT NULL;

-- Step 2: Create a View/CTE casting types explicitly to matching structures
CREATE OR REPLACE VIEW prod_analytics.v_cleaned_transactions AS
SELECT
    CAST(transaction_id AS VARCHAR(50)) AS transaction_id,
    CAST(user_id AS VARCHAR(50)) AS user_id,
    
    -- Explicitly cast Double to Decimal safely, clamping or rounding
    CAST(COALESCE(amount, 0.0) AS DECIMAL(10,2)) AS amount,
    
    -- Parse dates safely
    CASE 
        WHEN transaction_date LIKE '%/%' THEN TO_DATE(transaction_date, 'YYYY/MM/DD')
        WHEN transaction_date = 'INVALID_DATE' THEN NULL
        ELSE TO_DATE(transaction_date, 'YYYY-MM-DD')
    END AS transaction_date,
    
    CAST(country AS VARCHAR(100)) AS country,
    CAST(device_type AS VARCHAR(255)) AS device_type
FROM raw_incoming_transactions;

-- Step 3: Optional DML fix to clean anomalous negative amounts
UPDATE prod_analytics.staging_transactions
SET amount = ABS(amount)
WHERE amount < 0;
"""

MOCK_PYSPARK = """# =====================================================================
# DataSentinel AI - PySpark Schema Alignment & Healing Script
# Incident Context: Schema Drift Fix on Target Table staging_transactions
# =====================================================================
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, abs, to_date, when
from pyspark.sql.types import DecimalType, StringType

def heal_and_transform_data(input_df):
    spark = SparkSession.builder.getOrCreate()
    
    # 1. Address Schema Drift: Inject missing columns as String type
    target_columns = ["transaction_id", "user_id", "amount", "transaction_date", "country", "device_type"]
    healed_df = input_df
    
    if "device_type" not in healed_df.columns:
        print("Warning: [Schema Drift] Column 'device_type' missing. Injecting Empty column.")
        healed_df = healed_df.withColumn("device_type", lit(None).cast(StringType()))
        
    # 2. Correct Type Mismatches: Cast Double to Decimal(10,2)
    print("Alignment: Casting 'amount' to DecimalType(10,2)...")
    healed_df = healed_df.withColumn("amount", col("amount").cast(DecimalType(10, 2)))
    
    # 3. Clean anomalous values: Correct negative financial metrics
    print("Sanitization: Standardizing negative amounts to absolute values...")
    healed_df = healed_df.withColumn("amount", when(col("amount") < 0, abs(col("amount"))).otherwise(col("amount")))
    
    # 4. Standardize date format formats: parse slashes or invalid strings
    healed_df = healed_df.withColumn(
        "transaction_date",
        when(col("transaction_date").like("%/%"), to_date(col("transaction_date"), "yyyy/MM/dd"))
        .when(col("transaction_date") == "INVALID_DATE", None)
        .otherwise(to_date(col("transaction_date"), "yyyy-MM-dd"))
    )
    
    # Select final aligned structure
    return healed_df.select(*target_columns)
"""

MOCK_GLUE = """# =====================================================================
# DataSentinel AI - AWS Glue Job Generation Script
# Job Title: datasentinel_heal_staging_transactions
# =====================================================================
import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, lit, abs, to_date, when
from pyspark.sql.types import DecimalType, StringType

# Initialize Glue Context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# 1. Read Raw Source Catalog Data
print("Loading catalog dataset dynamic frame...")
source_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="prod_raw", 
    table_name="raw_transactions"
)
df = source_dyf.toDF()

# 2. Schema Repair & Transformation
# Heal missing schema column drift
if "device_type" not in df.columns:
    df = df.withColumn("device_type", lit(None).cast(StringType()))

# Cast Amount to correct precision matching Target Schema
df = df.withColumn("amount", col("amount").cast(DecimalType(10, 2)))

# Fix data quality errors: Correct negative values
df = df.withColumn("amount", when(col("amount") < 0, abs(col("amount"))).otherwise(col("amount")))

# Save output back into target database catalog
print("Writing healed dataframe to catalog Target staging_transactions...")
healed_dyf = glueContext.write_dynamic_frame.from_catalog(
    frame=glueContext.create_dynamic_frame.fromDF(df, glueContext, "healed_df"),
    database="prod_analytics",
    table_name="staging_transactions"
)

job.commit()
print("AWS Glue job completed successfully.")
"""

MOCK_REPORT = """# 📘 DataSentinel AI - Incident Post-Mortem Report

**Status:** Draft  
**Incident ID:** INC-2026-8742  
**Title:** Transaction ETL Failure: Schema Drift & OOM Crash  
**Assigned Lead:** Data Incident Commander  

---

## 1. Executive Summary
On June 28, 2026, the nightly transactional staging pipeline crashed. Immediate triage indicated a validation error when loading data into `prod_analytics.staging_transactions`, paired with JVM heap space depletion during key aggregations.

## 2. Quantitative Metrics
* **Total Records Inspected:** 16 records in raw payload.
* **Schema Anomalies Detected:** 2 critical drift failures.
* **Data Quality Score:** 68% Quality Rating.
* **Outliers & Bad Format Count:** 5 issues.

## 3. Root Cause Investigation
* **Schema Drift:** Source file format omitted field `device_type` and delivered column `amount` as `DoubleType` instead of the expected `Decimal(10,2)`. 
* **Executor OOM:** Exhausted heap space during `ObjectHashAggregateExec` logic.

## 4. Resolution & Corrective Actions
- [x] Add auto-alignment capabilities to PySpark loading step.
- [ ] Scale Glue Worker classes to handle volume surges.
- [ ] Set up automated schema drift alerting policies via EventBridge.

---
*Report compiled automatically by DataSentinel AI.*
"""

def get_ai_rca(log_content):
    if not is_api_configured():
        return MOCK_RCA
        
    model = get_gemini_model()
    if not model:
        return "Gemini API Configuration Error. Running in Demo Mode:\n\n" + MOCK_RCA

    prompt = f"""
    You are an Expert SRE, Principal Data Engineer, and Data Incident Commander.
    Analyze the following ETL/Spark/Glue pipeline log content and diagnose the error.
    
    Log Content:
    \"\"\"{log_content}\"\"\"
    
    Provide a professional Incident Root Cause Analysis (RCA). Your output must contain:
    1. Incident Summary (Incident ID, Timestamp, Primary Impact, Severity)
    2. Detailed Root Cause Breakdown (Explaining any Schema Drift, Exception Stacktraces, Memory / OOM failures, or configuration issues).
    3. Actionable Immediate Recommendations for resolution.
    
    Format the response using clean Markdown with clear headings and bullet points. Do not write code blocks here.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini API Error: {str(e)}\n\nFallback to Mock Analysis:\n\n" + MOCK_RCA

def get_sql_fix(log_content, anomalies=None):
    if not is_api_configured():
        return MOCK_SQL

    model = get_gemini_model()
    if not model:
        return MOCK_SQL

    anom_text = str(anomalies) if anomalies else "None"
    prompt = f"""
    You are a Principal Data Engineer.
    Write clean, database-agnostic SQL statements to fix the issues mentioned in these logs/anomalies.
    
    Log Error:
    \"\"\"{log_content}\"\"\"
    
    Data Profiler Anomalies:
    \"\"\"{anom_text}\"\"\"
    
    Provide a well-commented SQL script that:
    1. Repairs or evolves table schemas (e.g. ALTER TABLE statements) to solve schema drift.
    2. Generates queries to select/transform fields with proper type casts, date parsing, or missing column replacements.
    3. Performs DML operations to repair anomalies (e.g. null replacement, value bounds corrections).
    
    Return ONLY the code block containing valid SQL. Do not include any HTML tags.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"/* Gemini API Error: {str(e)} */\n\n" + MOCK_SQL

def get_pyspark_fix(log_content, anomalies=None):
    if not is_api_configured():
        return MOCK_PYSPARK

    model = get_gemini_model()
    if not model:
        return MOCK_PYSPARK

    anom_text = str(anomalies) if anomalies else "None"
    prompt = f"""
    You are a Senior Spark Developer.
    Write a Python PySpark script snippet that reads data, aligns target schema types, and fixes data quality failures.
    
    Logs:
    \"\"\"{log_content}\"\"\"
    
    Anomalies:
    \"\"\"{anom_text}\"\"\"
    
    Provide PySpark transformation code that:
    1. Checks for missing columns and adds them with safe defaults.
    2. Casts column data types to align with targets (e.g., DecimalType, DoubleType).
    3. Resolves negative amounts or other numerical anomalies.
    4. Handles invalid dates or nulls.
    
    Return ONLY python code. Code must contain functions or clear pipeline blocks.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"# Gemini API Error: {str(e)}\n\n" + MOCK_PYSPARK

def get_aws_glue_job(log_content, repair_code):
    if not is_api_configured():
        return MOCK_GLUE

    model = get_gemini_model()
    if not model:
        return MOCK_GLUE

    prompt = f"""
    You are an AWS Glue Expert.
    Write a complete AWS Glue PySpark job template that implements this repair/transformation logic.
    
    Log Error:
    \"\"\"{log_content}\"\"\"
    
    Transformation logic:
    \"\"\"{repair_code}\"\"\"
    
    Create a production-ready AWS Glue job script:
    1. Initialize Glue Job, GlueContext, Job parameters.
    2. Read from Database Catalog using dynamic frames.
    3. Apply the transformation/repair logic on DataFrame or DynamicFrame.
    4. Write output catalog.
    5. Call job.commit().
    
    Return ONLY clean python code for AWS Glue.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"# Gemini API Error: {str(e)}\n\n" + MOCK_GLUE

def get_incident_report(log_content, rca_text, anomalies=None):
    if not is_api_configured():
        return MOCK_REPORT

    model = get_gemini_model()
    if not model:
        return MOCK_REPORT

    anom_text = str(anomalies) if anomalies else "None"
    prompt = f"""
    You are a Principal AI Architect and SRE Manager.
    Generate a highly professional, comprehensive Data Incident Post-Mortem Report in Markdown format.
    
    Inputs:
    - Log Analysis: {log_content}
    - RCA details: {rca_text}
    - Profile Anomalies: {anom_text}
    
    Include standard sections:
    1. Metadata (Status, Incident ID, Incident Date, Incident Lead).
    2. Executive Summary.
    3. Failure Breakdown (Logs, Drift details, OOM causes).
    4. Quantified Quality Impact (Count of records, bad values).
    5. Action Plan & Timeline for permanent fixes.
    
    Write the response in structured, beautifully aligned Markdown format.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"# Gemini API Error: {str(e)}\n\n" + MOCK_REPORT
