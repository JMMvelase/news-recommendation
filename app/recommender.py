import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


class NewsRecommender:

    def __init__(
        self,
        index_path="data/news_rec_embeddings.faiss",
        articles_path="data/news_articles.parquet",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

        self.index = faiss.read_index(index_path)
        self.articles = pd.read_parquet(articles_path)

        if self.index.ntotal != len(self.articles):
            raise ValueError(
                f"FAISS index ({self.index.ntotal} vectors) and "
                f"articles ({len(self.articles)} rows) are misaligned."
            )

    def recommend(self, query, k=5):
        query_embedding = (
            self.model.encode(
                [query],
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            .astype("float32")
        )

        k = min(k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, k)

        recommendations = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue
            article = self.articles.iloc[int(index)]
            recommendations.append({
                "headline": str(article["headline"]),
                "category": str(article["category"]),
                "similarity": float(score),
                "link": str(article["link"]),
            })

        return recommendations