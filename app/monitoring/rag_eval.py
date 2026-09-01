import numpy as np
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_precision_at_k(actual_relevant: set, recommended_items: list, k: int = 3) -> float:
    """Calculates Precision@K for a query recommendation list."""
    if k <= 0 or not recommended_items:
        return 0.0
    top_k = recommended_items[:k]
    relevant_in_top_k = set(top_k).intersection(actual_relevant)
    return len(relevant_in_top_k) / float(k)

def calculate_recall_at_k(actual_relevant: set, recommended_items: list, k: int = 3) -> float:
    """Calculates Recall@K for a query recommendation list."""
    if not actual_relevant or not recommended_items:
        return 0.0
    top_k = recommended_items[:k]
    relevant_in_top_k = set(top_k).intersection(actual_relevant)
    return len(relevant_in_top_k) / float(len(actual_relevant))

def calculate_mrr(actual_relevant: set, recommended_items: list) -> float:
    """Calculates Mean Reciprocal Rank (MRR) for a single query."""
    for rank_idx, item in enumerate(recommended_items, start=1):
        if item in actual_relevant:
            return 1.0 / rank_idx
    return 0.0

def evaluate_retrieval_system(k: int = 3):
    """
    Evaluates the TF-IDF / RAG Course Recommendation Engine using standard IR metrics:
    Precision@K, Recall@K, and MRR (Mean Reciprocal Rank).
    """
    catalog = [
        {"title": "Advanced Python & Automated Analytics", "skills": ["Python", "Automated Analytics", "Data Value", "Programming"]},
        {"title": "Enterprise Cloud Architecture (AWS/Azure)", "skills": ["AWS Cloud", "Azure", "Cloud Architecture", "Infrastructure"]},
        {"title": "SQL & Big Data Engineering Masterclass", "skills": ["SQL", "Big Data", "Data Engineering", "Database Administration"]},
        {"title": "Critical Thinking & Strategic Problem Solving", "skills": ["Critical Thinking", "Complex Problem Solving", "Active Learning", "Judgment"]},
        {"title": "Executive Leadership & Team Management", "skills": ["Leadership", "Management", "Negotiation", "Time Management"]},
        {"title": "Machine Learning & Predictive Modeling", "skills": ["Machine Learning", "Predictive Modeling", "Python", "Data Science"]},
        {"title": "Advanced Microsoft Excel & Power BI", "skills": ["Microsoft Excel", "Power BI", "Data Analysis", "Spreadsheets"]}
    ]
    
    # Test queries with ground-truth relevant courses
    test_queries = [
        {
            "missing_skills": ["Python", "Data Science"],
            "ground_truth": {"Advanced Python & Automated Analytics", "Machine Learning & Predictive Modeling"}
        },
        {
            "missing_skills": ["AWS Cloud", "Cloud Architecture"],
            "ground_truth": {"Enterprise Cloud Architecture (AWS/Azure)"}
        },
        {
            "missing_skills": ["Critical Thinking", "Active Learning"],
            "ground_truth": {"Critical Thinking & Strategic Problem Solving"}
        },
        {
            "missing_skills": ["Microsoft Excel", "SQL"],
            "ground_truth": {"Advanced Microsoft Excel & Power BI", "SQL & Big Data Engineering Masterclass"}
        }
    ]
    
    vectorizer = TfidfVectorizer()
    corpus = [" ".join(item["skills"]) for item in catalog]
    catalog_matrix = vectorizer.fit_transform(corpus)
    
    precisions = []
    recalls = []
    mrrs = []
    
    for q in test_queries:
        query_str = " ".join(q["missing_skills"])
        query_vec = vectorizer.transform([query_str])
        sims = cosine_similarity(query_vec, catalog_matrix).flatten()
        
        ranked_indices = np.argsort(sims)[::-1]
        recommended_titles = [catalog[idx]["title"] for idx in ranked_indices]
        
        p = calculate_precision_at_k(q["ground_truth"], recommended_titles, k=k)
        r = calculate_recall_at_k(q["ground_truth"], recommended_titles, k=k)
        mrr = calculate_mrr(q["ground_truth"], recommended_titles)
        
        precisions.append(p)
        recalls.append(r)
        mrrs.append(mrr)
        
    return {
        "Evaluated_Metric_K": k,
        "Mean_Precision_at_K": round(float(np.mean(precisions)), 4),
        "Mean_Recall_at_K": round(float(np.mean(recalls)), 4),
        "Mean_Reciprocal_Rank_MRR": round(float(np.mean(mrrs)), 4)
    }

if __name__ == "__main__":
    results = evaluate_retrieval_system(k=3)
    print("=== RAG / Retrieval Evaluation Metrics Results ===")
    print(results)
