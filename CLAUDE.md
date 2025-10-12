# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EmailRecruiters - A tool for analyzing job postings and identifying relevant roles to contact for cold emailing purposes. Uses AI to intelligently suggest who to reach out to based on job descriptions.

## Project Status

Active development. Core job analysis feature is implemented and functional.

## Features

- **Job Posting Analysis**: Fetches and parses job postings from any URL using Jina AI
- **AI-Powered Role Suggestions**: Uses Google Gemini to suggest relevant contacts to reach out to
- **Database Storage**: SQLAlchemy-based storage for analyzed jobs and suggested roles
- **CLI Interface**: Command-line tool for easy job analysis

## Development Setup

### Prerequisites
- Python 3.9+
- Virtual environment (venv)

### Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

The following API keys are required (stored in `.env`):
- `JINA_API_KEY` - For web scraping via Jina AI Reader API
- `GEMINI_API_KEY` - For AI-powered role analysis via Google Gemini

### Running the CLI

```bash
# Using the wrapper script
./run_cli.sh analyze <job_url>

# Or directly with Python
export PYTHONPATH=/Users/anudeepnarala/Projects/EmailRecruiters/src:$PYTHONPATH
python -m email_recruiters.cli.main analyze <job_url>
```

### Running Tests

```bash
source venv/bin/activate
python test_basic.py
```

## Architecture

### Project Structure

```
src/email_recruiters/
├── core/
│   ├── job_scraper.py      # Jina AI integration for fetching job postings
│   └── role_analyzer.py     # Gemini AI integration for role suggestions
├── database/
│   ├── models.py           # SQLAlchemy models (AnalyzedJob, SuggestedRole, Contact)
│   └── db.py               # Database utilities and session management
├── cli/
│   ├── main.py             # CLI entry point
│   └── analyze.py          # Analyze command implementation
├── templates/              # Future: Email templates
└── mcp/                    # Future: MCP integration
```

### Key Components

1. **JobScraper** (`core/job_scraper.py`)
   - Uses Jina AI Reader API to convert job posting URLs to clean markdown
   - Extracts title, company, location, and description
   - Supports all major job boards (LinkedIn, Indeed, Greenhouse, Lever, etc.)

2. **RoleAnalyzer** (`core/role_analyzer.py`)
   - Uses Google Gemini (gemini-1.5-flash) for fast analysis
   - Analyzes job description to suggest 5-7 relevant contact roles
   - Returns prioritized list with search keywords and reasoning

3. **Database** (`database/`)
   - SQLite database at `~/.email_recruiters/data.db`
   - Models: AnalyzedJob, SuggestedRole, Contact
   - Tracks all analyzed jobs for future reference

4. **CLI** (`cli/`)
   - Built with Click framework
   - Main command: `analyze <job_url>`
   - Options: `--format json`, `--no-save`

### Data Flow

1. User provides job URL
2. JobScraper fetches content via Jina AI
3. RoleAnalyzer sends to Gemini for analysis
4. Results displayed to user
5. Data saved to SQLite database (optional)

### Dependencies

- `google-generativeai` - Gemini AI client
- `requests` - HTTP client for Jina API
- `sqlalchemy` - ORM for database
- `click` - CLI framework
- `python-dotenv` - Environment variable management
- `jinja2` - Template engine (future use)

## Common Tasks

### Adding a New CLI Command

1. Create command file in `src/email_recruiters/cli/`
2. Define command function with `@click.command()` decorator
3. Register in `cli/main.py` with `cli.add_command()`

### Modifying the Analysis Prompt

Edit the `ANALYSIS_PROMPT` in `src/email_recruiters/core/role_analyzer.py`

### Adding Database Models

1. Define model in `src/email_recruiters/database/models.py`
2. Update database utilities in `db.py` as needed
3. Database auto-creates tables on first run

## Notes for Future Development

- MCP integration planned for people finder functionality
- Email template system to be added
- Contact management features planned
- Campaign tracking to be implemented
