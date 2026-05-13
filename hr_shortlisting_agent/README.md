# 🤖 HR Resume & LinkedIn Shortlisting Agent

> An AI-powered agent that evaluates candidates against a Job Description using Claude LLM, producing a transparent, rubric-based ranked shortlist with human-in-the-loop override capability.

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Scoring Rubric](#-scoring-rubric)
- [Project Structure](#-project-structure)
- [Running Tests](#-running-tests)
- [Sample Output](#-sample-output)
- [Human-in-the-Loop Override](#-human-in-the-loop-override)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 1. **Intelligent JD Parser**
   - Uses Claude LLM to parse Job Descriptions into structured JSON
   - Extracts required/preferred skills, experience level, responsibilities
   - Identifies key competencies and nice-to-have qualifications

### 2. **Multi-Format Resume Ingestion**
   - Supports PDF and DOCX resume files
   - Supports LinkedIn JSON profile exports
   - Automatic text extraction and normalization

### 3. **Semantic Skill Matching**
   - Uses sentence transformers for embedding-based skill similarity
   - Cross-validates LLM scoring against semantic similarity metrics
   - Detects skill mismatches exceeding 30% threshold

### 4. **Transparent Rubric-Based Scoring**
   - 5-dimensional scoring framework (Skills, Experience, Education, Portfolio, Communication)
   - Weighted scoring: 30%, 25%, 15%, 20%, 10% respectively
   - Individual justifications for each dimension (0-10 scale)

### 5. **Automated Shortlist Ranking**
   - Ranks candidates by weighted total score (descending)
   - Automatic categorization: Hire (≥7.0), Maybe (4.0-6.9), No Hire (<4.0)
   - Filters available by recommendation category

### 6. **Multi-Format Report Generation**
   - **HTML**: Interactive report with expandable candidate details, styled tables, summary metrics
   - **PDF**: Professional PDF with candidate table, color-coded recommendations, justifications
   - **JSON**: Machine-readable format for downstream integration

## 🏗️ Architecture

The agent follows a 7-step pipeline architecture:

```
┌─────────────────┐
│  Input Layer    │
├─────────────────┤
│ 1. JD Ingestion │ → Raw job description text
└────────┬────────┘
         │
┌────────▼────────────────┐
│ 2. JD Parsing (Claude)  │ → Structured JD JSON
└────────┬────────────────┘
         │
┌────────▼─────────────────────┐
│ 3. Resume/Profile Ingestion  │ → Extract text from PDF/DOCX/JSON
└────────┬─────────────────────┘
         │
┌────────▼──────────────────────┐
│ 4. Profile Parsing (Claude)   │ → Structured Candidate JSON
└────────┬──────────────────────┘
         │
┌────────▼──────────────────────────────┐
│ 5. Semantic Matching & Scoring        │
│    (Claude + Embeddings)              │ → 5D Score + Recommendation
└────────┬──────────────────────────────┘
         │
┌────────▼─────────────────┐
│ 6. Ranking & Filtering   │ → Sorted Candidates by Score
└────────┬─────────────────┘
         │
┌────────▼────────────────────────┐
│ 7. HR Override & Audit Logging  │ → Candidate Override Record
└────────┬────────────────────────┘
         │
┌────────▼──────────────┐
│ Output Layer         │
├──────────────────────┤
│ HTML/PDF/JSON Report │
└──────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM & Reasoning** | Anthropic Claude (Sonnet/Opus/Haiku) via SDK |
| **Agent Framework** | Direct Python orchestration (no frameworks) |
| **Embeddings** | `sentence-transformers` (all-MiniLM-L6-v2) |
| **Resume Parsing** | `pymupdf` (PDF) + `python-docx` (DOCX) |
| **LinkedIn Data** | Manual JSON export parsing |
| **Report Generation** | `reportlab` (PDF) + `jinja2` (HTML templating) + JSON |
| **Web UI** | Streamlit (reactive frontend) |
| **Testing** | pytest + unittest.mock |
| **Configuration** | python-dotenv |

## 🚀 Installation

### Prerequisites
- Python 3.9+
- Anthropic API Key (get one at [console.anthropic.com](https://console.anthropic.com))

### Step-by-Step

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd hr_shortlisting_agent
   ```

2. **Create and activate a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API Key
   ```

5. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## ⚙️ Configuration

Environment variables (set in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *required* | Your Anthropic Claude API key |
| `LLM_MODEL` | `claude-sonnet-4-20250514` | Claude model to use (sonnet/opus/haiku) |
| `OUTPUT_DIR` | `outputs/` | Directory for generated reports |

## 🖥️ Usage

### Quick Start

1. **Launch the app**
   ```bash
   streamlit run app.py
   ```

2. **Tab 1: Job Description**
   - Paste or upload the job description
   - Click "Parse JD"
   - Review extracted requirements

3. **Tab 2: Candidates**
   - Upload resume files (PDF/DOCX) and/or LinkedIn JSON profiles
   - Click "Parse & Score All Candidates"
   - Wait for processing (progress bar shows status)

4. **Tab 3: Results & Report**
   - View ranked candidates with scores
   - Expand candidates to see detailed justifications
   - Log score overrides with reason (audit trail)
   - Generate and download report (HTML/PDF/JSON)

### Example Workflow

```
1. Paste Job Description (Senior Backend Engineer)
   ↓
2. Upload 5 resumes (PDF) + 3 LinkedIn profiles (JSON)
   ↓
3. System processes all 8 candidates
   ↓
4. Results: 2 "Hire", 3 "Maybe", 3 "No Hire"
   ↓
5. HR reviews justifications and logs 1 override
   ↓
6. Generate HTML report for stakeholders
```

## 📊 Scoring Rubric

Each candidate is scored on 5 dimensions (0-10 scale, then weighted):

### 1. **Skills Match** (Weight: 30%)
| Score | Interpretation |
|-------|-----------------|
| 0-3 | < 30% skill overlap with JD |
| 4-6 | 50-70% skill overlap |
| 7-9 | 75-85% skill overlap |
| 10 | > 85% skill overlap / exact match |

### 2. **Experience Relevance** (Weight: 25%)
| Score | Interpretation |
|-------|-----------------|
| 0-3 | Completely unrelated domain |
| 4-6 | Adjacent/tangential domain |
| 7-9 | Same domain, partial seniority match |
| 10 | Exact domain match with appropriate seniority |

### 3. **Education & Certifications** (Weight: 15%)
| Score | Interpretation |
|-------|-----------------|
| 0-3 | Does not meet minimum requirement |
| 4-6 | Meets minimum education requirement |
| 7-9 | Exceeds requirement (e.g., advanced degree) |
| 10 | Significantly exceeds + relevant certifications |

### 4. **Project / Portfolio** (Weight: 20%)
| Score | Interpretation |
|-------|-----------------|
| 0-3 | No evidence of relevant projects |
| 4-6 | 1-2 generic or tangential projects |
| 7-9 | 2-3 directly relevant, well-documented projects |
| 10 | Strong, impressive portfolio with scale/impact |

### 5. **Communication Quality** (Weight: 10%)
| Score | Interpretation |
|-------|-----------------|
| 0-3 | Poor structure, grammar errors, unclear |
| 4-6 | Adequate clarity, minor issues |
| 7-9 | Clear, well-structured, professional |
| 10 | Crisp, articulate, impactful, compelling narrative |

### Weighted Total Calculation
```
Weighted Total = (Skills×0.30) + (Experience×0.25) + (Education×0.15) + (Portfolio×0.20) + (Comms×0.10)
```

### Hiring Recommendation
- **Hire**: weighted_total ≥ 7.0 (strong candidate)
- **Maybe**: 4.0 ≤ weighted_total < 7.0 (requires discussion)
- **No Hire**: weighted_total < 4.0 (does not meet threshold)

## 📁 Project Structure

```
hr_shortlisting_agent/
│
├── app.py                         # Main Streamlit UI entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── README.md                      # Project documentation
│
├── agent/
│   ├── __init__.py
│   ├── jd_parser.py               # JD parsing using Claude LLM
│   ├── profile_parser.py          # Resume/LinkedIn profile parsing
│   ├── scoring_engine.py          # Semantic matching & rubric scoring
│   ├── ranker.py                  # Sort & filter candidates
│   └── report_generator.py        # PDF/HTML/JSON report generation
│
├── utils/
│   ├── __init__.py
│   ├── file_reader.py             # PDF/DOCX text extraction
│   ├── linkedin_reader.py         # LinkedIn JSON profile parsing
│   └── override_logger.py         # Audit trail for HR overrides
│
├── prompts/
│   ├── jd_parse_prompt.txt        # LLM prompt for JD parsing
│   ├── profile_parse_prompt.txt   # LLM prompt for profile parsing
│   └── scoring_prompt.txt         # LLM prompt for scoring
│
├── outputs/
│   └── .gitkeep                   # Directory for generated reports
│
└── tests/
    ├── __init__.py
    ├── test_jd_parser.py          # Tests for JD Parser
    ├── test_profile_parser.py     # Tests for Profile Parser
    └── test_scoring_engine.py     # Tests for Scoring Engine
```

## 🧪 Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_jd_parser.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=agent --cov=utils --cov-report=html
```

### Test files and coverage

- **test_jd_parser.py**: 5 tests
  - Parsing returns dict
  - Invalid JSON handling
  - Required keys validation
  - Markdown fence stripping

- **test_profile_parser.py**: 6 tests
  - Profile parsing
  - Skill extraction validation
  - File parsing (PDF/DOCX)
  - LinkedIn profile parsing
  - Error handling

- **test_scoring_engine.py**: 7 tests
  - Scoring returns dict with weighted_total
  - Score range validation (0-10)
  - Recommendation values validation
  - Batch scoring
  - All 5 dimensions present

## 📄 Sample Output

### Sample Scoring Result (JSON)
```json
{
  "skills_match": {
    "score": 8,
    "justification": "Strong match: has 4 of 4 required skills (Python, AWS, Docker, PostgreSQL)."
  },
  "experience_relevance": {
    "score": 9,
    "justification": "7 years of backend engineering experience, directly relevant to Senior role."
  },
  "education_certs": {
    "score": 8,
    "justification": "B.S. in Computer Science meets requirement; has AWS Solutions Architect cert."
  },
  "project_portfolio": {
    "score": 9,
    "justification": "3 strong projects: Microservices Migration, Kubernetes Infrastructure, Cloud Migration."
  },
  "communication_quality": {
    "score": 8,
    "justification": "Well-structured resume with clear metrics and accomplishments."
  },
  "weighted_total": 8.35,
  "hire_recommendation": "Hire",
  "candidate": {
    "name": "John Doe",
    "email": "john@example.com",
    "total_experience_years": 7,
    "skills": ["Python", "AWS", "Docker", "PostgreSQL", "Kubernetes"],
    "experience_domains": ["Backend Engineering", "DevOps"]
  },
  "rank": 1
}
```

### Sample HTML Report
The HTML report includes:
- Header with job title and generation timestamp
- Summary metrics (total screened, hire/maybe/no-hire counts)
- Ranked candidate table with color-coded recommendations
- Expandable candidate details showing all 5 scoring justifications
- Responsive, professional styling

### Sample PDF Report
The PDF report includes:
- Title page with job title
- Summary statistics
- Compact candidate table
- Detailed justifications for each candidate
- Print-optimized layout

## 🔄 Human-in-the-Loop Override

The system includes an audit trail for HR score adjustments:

### How to Override Scores

1. In the **Results & Report** tab, expand any candidate
2. Select the dimension to override (Skills, Experience, Education, Projects, Communication)
3. Enter the new score (0-10)
4. Provide a reason for the override (e.g., "Unique expertise" or "Team recommendation")
5. Click "Log Override"

### Audit Trail

All overrides are logged to `outputs/override_log.json`:

```json
[
  {
    "timestamp": "2024-05-12T14:23:45.123456",
    "candidate_name": "John Doe",
    "dimension": "Skills Match",
    "original_score": 8,
    "new_score": 9,
    "reason": "Has specialized experience in rare skill set"
  }
]
```

Each override entry includes:
- ISO timestamp
- Candidate name
- Dimension adjusted
- Original and new scores
- Reason for change

This enables HR to maintain accountability and track decision rationale.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and install dev dependencies
git clone <repo-url>
cd hr_shortlisting_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for HR professionals using Claude AI**

For issues, feature requests, or questions, please open an [issue](../../issues) on GitHub.
