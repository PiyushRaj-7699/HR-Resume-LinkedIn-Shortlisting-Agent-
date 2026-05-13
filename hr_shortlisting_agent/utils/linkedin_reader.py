"""
LinkedIn profile JSON parser for extracting and normalizing profile data.
"""

import json
import logging

logger = logging.getLogger(__name__)


def parse_linkedin_json(data: dict) -> str:
    """
    Parse and format a LinkedIn profile dict into a structured plain-text string.

    Args:
        data: Python dict parsed from LinkedIn export JSON.

    Returns:
        Formatted plain-text string with profile information.
    """
    text_blocks = []

    # Name
    name = data.get("name") or f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
    if name:
        text_blocks.append(f"Name: {name}")

    # Email
    email = data.get("email")
    if email:
        text_blocks.append(f"Email: {email}")

    # Headline
    headline = data.get("headline")
    if headline:
        text_blocks.append(f"Headline: {headline}")

    # Summary
    summary = data.get("summary")
    if summary:
        text_blocks.append(f"Summary: {summary}")

    # Positions (job history)
    positions = data.get("positions", [])
    if positions:
        text_blocks.append("\nJob Positions:")
        for pos in positions:
            title = pos.get("title", "Unknown Title")
            company = pos.get("company", "Unknown Company")
            duration = pos.get("duration", "Unknown Duration")
            description = pos.get("description", "")
            
            pos_text = f"  - {title} at {company} ({duration})"
            if description:
                pos_text += f"\n    {description}"
            text_blocks.append(pos_text)

    # Education
    educations = data.get("educations", [])
    if educations:
        text_blocks.append("\nEducation:")
        for edu in educations:
            degree = edu.get("degree", "")
            school = edu.get("school", "")
            year = edu.get("year", "")
            
            edu_text = f"  - {degree} from {school}"
            if year:
                edu_text += f" ({year})"
            text_blocks.append(edu_text)

    # Skills
    skills = data.get("skills", [])
    if skills:
        skill_names = [s.get("name", "") if isinstance(s, dict) else str(s) for s in skills]
        text_blocks.append(f"\nSkills: {', '.join(skill_names)}")

    # Projects
    projects = data.get("projects", [])
    if projects:
        text_blocks.append("\nProjects:")
        for proj in projects:
            title = proj.get("title", "Unknown Project")
            description = proj.get("description", "")
            
            proj_text = f"  - {title}"
            if description:
                proj_text += f"\n    {description}"
            text_blocks.append(proj_text)

    return "\n".join(text_blocks)


def load_linkedin_from_file(file_path: str) -> str:
    """
    Load and parse a LinkedIn JSON export file.

    Args:
        file_path: Path to the LinkedIn JSON export file.

    Returns:
        Formatted plain-text string with profile information.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return parse_linkedin_json(data)
    except FileNotFoundError as e:
        logger.error(f"LinkedIn JSON file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
