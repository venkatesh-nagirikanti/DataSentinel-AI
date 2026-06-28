import pandas as pd
import numpy as np

def analyze_csv_data(file_path_or_buffer):
    """
    Performs comprehensive data profiling and quality analysis on a CSV input.
    Returns a dictionary of analysis results.
    """
    try:
        df = pd.read_csv(file_path_or_buffer)
    except Exception as e:
        return {"error": f"Failed to read CSV file: {str(e)}"}

    total_rows = len(df)
    total_cols = len(df.columns)
    
    # Missing values
    missing_counts = df.isnull().sum().to_dict()
    missing_percentages = {col: round((count / total_rows) * 100, 2) for col, count in missing_counts.items()}
    
    # Duplicates
    duplicate_count = df.duplicated().sum()
    duplicate_percentage = round((duplicate_count / total_rows) * 100, 2) if total_rows > 0 else 0
    
    # Data types
    dtypes = {col: str(val) for col, val in df.dtypes.items()}
    
    # Summary stats for numeric columns
    numeric_summary = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        col_clean = df[col].dropna()
        if not col_clean.empty:
            # Simple outlier detection (IQR)
            q1 = col_clean.quantile(0.25)
            q3 = col_clean.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = col_clean[(col_clean < lower_bound) | (col_clean > upper_bound)]
            
            numeric_summary[col] = {
                "mean": round(col_clean.mean(), 2),
                "median": round(col_clean.median(), 2),
                "min": round(col_clean.min(), 2),
                "max": round(col_clean.max(), 2),
                "std": round(col_clean.std(), 2),
                "outliers_count": len(outliers),
                "negative_count": int((col_clean < 0).sum())
            }
            
    # Schema checks & anomalies
    anomalies = []
    
    # 1. Null columns check
    for col, count in missing_counts.items():
        if count > 0:
            anomalies.append({
                "column": col,
                "type": "Missing Values",
                "severity": "High" if (count / total_rows) > 0.3 else "Medium",
                "description": f"Column '{col}' has {count} missing values ({missing_percentages[col]}%)."
            })
            
    # 2. Negative values in numeric columns (assuming they should be positive like amounts/counts)
    for col, stats in numeric_summary.items():
        if stats["negative_count"] > 0 and any(keyword in col.lower() for keyword in ["amount", "price", "count", "quantity", "id"]):
            anomalies.append({
                "column": col,
                "type": "Negative Value Anomaly",
                "severity": "Medium",
                "description": f"Column '{col}' contains {stats['negative_count']} negative values."
            })
            
    # 3. Numeric Outliers
    for col, stats in numeric_summary.items():
        if stats["outliers_count"] > 0:
            anomalies.append({
                "column": col,
                "type": "Statistical Outliers",
                "severity": "Low",
                "description": f"Column '{col}' has {stats['outliers_count']} statistical outliers (beyond 1.5x IQR)."
            })

    # 4. Date formatting issues
    date_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ["date", "time", "timestamp"])]
    for col in date_cols:
        invalid_dates = 0
        non_standard_dates = 0
        for val in df[col].dropna():
            val_str = str(val).strip()
            # Try parsing with standard Pandas to_datetime
            try:
                pd.to_datetime(val_str, errors='raise')
                # Check for formatting (expecting YYYY-MM-DD or similar)
                if "/" in val_str:
                    non_standard_dates += 1
            except (ValueError, TypeError):
                invalid_dates += 1
                
        if invalid_dates > 0:
            anomalies.append({
                "column": col,
                "type": "Invalid Date Format",
                "severity": "High",
                "description": f"Column '{col}' has {invalid_dates} unparsable date values."
            })
        if non_standard_dates > 0:
            anomalies.append({
                "column": col,
                "type": "Non-Standard Date Format",
                "severity": "Low",
                "description": f"Column '{col}' has {non_standard_dates} dates using slashes (/) instead of standard hyphens (-)."
            })

    return {
        "df": df,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "columns": df.columns.tolist(),
        "missing_counts": missing_counts,
        "missing_percentages": missing_percentages,
        "duplicate_count": int(duplicate_count),
        "duplicate_percentage": duplicate_percentage,
        "dtypes": dtypes,
        "numeric_summary": numeric_summary,
        "anomalies": anomalies
    }
