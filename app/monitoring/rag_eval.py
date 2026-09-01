import numpy as np
import pandas as pd
from app.services.hybrid_rag import HybridRAGRetriever

def calculate_precision_at_k(actual_relevant: set, recommended_items: list, k: int = 3) -> float:
    if k <= 0 or not recommended_items:
        return 0.0
    top_k = recommended_items[:k]
    relevant_in_top_k = set(top_k).intersection(actual_relevant)
    return len(relevant_in_top_k) / float(k)

def calculate_recall_at_k(actual_relevant: set, recommended_items: list, k: int = 3) -> float:
    if not actual_relevant or not recommended_items:
        return 0.0
    top_k = recommended_items[:k]
    relevant_in_top_k = set(top_k).intersection(actual_relevant)
    return len(relevant_in_top_k) / float(len(actual_relevant))

def calculate_mrr(actual_relevant: set, recommended_items: list) -> float:
    for rank_idx, item in enumerate(recommended_items, start=1):
        if item in actual_relevant:
            return 1.0 / rank_idx
    return 0.0

def evaluate_retrieval_system(k: int = 3):
    """
    Evaluates Dense Vector, Lexical BM25, and Hybrid RAG (Reciprocal Rank Fusion)
    on standard IR metrics: Precision@K, Recall@K, and MRR.
    """
    retriever = HybridRAGRetriever()
    
    test_queries = [
        {
            "missing_skills": ["Python", "Data Science", "Machine Learning"],
            "ground_truth": {"Advanced Python & Automated Analytics", "Machine Learning & Predictive Modeling"}
        },
        {
            "missing_skills": ["AWS Cloud", "Cloud Architecture", "Azure"],
            "ground_truth": {"Enterprise Cloud Architecture (AWS/Azure)"}
        },
        {
            "missing_skills": ["Critical Thinking", "Active Learning", "Complex Problem Solving"],
            "ground_truth": {"Critical Thinking & Strategic Problem Solving"}
        },
        {
            "missing_skills": ["Microsoft Excel", "SQL", "Database Administration"],
            "ground_truth": {"Advanced Microsoft Excel & Power BI", "SQL & Big Data Engineering Masterclass"}
        }
    ]
    
    hybrid_precisions, hybrid_recalls, hybrid_mrrs = [], [], []
    
    for q in test_queries:
        recs = [item["title"] for item in retriever.retrieve_hybrid(q["missing_skills"], top_k=k)]
        
        p = calculate_precision_at_k(q["ground_truth"], recs, k=k)
        r = calculate_recall_at_k(q["ground_truth"], recs, k=k)
        mrr = calculate_mrr(q["ground_truth"], recs)
        
        hybrid_precisions.append(p)
        hybrid_recalls.append(r)
        hybrid_mrrs.append(mrr)
        
    return {
        "Evaluated_Metric_K": k,
        "Retrieval_Strategy": "Hybrid RAG (BM25 + Dense Vector + Reciprocal Rank Fusion)",
        "Mean_Precision_at_K": round(float(np.mean(hybrid_precisions)), 4),
        "Mean_Recall_at_K": round(float(np.mean(hybrid_recalls)), 4),
        "Mean_Reciprocal_Rank_MRR": round(float(np.mean(hybrid_mrrs)), 4)
    }

if __name__ == "__main__":
    results = evaluate_retrieval_system(k=3)
    print("=== Hybrid RAG Retrieval System Evaluation Results ===")
    print(results)
