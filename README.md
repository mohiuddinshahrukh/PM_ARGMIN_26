# UP Microtext Corpus: AMR-Based Similarity Analysis

This repository contains an end-to-end experimental pipeline for analyzing argumentative texts from the **UP Argumentative Microtext Corpus**, with a particular focus on **semantic similarity between claims**. The project combines corpus analysis, AMR graph construction, graph-based similarity metrics, and neural sentence embeddings to study where and why human similarity judgments diverge from automatic measures.

The core research question is:

> *Do AMR-based similarity measures capture argumentative meaning in the same way humans do?*

To answer this, the project systematically compares **human annotations**, **graph-based similarity scores**, and **embedding-based similarity scores**, and probes discrepancies using controlled linguistic tests.

---

## Project Overview

The pipeline consists of four main components:

1. **UP Microtext Corpus Analysis**
2. **AMR Graph Construction**
3. **AMR Graph Similarity Computation (Smatch & S2match)**
4. **Sentence-BERT Similarity Baseline**

Each component can be run independently, but they are designed to work together as a unified experimental framework.

---

## 1. UP Microtext Corpus Analysis

This stage prepares and explores the argumentative data.

### Corpus Processing

* Extraction of **topics** from the corpus metadata
* Identification and extraction of **Argumentative Discourse Units (ADUs)**
* Classification of ADUs by type (e.g. *claim*, *premise*)

### Topic-Grouped ADUs

* ADUs are grouped by topic to enable **within-topic similarity comparisons**
* This ensures that similarity judgments are not confounded by topic drift

### Statistical Analysis

* Computation of **topic-level and corpus-level statistics**, including:

  * Distribution of ADU types
  * Number of claims per topic
  * Claim pair counts per topic

These statistics guide the selection of meaningful claim pairs for similarity analysis.

**Corpus Source**

The UP Argumentative Microtext Corpus is publicly available at:

```bash
https://github.com/peldszus/arg-microtexts
```

---

## 2. AMR Graph Construction

In the second stage, textual ADUs are mapped to **Abstract Meaning Representation (AMR)** graphs.

### Graph Generation

* AMR graphs are constructed for different **ADU types**
* The pipeline aligns ADU text and generates one AMR graph per ADU

### Design Choices

* AMRs are built directly from ADUs (not full documents)

The resulting AMR graphs form the basis for graph-based similarity computation.

---

## 3. AMR Graph Similarity Check

This stage evaluates semantic similarity **at the graph level**.

### Smatch

* Standard **Smatch** measures overlap between AMR triples under optimal node alignment

### S2match

* **S2match** is an extended Smatch similarity metric
* The implementation used here was **developed within this project**
* It is designed to be more tolerant to lexical variation (e.g. synonyms)

### Experimental Setup

* Claim pairs are compared using Smatch and S2match
* Scores are analyzed against **human similarity annotations**
* Discrepancies are further examined using **minimal pair tests**, where only one linguistic feature is varied (e.g. synonym choice or word order)

This component is central for diagnosing *why* graph-based similarity may fail (or succeed) to match human judgments.

---

## 4. Sentence-BERT Similarity Baseline

To complement graph-based methods, the project includes a **neural baseline**.

### Sentence-BERT

* Claim similarity is computed using a **pre-trained Sentence-BERT model**
* No graphs or symbolic representations are involved

### Purpose

* Provides a baseline
* Allows comparison between:

  * Symbolic semantic similarity (AMR-based)
  * Embedding-based similarity (Sentence-BERT)

This helps determine whether observed discrepancies are specific to AMR-based methods or reflect a broader challenge in modeling argumentative similarity.

---

## Experimental Philosophy

A key methodological principle of the project is **controlled probing**:

* When human and machine similarity scores diverge, we:

  1. Formulate a linguistic hypothesis (e.g. synonym sensitivity)
  2. Construct **minimal sentence pairs** differing in exactly one feature to test the hypothesis
  3. Compare graph structures and similarity scores

This approach allows precise attribution of errors to specific linguistic phenomena.

---

## Outcome

The project delivers:

* A reproducible pipeline for argumentative similarity analysis
* A custom S2match implementation
* Detailed empirical evidence on the strengths and limitations of AMR-based similarity for arguments

Together, these components contribute to a better understanding of semantic similarity in argumentative text and the gap between symbolic meaning representations and human interpretation.

## Installation & Requirements

To run the pipeline, install the required dependencies listed in the requirements.txt file.

### Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Pipeline

Each stage of the pipeline is implemented as an independent script.

👉 **Instructions for running individual scripts are provided in the README file within each module or script directory.**