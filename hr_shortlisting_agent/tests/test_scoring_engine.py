"""
Tests for the Scoring Engine module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from agent.scoring_engine import ScoringEngine


@pytest.fixture
def mock_api_key():
    """Fixture for mock API key."""
    return "test-api-key-12345"


@pytest.fixture
def mock_model():
    """Fixture for mock model."""
    return "claude-sonnet-4-20250514"


@pytest.fixture
def jd_dict():
    """Fixture for job description dict."""
    return {
        "job_title": "Senior Backend Engineer",
        "required_skills": ["Python", "AWS", "Docker"],
        "minimum_experience_years": 5,
        "experience_domain": "Backend Engineering",
    }


@pytest.fixture
def candidate_dict():
    """Fixture for candidate profile dict."""
    return {
        "name": "John Doe",
        "skills": ["Python", "AWS", "Docker", "PostgreSQL"],
        "total_experience_years": 7,
        "experience_domains": ["Backend Engineering"],
    }


@pytest.fixture
def valid_scoring_response():
    """Fixture for valid scoring engine response."""
    return {
        "skills_match": {"score": 8, "justification": "Strong match on core technologies."},
        "experience_relevance": {"score": 9, "justification": "7 years in backend engineering."},
        "education_certs": {"score": 7, "justification": "Meets education requirement."},
        "project_portfolio": {"score": 8, "justification": "Strong project experience."},
        "communication_quality": {"score": 8, "justification": "Well-structured resume."},
        "weighted_total": 8.05,
        "hire_recommendation": "Hire",
    }


@patch("agent.scoring_engine.SentenceTransformer")
@patch("agent.scoring_engine.anthropic.Anthropic")
def test_score_returns_weighted_total(
    mock_anthropic_cls, mock_embedder_cls, mock_api_key, mock_model, jd_dict, candidate_dict, valid_scoring_response
):
    """Test that score returns dict with weighted_total."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_scoring_response))]
    mock_client.messages.create.return_value = mock_response
    
    mock_embedder = MagicMock()
    mock_embedder_cls.return_value = mock_embedder
    
    engine = ScoringEngine(api_key=mock_api_key, model=mock_model)
    result = engine.score(jd_dict, candidate_dict)
    
    assert "weighted_total" in result
    assert isinstance(result["weighted_total"], float)


@patch("agent.scoring_engine.SentenceTransformer")
@patch("agent.scoring_engine.anthropic.Anthropic")
def test_weighted_total_range(
    mock_anthropic_cls, mock_embedder_cls, mock_api_key, mock_model, jd_dict, candidate_dict, valid_scoring_response
):
    """Test that weighted_total is within 0-10 range."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_scoring_response))]
    mock_client.messages.create.return_value = mock_response
    
    mock_embedder = MagicMock()
    mock_embedder_cls.return_value = mock_embedder
    
    engine = ScoringEngine(api_key=mock_api_key, model=mock_model)
    result = engine.score(jd_dict, candidate_dict)
    
    assert 0.0 <= result["weighted_total"] <= 10.0


@patch("agent.scoring_engine.SentenceTransformer")
@patch("agent.scoring_engine.anthropic.Anthropic")
def test_hire_recommendation_values(
    mock_anthropic_cls, mock_embedder_cls, mock_api_key, mock_model, jd_dict, candidate_dict, valid_scoring_response
):
    """Test that hire_recommendation is a valid value."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_scoring_response))]
    mock_client.messages.create.return_value = mock_response
    
    mock_embedder = MagicMock()
    mock_embedder_cls.return_value = mock_embedder
    
    engine = ScoringEngine(api_key=mock_api_key, model=mock_model)
    result = engine.score(jd_dict, candidate_dict)
    
    valid_recommendations = ["Hire", "Maybe", "No Hire"]
    assert result["hire_recommendation"] in valid_recommendations


@patch("agent.scoring_engine.SentenceTransformer")
@patch("agent.scoring_engine.anthropic.Anthropic")
def test_score_all_returns_list(
    mock_anthropic_cls, mock_embedder_cls, mock_api_key, mock_model, jd_dict, valid_scoring_response
):
    """Test that score_all returns list of correct length."""
    # Create 3 mock candidate profiles
    candidates = [
        {"name": "Candidate 1", "skills": ["Python"]},
        {"name": "Candidate 2", "skills": ["Python", "AWS"]},
        {"name": "Candidate 3", "skills": ["Python", "AWS", "Docker"]},
    ]
    
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_scoring_response))]
    mock_client.messages.create.return_value = mock_response
    
    mock_embedder = MagicMock()
    mock_embedder_cls.return_value = mock_embedder
    
    engine = ScoringEngine(api_key=mock_api_key, model=mock_model)
    results = engine.score_all(jd_dict, candidates)
    
    assert isinstance(results, list)
    assert len(results) == 3
    
    # Check that candidate data is attached
    for result in results:
        assert "candidate" in result


@patch("agent.scoring_engine.SentenceTransformer")
@patch("agent.scoring_engine.anthropic.Anthropic")
def test_score_invalid_json_raises(mock_anthropic_cls, mock_embedder_cls, mock_api_key, mock_model, jd_dict, candidate_dict):
    """Test that score raises ValueError on invalid JSON."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Invalid JSON {")]
    mock_client.messages.create.return_value = mock_response
    
    mock_embedder = MagicMock()
    mock_embedder_cls.return_value = mock_embedder
    
    engine = ScoringEngine(api_key=mock_api_key, model=mock_model)
    
    with pytest.raises(ValueError, match="invalid JSON"):
        engine.score(jd_dict, candidate_dict)


@patch("agent.scoring_engine.SentenceTransformer")
@patch("agent.scoring_engine.anthropic.Anthropic")
def test_all_dimensions_present(
    mock_anthropic_cls, mock_embedder_cls, mock_api_key, mock_model, jd_dict, candidate_dict, valid_scoring_response
):
    """Test that all 5 scoring dimensions are present."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps(valid_scoring_response))]
    mock_client.messages.create.return_value = mock_response
    
    mock_embedder = MagicMock()
    mock_embedder_cls.return_value = mock_embedder
    
    engine = ScoringEngine(api_key=mock_api_key, model=mock_model)
    result = engine.score(jd_dict, candidate_dict)
    
    dimensions = [
        "skills_match",
        "experience_relevance",
        "education_certs",
        "project_portfolio",
        "communication_quality",
    ]
    for dimension in dimensions:
        assert dimension in result
        assert "score" in result[dimension]
        assert "justification" in result[dimension]
