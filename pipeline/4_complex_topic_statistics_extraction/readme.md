# Advanced Microtext Argument Extractor

A script designed to extract, aggregate, and analyze argument structures from the Microtext Corpus (XML).

## Features

1.  **Topic & Stance Grouping:**
    Aggregates data first by `topic_id`, then by `stance` (e.g., `pro` vs. `con`). This allows you to view all supporting arguments for a topic separately from opposing ones.

2.  **Source Traceability:**
    Every extracted text segment is tagged with its original filename (e.g., `[micro_b005]`). You never lose track of where a sentence came from, even after aggregation.

3.  **Argument Statistics:**
    Automatically calculates complexity metrics for every topic/stance group:
    * `count_claims`: Number of central claims.
    * `count_premises`: Number of supporting premises.
    * `count_objections`: Number of counter-arguments.
    * `count_relations`: Number of logical links (edges) found.

4.  **Relation Mapping (Feature C):**
    Extracts the logical graph structure as readable pairs. Instead of just "Premise X," it extracts:
    `"Premise X" --supports--> "Claim Y"`
    This is essential for training AI models on argument structure rather than just content.

## Usage

```bash
python advanced_extraction.py <corpus_dir> <output_file> --units <ADU_type>

```

## Output Format

### XML Example

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
