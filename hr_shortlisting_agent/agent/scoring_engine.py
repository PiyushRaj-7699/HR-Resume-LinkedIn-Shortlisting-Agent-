"""
Scoring engine for evaluating candidates against job descriptions using Claude LLM.
"""

import json
import logging
import re
from pathlib import Path
import numpy as np
import anthropic
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Scores candidate profiles against a job description using Claude LLM reasoning
    and optional semantic similarity as a cross-check.
    """

    def __init__(self, api_key: str, model: str):
        """
        Initialize the scoring engine with LLM and embedding model.

        Args:
            api_key: Anthropic API key.
            model: Claude model identifier (e.g., "claude-sonnet-4-20250514").
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

        # Load prompt template
        prompt_file = Path(__file__).parent.parent / "prompts" / "scoring_prompt.txt"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

        # Load embedding model for optional semantic similarity check
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.embedder = None

    def _compute_skill_similarity(self, jd_skills: list, candidate_skills: list) -> float:
        """
        Compute cosine similarity between JD skills and candidate skills using embeddings.

        Args:
            jd_skills: List of required skills from JD.
            candidate_skills: List of skills from candidate profile.

        Returns:
            Cosine similarity score between 0 and 1.
        """
        if not self.embedder or not jd_skills or not candidate_skills:
            return 0.5  # Neutral if embedder unavailable or empty lists

        try:
            jd_text = ", ".join(jd_skills)
            candidate_text = ", ".join(candidate_skills)

            jd_embedding = self.embedder.encode(jd_text)
            candidate_embedding = self.embedder.encode(candidate_text)

            # Compute cosine similarity
            similarity = np.dot(jd_embedding, candidate_embedding) / (
                np.linalg.norm(jd_embedding) * np.linalg.norm(candidate_embedding)
            )
            return float(similarity)
        except Exception as e:
            logger.warning(f"Error computing skill similarity: {e}")
            return 0.5

    def score(self, jd_dict: dict, candidate_dict: dict) -> dict:
        """
        Score a candidate profile against the job description.

        Args:
            jd_dict: Parsed job description dict.
            candidate_dict: Parsed candidate profile dict.

        Returns:
            Scoring result dict with all dimension scores and weighted total.

        Raises:
            ValueError: If the LLM response is not valid JSON.
        """
        # Format prompt with JSON dicts
        prompt = self.prompt_template.format(
            jd_json=json.dumps(jd_dict),
            candidate_json=json.dumps(candidate_dict),
        )

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # Extract response text
        response_text = message.content[0].text.strip()

        # Remove markdown fences
        response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
        response_text = re.sub(r"\s*```$", "", response_text)
        response_text = response_text.strip()

        # Parse JSON
        try:
            result = json.loads(response_text)
            logger.info(
                f"Scored {candidate_dict.get('name', 'Unknown')}: {result.get('weighted_total', 'N/A')}"
            )

            # Optional: Cross-check skills similarity
            if self.embedder:
                jd_skills = jd_dict.get("required_skills", [])
                candidate_skills = candidate_dict.get("skills", [])
                skill_similarity = self._compute_skill_similarity(jd_skills, candidate_skills)
                llm_skill_score = result.get("skills_match", {}).get("score", 5) / 10.0

                if abs(skill_similarity - llm_skill_score) > 0.3:
                    logger.warning(
                        f"Skill similarity mismatch for {candidate_dict.get('name', 'Unknown')}: "
                        f"LLM={llm_skill_score:.2f}, Semantic={skill_similarity:.2f}"
                    )

            return result
        except json.JSONDecodeError as e:
            logger.error(f"Scoring Engine returned invalid JSON: {response_text[:200]}")
            raise ValueError(
                f"Scoring Engine returned invalid JSON. Error: {e}. Response: {response_text[:200]}"
            )

    def score_all(self, jd_dict: dict, candidate_profiles: list) -> list:
        """
        Score all candidate profiles against the job description.

        Args:
            jd_dict: Parsed job description dict.
            candidate_profiles: List of parsed candidate profile dicts.

        Returns:
            List of scoring result dicts with original candidate data attached.
        """
        results = []
        for i, candidate in enumerate(candidate_profiles):
            logger.info(f"Scoring candidate {i+1}/{len(candidate_profiles)}")
            try:
                score_result = self.score(jd_dict, candidate)
                # Attach original candidate profile data
                score_result["candidate"] = candidate
                results.append(score_result)
            except Exception as e:
                logger.error(f"Failed to score candidate {candidate.get('name', 'Unknown')}: {e}")
                continue

        logger.info(f"Successfully scored {len(results)}/{len(candidate_profiles)} candidates")
        return results
