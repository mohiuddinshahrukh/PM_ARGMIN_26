
### README.md

```markdown
# Microtext Argument Grouping Tool

This tool extracts argument units (claims, premises, and objections) from a directory of Microtext Corpus XML files. It groups the units with a specific topic into a single entry.

## Features
* **Topic-Based Grouping:** Automatically groups extracted text segments by their unique `topic_id`.
* **Flexible Extraction:** You can choose to extract specific units (`claims`, `premises`, `objections`) or any combination of them.
* **Dual Output Formats:** Supports exporting data to **CSV** (for spreadsheets) or **XML** (for hierarchical data).
* **Auto-Directory Creation:** Automatically creates the output directory if it does not exist.

## Usage

Run the script from the command line using the following syntax:

```bash
python unified_extractor.py <input_dir> <output_file> --units <unit_types>

```

## Output Structure

### CSV Output

The CSV output uses `|` as a separator for multiple text segments within the same topic.

| topic_id | premises |
| --- | --- |
| waste_separation | Text segment 1... |
| higher_dog_poo_fines | Text segment A... |

### XML Output

The XML output is hierarchical, nesting unit types under their specific topic.

```xml
<grouped_corpus>
  <topic id="waste_separation">
    <premises count="2">
      <item>Text segment 1...</item>
      <item>Text segment 2...</item>
    </premises>
  </topic>
</grouped_corpus>

```

