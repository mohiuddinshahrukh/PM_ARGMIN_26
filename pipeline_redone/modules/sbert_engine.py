"""
modules/sbert_engine.py
Handles loading Sentence-BERT and calculating semantic similarity between texts.
"""

try:
    from sentence_transformers import SentenceTransformer, util
    import torch
except ImportError:
    print("⚠️ Error: 'sentence-transformers' not found.")
    print("   Run: pip install sentence-transformers")
    SentenceTransformer = None


class SBERTEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Loads the S-BERT model.
        'all-MiniLM-L6-v2' is chosen for speed/performance balance.
        """
        if SentenceTransformer is None:
            raise RuntimeError("Library not installed.")

        print(f"⏳ Loading S-BERT model: {model_name}...")
        # Check for GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=device)
        print(f"✅ Model loaded on {device.upper()}")

    def encode(self, texts):
        """Encodes a list of texts into vectors."""
        return self.model.encode(texts, convert_to_tensor=True)

    def calculate_similarity(self, text_a, text_b):
        """Calculates cosine similarity between two single texts."""
        emb1 = self.model.encode(text_a, convert_to_tensor=True)
        emb2 = self.model.encode(text_b, convert_to_tensor=True)
        return float(util.cos_sim(emb1, emb2)[0][0])

    def calculate_pairwise_matrix(self, texts):
        """
        Optimized: Calculates similarity matrix for a list of texts.
        Much faster than looping pairwise!
        """
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        # Compute cosine similarity for all pairs
        return util.cos_sim(embeddings, embeddings)
