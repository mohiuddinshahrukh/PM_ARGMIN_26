# AMR Graph Generation Module

This module is responsible for constructing Abstract Meaning Representation (AMR) graphs for argument units (ADUs) in the Microtext Corpus.

The module consists of two sequential processing steps:
1. Argument Discourse Units (ADUs) extraction
2. Generation of AMR graphs

---

## Processing

The script extracts ADUs with their corresponding full sentences.

**Input:**  
The Microtext Corpus.

**Output:**  
XML/CSV files where each `<argument>` element contains both:
- `full_sentence`: the full sentence context
- `fragment_text`: the ADU text span
- `graph`: the AMR graph of the ADU text

**Example output:**
```xml
<argument>
    <file_id>micro_b003</file_id>
    <topic_id>health_insurance_cover_complementary_medicine</topic_id>
    <adu_id>a1</adu_id>
    <type>claim</type>
    <is_major_claim>True</is_major_claim>
    <stance>con</stance>
    <full_sentence>Health insurance companies should not cover treatment in complementary medicine unless the promised effect and its medical benefit have been concretely proven.</full_sentence>
    <fragment_text>Health insurance companies should not cover treatment in complementary medicine</fragment_text>
    <graph># ::snt Health insurance companies should not cover treatment in complementary medicine
# ::tokens ["Health", "insurance", "companies", "should", "not", "cover", "treatment", "in", "complementary", "medicine"]
# ::ner_tags ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"]
# ::ner_iob ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"]
# ::pos_tags ["NN", "NN", "NNS", "MD", "RB", "VB", "NN", "IN", "JJ", "NN"]
# ::lemmas ["health", "insurance", "company", "should", "not", "cover", "treatment", "in", "complementary", "medicine"]
(r0 / recommend-01
  :polarity -
  :ARG1 (c0 / cover-01
    :ARG0 (c1 / company
      :ARG0-of (i0 / insure-02
        :ARG1 (h0 / health)))
    :ARG1 (t0 / treat-03
      :ARG2 (m0 / medicine
        :ARG1-of (c2 / compare-01)))))</graph>
  </argument>
```

## Usage

```bash
python 5_amr_graph_construction.py --input_dir <corpus_dir> --output <output_file> --types <ADU_type>

```
