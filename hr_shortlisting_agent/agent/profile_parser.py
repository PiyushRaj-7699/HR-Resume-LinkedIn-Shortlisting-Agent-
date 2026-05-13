"""
Profile parser for resumes and LinkedIn profiles using Claude LLM.
"""

import json
import logging
import re
from pathlib import Path
import anthropic

from utils.file_reader import extract_text
from utils.linkedin_reader import parse_linkedin_json

logger = logging.getLogger(__name__)


class ProfileParser:
    """
    Parses candidate resumes and LinkedIn profiles into structured JSON using Claude LLM.
    """

    def __init__(self, api_key: str, model: str):
        """
        Initialize the profile parser with Anthropic API credentials and model.

        Args:
            api_key: Anthropic API key.
            model: Model identifier (e.g., "claude-sonnet-4-20250514").
        """
        self.api_key = api_key
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

        # Load prompt template
        prompt_file = Path(__file__).parent.parent / "prompts" / "profile_parse_prompt.txt"
        with open(prompt_file, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()

    def parse(self, profile_text: str) -> dict:
        """
        Parse a resume or profile text and return structured JSON.

        Args:
            profile_text: Raw resume or profile text.

        Returns:
            Structured dict with candidate information.

        Raises:
            ValueError: If the LLM response is not valid JSON.
        """
        # Format prompt with profile text
        prompt = self.prompt_template.format(resume_text=profile_text)

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
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
            logger.info(f"Profile parsed successfully for {result.get('name', 'Unknown')}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Profile Parser returned invalid JSON: {response_text[:200]}")
            raise ValueError(
                f"Profile Parser returned invalid JSON. Error: {e}. Response: {response_text[:200]}"
            )

    def parse_from_file(self, file_path: str) -> dict:
        """
        Parse a resume from a PDF or DOCX file.

        Args:
            file_path: Path to the resume file (PDF or DOCX).

        Returns:
            Structured dict with candidate information.

        Raises:
            ValueError: If the file format is unsupported or parsing fails.
        """
        # Extract text from file
        profile_text = extract_text(file_path)
        if not profile_text.strip():
            raise ValueError(f"No text could be extracted from file: {file_path}")

        # Parse the extracted text
        return self.parse(profile_text)

    def parse_from_linkedin(self, linkedin_data: dict) -> dict:
        """
        Parse a LinkedIn profile from a dict.

        Args:
            linkedin_data: LinkedIn profile data as a dict (from JSON export).

        Returns:
            Structured dict with candidate information.

        Raises:
            ValueError: If parsing fails.
        """
        # Convert LinkedIn dict to text
        profile_text = parse_linkedin_json(linkedin_data)

        # Parse the formatted text
        return self.parse(profile_text)
