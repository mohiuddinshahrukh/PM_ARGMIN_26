import sys
import os
import argparse
import pandas as pd
from tqdm import tqdm
import sys
import os

# 1. Get the directory where THIS script is located (.../pipeline_redone/9_s2match)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the parent directory (.../pipeline_redone)
# This is where the 'modules' folder lives
parent_dir = os.path.dirname(current_dir)

# 3. Add it to Python's path so it can find 'modules'
sys.path.append(parent_dir)
# Boilerplate to find modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if "src" in current_dir:
    sys.path.append(os.path.dirname(current_dir))
else:
    sys.path.append(current_dir)

from modules.utils import load_data, save_data
# Import our new advanced logic
from modules.s2Match_utils import compute_s2match_score


def main():
    parser = argparse.ArgumentParser(description="Run S2Match (Soft Similarity) Analysis")
    parser.add_argument("--input", required=True, help="Input CSV/XML (must contain 'graph')")
    parser.add_argument("--output", default="results/s2_similarity.csv")
    parser.add_argument("--threshold", type=float, default=0.00, help="Minimum score to save")
    args = parser.parse_args()

    # 1. Load Data
    print(f"Loading data from {args.input}...")
    df = load_data(args.input)

    if 'graph' not in df.columns:
        print("Error: Input file missing 'graph'.")
        return

    # Filter out empty AMRs
    df = df[df['graph'].notna() & (df['graph'] != "")]
    print(f"Valid AMRs found: {len(df)}")

    results = []

    # 2. Group by pairs
    group_cols = ['id_pair']
    grouped = df.groupby(group_cols)

    print("Calculating Soft Similarity (S2Match)...")
    for _, group in tqdm(grouped):

        text_series = group["fragment_text"] if "fragment_text" in group.columns else group["my_sentence"]

        rows = list(zip(group['id_pair'], text_series, group['graph']))
        items = [ (rows[0], rows[1]) ] 
        for (id_pair, txt1, g1), (id_pair, txt2, g2) in items:
            score = compute_s2match_score(g1, g2)

            if score > 0.01:
                results.append({
                    'pair_id': id_pair,
                    'score': round(score, 3),
                    'text_A': txt1,
                    'text_B': txt2
                })

    # 3. Save Results
    if results:
        res_df = pd.DataFrame(results)
        save_data(res_df, args.output)

        # Print Stats
        print("\n--- Results Summary ---")
        print(f"Total Pairs Found: {len(res_df)}")
        print("\nTop Match Example:")
        top = res_df.iloc[0]
        print(f"A: {top['text_A']}")
        print(f"B: {top['text_B']}")
    else:
        print("No pairs found matching threshold.")


if __name__ == "__main__":
    main()
