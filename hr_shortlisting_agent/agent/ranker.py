"""
Ranker module for sorting scored candidates by performance.
"""

import logging

logger = logging.getLogger(__name__)


def rank_candidates(scored_results: list) -> list:
    """
    Sort candidates by weighted_total score in descending order and add rank.

    Args:
        scored_results: List of scoring result dicts.

    Returns:
        Sorted list with added "rank" key (1 = highest score).
    """
    # Sort by weighted_total descending
    sorted_results = sorted(
        scored_results,
        key=lambda x: x.get("weighted_total", 0),
        reverse=True,
    )

    # Add rank
    for i, result in enumerate(sorted_results, start=1):
        result["rank"] = i

    logger.info(f"Ranked {len(sorted_results)} candidates")
    return sorted_results


def filter_by_recommendation(ranked_results: list, recommendation: str) -> list:
    """
    Filter candidates by hire recommendation.

    Args:
        ranked_results: List of ranked result dicts.
        recommendation: One of "Hire", "Maybe", "No Hire".

    Returns:
        Filtered list of results matching the recommendation.

    Raises:
        ValueError: If recommendation is not a valid value.
    """
    valid_recommendations = ["Hire", "Maybe", "No Hire"]
    if recommendation not in valid_recommendations:
        raise ValueError(
            f"Invalid recommendation '{recommendation}'. Must be one of: {valid_recommendations}"
        )

    filtered = [r for r in ranked_results if r.get("hire_recommendation") == recommendation]
    logger.info(f"Filtered {len(filtered)} candidates with recommendation: {recommendation}")
    return filtered
