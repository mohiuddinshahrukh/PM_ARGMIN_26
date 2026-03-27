import pandas as pd
import argparse
import os
import sys
from tqdm import tqdm


# --- Smatch Wrapper Class ---
class SmatchScorer:
    def __init__(self):
        try:
            import smatch
            self.smatch = smatch
        except ImportError:
            print("Error: 'smatch' library not found.")
            print("Please run: pip install smatch")
            sys.exit(1)

    def calculate(self, str1, str2):
        # 1. Safety check
        if not isinstance(str1, str) or not isinstance(str2, str):
            return 0.0

        # 2. Clean the AMR
        def clean_amr_string(raw_text):
            lines = raw_text.split('\n')
            valid_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            return " ".join(valid_lines)

        line1 = clean_amr_string(str1)
        line2 = clean_amr_string(str2)

        if not line1 or not line2: return 0.0

        # 3. Calculate Score
        try:
            best_match, test_total, gold_total = self.smatch.get_amr_match(line1, line2)
        except Exception:
            return 0.0

        # 4. Compute F-Score with Safety Clamp
        if test_total == 0 or gold_total == 0:
            return 0.0

        precision = best_match / float(test_total)
        recall = best_match / float(gold_total)

        if precision + recall > 0:
            f_score = 2 * (precision * recall) / (precision + recall)
            return min(1.0, f_score)

        return 0.0


def main():
    parser = argparse.ArgumentParser(description="Calculate AMR Similarity by Argument Type")
    parser.add_argument("--input", required=True, help="Path to XML/CSV (must contain 'graph')")
    parser.add_argument("--output", default="similarity_results.csv", help="Output filename")

    args = parser.parse_args()

    # 1. Load Data
    print(f"Loading data from {args.input}...")
    try:
        ext = os.path.splitext(args.input)[1].lower()
        if ext == '.xml':
            df = pd.read_xml(args.input)
        else:
            df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 2. Critical Check
    if 'graph' not in df.columns:
        print("\nCRITICAL ERROR: Input file is missing AMR graphs.")
        return

    # 3. Run Analysis
    scorer = SmatchScorer()
    results = []

    # args.topic comes from argparse
        
    group_cols = ['id_pair']
    grouped = df.groupby(group_cols)

    print(f"Calculating similarity across {len(grouped)} groups...")

    for name, group in tqdm(grouped):

        # Extract text

        text_series = group["fragment_text"] if "fragment_text" in group.columns else group["my_sentence"]

        rows = list(zip(group['id_pair'], text_series, group['graph']))
        items = [ (rows[0], rows[1]) ] 
        for (id_pair, txt1, g1), (id_pair, txt2, g2) in items:
            score = scorer.calculate(g1, g2)

            if score > 0.01:
                results.append({
                    'pair_id': id_pair,
                    'score': round(score, 3),
                    'text_A': txt1,
                    'text_B': txt2
                })

    # 4. Save Results
    if results:
        res_df = pd.DataFrame(results)

        out_ext = os.path.splitext(args.output)[1].lower()
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

        try:
            if out_ext == '.xml':
                res_df.to_xml(args.output, index=False, root_name='similarities', row_name='pair')
                print(f"\nSuccess! Saved {len(res_df)} matches to {args.output} (XML Format)")
            else:
                res_df.to_csv(args.output, index=False)
                print(f"\nSuccess! Saved {len(res_df)} matches to {args.output} (CSV Format)")

            # Print a small preview, but truncate ONLY the print, not the file
            print(res_df.head(5).to_string(index=False, max_colwidth=50))

        except Exception as e:
            print(f"Error saving file: {e}")
    else:
        print("No similarities found.")


if __name__ == "__main__":
    main()
