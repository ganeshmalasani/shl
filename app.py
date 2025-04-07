import streamlit as st
import faiss
import pickle
import numpy as np
import google.generativeai as genai
import os

# === Configure Gemini API ===
genai.configure(api_key="AIzaSyBZDJOoKDRnV89ME9QY5-xAeY5AgJS73bQ")

# === Load FAISS index and metadata ===
index = faiss.read_index("gemini_txt_index.faiss")
with open("gemini_txt_metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# === Setup folders ===
TEXT_FOLDER = "txts"

# === Mapping for test type full forms ===
test_type_map = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

# === Gemini summarization function ===
def gemini_summary(text):
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

# === FAISS Search + Summary Function ===
def search_assessments(query, top_k):
    try:
        # Embed query
        response = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_vector = np.array(response["embedding"], dtype=np.float32).reshape(1, -1)

        # FAISS search
        distances, indices = index.search(query_vector, top_k)
        results = []

        for i, idx in enumerate(indices[0]):
            match = metadata[idx]
            filename = match['filename']
            file_path = os.path.join(TEXT_FOLDER, filename)

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    summary = gemini_summary(text)
                    results.append({
                        "rank": i + 1,
                        "filename": filename,
                        "path": file_path,
                        "distance": distances[0][i],
                        "summary": summary
                    })
            else:
                results.append({
                    "rank": i + 1,
                    "filename": filename,
                    "path": file_path,
                    "distance": distances[0][i],
                    "summary": "❌ File not found"
                })

        return results

    except Exception as e:
        return [{"rank": 0, "filename": "N/A", "path": "", "distance": 0, "summary": f"❌ Error: {e}"}]

# === Streamlit App ===
st.set_page_config(page_title="SHL Assessment Search", layout="wide")
st.title("🔍 SHL Assessment Recommender")
st.markdown("Enter a natural language job role or skill you're hiring for. You'll receive top matching assessments with key attributes.")

query = st.text_input("💬 Enter your search query:", placeholder="e.g., cognitive ability test for data analysts")
top_k = st.slider("🔢 Number of results to show", 1, 10, 5)

if st.button("🔍 Search"):
    if query.strip():
        with st.spinner("Searching and summarizing..."):
            results = search_assessments(query, top_k)
            for res in results:
                st.subheader(f"{res['rank']}. {res['filename'].replace('_', ' ').replace('.txt', '')}")
                st.markdown(f"**Distance:** {res['distance']:.2f}")
                st.markdown(res['summary'], unsafe_allow_html=True)
                st.divider()

    else:
        st.warning("Please enter a query.")
