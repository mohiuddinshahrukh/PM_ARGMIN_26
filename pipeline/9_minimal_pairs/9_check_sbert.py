import argparse
import pandas as pd
import sys
import os

import sys
import os

import yaml

# 1. Get the folder where THIS script is (e.g. .../10_run_sbert)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the parent folder (e.g. .../pipeline_redone)
# This is where the 'modules' folder lives
parent_dir = os.path.dirname(current_dir)

# 3. Add parent folder to Python's lookup path
sys.path.append(parent_dir)

# --- Now your imports will work ---
from modules.utils import save_data

# --- Boilerplate to find modules ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if "src" in current_dir:
    sys.path.append(os.path.dirname(current_dir))
else:
    sys.path.append(current_dir)

from modules.utils import save_data
from modules.sbert_engine import SBERTEngine

def main():
    parser = argparse.ArgumentParser(description="Run S-BERT Semantic Similarity")
    parser.add_argument("--input", required=True, help="Input yaml file with minimal pairs")
    parser.add_argument("--output", default="results/sbert_similarity.csv")
    parser.add_argument("--threshold", type=float, default=0.00, help="Minimum score to save")
    args = parser.parse_args()

    # 1. Load Data
    #read yaml file

    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist.")
        return

    with open(args.input, "r") as f:
        data = yaml.safe_load(f)

    pairs = data.get("pairs", [])

    if not pairs:
        print(f"Error: No sentence pairs found in '{args.input}'.")
        return

    print(f"Found {len(pairs)} sentence pairs in '{args.input}'...")


    # 2. Initialize Engine
    engine = SBERTEngine()

    results = []

    # 3. Process

    print("Calculating S-BERT Embeddings & Similarity...")

    pairs = data["pairs"]

    for pair in pairs:
        id_pair = pair["id"]
        s1, s2 = pair["sentences"]
        
        text1 = s1["text"]
        text2 = s2["text"]

        score = engine.calculate_similarity(text1, text2)

        if score > 0.01:
                results.append({
                    'pair_id': id_pair,
                    'score': round(score, 4),
                    'text_A': text1,
                    'text_B': text2,
                })

    # 4. Save Results
    if results:
        res_df = pd.DataFrame(results)
        save_data(res_df, args.output)

        print("\n--- Results Summary ---")
        print(f"A: {res_df.iloc[0]['text_A']}")
        print(f"B: {res_df.iloc[0]['text_B']}")
    else:
        print("No pairs found matching threshold.")


if __name__ == "__main__":
    main()
