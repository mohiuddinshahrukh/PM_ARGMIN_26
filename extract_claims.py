import os
import glob
import xml.etree.ElementTree as ET
import pandas as pd


def parse_microtext_xml(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    file_id = root.get('id')
    topic_id = root.get('topic_id', 'MISSING_TOPIC')  # Handles missing topics
    stance = root.get('stance', 'unknown')

    # 1. Map EDU IDs to their Text
    edu_map = {}
    for edu in root.findall('edu'):
        # .strip() removes surrounding whitespace/newlines
        edu_map[edu.get('id')] = edu.text.strip() if edu.text else ""

    # 2. Map ADU IDs to their constituent EDU IDs
    # The link is defined in edges with type="seg"
    adu_segments = {}
    for edge in root.findall('edge'):
        if edge.get('type') == 'seg':
            adu_id = edge.get('trg')
            edu_id = edge.get('src')

            if adu_id not in adu_segments:
                adu_segments[adu_id] = []
            adu_segments[adu_id].append(edu_id)

    # 3. Identify the "Major Claim" (Root of the graph)
    # The Major Claim is an ADU that is NOT the source of any support/attack edge.
    # It is the final conclusion.
    source_adus = set()
    all_adus = set(adu_segments.keys())

    for edge in root.findall('edge'):
        # sup = support, reb = rebuttal, und = undercut, add = addition
        if edge.get('type') in ['sup', 'reb', 'und', 'add']:
            source_adus.add(edge.get('src'))

    # The Major Claims are those that never appear as a source
    major_claims = all_adus - source_adus

    # 4. Build the Result Rows
    results = []
    for adu_id, edu_ids in adu_segments.items():
        # Sort EDU ids to ensure text is in correct order (e.g., e1, e2)
        # Assuming IDs are like 'e1', 'e2', we sort by the integer part
        edu_ids.sort(key=lambda x: int(x[1:]))

        # Join the text parts
        full_text = " ".join([edu_map[eid] for eid in edu_ids])

        is_major = adu_id in major_claims

        results.append({
            'file_id': file_id,
            'topic_id': topic_id,
            'adu_id': adu_id,
            'is_major_claim': is_major,  # True if this is the main conclusion
            'stance': stance,
            'text': full_text
        })

    return results


# --- Main Execution ---
def main():
    # Adjust this path to where your xml files are located
    # Based on your upload, they are in 'corpus/en/' and 'corpus/de/'
    base_path = 'arg-microtexts\corpus\en'

    all_claims = []
    xml_files = glob.glob(os.path.join(base_path, "*.xml"))

    if not xml_files:
        print(f"No XML files found in {base_path}. Check the path.")
        return

    print(f"Processing {len(xml_files)} files...")

    for xml_file in xml_files:
        try:
            claims = parse_microtext_xml(xml_file)
            all_claims.extend(claims)
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")

    # Create DataFrame
    df = pd.read_csv(all_claims) if isinstance(all_claims, str) else pd.DataFrame(all_claims)

    # Save to CSV
    output_filename = "microtext_claims.csv"
    df.to_csv(output_filename, index=False)
    print(f"Done! Extracted {len(df)} ADUs to '{output_filename}'.")

    # --- Quick Stat Check ---
    print("\nMissing Topics Count:")
    print(df[df['topic_id'] == 'MISSING_TOPIC']['file_id'].nunique())

    print("\nSample Rows:")
    print(df.head())


if __name__ == "__main__":
    main()
