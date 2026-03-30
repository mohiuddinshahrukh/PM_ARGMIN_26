
# Microtext ADU Extractor

This script automates the extraction of **argumentative discourse units** (ADUs: Claims, Premises, and Objections) from the UP Argumentative Microtext Corpus. 

## Usage

```bash
python 2_adu_extraction.py <corpus_dir> --extract <ADU_type> --output <output_file>

```

## Output Format

### XML Example

```xml
<extraction_results>
  <item>
    <filename>micro_b003.xml</filename>
    <type>objection</type>
    <text>Patients do often report relief...</text>
  </item>
</extraction_results>

```