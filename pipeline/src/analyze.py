import argparse
import pandas as pd
import networkx as nx
import random
from pyvis.network import Network
from modules.utils import load_data, ensure_dir


def main():
    parser = argparse.ArgumentParser(description="Cluster & Visualize Arguments")
    parser.add_argument("--input", required=True, help="Similarity file from Step 2")
    parser.add_argument("--output_html", default="results/graph.html", help="Path for visualization")
    parser.add_argument("--output_csv", default="results/clusters.csv", help="Path for cluster data")
    args = parser.parse_args()

    df = load_data(args.input)

    # 1. Build Graph
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row['arg_A'], row['arg_B'], weight=row['score'])
        # Store metadata
        G.nodes[row['arg_A']]['text'] = str(row['text_A'])
        G.nodes[row['arg_A']]['topic'] = row['topic']
        G.nodes[row['arg_B']]['text'] = str(row['text_B'])
        G.nodes[row['arg_B']]['topic'] = row['topic']

    # 2. Detect Clusters (Connected Components)
    clusters = []
    for comp in nx.connected_components(G):
        # Find representative (node with highest degree)
        subgraph = G.subgraph(comp)
        rep_node = max(subgraph.degree, key=lambda x: x[1])[0]
        rep_text = G.nodes[rep_node]['text']

        for node in comp:
            clusters.append({
                'cluster_id': f"C_{rep_node}",
                'rep_text': rep_text,
                'node_id': node,
                'text': G.nodes[node]['text'],
                'topic': G.nodes[node]['topic']
            })

    # Save Clusters
    pd.DataFrame(clusters).to_csv(args.output_csv, index=False)
    print(f"Clusters saved to {args.output_csv}")

    # 3. Visualize (PyVis)
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", cdn_resources='remote')

    # Generate colors per topic
    topics = list(set(c['topic'] for c in clusters))
    colors = {t: f"#{random.randint(0, 0xFFFFFF):06x}" for t in topics}

    for node in G.nodes(data=True):
        nid, attrs = node
        txt = attrs.get('text', "")
        topic = attrs.get('topic', "unknown")

        net.add_node(nid,
                     label=txt[:20] + "...",
                     title=txt,
                     color=colors.get(topic, "#ffffff"))

    for u, v, w in G.edges(data='weight'):
        net.add_edge(u, v, title=f"Score: {w}", value=w)

    ensure_dir(args.output_html)
    net.save_graph(args.output_html)
    print(f"Visualization saved to {args.output_html}")


if __name__ == "__main__":
    main()
