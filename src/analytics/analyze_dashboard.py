import os
import json
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================
# PATHS
# ==========================
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PROCESSED = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "db" / "claims.db"
LOG_PATH = BASE_DIR / "logs" / "app.log"

# ==========================
# HELPER FUNCTIONS
# ==========================
def load_processed_claims():
    rows = []
    for file in DATA_PROCESSED.glob("processed_*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            rows.append({
                "file_name": file.name,
                "claim_id": data.get("claim_id", "N/A"),
                "error": data.get("error", ""),
                "validation_errors": ", ".join(data.get("validation_errors", [])),
                "has_summary": "summary" in data,
                "has_normalized": "normalized" in data,
            })
        except Exception as e:
            rows.append({"file_name": file.name, "error": str(e)})
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["file_name", "claim_id", "error", "validation_errors"])

def load_hitl_data():
    if not DB_PATH.exists():
        return pd.DataFrame(columns=["claim_id", "amount", "date", "errors"])
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM hitl_claims", conn)
    conn.close()
    return df

# ==========================
# DASHBOARD LAYOUT
# ==========================
st.set_page_config(page_title="Claims Processor Dashboard", layout="wide")

st.title("📊 Intelligent Claims Processing Dashboard")
st.markdown("Real-time analytics for processed insurance claims")

# Load data
processed_df = load_processed_claims()
hitl_df = load_hitl_data()

col1, col2, col3 = st.columns(3)
col1.metric("Total Processed", len(processed_df))
col2.metric("HITL Reviews", len(hitl_df))
col3.metric("Validation Failures", processed_df["validation_errors"].astype(bool).sum())

# ==========================
# SECTION 1: Processed Claims
# ==========================
st.subheader("🧾 Processed Claims Summary")
if not processed_df.empty:
    st.dataframe(processed_df, use_container_width=True)
    fig, ax = plt.subplots(figsize=(6, 3))
    processed_df["error"].value_counts().plot(kind="bar", ax=ax, title="Error Distribution")
    st.pyplot(fig)
else:
    st.info("No processed claims found yet. Run the pipeline first.")

# ==========================
# SECTION 2: HITL (Human in the Loop)
# ==========================
st.subheader("👨‍💼 Human-in-the-Loop Review Queue")
if not hitl_df.empty:
    st.dataframe(hitl_df, use_container_width=True)
else:
    st.success("No pending HITL reviews — all claims validated successfully!")

# ==========================
# SECTION 3: Logs Viewer
# ==========================
st.subheader("🧠 System Logs")
if LOG_PATH.exists():
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        log_lines = f.readlines()[-50:]
    st.text("".join(log_lines))
else:
    st.warning("No logs found yet.")
