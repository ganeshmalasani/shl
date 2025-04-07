import pandas as pd

# Load the CSVs
csv1 = "step1_links_metadata.csv"
csv2 = "step2_details_with_pdf_links.csv"
output_csv = "merged_step1_step2.csv"

# Read both files
df1 = pd.read_csv(csv1)
df2 = pd.read_csv(csv2)

# Merge on title and url
merged_df = pd.merge(df1, df2, on=["title", "url"], how="inner")

# Save to new CSV
merged_df.to_csv(output_csv, index=False, encoding="utf-8")
print(f"✅ Merged CSV saved to {output_csv}")
