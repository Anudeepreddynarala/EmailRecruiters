# EmailRecruiters

A tool for analyzing job postings and identifying relevant roles to contact for cold emailing purposes.

## Features

- **Job Posting Analysis**: Fetches and parses job postings from any URL using Jina AI
- **AI-Powered Role Suggestions**: Uses Google Gemini to suggest relevant contacts to reach out to
- **Database Storage**: Saves analyzed jobs for future reference
- **CLI Interface**: Easy-to-use command-line tool

## Setup

### 1. Clone the repository and navigate to the project directory

```bash
cd EmailRecruiters
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure API keys

The project uses:
- **Jina AI** for web scraping and HTML parsing
- **Google Gemini** for AI-powered role analysis

API keys are already configured in the `.env` file.

## Usage

### Analyze a Job Posting

Use the `analyze` command to fetch and analyze a job posting:

```bash
./run_cli.sh analyze <job_url>
```

**Example:**

```bash
./run_cli.sh analyze https://www.linkedin.com/jobs/view/123456789
```

This will:
1. Fetch the job posting using Jina AI
2. Extract key information (title, company, location, description)
3. Analyze the job with Gemini to suggest relevant contacts
4. Display prioritized list of roles to reach out to
5. Save the analysis to the database

### Output Format

The tool provides:
- **Job Information**: Title, company, location
- **Suggested Contacts**: Prioritized list (1-7) of roles to contact
- **Search Keywords**: Keywords to use when searching for these roles on LinkedIn/Apollo
- **Reasoning**: Why each role is relevant

**Example Output:**

```
================================================================================
Job Title: Senior Backend Engineer
Company: Acme Corp
Location: San Francisco, CA
URL: https://www.linkedin.com/jobs/view/123456789
================================================================================

Analysis complete! Found 5 suggested roles.

Suggested Contacts (in priority order):

1. Engineering Manager, Backend
   Keywords: Engineering Manager, Backend, Platform
   Reasoning: Direct hiring manager who would oversee this role

2. Director of Engineering
   Keywords: Director Engineering, Engineering Lead
   Reasoning: Senior decision maker for engineering hires

3. VP of Engineering
   Keywords: VP Engineering, Head of Engineering
   Reasoning: Executive sponsor for senior engineering roles

4. Technical Recruiter, Engineering
   Keywords: Technical Recruiter, Engineering Recruiter
   Reasoning: Dedicated recruiter for technical positions

5. Senior Engineering Manager
   Keywords: Senior Engineering Manager, Staff Engineer Manager
   Reasoning: May be involved in senior engineering hiring decisions

Saved successfully! Job ID: 1
```

### Options

- `--no-save`: Don't save the analysis to the database
- `--format json`: Output results in JSON format instead of text

**Example:**

```bash
./run_cli.sh analyze https://example.com/job --format json --no-save
```

## Project Structure

```
EmailRecruiters/
├── src/
│   └── email_recruiters/
│       ├── core/
│       │   ├── job_scraper.py      # Jina AI integration
│       │   └── role_analyzer.py     # Gemini AI integration
│       ├── database/
│       │   ├── models.py           # SQLAlchemy models
│       │   └── db.py               # Database utilities
│       └── cli/
│           ├── main.py             # CLI entry point
│           └── analyze.py          # Analyze command
├── .env                            # API keys (gitignored)
├── requirements.txt                # Dependencies
├── run_cli.sh                      # CLI wrapper script
└── README.md                       # This file
```

## Database

The tool automatically creates a SQLite database at `~/.email_recruiters/data.db` to store:
- Analyzed job postings
- Suggested roles for each job
- Contact information (for future features)

## Next Steps

After analyzing a job, use the suggested roles and keywords to:
1. Search for contacts on LinkedIn or Apollo
2. Find the right people to reach out to
3. Craft personalized cold emails

## Development

### Running Tests

```bash
source venv/bin/activate
python test_basic.py
```

### Code Style

The project uses:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## License

MIT
