
# XML Attribute Extractor

A command-line tool to scan the UP Argumentative Microtext Corpus, extract specific attributes (primarily `topic_id`) from it, and generate a summary report in CSV or XML format.

## Usage

```bash
python 1_extract_all_topics.py <corpus_dir> <output_file>
```

## Output Format

### XML Example

```xml
<report target_attribute="topic_id" total_files_in_directory="122" total_xml_files="120" processed_files_with_match="120" unique_values_count="18">
  <topic value="waste_separation" count="2">
    <file>micro_b001.xml</file>
    <file>micro_b005.xml</file>
  </topic>
  <topic value="public_transport" count="1">
    <file>micro_k002.xml</file>
  </topic>
</report>

```