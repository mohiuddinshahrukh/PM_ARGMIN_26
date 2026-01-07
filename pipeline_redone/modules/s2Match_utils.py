"""
modules/s2match_utils.py
Implementation of S2Match (Soft Semantic Match) using SpaCy vectors and Hungarian Alignment.
Based on the provided notebook logic.
"""

import penman
import spacy
import numpy as np
from scipy.optimize import linear_sum_assignment
import os
import sys
sys.path.append(os.getcwd())
from modules.loader import load_corpus_to_dataframe
from modules.utils import save_data
# Load SpaCy model only once when module is imported
try:
    nlp = spacy.load("en_core_web_md")
    print("✅ Loaded SpaCy model: en_core_web_md")
except OSError:
    print("⚠️ Warning: 'en_core_web_md' not found. S2Match will fail unless you run:")
    print("   python -m spacy download en_core_web_md")
    nlp = None


def get_triples(amr_text):
    """Parses AMR text into instances (concepts) and edges (relations)."""
    try:
        g = penman.decode(amr_text)
    except Exception:
        return [], []

    instances = []
    edges = []
    for t in g.triples:
        if t[1] == ":instance":
            instances.append((t[0], t[2]))  # (variable, concept)
        else:
            edges.append((t[0], t[1], t[2]))  # (source, role, target)
    return instances, edges


def clean_concept(c):
    """Removes Sense IDs (e.g., 'run-01' -> 'run') for better vector matching."""
    if not isinstance(c, str): return ""
    if "-" in c and c.split("-")[-1].isdigit():
        return "-".join(c.split("-")[:-1])
    return c


def build_sim_matrix(inst1, inst2):
    """Builds a similarity matrix between concepts in Graph A and Graph B."""
    if nlp is None: raise RuntimeError("SpaCy model not loaded.")

    # Pre-compute vectors for speed
    docs1 = [nlp(clean_concept(x[1])) for x in inst1]
    docs2 = [nlp(clean_concept(x[1])) for x in inst2]

    n, m = len(inst1), len(inst2)
    sim = np.zeros((n, m), dtype=float)

    for i in range(n):
        for j in range(m):
            try:
                # Cosine similarity
                s = docs1[i].similarity(docs2[j])
            except Exception:
                s = 0.0

            # Boost exact text matches (identity)
            if clean_concept(inst1[i][1]) == clean_concept(inst2[j][1]):
                s = max(s, 1.0)

            sim[i, j] = float(np.clip(s, 0.0, 1.0))
    return sim


def refine_with_support(inst1, edges1, inst2, edges2, sim_matrix, iterations=1, beta=0.4):
    """
    Refines the similarity matrix by checking if neighbors also match.
    This ensures structural consistency (not just word similarity).
    """
    n, m = sim_matrix.shape

    # Map: variable -> list of neighbors (target, role, direction)
    def build_neighbors(edges):
        nbr = {}
        for s, r, t in edges:
            nbr.setdefault(s, set()).add((t, r, 'out'))
            nbr.setdefault(t, set()).add((s, r, 'in'))
        return nbr

    nbr1 = build_neighbors(edges1)
    nbr2 = build_neighbors(edges2)

    sim = sim_matrix.copy()

    # Iterative Refinement
    for it in range(iterations + 1):
        # Hungarian Algorithm: Find best alignment for current matrix
        if sim.size == 0: return [], [], sim
        row_ind, col_ind = linear_sum_assignment(-sim)

        # Create temporary mapping based on this alignment
        mapping = {inst1[r][0]: inst2[c][0] for r, c in zip(row_ind, col_ind)}

        if it == iterations: break

        # Calculate "Support Score" (Do the neighbors of aligned nodes also align?)
        support = np.zeros_like(sim)

        for i in range(n):
            v1 = inst1[i][0]
            neighbors1 = nbr1.get(v1, set())
            if not neighbors1: continue

            for j in range(m):
                v2 = inst2[j][0]
                neighbors2 = nbr2.get(v2, set())

                matched = 0
                for (nb1_var, role, direction) in neighbors1:
                    mapped_nb1 = mapping.get(nb1_var)
                    if mapped_nb1 and (mapped_nb1, role, direction) in neighbors2:
                        matched += 1

                if len(neighbors1) > 0:
                    support[i, j] = matched / len(neighbors1)

        # Update Matrix: Weighted average of Concept Sim and Structural Support
        sim = (1.0 - beta) * sim_matrix + beta * support
        sim = np.clip(sim, 0.0, 1.0)

    return row_ind, col_ind, sim


def compute_s2match_score(amr1, amr2):
    """
    Main entry point. Calculates S2Match F1 Score.
    """
    if not amr1 or not amr2: return 0.0

    inst1, edges1 = get_triples(amr1)
    inst2, edges2 = get_triples(amr2)

    if not inst1 or not inst2: return 0.0

    # 1. Similarity Matrix
    sim_matrix = build_sim_matrix(inst1, inst2)

    # 2. Structural Alignment (Hungarian + Refinement)
    row_ind, col_ind, final_sim = refine_with_support(inst1, edges1, inst2, edges2, sim_matrix)

    # 3. Calculate Final Score
    total_concept_sim = 0.0
    mapping = {}

    # Sum up concept similarities of aligned pairs
    for r, c in zip(row_ind, col_ind):
        v1, v2 = inst1[r][0], inst2[c][0]
        mapping[v1] = v2
        total_concept_sim += final_sim[r, c]

    # Count Edge Matches (Structural overlap)
    matched_edges = 0.0
    edges2_set = set(edges2)

    for s, role, t in edges1:
        if s in mapping and t in mapping:
            # Check if the mapped edge exists in Graph 2
            if (mapping[s], role, mapping[t]) in edges2_set:
                matched_edges += 1.0

    # 4. F1 Calculation
    total_match = total_concept_sim + matched_edges
    len1 = len(inst1) + len(edges1)
    len2 = len(inst2) + len(edges2)

    if len1 == 0 or len2 == 0: return 0.0

    p = total_match / len1
    r = total_match / len2

    if p + r == 0: return 0.0
    return 2 * p * r / (p + r)
