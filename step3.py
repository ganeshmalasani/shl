import pandas as pd
import os
import requests
import time
from pdfminer.high_level import extract_text

# Paths
input_csv = "merged_step1_step2.csv"
pdf_folder = "pdfs"
txt_folder = "txts"

os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(txt_folder, exist_ok=True)

# Load data
df = pd.read_csv(input_csv)

for _, row in df.iterrows():
    try:
        title = str(row["title"]).strip()
        url = str(row["url"]).strip()
        description = str(row.get("description", "")).strip()
        job_levels = str(row.get("job_levels", "")).strip()
        languages = str(row.get("languages", "")).strip()
        assessment_length = str(row.get("assessment_length", "")).strip()
        remote_testing = str(row.get("remote_testing", "")).strip()
        adaptive_irt = str(row.get("adaptive_irt", "")).strip()
        test_type = str(row.get("test_type", "")).strip()
        pdf_url = str(row.get("fact_sheet_url", "")).strip()

        # Safe file name
        safe_filename = title.replace(" ", "_").replace("/", "-").replace("\\", "-")
        txt_path = os.path.join(txt_folder, f"{safe_filename}.txt")

        # Skip if already exists
        if os.path.exists(txt_path):
            continue

        print(f"📄 Generating file: {safe_filename}.txt")

        # Download and extract PDF content if available
        pdf_text = ""
        if pdf_url and pdf_url.startswith("http"):
            pdf_path = os.path.join(pdf_folder, f"{safe_filename}.pdf")
            try:
                response = requests.get(pdf_url, timeout=30)
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                pdf_text = extract_text(pdf_path).strip()
            except Exception as e:
                print(f"⚠️ Failed to fetch PDF for {title}: {e}")

        # Combine all content
        combined_text = f"""Title: {title}
URL: {url}

Remote Testing: {remote_testing}
Adaptive/IRT: {adaptive_irt}
Test Type: {test_type}
Languages: {languages}
Job Levels: {job_levels}
Assessment Length: {assessment_length}

Description:
{description}

PDF Text:
{pdf_text}
"""

        # Save .txt file
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(combined_text)

        print(f"✅ Saved: {txt_path}")
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error processing {row.get('title', 'UNKNOWN')}: {e}")
