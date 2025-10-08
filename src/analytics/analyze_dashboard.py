import streamlit as st
import pandas as pd
import json
import os
import sqlite3
from pathlib import Path

# Define paths
DATA_PROCESSED_DIR = Path("data/processed")
DB_PATH = Path("db/claims.db")

st.set_page_config(page_title="Claims Processor Dashboard", layout="wide")

st.title("💼 Intelligent Claims Processing Dashboard")
st.markdown("Monitor your AI-powered claim extraction, validation, and approval pipeline in real-time.")

# ========== SECTION 1: Summary from JSON Files ==========
st.header("📊 Processed Claim Summary")

summary_path = DATA_PROCESSED_DIR / "summary.json"

if summary_path.exists():
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    success_count = len(df[df["status"] == "success"])
    failed_count = len(df[df["status"] == "failed"])

    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Successful Claims", success_count)
    col2.metric("❌ Failed Claims", failed_count)
    col3.metric("📁 Total Processed", len(df))

    st.dataframe(df[["file", "status", "output"]], use_container_width=True)
else:
    st.warning("No processed summary found yet. Run your claim processing first.")

# ========== SECTION 2: Processed JSONs ==========
st.header("🧾 Claim Data Explorer")

processed_files = list(DATA_PROCESSED_DIR.glob("processed_*.json"))

if processed_files:
    selected_file = st.selectbox("Select a processed claim file", processed_files)
    with open(selected_file, "r", encoding="utf-8") as f:
        claim_data = json.load(f)
    st.json(claim_data)
else:
    st.info("No processed claim JSONs found yet.")

# ========== SECTION 3: Human-in-the-Loop (HITL) Records ==========
st.header("🧍 Human-in-the-Loop (HITL) Review Records")

if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    try:
        df_hitl = pd.read_sql_query("SELECT * FROM hitl_claims", conn)
        if not df_hitl.empty:
            st.dataframe(df_hitl, use_container_width=True)
        else:
            st.info("No HITL records yet — all claims validated successfully 🎉")
    except Exception as e:
        st.error(f"Error reading HITL DB: {e}")
    finally:
        conn.close()
else:
    st.warning("HITL database not found yet. It will be created after validation step.")

# ========== SECTION 4: Insights ==========
st.header("📈 Insights")

if summary_path.exists():
    st.bar_chart(df["status"].value_counts())
    st.caption("Claim success vs failure rates")
else:
    st.info("Run at least one batch before viewing insights.")
