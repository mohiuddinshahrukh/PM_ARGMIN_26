import sys
import os
import argparse

# --- Boilerplate to find 'modules' ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from modules.loader import load_corpus_to_dataframe
from modules.utils import save_data


def main():
    parser = argparse.ArgumentParser(description="Generate clean input file for S-BERT")
    # Default to the standard corpus location, but allow changing it
    parser.add_argument("--input_dir", default="data/arg-microtexts/corpus/en",
                        help="Path to the folder containing raw XML files")
    parser.add_argument("--output", default="10_output/sbert_input.csv",
                        help="Where to save the clean CSV")
    args = parser.parse_args()

    print(f"Reading raw XMLs from: {args.input_dir}")

    # 1. Use the God Parser to get EVERYTHING (IDs, Topics, Text)
    df = load_corpus_to_dataframe(args.input_dir)

    if df.empty:
        print("❌ Error: No data found. Check your input path.")
        return

    # 2. Select ONLY what S-BERT needs
    # We filter for 'claim' and 'premise' usually, but let's keep everything for now.
    sbert_df = df[['topic_id', 'adu_id', 'type', 'text']].copy()

    # 3. Save it
    print(f"✅ Extracted {len(sbert_df)} arguments.")
    print(f"Saving to: {args.output}")
    save_data(sbert_df, args.output)


if __name__ == "__main__":
    main()