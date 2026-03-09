"""
Response-level evaluation: faithfulness and relevance.
Measures downstream decision impact of RAG answers.
"""

import re
from typing import List, Optional


def compute_faithfulness(answer: str, context: str) -> float:
    """
    Faithfulness: does the answer stay grounded in the context?
    Uses simple lexical overlap as a heuristic (0-1).
    For production, use LLM-as-judge or NLI models.
    """
    if not answer or not context:
        return 0.0
    # Normalize: lowercase, split into words
    answer_words = set(re.findall(r"\b\w+\b", answer.lower()))
    context_words = set(re.findall(r"\b\w+\b", context.lower()))
    # Remove common stopwords for a cleaner signal
    stop = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "of", "to", "in", "on", "at"}
    answer_words -= stop
    context_words -= stop
    if not answer_words:
        return 1.0  # Empty answer is trivially faithful
    overlap = len(answer_words & context_words) / len(answer_words)
    return min(1.0, overlap * 1.5)  # Slight boost for partial overlap


def compute_relevance(question: str, answer: str) -> float:
    """
    Relevance: does the answer address the question?
    Uses keyword overlap heuristic (0-1).
    For production, use LLM-as-judge or semantic similarity.
    """
    if not question or not answer:
        return 0.0
    q_words = set(re.findall(r"\b\w+\b", question.lower()))
    a_words = set(re.findall(r"\b\w+\b", answer.lower()))
    stop = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "of", "to", "in", "on", "at", "what", "how", "why"}
    q_words -= stop
    a_words -= stop
    if not q_words:
        return 1.0
    overlap = len(q_words & a_words) / len(q_words)
    return min(1.0, overlap * 1.2)
