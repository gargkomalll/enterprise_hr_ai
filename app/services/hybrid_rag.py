import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class HybridRAGRetriever:
    """
    Hybrid RAG Retrieval Engine combining Lexical BM25-style keyword matching
    with Dense Vector / TF-IDF Cosine Similarity via Reciprocal Rank Fusion (RRF).
    """
    def __init__(self, catalog: list = None):
        if catalog is None:
            catalog = [
                {"title": "Advanced Python & Automated Analytics", "skills": ["Python", "Automated Analytics", "Data Value", "Programming", "Data Science"]},
                {"title": "Enterprise Cloud Architecture (AWS/Azure)", "skills": ["AWS Cloud", "Azure", "Cloud Architecture", "Infrastructure", "DevOps"]},
                {"title": "SQL & Big Data Engineering Masterclass", "skills": ["SQL", "Big Data", "Data Engineering", "Database Administration", "ETL"]},
                {"title": "Critical Thinking & Strategic Problem Solving", "skills": ["Critical Thinking", "Complex Problem Solving", "Active Learning", "Judgment", "Strategy"]},
                {"title": "Executive Leadership & Team Management", "skills": ["Leadership", "Management", "Negotiation", "Time Management", "Communication"]},
                {"title": "Machine Learning & Predictive Modeling", "skills": ["Machine Learning", "Predictive Modeling", "Python", "Data Science", "AI"]},
                {"title": "Advanced Microsoft Excel & Power BI", "skills": ["Microsoft Excel", "Power BI", "Data Analysis", "Spreadsheets", "Reporting"]}
            ]
        self.catalog = catalog
        self._build_indices()
        
    def _build_indices(self):
        self.corpus = [" ".join(item["skills"]) for item in self.catalog]
        
        # Dense Semantic Vector Index (TF-IDF Cosine)
        self.dense_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.dense_matrix = self.dense_vectorizer.fit_transform(self.corpus)
        
        # Lexical Keyword Index (BM25 Count-based overlap)
        self.lexical_vectorizer = CountVectorizer(ngram_range=(1, 2))
        self.lexical_matrix = self.lexical_vectorizer.fit_transform(self.corpus)
        
    def _get_dense_ranks(self, query_str: str) -> dict:
        query_vec = self.dense_vectorizer.transform([query_str])
        sims = cosine_similarity(query_vec, self.dense_matrix).flatten()
        ranked_indices = np.argsort(sims)[::-1]
        return {idx: rank_pos + 1 for rank_pos, idx in enumerate(ranked_indices)}
        
    def _get_lexical_ranks(self, query_str: str) -> dict:
        query_vec = self.lexical_vectorizer.transform([query_str])
        counts = (self.lexical_matrix * query_vec.T).toarray().flatten()
        ranked_indices = np.argsort(counts)[::-1]
        return {idx: rank_pos + 1 for rank_pos, idx in enumerate(ranked_indices)}
        
    def retrieve_hybrid(self, query_skills: list, top_k: int = 3, rrf_k: int = 60) -> list:
        """
        Executes Hybrid RAG Retrieval fusing Dense Vector & Lexical Keyword ranks via Reciprocal Rank Fusion (RRF).
        RRF Score(d) = 1 / (rrf_k + rank_dense(d)) + 1 / (rrf_k + rank_lexical(d))
        """
        if not query_skills:
            return self.catalog[:top_k]
            
        query_str = " ".join(query_skills)
        dense_ranks = self._get_dense_ranks(query_str)
        lexical_ranks = self._get_lexical_ranks(query_str)
        
        rrf_scores = {}
        for idx in range(len(self.catalog)):
            r_dense = dense_ranks.get(idx, len(self.catalog))
            r_lexical = lexical_ranks.get(idx, len(self.catalog))
            
            # Reciprocal Rank Fusion Formula
            score = (1.0 / (rrf_k + r_dense)) + (1.0 / (rrf_k + r_lexical))
            rrf_scores[idx] = score
            
        sorted_indices = sorted(rrf_scores.keys(), key=lambda i: rrf_scores[i], reverse=True)
        return [self.catalog[idx] for idx in sorted_indices[:top_k]]

# Singleton Retriever Instance
hybrid_retriever = HybridRAGRetriever()

def get_hybrid_course_recommendations(query_skills: list, top_k: int = 3) -> list:
    results = hybrid_retriever.retrieve_hybrid(query_skills, top_k=top_k)
    return [r["title"] for r in results]
