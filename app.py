import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(
    page_title="Web Scraping Assignment",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Python Web Scraping Assignment")
st.write("Scraped and processed data from multiple web sources.")

# Paths
base_dir = Path(__file__).parent
csv_file = base_dir / "output" / "final_dataset.csv"
json_file = base_dir / "output" / "summary_report.json"

# Dataset
if csv_file.exists():
    df = pd.read_csv(csv_file)

    st.subheader("📊 Dataset")
    st.write(f"Total records: **{len(df)}**")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download CSV",
        df.to_csv(index=False),
        "final_dataset.csv",
        "text/csv"
    )
else:
    st.error("Dataset file not found.")

# Summary
if json_file.exists():
    with open(json_file, "r", encoding="utf-8") as f:
        report = json.load(f)

    st.subheader("📈 Summary Report")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Records",
        report.get("total_records_collected", 0)
    )

    col2.metric(
        "Final Records",
        report.get("final_record_count", 0)
    )

    col3.metric(
        "Duplicates Removed",
        report.get("duplicate_records_detected_or_removed", 0)
    )

    st.json(report)
else:
    st.warning("Summary report not found.")
