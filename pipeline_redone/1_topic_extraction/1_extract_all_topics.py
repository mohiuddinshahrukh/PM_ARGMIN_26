import argparse
import os
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup
from collections import defaultdict


def ensure_directory_exists(file_path):
    """
    Checks if the directory for the given file path exists.
    If not, it creates the directory.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        print(f"Directory '{directory}' not found. Creating it...")
        os.makedirs(directory, exist_ok=True)


def get_data(directory_path: str, target_attribute: str):
    """
    Scans directory and returns:
    1. data_map (dict)
    2. total_files_in_dir (int)
    3. total_xml_files (int)
    4. processed_count (int)
    """
    if not os.path.exists(directory_path):
        print(f"Error: The directory '{directory_path}' was not found.")
        return None, 0, 0, 0

    data_map = defaultdict(dict)
    processed_count = 0
    total_xml_files = 0

    # 1. Get all files
    all_files = os.listdir(directory_path)
    total_files_in_dir = len(all_files)

    print(f"Scanning directory: {directory_path} for attribute '{target_attribute}'...")

    # 2. Iterate and count
    for filename in all_files:
        if filename.endswith(".xml"):
            total_xml_files += 1
            full_path = os.path.join(directory_path, filename)

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                soup = BeautifulSoup(content, "xml")
                # Look for the attribute in <arggraph>
                main_tag = soup.find("arggraph")

                if main_tag and target_attribute in main_tag.attrs:
                    value = main_tag[target_attribute]
                    # join all EDU texts in order (e1..eN as they appear)
                    full_text = " ".join(edu.get_text(" ", strip=True) for edu in main_tag.find_all("edu"))
                    data_map[value][filename] = full_text
                    processed_count += 1
            except Exception as e:
                print(f"Failed to parse {filename}: {e}")

    print(f"Scan Complete.")
    print(
        f"Total files: {total_files_in_dir} | XML Files: {total_xml_files} | Processed (matches found): {processed_count}")
    return data_map, total_files_in_dir, total_xml_files, processed_count


def save_as_csv(data, total_files, total_xml_files, processed_files, output_path, attribute_name):
    ensure_directory_exists(output_path)

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # --- SUMMARY SECTION ---
            writer.writerow(["--- SUMMARY STATISTICS ---"])
            writer.writerow(["Total Files in Directory", total_files])
            writer.writerow(["Total XML Files", total_xml_files])
            writer.writerow(["Files containing '" + attribute_name + "'", processed_files])
            writer.writerow(["Unique '" + attribute_name + "' values", len(data)])
            writer.writerow([])

            # --- MAIN DATA ---
            writer.writerow([attribute_name, "Found In Files", "Text"])
            for key, files_dict in data.items():
                for file_id, file_text in files_dict.items():
                    writer.writerow([key, file_id, file_text])
                #files_string = ", ".join(files)
                #writer.writerow([key, files_string])

        print(f"Successfully saved CSV to: {output_path}")
    except IOError as e:
        print(f"Error writing CSV: {e}")


def save_as_xml(data, total_files, total_xml_files, processed_files, output_path, attribute_name):
    ensure_directory_exists(output_path)

    try:
        # Dynamic Root Attributes
        root = ET.Element("report", {
            "target_attribute": attribute_name,
            "total_files_in_directory": str(total_files),
            "total_xml_files": str(total_xml_files),
            "processed_files_with_match": str(processed_files),
            "unique_values_count": str(len(data))
        })

        for key, files_dict in data.items():
            # Use the attribute name as the tag (e.g., <topic>, <stance>)
            tag_name = attribute_name if " " not in attribute_name else "item"

            item_elem = ET.SubElement(root, tag_name)
            item_elem.set("value", key)
            item_elem.set("count", str(len(files_dict)))

            for file_id, file_text in files_dict.items():
                file_elem = ET.SubElement(item_elem, "file")
                #file_elem.text = fname

                file_elem.set("name", file_id)
                file_elem.text = file_text

        xml_str = ET.tostring(root, encoding='utf-8')
        parsed_str = minidom.parseString(xml_str)
        pretty_xml = parsed_str.toprettyxml(indent="  ")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        print(f"Successfully saved XML to: {output_path}")
    except IOError as e:
        print(f"Error writing XML: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract attributes from XML files.")

    # Required Arguments
    parser.add_argument("input_dir", type=str, help="Path to input .xml files")
    parser.add_argument("output_file", type=str, help="Output file path (.csv or .xml)")

    # Optional Argument (Defaults to 'topic_id')
    parser.add_argument("--attribute", type=str, default="topic_id",
                        help="The XML attribute to extract (e.g., topic_id, stance, id). Defaults to 'topic_id'.")

    args = parser.parse_args()

    # Call get_data (which now returns 4 values)
    data_map, total_files, total_xml, processed = get_data(args.input_dir, args.attribute)

    if data_map:
        if args.output_file.endswith(".csv"):
            save_as_csv(data_map, total_files, total_xml, processed, args.output_file, args.attribute)
        elif args.output_file.endswith(".xml"):
            save_as_xml(data_map, total_files, total_xml, processed, args.output_file, args.attribute)
        else:
            print("Error: The output file must end with either .csv or .xml")
