"""
Job Description parser using Claude LLM to extract structured information.
"""

import json
import logging
import re
from pathlib import Path
import anthropic

logger = logging.getLogger(__name__)


class JDParser:
    """
    Parses a job description into structured JSON using Claude LLM.
    """

    def __init__(self, api_key: str, model: str):
        """
        Initialize the JD parser with Anthropic API credentials and model.

        Args:
            api_key: Anthropic API key.
            model: Model identifier (e.g., "claude-sonnet-4-20250514").
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

        # Load prompt template
        prompt_file = Path(__file__).parent.parent / "prompts" / "jd_parse_prompt.txt"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def parse(self, jd_text: str) -> dict:
        """
        Parse a job description and return structured JSON.

        Args:
            jd_text: Raw job description text.

        Returns:
            Structured dict with JD information.

        Raises:
            ValueError: If the LLM response is not valid JSON.
        """
        # Format prompt with JD text
        prompt = self.prompt_template.format(job_description=jd_text)

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # Extract response text
        response_text = message.content[0].text.strip()

        # Remove markdown fences if present
        response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
        response_text = re.sub(r"\s*```$", "", response_text)
        response_text = response_text.strip()

        # Parse JSON
        try:
            result = json.loads(response_text)
            logger.info("JD parsed successfully")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JD Parser returned invalid JSON: {response_text}")
            raise ValueError(
                f"JD Parser returned invalid JSON. Error: {e}. Response: {response_text[:200]}"
            )
