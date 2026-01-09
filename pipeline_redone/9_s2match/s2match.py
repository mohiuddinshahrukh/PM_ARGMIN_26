import sys
import os
import argparse
import itertools
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
    parser.add_argument("--input", required=True, help="Input CSV/XML (must contain 'amr_penman')")
    parser.add_argument("--output", default="results/s2_similarity.csv")
    parser.add_argument("--threshold", type=float, default=0.00, help="Minimum score to save")
    args = parser.parse_args()

    # 1. Load Data
    print(f"Loading data from {args.input}...")
    df = load_data(args.input)

    if 'fragment_text' in df.columns and 'text' not in df.columns:
        print("Fixing column names: 'fragment_text' -> 'text'")
        df['text'] = df['fragment_text']

    if 'amr_penman' not in df.columns:
        print("Error: Input file missing 'amr_penman'. Run 2_process.py first.")
        return

    # Filter out empty AMRs
    df = df[df['amr_penman'].notna() & (df['amr_penman'] != "")]
    print(f"Valid AMRs found: {len(df)}")

    results = []

    # 2. Group by Topic (Comparison Strategy)
    grouped = df.groupby('topic_id')

    print("Calculating Soft Similarity (S2Match)...")
    for topic, group in tqdm(grouped):
        if len(group) < 2: continue

        # Compare all pairs within the topic
        for (i, row_a), (j, row_b) in itertools.combinations(group.iterrows(), 2):

            # --- THE CORE CALL ---
            score = compute_s2match_score(row_a['amr_penman'], row_b['amr_penman'])
            # ---------------------

            if score >= args.threshold:
                results.append({
                    'topic': topic,
                    'arg_A': row_a['adu_id'],
                    'arg_B': row_b['adu_id'],
                    'text_A': row_a['text'],
                    'text_B': row_b['text'],
                    'type_A': row_a['type'],
                    'type_B': row_b['type'],
                    's2_score': round(score, 4)
                })

    # 3. Save Results
    if results:
        res_df = pd.DataFrame(results)
        res_df = res_df.sort_values(by=['topic', 's2_score'], ascending=[True, False])
        save_data(res_df, args.output)

        # Print Stats
        print("\n--- Results Summary ---")
        print(f"Total Pairs Found: {len(res_df)}")
        print(f"Average Score: {res_df['s2_score'].mean():.3f}")
        print("\nTop Match Example:")
        top = res_df.iloc[0]
        print(f"Score: {top['s2_score']}")
        print(f"A: {top['text_A']}")
        print(f"B: {top['text_B']}")
    else:
        print("No pairs found matching threshold.")


if __name__ == "__main__":
    main()
