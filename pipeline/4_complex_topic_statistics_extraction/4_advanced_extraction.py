import os
import argparse
import xml.etree.ElementTree as ET
import csv
import sys
from collections import defaultdict


def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            sys.exit(1)


def parse_xml_file(filepath):
    """
    Extracts Topic, Stance, Argument Units, AND Relations (Pairs).
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing {filepath}", file=sys.stderr)
        return None

    filename = os.path.basename(filepath)

    # 1. Attributes
    topic_id = root.get('topic_id')
    stance = root.get('stance', 'unknown')

    if not topic_id:
        return None

    # 2. Map EDU ID -> Text
    edu_map = {}
    for edu in root.findall('edu'):
        edu_id = edu.get('id')
        text = edu.text.strip() if edu.text else ""
        edu_map[edu_id] = text

    # 3. Build Graph Nodes (ADUs) & Edges
    adu_to_edu = {}  # {adu_id: edu_id}
    adu_edges = []  # List of (src_adu, trg_adu, type)

    # First pass: Map ADU to EDU (seg edges)
    for edge in root.findall('edge'):
        if edge.get('type') == 'seg':
            adu_to_edu[edge.get('trg')] = edge.get('src')

    # Second pass: Collect Argument Relations
    for edge in root.findall('edge'):
        edge_type = edge.get('type')
        if edge_type in ['sup', 'reb', 'und', 'add']:
            adu_edges.append({
                'src': edge.get('src'),
                'trg': edge.get('trg'),
                'type': edge_type
            })

    # 4. Classify Units & Build Pairs
    file_data = {
        'claims': [],
        'premises': [],
        'objections': [],
        'relations': []
    }

    # Helper to get text from ADU ID
    def get_text(adu_id):
        edu_id = adu_to_edu.get(adu_id)
        return edu_map.get(edu_id, None)

    # -- Identify Unit Types based on outgoing edges --
    # We need a map of outgoing edges per ADU to classify them
    outgoing_types = defaultdict(list)
    for rel in adu_edges:
        outgoing_types[rel['src']].append(rel['type'])

    # Get all ADU IDs
    all_adus = [adu.get('id') for adu in root.findall('adu')]

    for adu_id in all_adus:
        text = get_text(adu_id)
        if not text: continue

        types = outgoing_types.get(adu_id, [])

        # Classification Logic
        unit_data = {'text': text, 'source': filename}

        if not types:
            file_data['claims'].append(unit_data)
        elif 'sup' in types:
            file_data['premises'].append(unit_data)
        elif 'reb' in types or 'und' in types:
            file_data['objections'].append(unit_data)

    # -- Build Relation Pairs (Feature C) --
    for rel in adu_edges:
        src_text = get_text(rel['src'])
        trg_text = get_text(rel['trg'])

        # We only record pairs where both source and target resolve to text
        # (This skips 'undercuts' that target an *edge* instead of a node)
        if src_text and trg_text:
            file_data['relations'].append({
                'src_text': src_text,
                'trg_text': trg_text,
                'type': rel['type'],
                'source': filename
            })

    return {'topic_id': topic_id, 'stance': stance, 'data': file_data}


def write_csv(aggregated_data, output_path, requested_units):
    ensure_directory_exists(output_path)

    # Define columns: Topic, Stance, Stats... then Data
    fieldnames = ['topic_id', 'stance']

    # Add stats columns dynamically
    stats_cols = [f"count_{u}" for u in requested_units] + ['count_relations']
    fieldnames.extend(stats_cols)

    # Add data columns
    fieldnames.extend(requested_units)
    fieldnames.append('relations')

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for topic, stance_dict in aggregated_data.items():
                for stance, data in stance_dict.items():
                    row = {'topic_id': topic, 'stance': stance}

                    # Fill Data & Stats
                    for unit in requested_units:
                        items = data[unit]
                        row[f"count_{unit}"] = len(items)
                        # Format: "[filename] Text content"
                        row[unit] = " | ".join([f"[{x['source']}] {x['text']}" for x in items])

                    # Fill Relations
                    rels = data['relations']
                    row['count_relations'] = len(rels)
                    # Format: "[filename] Premise -> type -> Claim"
                    rel_strings = [
                        f"[{r['source']}] \"{r['src_text']}\" --{r['type']}--> \"{r['trg_text']}\""
                        for r in rels
                    ]
                    row['relations'] = " | ".join(rel_strings)

                    writer.writerow(row)

        print(f"Successfully wrote CSV to {output_path}")
    except IOError as e:
        print(f"Error writing CSV: {e}")


def write_xml(aggregated_data, output_path, requested_units):
    ensure_directory_exists(output_path)
    root = ET.Element("advanced_corpus")

    for topic, stance_dict in aggregated_data.items():
        topic_elem = ET.SubElement(root, "topic")
        topic_elem.set("id", topic)

        for stance, data in stance_dict.items():
            stance_elem = ET.SubElement(topic_elem, "stance")
            stance_elem.set("type", stance)

            # 1. Write Statistics as attributes
            stats_elem = ET.SubElement(stance_elem, "statistics")
            for unit in requested_units:
                stats_elem.set(f"count_{unit}", str(len(data[unit])))
            stats_elem.set("count_relations", str(len(data['relations'])))

            # 2. Write Units
            for unit_type in requested_units:
                if data[unit_type]:
                    container = ET.SubElement(stance_elem, unit_type)
                    for item in data[unit_type]:
                        entry = ET.SubElement(container, "item")
                        entry.set("source_file", item['source'])
                        entry.text = item['text']

            # 3. Write Relations
            if data['relations']:
                rel_container = ET.SubElement(stance_elem, "relations")
                for r in data['relations']:
                    pair = ET.SubElement(rel_container, "pair")
                    pair.set("type", r['type'])
                    pair.set("source_file", r['source'])

                    src = ET.SubElement(pair, "source_text")
                    src.text = r['src_text']

                    trg = ET.SubElement(pair, "target_text")
                    trg.text = r['trg_text']

    try:
        tree = ET.ElementTree(root)
        if hasattr(ET, "indent"):
            ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully wrote XML to {output_path}")
    except IOError as e:
        print(f"Error writing XML: {e}")


def main():
    parser = argparse.ArgumentParser(description="Advanced Argument Extractor with Stats and Relations.")

    parser.add_argument("input_dir", help="Directory containing XML files.")
    parser.add_argument("output_file", help="Path to output file (.csv or .xml).")
    parser.add_argument("--units", nargs='+', choices=['claims', 'premises', 'objections'],
                        default=['claims', 'premises', 'objections'],
                        help="Units to extract (default: all).")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' not found.")
        return

    # Structure: topic -> stance -> type -> list
    aggregated_data = defaultdict(lambda: defaultdict(lambda: {
        'claims': [], 'premises': [], 'objections': [], 'relations': []
    }))

    files_count = 0

    print(f"Scanning {args.input_dir}...")

    for filename in os.listdir(args.input_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(args.input_dir, filename)
            result = parse_xml_file(filepath)

            if result:
                files_count += 1
                t_id = result['topic_id']
                st = result['stance']
                data = result['data']

                # Merge into main dict
                for key in ['claims', 'premises', 'objections', 'relations']:
                    aggregated_data[t_id][st][key].extend(data[key])

    print(f"Processed {files_count} files.")

    if args.output_file.lower().endswith('.csv'):
        write_csv(aggregated_data, args.output_file, args.units)
    elif args.output_file.lower().endswith('.xml'):
        write_xml(aggregated_data, args.output_file, args.units)
    else:
        print("Error: Output file must have .csv or .xml extension")


if __name__ == "__main__":
    main()
