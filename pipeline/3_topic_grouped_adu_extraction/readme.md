
# Microtext Argument Grouping Tool

This tool extracts argument units (claims, premises, and objections). It groups the units with a specific topic into a single entry.

## Usage

```bash
python unified_extractor.py <corpus_dir> <output_file> --units <ADU_type>

```

## Output Format

### XML Output

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

