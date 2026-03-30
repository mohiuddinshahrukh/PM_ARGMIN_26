# SBERT Similarity Module

This module computes semantic similarity between arguments using Sentence-BERT (SBERT).

## The module consists of two steps:

### 1. Data Preparation
```
python 8_prep_data.py --input_dir <corpus_dir> --output sbert_input.csv
```
- parses XML corpus
- extracts arguments (topic_id, adu_id, type, text)
- saves a clean CSV for SBERT

### 2. Similarity Computation
```
python 8_run_sbert.py --input sbert_input.csv --output sbert_results.csv
```
- groups arguments by topic
- computes pairwise similarity using SBERT
- outputs ranked argument pairs with scores

## Output

Each row contains:
```
topic
argument IDs (A, B)
texts (A, B)
argument types
SBERT similarity score
```
