import os
import argparse
import xml.etree.ElementTree as ET
import csv
import sys


def parse_microtext_file(filepath):
    """
    Parses a single XML file and categorizes ADUs into Claims, Premises, and Objections.
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing {filepath}", file=sys.stderr)
        return None

    # 1. Map EDUs to Text
    edu_map = {}  # {id: text}
    for edu in root.findall('edu'):
        edu_id = edu.get('id')
        text = edu.text.strip() if edu.text else ""
        edu_map[edu_id] = text

    # 2. Map ADUs to EDUs (via 'seg' edges)
    # and Identify Edge Relations
    adu_to_edu = {}  # {adu_id: edu_id}
    outgoing_edges = {}  # {src_adu_id: [(type, trg_adu_id)]}
    all_adu_ids = set()

    # Get all ADUs first to ensure existence
    for adu in root.findall('adu'):
        all_adu_ids.add(adu.get('id'))

    for edge in root.findall('edge'):
        edge_type = edge.get('type')
        src = edge.get('src')
        trg = edge.get('trg')

        if edge_type == 'seg':
            # src is edu, trg is adu
            adu_to_edu[trg] = src
        elif edge_type in ['sup', 'reb', 'und', 'add']:
            # These are argument relations between ADUs
            if src not in outgoing_edges:
                outgoing_edges[src] = []
            outgoing_edges[src].append(edge_type)

    # 3. Classify ADUs
    results = {
        'claims': [],
        'premises': [],
        'objections': []
    }

    for adu_id in all_adu_ids:
        # Get the text for this ADU
        edu_id = adu_to_edu.get(adu_id)
        text = edu_map.get(edu_id, "[Text not found]")

        edges = outgoing_edges.get(adu_id, [])

        # Check for Claim (Root node - no outgoing argument edges)
        if not edges:
            results['claims'].append(text)

        # Check for Premise
        if 'sup' in edges:
            results['premises'].append(text)

        # Check for Objection
        if 'reb' in edges or 'und' in edges:
            results['objections'].append(text)

    return results


def ensure_directory_exists(file_path):
    """
    Checks if the directory for the file exists, creates it if not.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            sys.exit(1)


def write_csv(data, output_path):
    # Ensure folder exists before writing
    ensure_directory_exists(output_path)

    # data format: [{'file': name, 'type': type, 'text': text}, ...]
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'type', 'text'])
        writer.writeheader()
        writer.writerows(data)
    print(f"Successfully wrote CSV to {output_path}")

def write_xml(data, output_path):
    # Ensure folder exists before writing
    ensure_directory_exists(output_path)

    root = ET.Element("extraction_results")

    for entry in data:
        item = ET.SubElement(root, "item")

        fname = ET.SubElement(item, "filename")
        fname.text = entry['filename']

        etype = ET.SubElement(item, "type")
        etype.text = entry['type']

        content = ET.SubElement(item, "text")
        content.text = entry['text']

    tree = ET.ElementTree(root)

    # Pretty print
    ET.indent(tree, space="  ", level=0)

    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Successfully wrote XML to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract arguments from Microtext Corpus XMLs.")

    parser.add_argument("input_dir", help="Path to the directory containing XML files")
    parser.add_argument("--extract", nargs='+', choices=['claims', 'premises', 'objections'],
                        required=True, help="Which attributes to extract (space separated)")
    parser.add_argument("--output", required=True, help="Path to output file (must end in .csv or .xml)")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' not found.")
        return

    all_extracted_data = []

    # Iterate over XML files
    for filename in os.listdir(args.input_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(args.input_dir, filename)
            file_results = parse_microtext_file(filepath)

            if file_results:
                # Flatten results based on user request
                for req_type in args.extract:
                    for text_segment in file_results.get(req_type, []):
                        all_extracted_data.append({
                            'filename': filename,
                            'type': req_type,
                            'text': text_segment
                        })

    # Output generation
    if args.output.lower().endswith('.csv'):
        write_csv(all_extracted_data, args.output)
    elif args.output.lower().endswith('.xml'):
        write_xml(all_extracted_data, args.output)
    else:
        print("Error: Output file must represent .csv or .xml extension")


if __name__ == "__main__":
    main()
