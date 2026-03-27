# Minimal Pair Similarity Module

This module computes semantic similarity between minimal pairs of sentences using:

- Smatch
- S2Match
- SBERT

It also includes functionality for automatic AMR graph construction from raw text.

## Overview

The workflow consists of four main steps:

- Input preparation (YAML with minimal pairs)
- AMR graph construction
- Similarity computation (Smatch / S2Match / SBERT)
- Saving results (CSV/XML)

## Input Format

Minimal pairs are defined in a YAML file:
```
pairs:
  - id: pair_1
    sentences:
      - text: "Sentence A"
      - text: "Sentence B"
```

## Components

### 1. AMR Graph Construction

Script: amr_graph_construction.py

Converts sentences into AMR graphs using amrlib
Outputs a CSV/XML with:
- id_pair
- my_sentence
- graph

Usage:
```
python 9_amr_graph_construction.py \
  --input minimal_pair.yaml \
  --output minimal_pair_graphs.xml
```

### 2. Smatch Similarity

Script: check_smatch.py

- Computes strict AMR similarity based on triple overlap
- Groups rows by id_pair
- Compares the two graphs within each pair

Usage:
```
python 9_check_smatch.py \
  --input minimal_pair_graphs.xml \
  --output smatch_results.csv
```

### 3. S2Match Similarity

Script: check_s2match.py

Computes soft AMR similarity
Uses:
- concept similarity
- structural alignment (Hungarian + refinement)

Usage:
```
python 9_check_s2match.py \
  --input minimal_pair_graphs.xml \
  --output s2match_results.csv
```

### 4. SBERT Similarity

Script: check_sbert.py

- Computes sentence-level semantic similarity
- Uses pretrained SBERT embeddings
- Works directly on the YAML input (no AMR required)

Usage:
```
python 9_check_sbert.py \
  --input minimal_pair.yaml \
  --output sbert_results.csv
```

## Output Format

All scripts produce a table with:
```
pair_id
score
text_A
text_B
```
