import requests
from bs4 import BeautifulSoup
import csv
import os
import time

BASE_URL = "https://www.shl.com"
csv_file = "step1_links_metadata.csv"
fieldnames = ["title", "url", "remote_testing", "adaptive_irt", "test_type"]

# Ensure CSV exists
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

def parse_listing_page(page_url):
    res = requests.get(page_url)
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select('div.custom__table-wrapper table tr[data-entity-id]')

    for row in rows:
        title_tag = row.select_one("td.custom__table-heading__title a")
        test_type_tags = row.select("td.product-catalogue__keys span")
        remote = row.select("td")[1].find("span", class_="-yes")
        adaptive = row.select("td")[2].find("span", class_="-yes")

        data = {
            "title": title_tag.text.strip(),
            "url": BASE_URL + title_tag["href"],
            "remote_testing": "Yes" if remote else "No",
            "adaptive_irt": "Yes" if adaptive else "No",
            "test_type": ", ".join(tag.text for tag in test_type_tags)
        }

        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(data)

        print(f"✅ Scraped: {data['title']}")

# Loop through all individual assessment pages
for start in range(12, 373, 12):  # 12 to 372 inclusive
    url = f"{BASE_URL}/solutions/products/product-catalog/?start={start}&type=1"
    print(f"🌐 Scraping page: {url}")
    try:
        parse_listing_page(url)
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed: {url} - {e}")
