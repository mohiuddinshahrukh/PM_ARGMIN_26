# AMR Graph Generation Module

This module is responsible for constructing Abstract Meaning Representation (AMR) graphs for argument units (ADUs) in the Microtext Corpus.

The module consists of two sequential processing steps:
1. Argument Discourse Units (ADUs) extraction
2. Generation of AMR graphs in PENMAN notation

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

**Command line execution**
python 5_amr_graph_construction.py --input ../../../arg-microtexts/corpus/en/ --output ./results/test.xml --types claim

**Arguments**:
| Argument        | Type       | Description                                                                                    |
| --------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| `input_file`    | Optional | The Microtext Corpus.                        |
| `output_file`   | Positional | Output XML/CSV file with AMR graphs added.                                                         |
| `types` | Optional   | Which ADU types  (claims, premises, etc.) to extract.                 

#### Extension: AMR Graph Construction for Sentence Pairs

In addition to ADU-based processing, the module supports AMR graph construction for (minimal) pairs of sentences. This functionality is intended for experiments when two sentences with minor difference are to be compared, e.g. "Tuition fees should not be **charged** in Germany" vs. "Tuition fees should not be **introduced** in Germany." Note: In this mode, the module operates directly on sentence pairs, without reference to the Microtext Corpus or ADU annotations.

Sentence pairs are provided in a YAML file containing one or more pairs. Each pair consists of exactly two sentences.

pairs:
  - id: pair_1
    sentences:
      - text: "Tuition fees should not be charged in Germany."
      - text: "Tuition fees should not be introduced in Germany."

  - id: pair_2
    sentences:
      - text: "Smoking should be banned in public places."
      - text: "Smoking should not be allowed in public places."

For each sentence pair:

- AMR graphs are generated independently for each sentence.
- The resulting graphs are stored alongside the original sentence text.
- The pair structure is preserved in the output, enabling direct downstream comparison.

Note: No ADU extraction or sentence reconstruction is performed in this mode.

**Command line execution**
python amr_graph_generation.py --input_pair pairs.yaml --output_file sentence_pairs.xml

## Features

1. ADU extraction and AMR construction

2. Pair-Based AMR Construction
Supports AMR graph generation for minimal sentence pairs, enabling controlled semantic similarity experiments.