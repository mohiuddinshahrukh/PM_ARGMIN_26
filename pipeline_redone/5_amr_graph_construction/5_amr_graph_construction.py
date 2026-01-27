import os
import glob
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
def parse_microtext_xml_enhanced(filepath, target_types, stog):
    tree = ET.parse(filepath)
    root = tree.getroot()

    file_id = root.get('id')
    topic_id = root.get('topic_id', 'MISSING_TOPIC')
    if topic_id == "MISSING_TOPIC":
        return
    stance = root.get('stance', 'unknown')

    # 1. Collect and Sort EDUs (Elementary Discourse Units)
    edus = []
    for edu in root.findall('edu'):
        eid = edu.get('id')
        text = edu.text.strip() if edu.text else ""
        # Sort key: e1 -> 1, e2 -> 2
        sort_key = int(eid[1:]) if len(eid) > 1 and eid[1:].isdigit() else 0
        edus.append({
            'id': eid,
            'text': text,
            'sort_key': sort_key
        })

    # Restore reading order
    edus.sort(key=lambda x: x['sort_key'])

    # Reconstruct full document text for sentence segmentation
    full_doc_text = " ".join([e['text'] for e in edus])
    sentences = nltk.sent_tokenize(full_doc_text)

    # 2. Map Edges to determine Argument Types
    outgoing_edges = {}
    for edge in root.findall('edge'):
        src = edge.get('src')
        type_ = edge.get('type')
        if type_ != 'seg':  # Ignore segmentation edges
            outgoing_edges[src] = type_

    # 3. Map ADUs to their constituent EDUs
    adu_segments = {}
    for edge in root.findall('edge'):
        if edge.get('type') == 'seg':
            adu_id = edge.get('trg')
            edu_id = edge.get('src')
            if adu_id not in adu_segments:
                adu_segments[adu_id] = []
            adu_segments[adu_id].append(edu_id)

    # 4. Build Results
    results = []
    for adu_id, edu_ids in adu_segments.items():
        # Determine Type: Claim, Premise, or Objection
        arg_type = determine_argument_type(adu_id, outgoing_edges)

        # FILTER: Skip if this type wasn't requested by the user
        if arg_type not in target_types:
            continue

        # Sortpretty = penman.encode(graph, indent=2) EDU IDs within this ADU
        edu_ids.sort(key=lambda x: int(x[1:]) if len(x) > 1 and x[1:].isdigit() else 0)

        # Reconstruct the fragment text
        adu_texts = []
        for eid in edu_ids:
            txt = next((e['text'] for e in edus if e['id'] == eid), "")
            adu_texts.append(txt)
        adu_text = " ".join(adu_texts)

        # 5. Find the Full Sentence Context
        # Heuristic: Find the first sentence containing the ADU text
        context_sentence = adu_text  # Fallback
        for sent in sentences:
            if adu_text in sent:
                context_sentence = sent
                break

        is_major = (arg_type == 'claim')

        graph_string = stog.parse_sents([adu_text])
        graph = penman.decode(graph_string[0])
        pretty = penman.encode(graph, indent=2)
        print(f"Building AMR graph for {adu_text}")

        results.append({
            'file_id': file_id,
            'topic_id': topic_id,
            'adu_id': adu_id,
            'type': arg_type,  # New column: claim/premise/objection
            'is_major_claim': is_major,
            'stance': stance,
            'full_sentence': context_sentence,
            'fragment_text': adu_text,
            'graph': pretty
        })

    return results

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
    parser.add_argument("--input_dir",
                        default=None,
                        help="Path to the folder containing microtext corpus with input CSV/XML files.")
    
    parser.add_argument("--input_pair",
                        default=None,
                        help="Path to yaml file with a pair of sentences.")

    parser.add_argument("--output",
                        required=True,
                        help="Full path for the output file (e.g., 'results/output.csv')")

    parser.add_argument("--format",
                        choices=['csv', 'xml'],
                        help="Force output format (csv or xml). If omitted, inferred from filename.")

    # NEW FLAG: Filter by type
    parser.add_argument("--types",
                        nargs='+',
                        choices=['claim', 'premise', 'objection'],
                        default=['claim', 'premise', 'objection'],
                        help="Specify which argument types to extract. Default: all.")
    
    parser.add_argument("--model", default="amr_model", help="Path to local AMR model (optional)")

    args = parser.parse_args()

    # 1. Setup
    setup_nltk()

    if args.input_dir:

        # 2. Input Validation
        if not os.path.exists(args.input_dir):
            print(f"Error: Input directory '{args.input_dir}' does not exist.")
            return

        xml_files = glob.glob(os.path.join(args.input_dir, "*.xml"))
        if not xml_files:
            print(f"Error: No .xml files found in '{args.input_dir}'.")
            return

        print(f"Found {len(xml_files)} XML files in '{args.input_dir}'...")
        print(f"Extracting types: {', '.join(args.types)}")

    elif args.input_pair:

        #2. Input Validation
        #read yaml file

        if not os.path.exists(args.input_pair):
            print(f"Error: Input directory '{args.input_pair}' does not exist.")
            return

        with open(args.input_pair, "r") as f:
            data = yaml.safe_load(f)

        pairs = data.get("pairs", [])

        if not pairs:
            print(f"Error: No sentence pairs found in '{args.input_pair}'.")
            return

        print(f"Found {len(pairs)} sentence pairs in '{args.input_pair}'...")

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
    
    if args.input_dir:
        
        # 4. Processing
        all_claims = []
        for xml_file in xml_files:
            try:
                # Pass the requested types to the parser
                claims = parse_microtext_xml_enhanced(xml_file, args.types, stog)
                if claims:
                    all_claims.extend(claims)
            except Exception as e:
                print(f"Warning: Failed to parse {os.path.basename(xml_file)}: {e}")

        if not all_claims:
            print("No results found matching your criteria.")
            return

        df = pd.DataFrame(all_claims)
        print(f"Successfully extracted {len(df)} items.")

        # Show classification stats
        print("\nExtraction Summary:")
        print(df['type'].value_counts())

    elif args.input_pair:
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
