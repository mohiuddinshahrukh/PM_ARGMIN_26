import pandas as pd
import networkx as nx
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Cluster Arguments based on AMR Similarity")
    parser.add_argument("--input", required=True,
                        help="Path to your similarity XML/CSV file (e.g., results/similarity_claims.csv)")
    parser.add_argument("--threshold", type=float, default=0.65,
                        help="Similarity threshold to link arguments (0.0-1.0). Default: 0.65")
    parser.add_argument("--output", default="results/clustered_arguments.csv",
                        help="Output path (ends in .csv or .xml)")

    args = parser.parse_args()

    # 1. Load Similarity Data
    print(f"Loading pairs from {args.input}...")
    try:
        ext = os.path.splitext(args.input)[1].lower()
        if ext == '.xml':
            df = pd.read_xml(args.input)
        else:
            df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # 2. Filter by Threshold
    # We only want strong links to form tight clusters
    strong_links = df[df['score'] >= args.threshold]
    print(f"Filtering: {len(df)} pairs -> {len(strong_links)} strong links (score >= {args.threshold})")

    if strong_links.empty:
        print("No pairs met the threshold. Try lowering it?")
        return

    # 3. Build Graphs per Topic
    # We cluster within topics to avoid mixing unrelated debates
    all_clusters = []

    for topic, group in strong_links.groupby('topic'):
        G = nx.Graph()

        # Add edges (Links between arguments)
        for _, row in group.iterrows():
            G.add_edge(row['arg_A'], row['arg_B'], weight=row['score'])
            # Store text so we can retrieve it later
            if 'text_A' in row: G.nodes[row['arg_A']]['text'] = row['text_A']
            if 'text_B' in row: G.nodes[row['arg_B']]['text'] = row['text_B']

        # 4. Find Connected Components (The Clusters)
        clusters = list(nx.connected_components(G))

        for i, cluster_nodes in enumerate(clusters):
            cluster_id = f"{topic}_C{i + 1}"

            # Find Representative Argument (Highest Degree Centrality)
            best_rep = "Unknown"
            highest_score = -1

            node_texts = []
            for node in cluster_nodes:
                text = G.nodes[node].get('text', "")
                node_texts.append(text)

                # "Degree" = how many other arguments this one is similar to
                score = G.degree(node, weight='weight')
                if score > highest_score and len(text) > 10:  # Avoid tiny fragments
                    highest_score = score
                    best_rep = text

            # Add members to list
            for node, text in zip(cluster_nodes, node_texts):
                all_clusters.append({
                    'topic': topic,
                    'cluster_id': cluster_id,
                    'representative_arg': best_rep,
                    'argument_id': node,
                    'argument_text': text,
                    'cluster_size': len(cluster_nodes)
                })

    # 5. Save Results
    if not all_clusters:
        print("No clusters found.")
        return

    results_df = pd.DataFrame(all_clusters)

    # Sort: Topic -> Largest Clusters first -> Cluster ID
    results_df = results_df.sort_values(by=['topic', 'cluster_size', 'cluster_id'], ascending=[True, False, True])

    # Detect Output Format
    out_ext = os.path.splitext(args.output)[1].lower()
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    try:
        if out_ext == '.xml':
            results_df.to_xml(args.output, index=False, root_name='clusters', row_name='member')
            print(f"\nSuccess! Identified {results_df['cluster_id'].nunique()} clusters.")
            print(f"Saved to: {args.output} (XML Format)")
        else:
            results_df.to_csv(args.output, index=False)
            print(f"\nSuccess! Identified {results_df['cluster_id'].nunique()} clusters.")
            print(f"Saved to: {args.output} (CSV Format)")

        print("\n--- Preview: Largest Clusters ---")
        # Show one row per cluster
        print(results_df.drop_duplicates('cluster_id')[['topic', 'cluster_size', 'representative_arg']].head(
            10).to_string(index=False))

    except Exception as e:
        print(f"Error saving file: {e}")


if __name__ == "__main__":
    main()
