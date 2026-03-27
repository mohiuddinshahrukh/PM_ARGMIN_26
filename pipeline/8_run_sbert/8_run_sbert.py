import argparse
import pandas as pd
from tqdm import tqdm
import sys
import os

import sys
import os

# 1. Get the folder where THIS script is (e.g. .../10_run_sbert)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the parent folder (e.g. .../pipeline_redone)
# This is where the 'modules' folder lives
parent_dir = os.path.dirname(current_dir)

# 3. Add parent folder to Python's lookup path
sys.path.append(parent_dir)

# --- Now your imports will work ---
from modules.utils import load_data, save_data

# --- Boilerplate to find modules ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if "src" in current_dir:
    sys.path.append(os.path.dirname(current_dir))
else:
    sys.path.append(current_dir)

from modules.utils import load_data, save_data
from modules.sbert_engine import SBERTEngine


def main():
    parser = argparse.ArgumentParser(description="Run S-BERT Semantic Similarity")
    parser.add_argument("--input", required=True, help="Input CSV (e.g., results/1_extracted.csv)")
    parser.add_argument("--output", default="results/sbert_similarity.csv")
    parser.add_argument("--threshold", type=float, default=0.00, help="Minimum score to save")
    args = parser.parse_args()

    # 1. Load Data
    print(f"Loading data from {args.input}...")
    df = load_data(args.input)

    # --- ROBUST COLUMN DETECTION ---
    print(f"Columns found: {df.columns.tolist()}")

    # 1. Check for standard names
    possible_names = ['text', 'fragment_text', 'claim', 'argument', 'sentence', 'full_text']
    text_col = None

    for name in possible_names:
        if name in df.columns:
            text_col = name
            break

    # 2. If not found, try to find any column containing "text"
    if not text_col:
        for col in df.columns:
            if "text" in str(col).lower():
                text_col = col
                break

    # 3. Apply the fix
    if text_col and text_col != 'text':
        print(f"Mapping column '{text_col}' -> 'text'")
        df['text'] = df[text_col]
    elif not text_col:
        print("\n❌ CRITICAL ERROR: Could not find a text column!")
        print(f"Available columns: {df.columns.tolist()}")
        print("Please rename the column in your CSV to 'text' or update the script.")
        return
    # -------------------------------

    # 2. Initialize Engine
    engine = SBERTEngine()

    results = []

    # 3. Process by Topic (Grouped)
    grouped = df.groupby('topic_id')

    print("Calculating S-BERT Embeddings & Similarity...")

    for topic, group in tqdm(grouped):
        if len(group) < 2: continue

        # Optimization: Encode ALL texts in this topic at once (Batching)
        texts = group['text'].tolist()
        ids = group['adu_id'].tolist()
        types = group['type'].tolist()

        # Get Matrix (N x N similarity)
        sim_matrix = engine.calculate_pairwise_matrix(texts)

        # Extract upper triangle pairs (avoid duplicates and self-matches)
        n = len(texts)
        for i in range(n):
            for j in range(i + 1, n):
                score = float(sim_matrix[i][j])

                if score >= args.threshold:
                    results.append({
                        'topic': topic,
                        'arg_A': ids[i],
                        'arg_B': ids[j],
                        'text_A': texts[i],
                        'text_B': texts[j],
                        'type_A': types[i],
                        'type_B': types[j],
                        'sbert_score': round(score, 4)
                    })

    # 4. Save Results
    if results:
        res_df = pd.DataFrame(results)
        res_df = res_df.sort_values(by=['topic', 'sbert_score'], ascending=[True, False])
        save_data(res_df, args.output)

        print("\n--- Results Summary ---")
        print(f"Top Match Example (Score: {res_df.iloc[0]['sbert_score']}):")
        print(f"A: {res_df.iloc[0]['text_A']}")
        print(f"B: {res_df.iloc[0]['text_B']}")
    else:
        print("No pairs found matching threshold.")


if __name__ == "__main__":
    main()
