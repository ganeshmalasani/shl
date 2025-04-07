import pandas as pd
from bs4 import BeautifulSoup
import requests
import csv
import os
import time

input_csv = "step1_links_metadata.csv"
output_csv = "step2_details_with_pdf_links.csv"
fieldnames = ["title", "url", "description", "job_levels", "languages", "assessment_length", "fact_sheet_url"]

# Ensure output file exists
if not os.path.exists(output_csv):
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

df = pd.read_csv(input_csv)
done = set(pd.read_csv(output_csv)["url"]) if os.path.exists(output_csv) else set()

for _, row in df.iterrows():
    if row["url"] in done:
        continue

    print(f"🔍 Scraping: {row['title']}")
    try:
        res = requests.get(row["url"])
        soup = BeautifulSoup(res.text, "html.parser")

        def get_text_after_h4(label):
            h4 = soup.find("h4", string=label)
            return h4.find_next_sibling("p").text.strip() if h4 and h4.find_next_sibling("p") else ""

        fact_sheet_link = soup.select_one("ul.product-catalogue__downloads a[href$='.pdf']")
        pdf_url = fact_sheet_link["href"] if fact_sheet_link else ""

        data = {
            "title": row["title"],
            "url": row["url"],
            "description": get_text_after_h4("Description"),
            "job_levels": get_text_after_h4("Job levels"),
            "languages": get_text_after_h4("Languages"),
            "assessment_length": get_text_after_h4("Assessment length"),
            "fact_sheet_url": pdf_url
        }

        with open(output_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(data)
            print(f"✅ Saved details for: {row['title']}")

    except Exception as e:
        print(f"❌ Error scraping {row['title']}: {e}")

    time.sleep(1)
