# AMR Graph Generation Module

This module is responsible for constructing Abstract Meaning Representation (AMR) graphs for argument units (ADUs) in the Microtext Corpus. It operates downstream of ADU extraction and prepares semantically enriched representations that can be used for similarity computation, clustering, or further semantic analysis.

The module consists of two sequential processing steps:
1. Preparation of textual input for AMR construction (full sentences vs. ADU fragments)
2. Generation of AMR graphs in PENMAN notation

---

## Overview

Argument Discourse Units (ADUs) in the Microtext Corpus are often realized as **clauses** embedded in longer sentences. For semantic analysis, it is therefore mught be useful to retain both:
- the **ADU fragment text** itself, and
- the **full sentence** from which the ADU was extracted.

This module supports AMR graph construction at **both levels**, allowing the user to choose whether AMRs should represent complete sentences or isolated ADU fragments.

---

## Processing Steps

### Step 1: ADU Text Preparation

The first step extracta ADUs with their corresponding full sentences.

**Input:**  
The Microtext Corpus.

**Output:**  
XML/CSV files where each `<argument>` element contains both:
- `fragment_text`: the ADU text span
- `full_sentence`: the full sentence context

**Example output:**
```xml
<argument>
  <file_id>micro_b003</file_id>
  <topic_id>health_insurance_cover_complementary_medicine</topic_id>
  <adu_id>a1</adu_id>
  <type>claim</type>
  <is_major_claim>True</is_major_claim>
  <stance>con</stance>
  <fragment_text>
    Health insurance companies should not cover treatment in complementary medicine
  </fragment_text>
  <full_sentence>
    Health insurance companies should not cover treatment in complementary medicine unless the promised effect and its medical benefit have been concretely proven.
  </full_sentence>
</argument>
```
This step does not generate AMRs; it only prepares and aligns textual representations for downstream semantic parsing.

**Command line execution**
python adu_text_alignment.py <input_file> <output_file>

**Arguments**:
| Argument        | Type       | Description                                                                                    |
| --------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| `input_file`    | Optional | The Microtext Corpus.                        |
| `output_file`   | Positional | Output XML/CSV file with AMR graphs added.                                                         |
| `types` | Optional   | Which ADU types  (claims, premises, etc.) to extract. |


### Step 2: AMR Graph Construction

The second step generates AMR graphs for each argument, based on either:
- the full sentence, or
- the ADU fragment text.

The choice of text source is configurable via command-line arguments.

**Output**:
The original argument structure augmented with an amr_penman field containing the AMR graph.

**Example output**:
```xml
<argument>
  <file_id>micro_b003</file_id>
  <topic_id>health_insurance_cover_complementary_medicine</topic_id>
  <adu_id>a1</adu_id>
  <type>claim</type>
  <is_major_claim>True</is_major_claim>
  <stance>con</stance>
  <fragment_text>
    Health insurance companies should not cover treatment in complementary medicine
  </fragment_text>
  <full_sentence>
    Health insurance companies should not cover treatment in complementary medicine unless the promised effect and its medical benefit have been concretely proven.
  </full_sentence>
  <amr_penman>
# ::snt Health insurance companies should not cover treatment in complementary medicine unless the promised effect and its medical benefit have been concretely proven.
(r / recommend-01
    :ARG1 (c / cover-01
          :polarity -
          :ARG0 (c2 / company
                :ARG0-of (ii / insure-02
                      :ARG1 (h / health)))
          :ARG1 (t / treat-03
                :ARG2 (m / medicine
                      :ARG1-of (c3 / complement-01))))
    :condition (p / prove-01
          :polarity -
          :ARG1 (a / and
                :op1 (t2 / thing
                      :ARG2-of (a2 / affect-01)
                      :ARG2-of (p2 / promise-01))
                :op2 (b / benefit-01
                      :ARG0 m))
          :ARG1-of (c4 / concrete-02)))
  </amr_penman>
</argument>
```

**Command line execution**
python amr_graph_generation.py <input_file> <output_file>

**Arguments**
| Argument        | Type       | Description                                                                                    |
| --------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| `input_file`    | Positional | XML/CSV file containing arguments with `fragment_text` and `full_sentence`.                        |
| `output_file`   | Positional | Output XML/CSV file with AMR graphs added.                                                         |
| `--text_source` | Optional   | Which text to use for AMR construction: `full_sentence` (default), `fragment_text`. |

## Features

1. Dual-Level Semantic Representation
Supports AMR construction for:
- full sentences
- ADU fragments

2. Configurable Text Source
Users can explicitly specify which textual representation the AMR was generated from, ensuring correct alignment in downstream processing.

3. Source Preservation
AMR graphs are embedded directly in the microtext core statistics, preserving:
- microtext file identifier
- topic ID
- ADU type
- text stance