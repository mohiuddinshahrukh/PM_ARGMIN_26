import pandas as pd
from pyvis.network import Network
import argparse
import os
import random
import networkx as nx


def main():
    parser = argparse.ArgumentParser(description="Visualize Detailed Argument Network")
    parser.add_argument("--input", required=True, help="Path to SIMILARITY file from Step 6 (output.xml)")
    parser.add_argument("--output", default="results/argument_map_detailed.html", help="Output path")
    parser.add_argument("--threshold", type=float, default=0.5, help="Minimum score to visualize connection")

    args = parser.parse_args()

    # 1. Output Path Logic
    output_path = args.output
    if not output_path.lower().endswith('.html'):
        output_path = os.path.join(output_path, "argument_map_detailed.html")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # 2. Load Similarity Data (Step 6 Output)
    print(f"Loading pairs from {args.input}...")
    try:
        if args.input.endswith('.xml'):
            df = pd.read_xml(args.input)
        else:
            df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Check if we have the right columns
    if 'text_A' not in df.columns:
        print(
            "Error: Input file missing 'text_A'. Make sure you use the output from Step 6 (Similarity), not Step 7 (Clusters).")
        return

    # Filter
    df = df[df['score'] >= args.threshold]
    print(f"Visualizing {len(df)} connections (score >= {args.threshold})...")

    # 3. Build Graph Data
    G_nx = nx.Graph()
    node_data = {}

    for _, row in df.iterrows():
        id_a, id_b = str(row['arg_A']), str(row['arg_B'])
        topic = row['topic']

        G_nx.add_edge(id_a, id_b, weight=row['score'])

        # Store metadata
        if id_a not in node_data:
            node_data[id_a] = {'text': str(row['text_A']), 'topic': topic}
        if id_b not in node_data:
            node_data[id_b] = {'text': str(row['text_B']), 'topic': topic}

    # 4. Initialize Pyvis (Remote CDN)
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white",
                  select_menu=True, filter_menu=True, cdn_resources='remote')

    topics = list(set(d['topic'] for d in node_data.values()))
    topic_colors = {t: f"#{random.randint(0, 0xFFFFFF):06x}" for t in topics}

    # 5. Add Nodes (With TEXT Labels)
    for node_id, data in node_data.items():
        full_text = data['text']
        topic = data['topic']

        # Create a readable label (first 5 words)
        words = full_text.split()
        label_text = " ".join(words[:5]) + "..." if len(words) > 5 else full_text

        degree = G_nx.degree[node_id]
        size = 15 + (degree * 3)

        hover_html = (f"<b>ID:</b> {node_id}<br><b>Topic:</b> {topic}<br><hr>{full_text}")

        net.add_node(
            node_id,
            label=label_text,  # <--- THIS IS THE FIX. Shows text, not ID.
            title=hover_html,
            color=topic_colors.get(topic, "#ffffff"),
            size=size,
            group=topic
        )

    # 6. Add Edges (With Score Labels)
    for _, row in df.iterrows():
        score = float(row['score'])
        net.add_edge(
            str(row['arg_A']),
            str(row['arg_B']),
            title=f"Score: {score}",
            label=f"{score:.2f}",  # <--- Shows score on the line
            value=score,
            color="#555555"
        )

    # 7. Save
    net.show_buttons(filter_=['physics'])
    net.save_graph(output_path)
    print(f"\nSuccess! Open: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
