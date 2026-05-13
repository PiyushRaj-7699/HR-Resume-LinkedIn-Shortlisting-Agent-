"""
Tests for the JD Parser module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from agent.jd_parser import JDParser


@pytest.fixture
def mock_api_key():
    """Fixture for mock API key."""
    return "test-api-key-12345"


@pytest.fixture
def mock_model():
    """Fixture for mock model."""
    return "claude-sonnet-4-20250514"


@pytest.fixture
def valid_jd_response():
    """Fixture for valid JD parser response."""
    return {
        "job_title": "Senior Software Engineer",
        "required_skills": ["Python", "AWS", "Docker", "PostgreSQL"],
        "preferred_skills": ["Kubernetes", "GraphQL"],
        "minimum_experience_years": 5,
        "experience_domain": "Backend Engineering",
        "education_requirement": "B.S. in Computer Science or equivalent",
        "key_responsibilities": [
            "Design and implement scalable backend services",
            "Lead code reviews and mentor junior developers",
        ],
        "nice_to_have": ["Open source contributions", "Publication record"],
    }


@patch("agent.jd_parser.anthropic.Anthropic")
def test_parse_returns_dict(mock_anthropic_cls, mock_api_key, mock_model, valid_jd_response):
    """Test that JDParser.parse returns a dict."""
    # Mock the API response
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_jd_response))]
    mock_client.messages.create.return_value = mock_response
    
    parser = JDParser(api_key=mock_api_key, model=mock_model)
    result = parser.parse("Senior Software Engineer job posting...")
    
    assert isinstance(result, dict)
    assert "job_title" in result
    assert result["job_title"] == "Senior Software Engineer"


@patch("agent.jd_parser.anthropic.Anthropic")
def test_parse_invalid_json_raises(mock_anthropic_cls, mock_api_key, mock_model):
    """Test that JDParser.parse raises ValueError on invalid JSON."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="This is not valid JSON {")]
    mock_client.messages.create.return_value = mock_response
    
    parser = JDParser(api_key=mock_api_key, model=mock_model)
    
    with pytest.raises(ValueError, match="invalid JSON"):
        parser.parse("Senior Software Engineer job posting...")


@patch("agent.jd_parser.anthropic.Anthropic")
def test_required_keys_present(mock_anthropic_cls, mock_api_key, mock_model, valid_jd_response):
    """Test that parsed result has all required keys."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_jd_response))]
    mock_client.messages.create.return_value = mock_response
    
    parser = JDParser(api_key=mock_api_key, model=mock_model)
    result = parser.parse("Job description...")
    
    required_keys = ["required_skills", "experience_domain", "job_title"]
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"


@patch("agent.jd_parser.anthropic.Anthropic")
def test_parse_with_markdown_fences(mock_anthropic_cls, mock_api_key, mock_model, valid_jd_response):
    """Test that parser strips markdown code fences."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    # Return JSON wrapped in markdown fences
    json_str = json.dumps(valid_jd_response)
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=f"```json\n{json_str}\n```")]
    mock_client.messages.create.return_value = mock_response
    
    parser = JDParser(api_key=mock_api_key, model=mock_model)
    result = parser.parse("Job description...")
    
    assert isinstance(result, dict)
    assert result["job_title"] == "Senior Software Engineer"
