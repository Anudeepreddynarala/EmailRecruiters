# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EmailRecruiters - A tool for analyzing job postings and identifying relevant roles to contact for cold emailing purposes. Uses AI to intelligently suggest who to reach out to based on job descriptions.

## Project Status

Active development. Core job analysis feature is implemented and functional.

## Features

- **Job Posting Analysis**: Fetches and parses job postings from any URL using Jina AI
- **AI-Powered Role Suggestions**: Uses Google Gemini to suggest relevant contacts to reach out to
- **Company Domain Discovery**: Extracts/infers company domain and LinkedIn URL for easy contact searches
- **Apollo.io Integration**: Search for actual contacts at companies using Apollo.io's people search API
- **Email Enrichment**: Automatically unlock real email addresses for top N most relevant contacts
- **Contact Management**: Save and track contacts with status and notes in database
- **Database Storage**: SQLAlchemy-based storage for analyzed jobs, suggested roles, and contacts
- **CLI Interface**: Command-line tool for easy job analysis and contact search

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
- `APOLLO_API_KEY` - (Optional) For finding contacts via Apollo.io API

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
│   ├── role_analyzer.py     # Gemini AI integration for role suggestions
│   └── apollo_search.py     # Apollo.io integration for finding contacts
├── database/
│   ├── models.py           # SQLAlchemy models (AnalyzedJob, SuggestedRole, Contact)
│   └── db.py               # Database utilities and session management
├── cli/
│   ├── main.py             # CLI entry point
│   ├── analyze.py          # Analyze command implementation
│   └── search_contacts.py  # Search contacts command
├── templates/              # Future: Email templates
└── mcp/                    # Future: MCP integration
```

### Key Components

1. **JobScraper** (`core/job_scraper.py`)
   - Uses Jina AI Reader API to convert job posting URLs to clean markdown
   - Extracts title, company, location, and description
   - Supports all major job boards (LinkedIn, Indeed, Greenhouse, Lever, etc.)

2. **RoleAnalyzer** (`core/role_analyzer.py`)
   - Uses Google Gemini (gemini-2.5-pro) for fast analysis
   - Analyzes job description to suggest 5-7 relevant contact roles
   - Returns prioritized list with search keywords and reasoning

3. **ApolloClient** (`core/apollo_search.py`)
   - Integrates with Apollo.io People Search API
   - Searches for contacts by company domain and job titles
   - Returns contact details: name, email, LinkedIn URL, title
   - Can search based on suggested roles from RoleAnalyzer
   - Email enrichment: unlocks real email addresses for top N contacts using Apollo.io enrichment API
   - Prioritizes contacts by role relevance to save API credits

4. **Database** (`database/`)
   - SQLite database at `~/.email_recruiters/data.db`
   - Models: AnalyzedJob, SuggestedRole, Contact
   - Tracks all analyzed jobs and found contacts

5. **CLI** (`cli/`)
   - Built with Click framework
   - Main commands: `analyze <job_url>`, `search-contacts`
   - Analyze options: `--format json`, `--no-save`, `--search-apollo`, `--max-contacts-per-role`, `--enrich-emails`
   - Search options: `--job-id`, `--domain`, `--title`, `--save`, `--enrich-emails`

### Data Flow

**Job Analysis Flow:**
1. User provides job URL
2. JobScraper fetches content via Jina AI
3. RoleAnalyzer sends to Gemini for analysis
4. Gemini returns suggested roles with keywords
5. Results displayed to user
6. Data saved to SQLite database (optional)

**Apollo.io Contact Search Flow:**
1. User enables `--search-apollo` flag (or uses `search-contacts` command)
2. ApolloClient uses company domain from job analysis
3. Searches Apollo.io for people matching suggested role titles
4. Identifies top N contacts based on role priority (default: 5)
5. Enriches top contacts to unlock real email addresses via Apollo.io enrichment API
6. Returns contact details (name, email, LinkedIn, title)
7. Contacts displayed to user
8. Contacts saved to database (optional, linked to job)

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

## Documentation Maintenance

**IMPORTANT**: After every commit that adds or modifies functionality, you MUST update the following documentation files:

1. **CLAUDE.md** (this file)
   - Update Features list if new capabilities added
   - Update Architecture section for structural changes
   - Update Common Tasks if new patterns emerge
   - Keep Dependencies list current

2. **README.md**
   - Update Features list to match new capabilities
   - Update example output if CLI output format changes
   - Add new usage examples for new features
   - Keep installation/setup instructions accurate

3. **USAGE_EXAMPLES.md**
   - Add practical examples for new features
   - Update workflow examples to include new steps
   - Add troubleshooting tips for new components
   - Keep search examples current with latest output format

### Documentation Update Checklist

Before committing, verify:
- [ ] All new features are documented in README.md Features section
- [ ] Example output in README.md reflects actual CLI output
- [ ] USAGE_EXAMPLES.md includes practical examples of new features
- [ ] CLAUDE.md architecture section is updated for structural changes
- [ ] Any new dependencies are listed in CLAUDE.md

### Why This Matters

Documentation that's out of sync with code creates confusion for:
- Future contributors (including yourself)
- Users trying to understand features
- AI assistants working on the project
- Anyone reviewing the codebase

Always commit documentation updates immediately after feature commits.

## Notes for Future Development

- Email template system to be added
- Campaign tracking to be implemented
- Contact status workflow (new -> contacted -> responded)
- Email sending integration
- Bulk contact search and management
- Analytics and reporting features
