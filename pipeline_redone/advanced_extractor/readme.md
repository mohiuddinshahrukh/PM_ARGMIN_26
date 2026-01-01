
### README.md

```markdown
# Advanced Microtext Argument Extractor

A powerful Python tool designed to extract, aggregate, and analyze argument structures from the Microtext Corpus (XML). This script goes beyond simple text extraction by preserving the logical structure of arguments, tracking their source files, and providing complexity statistics.

## Features

1.  **Topic & Stance Grouping:**
    Aggregates data first by `topic_id`, then by `stance` (e.g., `pro` vs. `con`). This allows you to view all supporting arguments for a topic separately from opposing ones.

2.  **Source Traceability (Feature A):**
    Every extracted text segment is tagged with its original filename (e.g., `[micro_b005]`). You never lose track of where a sentence came from, even after aggregation.

3.  **Argument Statistics (Feature B):**
    Automatically calculates complexity metrics for every topic/stance group:
    * `count_claims`: Number of central claims.
    * `count_premises`: Number of supporting premises.
    * `count_objections`: Number of counter-arguments.
    * `count_relations`: Number of logical links (edges) found.

4.  **Relation Mapping (Feature C):**
    Extracts the logical graph structure as readable pairs. Instead of just "Premise X," it extracts:
    `"Premise X" --supports--> "Claim Y"`
    This is essential for training AI models on argument structure rather than just content.

## Installation

1.  **Prerequisites:** Python 3.x
2.  **Dependencies:** None (uses standard libraries `os`, `argparse`, `xml.etree.ElementTree`, `csv`, `sys`, `collections`).
3.  **Setup:** Save the provided script as `advanced_extractor.py`.

## Usage

Run the script from the command line:

```bash
python advanced_extractor.py <input_dir> <output_file> [options]

```

### Arguments

| Argument | Type | Description |
| --- | --- | --- |
| `input_dir` | Positional | Path to the directory containing `.xml` files. |
| `output_file` | Positional | Path for the output file. Must end in `.csv` or `.xml`. |
| `--units` | Optional | Space-separated list of units to extract. Default: `claims premises objections`. |

## Examples

### 1. Generate a Rich CSV Dataset

Creates a flat file perfect for DataFrames or Excel analysis. Includes all statistics and logical pairs.

```bash
python advanced_extractor.py ./corpus/en results/rich_data.csv

```

### 2. Generate Hierarchical XML

Creates a structured XML file where arguments are nested under `<topic>` and `<stance>`.

```bash
python advanced_extractor.py ./corpus/en results/structure.xml

```

### 3. Extract Specific Units

If you only want premises and ignore objections:

```bash
python advanced_extractor.py ./corpus/en results/premises_only.csv --units premises

```

## Output Format Explained

### CSV Columns

* `topic_id`: The topic identifier (e.g., `waste_separation`).
* `stance`: The stance of the file (`pro`, `con`).
* `count_X`: Statistical count of units (e.g., `count_premises`).
* `premises`: Pipe-separated list of text with source tags.
* *Example:* `[micro_b001] It's annoying to separate rubbish | [micro_b002] It smells bad`


* `relations`: Pipe-separated list of logical connections.
* *Example:* `[micro_b001] "It's annoying..." --sup--> "We should stop separating"`



### XML Structure

```xml
<advanced_corpus>
  <topic id="waste_separation">
    <stance type="pro">
      <statistics count_premises="5" count_relations="3" ... />
      <premises>
        <item source_file="micro_b001.xml">It's annoying...</item>
      </premises>
      <relations>
        <pair type="sup" source_file="micro_b001.xml">
          <source_text>It's annoying...</source_text>
          <target_text>We should stop separating</target_text>
        </pair>
      </relations>
    </stance>
  </topic>
</advanced_corpus>

```
