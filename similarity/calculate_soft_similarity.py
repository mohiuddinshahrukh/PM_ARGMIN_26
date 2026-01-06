import pandas as pd
import spacy
import penman
import numpy as np
from scipy.optimize import linear_sum_assignment
from tqdm import tqdm
import itertools

# Load the medium model with vectors
print("Loading spaCy vectors (en_core_web_md)...")
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Error: Model 'en_core_web_md' not found.")
    print("Please run: python -m spacy download en_core_web_md")
    exit()


def clean_graph_strict(amr_string):
    """
    Same cleaning function as before to ensure valid graphs.
    """
    if pd.isna(amr_string) or not isinstance(amr_string, str):
        return ""
    text = amr_string.replace("\\n", "\n")
    lines = text.split('\n')
    graph_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    clean_text = "\n".join(graph_lines).strip()
    if not clean_text.startswith('(') or not clean_text.endswith(')'):
        return ""
    return clean_text


def get_concepts(amr_text):
    """
    Parses AMR and returns a list of concept strings (e.g., ['dog', 'run-01']).
    Removes the IDs (d / dog) and keeps only 'dog'.
    """
    try:
        g = penman.decode(amr_text)
        # g.instances() returns triples like ('d', 'instance', 'dog')
        # We want the target ('dog')
        concepts = [t.target for t in g.instances()]

        # Clean concepts: remove frame numbers usually?
        # Actually for S2 match, 'run-01' vs 'run-02' should be similar.
        # We strip the -01 for vector lookup to get better matches.
        clean_concepts = []
        for c in concepts:
            # Remove -01, -02 etc for the vector lookup
            if "-" in c and c.split("-")[-1].isdigit():
                token = "-".join(c.split("-")[:-1])
            else:
                token = c
            clean_concepts.append(token)

        return clean_concepts
    except Exception:
        return []


def compute_soft_score(concepts1, concepts2):
    """
    Computes a soft F1 score between two lists of concepts using optimal alignment.
    """
    if not concepts1 or not concepts2:
        return 0.0

    # 1. Get vectors
    # We process them in batch with nlp.pipe if lists were huge, but here standard is fine
    # We treat the list of concepts as a "sentence" just to get tokens
    doc1 = nlp(" ".join(concepts1))
    doc2 = nlp(" ".join(concepts2))

    # 2. Build Similarity Matrix
    # Matrix shape: (len1, len2)
    # rows = doc1 tokens, cols = doc2 tokens
    sim_matrix = np.zeros((len(doc1), len(doc2)))

    for i, token1 in enumerate(doc1):
        for j, token2 in enumerate(doc2):
            sim_matrix[i, j] = token1.similarity(token2)

    # 3. Solve Optimal Assignment (Hungarian Algorithm)
    # We want to MAXIMIZE similarity.
    # linear_sum_assignment finds MINIMUM cost, so we pass negative similarity.
    row_ind, col_ind = linear_sum_assignment(-sim_matrix)

    # 4. Calculate Score (Soft Precision/Recall/F1)
    # Sum of similarities of the aligned pairs
    total_similarity = sim_matrix[row_ind, col_ind].sum()

    # Soft Precision: Total Sim / Count 1
    # Soft Recall: Total Sim / Count 2
    # But wait, linear_sum_assignment only matches up to min(len1, len2).
    # Unmatched items have effectively 0 similarity contribution.

    p = total_similarity / len(doc1)
    r = total_similarity / len(doc2)

    if p + r == 0:
        return 0.0

    f1 = 2 * p * r / (p + r)
    return f1


def main():
    input_file = "microtext_major_claims_amr.csv"
    output_file = "soft_similarity_scores.csv"

    print("Loading data...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print("Input file not found.")
        return

    # Clean
    df['clean_amr'] = df['amr_penman'].apply(clean_graph_strict)
    df = df[df['clean_amr'] != ""].copy()

    records = df.to_dict('records')
    pairs = list(itertools.combinations(records, 2))

    print(f"Calculating Soft Concept Scores for {len(pairs)} pairs...")

    results = []

    for item1, item2 in tqdm(pairs):
        c1 = get_concepts(item1['clean_amr'])
        c2 = get_concepts(item2['clean_amr'])

        score = compute_soft_score(c1, c2)

        pair_type = "same_topic" if item1['topic_id'] == item2['topic_id'] else "different_topic"

        results.append({
            'pair_type': pair_type,
            'soft_score': score,
            'topic_1': item1['topic_id'],
            'text_1': item1['text'],
            'text_2': item2['text']
        })

    # Save
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

    print("\n" + "=" * 40)
    print(f"✅ Soft Analysis Complete! Saved to '{output_file}'")

    avg_same = results_df[results_df['pair_type'] == 'same_topic']['soft_score'].mean()
    avg_diff = results_df[results_df['pair_type'] == 'different_topic']['soft_score'].mean()

    print(f"Average Soft Score (Same Topic):      {avg_same:.4f}")
    print(f"Average Soft Score (Different Topic): {avg_diff:.4f}")
    print("=" * 40)


if __name__ == "__main__":
    main()
