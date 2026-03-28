# Annotation and evaluation

See [`annotation.md`](annotation.md) for our annotation scheme and process.

For evaluation `analysis.py` is used. First the machine scores need to be predicted (pipeline stage 6, 9 and 10). Then they can be used as input.

Example usage:
```
python analysis.py --input annotated/0-199_Afzal.xlsx annotated/0-199_Zorin.xlsx --computed ../pipeline_redone/10_run_sbert/10_output/sbert_similarity_scores.csv ../main_claim_similarity_smatch.csv ../main_claim_similarity_s2match.csv
```

