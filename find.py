import faiss
import pickle
import numpy as np
import google.generativeai as genai
import os

def gemini_summary(text):
    genai.configure(api_key="AIzaSyDd-A1Mtx8Ff_X438DAovMTo8MFTfhMGAc")
    query = f"""
Your job is to summarize this assessment description and give output like this as plain text:
- Assessment name and URL
- Remote Testing Support (Yes/No)
- Adaptive/IRT Support (Yes/No)
- Duration
- Test type

A - Ability & Aptitude  
B - Biodata & Situational Judgement  
C - Competencies  
D - Development & 360  
E - Assessment Exercises  
K - Knowledge & Skills  
P - Personality & Behavior  
S - Simulations

mention test type completely(full form)

Text:
{text}
"""

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {e}"
# === Step 1: Configure Gemini API ===
genai.configure(api_key="AIzaSyAUcxNaVNh_JrDmofPy4YwoJa6LspRxQTA")

# === Step 2: Load FAISS index and metadata ===
index = faiss.read_index("gemini_txt_index.faiss")

with open("gemini_txt_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# === Step 3: Define search function ===
def search_gemini_index(query, top_k=5, text_folder="txts"):
    try:
        # Embed the query
        response = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_vector = np.array(response["embedding"], dtype=np.float32).reshape(1, -1)

        # Perform FAISS search
        distances, indices = index.search(query_vector, top_k)

        print(f"\n🔍 Top {top_k} matches for: '{query}'\n")
        for i, idx in enumerate(indices[0]):
            match = metadata[idx]
            filename = match['filename']
            file_path = os.path.join(text_folder, filename)

            print(f"\n📄 {i+1}. {filename.replace('_', ' ').replace('.txt', '')}")
            print(f"→ Distance: {distances[0][i]:.2f}")
            print(f"→ File: {file_path}")

            if os.path.exists(file_path):
                print("\n--- Full Content ---")
                with open(file_path, "r", encoding="utf-8") as f:
                    print(gemini_summary(f.read()))
                print("-" * 60)
            else:
                print("❌ File not found:", file_path)

    except Exception as e:
        print(f"❌ Error during search: {e}")

# === Step 4: Run it ===
while True:
    query = input("\n💬 Enter your search query (or 'exit' to quit): ").strip()
    if query.lower() == "exit":
        break
    search_gemini_index(query)



