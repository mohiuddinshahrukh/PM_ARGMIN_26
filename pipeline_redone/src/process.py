import argparse
import pandas as pd
import amrlib
import itertools
from tqdm import tqdm
from modules.utils import load_data, save_data
from modules.amr_engine import SmatchScorer


def main():
    parser = argparse.ArgumentParser(description="AMR Parsing & Similarity Check")
    parser.add_argument("--input", required=True, help="Output from Step 1")
    parser.add_argument("--output", required=True, help="File to save similarity pairs")
    parser.add_argument("--model", default="amr_model", help="Path to AMR model")
    parser.add_argument("--threshold", type=float, default=0.65, help="Similarity threshold")
    args = parser.parse_args()

    # 1. Load Data
    df = load_data(args.input)

    # 2. AMR Parsing (Optimized)
    # Check if AMR already exists, if not, generate it
    if 'amr_penman' not in df.columns:
        print("\n--- Phase 1: AMR Parsing ---")
        try:
            stog = amrlib.load_stog_model(model_dir=args.model)
        except:
            print("Model path not found, downloading default...")
            stog = amrlib.load_stog_model()

        # Optimization: Parse unique sentences only
        unique_texts = df['text'].unique()
        print(f"Parsing {len(unique_texts)} unique text segments...")

        graphs = []
        batch_size = 16
        for i in tqdm(range(0, len(unique_texts), batch_size)):
            batch = unique_texts[i:i + batch_size]
            graphs.extend(stog.parse_sents(batch))

        lookup = dict(zip(unique_texts, graphs))
        df['amr_penman'] = df['text'].map(lookup)

        # Save intermediate state with AMR attached
        intermediate_path = args.input.replace('.csv', '_with_amr.csv').replace('.xml', '_with_amr.xml')
        save_data(df, intermediate_path)
    else:
        print("AMR data found in input. Skipping parsing.")

    # 3. Similarity Calculation
    print("\n--- Phase 2: Similarity Calculation ---")
    scorer = SmatchScorer()
    results = []

    # Group by Topic to limit comparisons (Optimization)
    grouped = df.groupby('topic_id')

    for topic, group in tqdm(grouped, total=len(grouped)):
        if len(group) < 2: continue

        # Compare every pair in the topic
        for (i, row_a), (j, row_b) in itertools.combinations(group.iterrows(), 2):
            # Calculate Score
            score = scorer.calculate(row_a['amr_penman'], row_b['amr_penman'])

            if score >= args.threshold:
                results.append({
                    'topic': topic,
                    'arg_A': row_a['adu_id'],
                    'arg_B': row_b['adu_id'],
                    'text_A': row_a['text'],
                    'text_B': row_b['text'],
                    'type_A': row_a['type'],
                    'type_B': row_b['type'],
                    'score': round(score, 3)
                })

    # 4. Save Results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by=['topic', 'score'], ascending=[True, False])
    save_data(results_df, args.output)


if __name__ == "__main__":
    main()
