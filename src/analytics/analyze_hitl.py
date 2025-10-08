import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "db" / "claims.db"

def analyze_hitl():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM hitl_claims", conn)
    conn.close()

    print("📊 HITL Claims Summary:")
    print(df.head())
    print("\n🔹 Total HITL claims:", len(df))
    print("🔹 Unique claim IDs:", df['claim_id'].nunique())
    print("🔹 Average errors per claim:", df['errors'].apply(lambda e: len(eval(e)) if e else 0).mean())

if __name__ == "__main__":
    analyze_hitl()
