import pandas as pd
from smatch import get_amr_match
import itertools
from tqdm import tqdm
import re


def clean_graph_strict(amr_string):
    """
    Robust cleaning for AMR strings.
    1. Un-escapes newlines from CSV format.
    2. REMOVES all metadata lines (starting with #).
    3. Returns only the graph structure (s-expression).
    """
    if pd.isna(amr_string) or not isinstance(amr_string, str):
        return ""

    # 1. Fix CSV newline escaping
    text = amr_string.replace("\\n", "\n")

    # 2. Split into lines and keep only non-comments
    lines = text.split('\n')
    graph_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]

    # 3. Rejoin
    clean_text = "\n".join(graph_lines).strip()

    # 4. Basic validation (must start with '(' and end with ')')
    if not clean_text.startswith('(') or not clean_text.endswith(')'):
        return ""

    return clean_text


def calculate_smatch_score(amr1, amr2):
    """
    Computes Smatch score between two clean AMR strings.
    """
    # Fail fast if empty
    if not amr1 or not amr2:
        return 0.0

    try:
        # get_amr_match returns generator (precision, recall, f_score)
        # We need the F-score (index 2)
        p, r, f_score = get_amr_match(amr1, amr2)
        return float(f_score)
    except AttributeError:
        # This catches the specific 'NoneType' error
        return 0.0
    except Exception:
        return 0.0


def main():
    input_file = "microtext_major_claims_amr.csv"
    output_file = "smatch_similarity_scores.csv"

    print(f"Loading {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("Error: Input file not found.")
        return

    # --- Pre-Processing ---
    print("Cleaning AMR graphs (removing metadata)...")
    # Apply strict cleaning
    df['clean_amr'] = df['amr_penman'].apply(clean_graph_strict)

    # Filter out any that failed to clean (became empty)
    valid_df = df[df['clean_amr'] != ""].copy()
    print(f"Original rows: {len(df)}")
    print(f"Valid rows after cleaning: {len(valid_df)}")

    if len(valid_df) < 2:
        print("Not enough valid graphs to compare.")
        return

    # --- Pair Generation ---
    records = valid_df.to_dict('records')
    # Generate all unique pairs
    pairs = list(itertools.combinations(records, 2))
    print(f"Calculating scores for {len(pairs)} pairs...")

    results = []

    # Use tqdm for progress bar
    for item1, item2 in tqdm(pairs):
        score = calculate_smatch_score(item1['clean_amr'], item2['clean_amr'])

        # Determine relationship
        pair_type = "same_topic" if item1['topic_id'] == item2['topic_id'] else "different_topic"

        results.append({
            'file_id_1': item1['file_id'],
            'file_id_2': item2['file_id'],
            'topic_1': item1['topic_id'],
            'topic_2': item2['topic_id'],
            'pair_type': pair_type,
            'smatch_score': score,
            'text_1': item1['text'],
            'text_2': item2['text']
        })

    # --- Save & Summary ---
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

    print("\n" + "=" * 40)
    print(f"✅ Analysis Complete! Saved to '{output_file}'")

    if not results_df.empty:
        avg_same = results_df[results_df['pair_type'] == 'same_topic']['smatch_score'].mean()
        avg_diff = results_df[results_df['pair_type'] == 'different_topic']['smatch_score'].mean()

        print(f"Average Similarity (Same Topic):      {avg_same:.4f}")
        print(f"Average Similarity (Different Topic): {avg_diff:.4f}")

        if avg_same > avg_diff:
            print("\nResult: Hypothesis supported! Arguments on the same topic are more semantically similar.")
        else:
            print("\nResult: Hypothesis unclear. Scores are close.")
    else:
        print("No results generated.")
    print("=" * 40)


if __name__ == "__main__":
    main()
