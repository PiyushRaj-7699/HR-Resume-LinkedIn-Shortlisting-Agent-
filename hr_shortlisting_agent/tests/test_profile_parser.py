"""
Tests for the Profile Parser module.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from agent.profile_parser import ProfileParser


@pytest.fixture
def mock_api_key():
    """Fixture for mock API key."""
    return "test-api-key-12345"


@pytest.fixture
def mock_model():
    """Fixture for mock model."""
    return "claude-sonnet-4-20250514"


@pytest.fixture
def valid_profile_response():
    """Fixture for valid profile parser response."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "skills": ["Python", "AWS", "Docker", "PostgreSQL", "Kubernetes"],
        "total_experience_years": 7,
        "experience_domains": ["Backend Engineering", "DevOps"],
        "job_history": [
            {
                "title": "Senior Backend Engineer",
                "company": "Tech Corp",
                "duration": "2021-present",
                "description": "Led backend infrastructure team",
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "State University",
                "year": "2016",
            }
        ],
        "certifications": ["AWS Solutions Architect Professional"],
        "projects": [
            {
                "title": "Microservices Migration",
                "description": "Migrated monolith to microservices",
                "technologies": ["Python", "Docker", "Kubernetes"],
            }
        ],
        "communication_quality": "crisp",
    }


@patch("agent.profile_parser.anthropic.Anthropic")
def test_parse_resume_returns_dict(mock_anthropic_cls, mock_api_key, mock_model, valid_profile_response):
    """Test that ProfileParser.parse returns a dict."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_profile_response))]
    mock_client.messages.create.return_value = mock_response
    
    parser = ProfileParser(api_key=mock_api_key, model=mock_model)
    result = parser.parse("John Doe\nSenior Backend Engineer at Tech Corp...")
    
    assert isinstance(result, dict)
    assert result["name"] == "John Doe"


@patch("agent.profile_parser.anthropic.Anthropic")
def test_skills_is_list(mock_anthropic_cls, mock_api_key, mock_model, valid_profile_response):
    """Test that skills is returned as a list."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_profile_response))]
    mock_client.messages.create.return_value = mock_response
    
    parser = ProfileParser(api_key=mock_api_key, model=mock_model)
    result = parser.parse("Resume text...")
    
    assert isinstance(result["skills"], list)
    assert len(result["skills"]) > 0


@patch("agent.profile_parser.extract_text")
@patch("agent.profile_parser.anthropic.Anthropic")
def test_parse_from_file_pdf(mock_anthropic_cls, mock_extract_text, mock_api_key, mock_model, valid_profile_response):
    """Test parsing a PDF resume file."""
    # Mock extract_text to return some sample text
    mock_extract_text.return_value = "John Doe\nSenior Backend Engineer..."
    
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_profile_response))]
    mock_client.messages.create.return_value = mock_response
    
    parser = ProfileParser(api_key=mock_api_key, model=mock_model)
    result = parser.parse_from_file("/path/to/resume.pdf")
    
    assert isinstance(result, dict)
    assert result["name"] == "John Doe"
    mock_extract_text.assert_called_once()


@patch("agent.profile_parser.extract_text")
@patch("agent.profile_parser.anthropic.Anthropic")
def test_parse_from_file_raises_on_empty(mock_anthropic_cls, mock_extract_text, mock_api_key, mock_model):
    """Test that parse_from_file raises error on empty extraction."""
    mock_extract_text.return_value = "   "  # Empty/whitespace only
    
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    parser = ProfileParser(api_key=mock_api_key, model=mock_model)
    
    with pytest.raises(ValueError, match="No text could be extracted"):
        parser.parse_from_file("/path/to/empty_resume.pdf")


@patch("agent.profile_parser.parse_linkedin_json")
@patch("agent.profile_parser.anthropic.Anthropic")
def test_parse_from_linkedin(mock_anthropic_cls, mock_parse_linkedin, mock_api_key, mock_model, valid_profile_response):
    """Test parsing LinkedIn profile data."""
    mock_parse_linkedin.return_value = "Name: John Doe\nHeadline: Senior Backend Engineer..."
    
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_profile_response))]
    mock_client.messages.create.return_value = mock_response
    
    parser = ProfileParser(api_key=mock_api_key, model=mock_model)
    linkedin_data = {"name": "John Doe", "headline": "Senior Backend Engineer"}
    result = parser.parse_from_linkedin(linkedin_data)
    
    assert isinstance(result, dict)
    assert result["name"] == "John Doe"


@patch("agent.profile_parser.anthropic.Anthropic")
def test_parse_invalid_json_raises(mock_anthropic_cls, mock_api_key, mock_model):
    """Test that parse raises ValueError on invalid JSON."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Invalid JSON {incomplete")]
    mock_client.messages.create.return_value = mock_response
    
    parser = ProfileParser(api_key=mock_api_key, model=mock_model)
    
    with pytest.raises(ValueError, match="invalid JSON"):
        parser.parse("Resume text...")
