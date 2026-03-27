import os
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import nltk
from pathlib import Path
import amrlib
import penman
import yaml


# --- Setup NLTK ---
def setup_nltk():
    required_packages = ['punkt', 'punkt_tab']
    for pkg in required_packages:
        try:
            # Check if tokenizer is available
            nltk.data.find(f'tokenizers/{pkg}')
        except LookupError:
            print(f"Downloading NLTK '{pkg}'...")
            nltk.download(pkg)


# --- Classification Logic ---
def determine_argument_type(adu_id, outgoing_edges):
    """
    Classifies an ADU as 'claim', 'objection', or 'premise' based on its outgoing edge.
    """
    # If no outgoing edges, it's the root node -> Major Claim
    if adu_id not in outgoing_edges:
        return 'claim'

    edge_type = outgoing_edges[adu_id]

    # Attack relations
    if edge_type in ['reb', 'und']:
        return 'objection'

    # Support relations (sup) or linking relations (add, exa)
    # Note: 'add' (addition) usually joins another node to form a support, effectively acting as a premise.
    if edge_type in ['sup', 'add', 'exa']:
        return 'premise'

    return 'premise'  # Default fallback


# --- Parsing Logic ---
def parse_sentence_pair(data, stog):
    results = []
    pairs = data["pairs"]

    for pair in pairs:
        id_pair = pair["id"]
        s1, s2 = pair["sentences"]
        
        texts = []
        text1 = s1["text"]
        text2 = s2["text"]
        texts.append(text1)
        texts.append(text2)

        # generate AMRs
        for text in texts:
            graph_string = stog.parse_sents([text])
            graph = penman.decode(graph_string[0])
            pretty = penman.encode(graph, indent=2)
            print(f"Building AMR graph for {text}")

            results.append({
                'id_pair': id_pair,
                'my_sentence': text,
                'graph': pretty
            })

    return results


# --- Main CLI Execution ---
def main():
    parser = argparse.ArgumentParser(description="Extract ADUs and build ADU AMR graphs")

    # Arguments
    parser.add_argument("--input",
                        default=None,
                        help="Path to the yaml file with minimal pairs.")

    parser.add_argument("--output",
                        required=True,
                        help="Full path for the output file (e.g., 'minimal_pairs_graph.xml')")
    
    parser.add_argument("--format",
                        choices=['csv', 'xml'],
                        help="Force output format (csv or xml). If omitted, inferred from filename.")
    
    parser.add_argument("--model", default="amr_model", help="Path to local AMR model (optional)")

    args = parser.parse_args()

    # 1. Setup
    setup_nltk()

    # 2. Input Validation
    #read yaml file

    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist.")
        return

    with open(args.input, "r") as f:
        data = yaml.safe_load(f)

    pairs = data.get("pairs", [])

    if not pairs:
        print(f"Error: No sentence pairs found in '{args.input}'.")
        return

    print(f"Found {len(pairs)} sentence pairs in '{args.input}'...")

    # 3. Load AMR Model
    print("\nLoading AMR Model...")
    try:
        if os.path.exists(args.model):
            print(f" - Loading local model from: {args.model}")
            stog = amrlib.load_stog_model(model_dir=args.model)
        else:
            print(f" - Local model not found at '{args.model}'.")
            print(" - Downloading/Loading default model (gsii-v3)...")
            stog = amrlib.load_stog_model()
    except Exception as e:
        print(f"Critical Error loading AMR model: {e}")
        return
        
    # 4. Processing
    all_sentences = []

    try:
        sentences = parse_sentence_pair(data, stog)
        if sentences:
            all_sentences.extend(sentences)
    except Exception as e:
        print(f"Warning: Failed to parse your yaml file: {e}")
    
    if not all_sentences:
        print("No results are obtained from your yaml file.")
        return
    
    df = pd.DataFrame(all_sentences)
    print(f"Successfully extracted {len(df)} sentences.")

    # Show classification stats
    print("\nExtraction Summary:")

    # 5. Handle Output Directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 6. Determine Format
    output_format = args.format
    if not output_format:
        suffix = output_path.suffix.lower()
        output_format = 'xml' if suffix == '.xml' else 'csv'

    # 7. Save File
    try:
        if output_format == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif output_format == 'xml':
            df.to_xml(output_path, index=False, root_name='arguments', row_name='argument', encoding='utf-8')

        print(f"\nSuccess! Results saved to: {output_path.resolve()}")

    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
