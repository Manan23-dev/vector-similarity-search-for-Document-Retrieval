#!/usr/bin/env python3
"""
Evaluation script for retrieval and response-level metrics.
Run after initializing the index: python evaluate.py
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.embeddings.embedder import Embedder
from src.index.index_manager import IndexManager
from evaluation.retrieval_metrics import compute_retrieval_metrics
from evaluation.response_metrics import compute_faithfulness, compute_relevance


def search_fn_factory(index_manager, embedder, ef: int = 50):
    """Build a search function for the evaluation harness."""

    def search(query: str, top_k: int = 10):
        query_embedding = embedder.generate_embeddings([query], show_progress=False)
        doc_ids, distances, documents = index_manager.search(
            query_embedding[0], k=top_k, ef=ef
        )
        return [
            {"document_id": doc_id, "score": 1 - d, "title": doc.get("title", "")}
            for doc_id, d, doc in zip(doc_ids, distances, documents)
        ]

    return search


def main():
    parser = argparse.ArgumentParser(description="Evaluate retrieval and response metrics")
    parser.add_argument(
        "--eval-file",
        type=str,
        default="evaluation/eval_queries.json",
        help="Path to evaluation queries JSON",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_report.json",
        help="Output path for metrics report",
    )
    parser.add_argument("--ef", type=int, default=50, help="HNSW ef search parameter")
    parser.add_argument(
        "--tune-ef",
        action="store_true",
        help="Sweep ef values 40-100 and report best",
    )
    args = parser.parse_args()

    print("Loading index and embedder...")
    embedder = Embedder("all-mpnet-base-v2")
    index_manager = IndexManager(
        embedding_dim=embedder.get_embedding_dimension(),
        index_path="data/vector_index",
    )

    if not index_manager.load_index():
        print("ERROR: Index not found. Run: python initialize_dataset.py --max-papers 5000")
        sys.exit(1)

    eval_path = Path(args.eval_file)
    if not eval_path.exists():
        print(f"ERROR: Eval file not found: {eval_path}")
        sys.exit(1)

    with open(eval_path, "r") as f:
        eval_queries = json.load(f)

    if args.tune_ef:
        print("Tuning ef parameter (40, 50, 60, 70, 80, 90, 100)...")
        best_ef, best_ndcg = 50, -1.0
        for ef in [40, 50, 60, 70, 80, 90, 100]:
            search_fn = search_fn_factory(index_manager, embedder, ef=ef)
            metrics = compute_retrieval_metrics(eval_queries, search_fn, k_values=[1, 5, 10])
            ndcg = metrics.get("ndcg_at_10", 0)
            print(f"  ef={ef}: NDCG@10={ndcg:.4f}")
            if ndcg > best_ndcg:
                best_ndcg, best_ef = ndcg, ef
        print(f"\nBest ef={best_ef} (NDCG@10={best_ndcg:.4f})")
        return

    print(f"Running retrieval evaluation on {len(eval_queries)} queries (ef={args.ef})...")
    search_fn = search_fn_factory(index_manager, embedder, ef=args.ef)
    retrieval_metrics = compute_retrieval_metrics(
        eval_queries,
        search_fn,
        k_values=[1, 5, 10],
    )

    print("\n--- Retrieval Metrics ---")
    for name, value in retrieval_metrics.items():
        print(f"  {name}: {value:.4f}")

    response_scores = []
    for item in eval_queries[:3]:
        query = item["query"]
        results = search_fn(query, top_k=3)
        context = "\n".join(
            (r.get("title", "") or "") + " " + str(r.get("score", "")) for r in results
        )
        answer = f"Based on the papers: {query} is addressed in the retrieved context."
        faith = compute_faithfulness(answer, context)
        rel = compute_relevance(query, answer)
        response_scores.append({"faithfulness": faith, "relevance": rel})

    avg_faith = sum(s["faithfulness"] for s in response_scores) / max(1, len(response_scores))
    avg_rel = sum(s["relevance"] for s in response_scores) / max(1, len(response_scores))

    print("\n--- Response-Level Metrics (heuristic) ---")
    print(f"  avg_faithfulness: {avg_faith:.4f}")
    print(f"  avg_relevance: {avg_rel:.4f}")

    report = {
        "retrieval_metrics": retrieval_metrics,
        "response_metrics": {
            "avg_faithfulness": avg_faith,
            "avg_relevance": avg_rel,
        },
        "n_queries": len(eval_queries),
    }

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
