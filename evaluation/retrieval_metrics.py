"""
Retrieval evaluation metrics: Recall@k, MRR, NDCG.
Measures ranking quality and retrieval effectiveness.
"""

import math
from typing import List, Dict, Any, Optional


def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """
    Recall@k: fraction of relevant docs in top-k results.
    Higher is better (max 1.0).
    """
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = len(set(top_k) & set(relevant_ids))
    return hits / len(relevant_ids)


def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """
    Mean Reciprocal Rank: 1/rank of first relevant doc.
    Higher is better (max 1.0).
    """
    if not relevant_ids:
        return 0.0
    relevant_set = set(relevant_ids)
    for rank, doc_id in enumerate(retrieved_ids, 1):
        if doc_id in relevant_set:
            return 1.0 / rank
    return 0.0


def dcg_at_k(relevances: List[float], k: int) -> float:
    """Discounted Cumulative Gain at k (relevance scores in order of retrieval)."""
    relevances = relevances[:k]
    if not relevances:
        return 0.0
    return sum((2**r - 1) / math.log2(rank + 1) for rank, r in enumerate(relevances, 1))


def ndcg_at_k(
    retrieved_ids: List[str],
    relevance_dict: Dict[str, float],
    k: int,
) -> float:
    """
    Normalized DCG@k: DCG / ideal DCG.
    relevance_dict maps doc_id -> relevance (0-3 typically).
    Higher is better (max 1.0).
    """
    relevances = [relevance_dict.get(doc_id, 0.0) for doc_id in retrieved_ids[:k]]
    dcg = dcg_at_k(relevances, k)
    ideal_relevances = sorted(
        (relevance_dict.get(doc_id, 0.0) for doc_id in relevance_dict),
        reverse=True,
    )
    idcg = dcg_at_k(ideal_relevances, k)
    if idcg <= 0:
        return 0.0
    return dcg / idcg


def compute_retrieval_metrics(
    queries: List[Dict[str, Any]],
    search_fn,
    k_values: List[int] = [1, 5, 10],
) -> Dict[str, float]:
    """
    Compute retrieval metrics over a labeled eval set.

    Args:
        queries: List of {"query": str, "relevant_ids": [doc_ids], "relevance": {doc_id: score}}
        search_fn: Function(query, top_k) -> List[dict with "document_id"]
        k_values: Values of k for Recall@k

    Returns:
        Dict with recall_at_1, recall_at_5, recall_at_10, mrr, ndcg_at_10
    """
    recall_sums = {k: 0.0 for k in k_values}
    mrr_sum = 0.0
    ndcg_sum = 0.0
    n = len(queries)
    if n == 0:
        return {}

    for item in queries:
        query = item["query"]
        relevant_ids = item.get("relevant_ids", [])
        relevance_dict = item.get("relevance", {})
        if not relevance_dict and relevant_ids:
            relevance_dict = {rid: 1.0 for rid in relevant_ids}

        results = search_fn(query, top_k=max(k_values))
        retrieved_ids = []
        for r in results:
            doc_id = r.get("document_id") or r.get("doc_id") if isinstance(r, dict) else getattr(r, "document_id", None)
            if doc_id:
                retrieved_ids.append(str(doc_id))

        for k in k_values:
            recall_sums[k] += recall_at_k(retrieved_ids, relevant_ids, k)
        mrr_sum += mrr(retrieved_ids, relevant_ids)
        ndcg_sum += ndcg_at_k(retrieved_ids, relevance_dict, max(k_values))

    metrics = {}
    for k in k_values:
        metrics[f"recall_at_{k}"] = recall_sums[k] / n
    metrics["mrr"] = mrr_sum / n
    metrics["ndcg_at_10"] = ndcg_sum / n
    return metrics
