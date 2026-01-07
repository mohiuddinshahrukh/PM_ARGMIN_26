import xml.etree.ElementTree as ET
import glob
import os
import pandas as pd


def parse_microtext_xml(filepath):
    """
    Parses a single Microtext XML file.
    Recovers: Metadata, Claims/Premises, Relations, and Full Text Context.
    """
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError:
        print(f"Warning: Failed to parse XML: {filepath}")
        return []

    file_id = root.get('id')
    topic_id = root.get('topic_id', 'MISSING_TOPIC')
    stance = root.get('stance', 'unknown')

    # 1. Map EDUs (Elementary Discourse Units)
    # Logic from File 5: Ensure correct sorting of segments
    edus = {}
    for edu in root.findall('edu'):
        eid = edu.get('id')
        text = edu.text.strip() if edu.text else ""
        edus[eid] = text

    # Reconstruct full document text (for context)
    # Sort by ID (e1, e2...) to ensure reading order
    sorted_edu_keys = sorted(edus.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
    full_doc_text = " ".join([edus[k] for k in sorted_edu_keys])

    # 2. Map ADU Segments & Relations (Logic from File 4)
    adu_segments = {}  # {adu_id: [edu_ids]}
    outgoing_edges = {}  # {src_adu: type}

    for edge in root.findall('edge'):
        src = edge.get('src')
        trg = edge.get('trg')
        etype = edge.get('type')

        if etype == 'seg':
            adu_segments.setdefault(trg, []).append(src)
        elif etype in ['sup', 'reb', 'und', 'add']:
            outgoing_edges[src] = etype

    # 3. Construct Rows
    rows = []
    for adu_id, edu_ids in adu_segments.items():
        # Classify Type
        edge_type = outgoing_edges.get(adu_id)
        if adu_id not in outgoing_edges:
            arg_type = 'claim'  # Root node
        elif edge_type in ['reb', 'und']:
            arg_type = 'objection'
        else:
            arg_type = 'premise'  # sup, add, etc.

        # Reconstruct ADU Fragment Text
        # Sort EDUs within the ADU (e.g. e3 before e4)
        edu_ids.sort(key=lambda x: int(x[1:]) if x[1:].isdigit() else 0)
        adu_text = " ".join([edus.get(eid, "") for eid in edu_ids])

        rows.append({
            'file_id': file_id,
            'topic_id': topic_id,
            'stance': stance,
            'adu_id': adu_id,
            'type': arg_type,
            'text': adu_text,
            'full_doc_text': full_doc_text,
            'relation_type': edge_type if edge_type else "root"
        })

    return rows


def load_corpus_to_dataframe(input_dir):
    all_data = []
    xml_files = glob.glob(os.path.join(input_dir, "*.xml"))

    print(f"Scanning {input_dir}... Found {len(xml_files)} files.")

    for f in xml_files:
        data = parse_microtext_xml(f)
        all_data.extend(data)

    return pd.DataFrame(all_data)
