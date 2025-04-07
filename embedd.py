

import os
import google.generativeai as genai
import pandas as pd

# ✅ Set your Gemini API key
genai.configure(api_key="AIzaSyAUcxNaVNh_JrDmofPy4YwoJa6LspRxQTA")  # Replace with your actual key

# ✅ Use Gemini's embedding model
embedding_model = genai.get_model("models/embedding-001")


# 📁 Folder containing .txt files
txt_folder = "txts"

# 📄 Output CSV file to store embeddings
output_csv = "embeddings.csv"

# 🧠 Prepare the CSV file
columns = ["filename"] + [f"dim_{i}" for i in range(768)]  # 768 is expected dimension size

if not os.path.exists(output_csv):
    pd.DataFrame(columns=columns).to_csv(output_csv, index=False)

# 📚 Load existing filenames to skip
existing = set(pd.read_csv(output_csv)["filename"].tolist())

# 🔁 Loop through and embed each txt file
for fname in os.listdir(txt_folder):
    if not fname.endswith(".txt") or fname in existing:
        continue

    file_path = os.path.join(txt_folder, fname)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"📌 Embedding: {fname}")
    try:
        response = embedding_model.embed_content(
            content=content,
            task_type="retrieval_document"  # Alternative: semantic_similarity
        )

        embedding = response["embedding"]
        row = [fname] + embedding

        # Append to CSV
        with open(output_csv, "a", encoding="utf-8", newline="") as f:
            pd.DataFrame([row]).to_csv(f, header=False, index=False)

        print(f"✅ Saved embedding for {fname}")

    except Exception as e:
        print(f"❌ Failed to embed {fname}: {e}")