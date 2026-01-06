import os
import argparse
import xml.etree.ElementTree as ET
import csv
import sys
from collections import defaultdict


def ensure_directory_exists(file_path):
    """
    Checks if the directory for the file exists, creates it if not.
    """
    directory = os.path.dirname(file_path)
    # Only create if a directory path is actually provided (e.g. not just "output.csv")
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")
            sys.exit(1)


def get_argument_units(filepath):
    """
    Parses a file and returns the topic_id and a dictionary of extracted text units.
    Returns: (topic_id, { 'claims': [], 'premises': [], 'objections': [] })
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Error parsing {filepath}", file=sys.stderr)
        return None, None, None

    # 1. Get Topic ID
    topic_id = root.get('topic_id')
    if not topic_id:
        return None, None, None
    
    # 1.2. Get Microtext ID
    microtext_id = root.get('id')

    # 2. Map EDU ID -> Text
    edu_map = {}
    for edu in root.findall('edu'):
        edu_id = edu.get('id')
        text = edu.text.strip() if edu.text else ""
        edu_map[edu_id] = text

    # 3. Map ADU connections
    adu_to_edu = {}
    outgoing_edges = {}
    all_adu_ids = set()

    for adu in root.findall('adu'):
        all_adu_ids.add(adu.get('id'))

    for edge in root.findall('edge'):
        edge_type = edge.get('type')
        src = edge.get('src')
        trg = edge.get('trg')

        if edge_type == 'seg':
            adu_to_edu[trg] = src
        elif edge_type in ['sup', 'reb', 'und', 'add']:
            if src not in outgoing_edges:
                outgoing_edges[src] = []
            outgoing_edges[src].append(edge_type)

    # 4. Classify Units
    file_units = {
        'claims': [],
        'premises': [],
        'objections': []
    }

    for adu_id in all_adu_ids:
        edges = outgoing_edges.get(adu_id, [])

        # Determine Type based on edges
        unit_type = None
        if not edges:
            unit_type = 'claims'
        elif 'sup' in edges:
            unit_type = 'premises'
        elif 'reb' in edges or 'und' in edges:
            unit_type = 'objections'

        if unit_type:
            edu_id = adu_to_edu.get(adu_id)
            text_content = edu_map.get(edu_id, "")
            if text_content:
                file_units[unit_type].append(text_content)
    
    return topic_id, microtext_id, file_units

def write_csv(aggregated_data, output_path, requested_units):
    """
    Writes data where each row is a Topic, and columns contain ALL combined texts for that unit type.
    """
    ensure_directory_exists(output_path)  # <--- Added check here

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            fieldnames = ['topic_id'] + ['file_id'] + requested_units
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for topic, file in aggregated_data.items():
                for file_id, units in file.items():
                    row = {'topic_id': topic, 'file_id': file_id}
                    for unit_type in requested_units:
                    # Join multiple premises/claims with a separator (e.g., " | ")
                        combined_text = " | ".join(units[unit_type])
                        row[unit_type] = combined_text
                    writer.writerow(row)

        print(f"Successfully wrote grouped CSV to {output_path}")
    except IOError as e:
        print(f"Error writing CSV: {e}")


def write_xml(aggregated_data, output_path, requested_units):
    """
    Writes a hierarchical XML.
    """
    ensure_directory_exists(output_path)  # <--- Added check here

    root = ET.Element("grouped_corpus")

    for topic, file in aggregated_data.items():
        topic_elem = ET.SubElement(root, "topic")
        topic_elem.set("id", topic)

        for unit_type in requested_units:
            all_items = []

            for file_id, units in file.items():
                for text_segment in units[unit_type]:
                        all_items.append((file_id, text_segment))
            
            container = ET.SubElement(topic_elem, unit_type)
            container.set("count", str(len(all_items)))

            for file_id, text in all_items:
                item = ET.SubElement(container, "item", file_id=file_id)
                item.text = text

    try:
        tree = ET.ElementTree(root)
        if hasattr(ET, "indent"):
            ET.indent(tree, space="  ", level=0)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        print(f"Successfully wrote grouped XML to {output_path}")
    except IOError as e:
        print(f"Error writing XML: {e}")


def main():
    parser = argparse.ArgumentParser(description="Group arguments by Topic ID from Microtext Corpus.")

    parser.add_argument("input_dir", help="Directory containing XML files.")
    parser.add_argument("output_file", help="Path to output file (.csv or .xml).")
    parser.add_argument("--units", nargs='+', choices=['claims', 'premises', 'objections'],
                        required=True, help="Which units to extract and group.")

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' not found.")
        return

    # Data Structure: { topic_id: { 'claims': [], 'premises': [], ... } }
    #aggregated_data = defaultdict(lambda: {'claims': [], 'premises': [], 'objections': []})
    aggregated_data = defaultdict(
    lambda: defaultdict(
        lambda: {'claims': [], 'premises': [], 'objections': []}
        )
    )

    files_processed = 0

    print(f"Scanning {args.input_dir}...")

    for filename in os.listdir(args.input_dir):
        if filename.endswith(".xml"):
            filepath = os.path.join(args.input_dir, filename)
            topic, file_id, units = get_argument_units(filepath)

            if topic and units:
                files_processed += 1
                # Aggregate data into the main dictionary
                for key in ['claims', 'premises', 'objections']:
                    aggregated_data[topic][file_id][key].extend(units[key])
    
    print(f"Processed {files_processed} files.")
    print(f"Found {len(aggregated_data)} unique topics.")

    # Output generation
    if args.output_file.lower().endswith('.csv'):
        write_csv(aggregated_data, args.output_file, args.units)
    elif args.output_file.lower().endswith('.xml'):
        write_xml(aggregated_data, args.output_file, args.units)
    else:
        print("Error: Output file must represent .csv or .xml extension")


if __name__ == "__main__":
    main()
