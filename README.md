# EmailRecruiters

A tool for analyzing job postings and identifying relevant roles to contact for cold emailing purposes.

## Features

- **Job Posting Analysis**: Fetches and parses job postings from any URL using Jina AI
- **AI-Powered Role Suggestions**: Uses Google Gemini to suggest relevant contacts to reach out to
- **Company Domain Discovery**: Automatically extracts company domain and LinkedIn URL for easy searches
- **Apollo.io Integration**: Find actual contacts at companies using Apollo.io's people search API
- **Email Enrichment**: Automatically unlock real email addresses for top 5 most relevant contacts
- **Sequence Integration**: Automatically add contacts to Apollo.io email sequences for outreach campaigns
- **Contact Management**: Save and track contacts in local database
- **Database Storage**: Saves analyzed jobs and contacts for future reference
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
- **Apollo.io** (optional) for finding actual contacts at companies

API keys are configured in the `.env` file. The Apollo.io integration is optional - you can still use the tool without it for job analysis and role suggestions.

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
2. Extract key information (title, company, location, domain, description)
3. Analyze the job with Gemini to suggest relevant contacts
4. Display prioritized list of roles to reach out to
5. Provide search tips with company domain for Apollo/LinkedIn
6. Save the analysis to the database

### Output Format

The tool provides:
- **Job Information**: Title, company, location, domain, LinkedIn URL
- **Suggested Contacts**: Prioritized list (1-7) of roles to contact
- **Search Keywords**: Keywords to use when searching for these roles on LinkedIn/Apollo
- **Reasoning**: Why each role is relevant
- **Search Tips**: How to use the company domain for Apollo/LinkedIn searches

**Example Output:**

```
================================================================================
Job Title: Senior Backend Engineer
Company: Acme Corp
Domain: acmecorp.com
LinkedIn: https://linkedin.com/company/acme-corp
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

================================================================================
Search Tips:
  On Apollo/LinkedIn, filter by domain: @acmecorp.com
  Example search: "Engineering Manager @acmecorp.com"
  LinkedIn company page: https://linkedin.com/company/acme-corp
================================================================================

Saved successfully! Job ID: 1
```

### Options

- `--no-save`: Don't save the analysis to the database
- `--format json`: Output results in JSON format instead of text
- `--search-apollo`: Automatically search for contacts on Apollo.io
- `--max-contacts-per-role N`: Maximum contacts to find per role (default: 3)
- `--enrich-emails N`: Number of top contacts to enrich/unlock emails (default: 5)

**Examples:**

```bash
# Basic analysis without Apollo.io
./run_cli.sh analyze https://example.com/job

# Analysis with Apollo.io contact search (emails enriched automatically for top 5)
./run_cli.sh analyze https://example.com/job --search-apollo

# Search with custom enrichment (unlock top 3 emails)
./run_cli.sh analyze https://example.com/job --search-apollo --enrich-emails 3

# No email enrichment (save credits)
./run_cli.sh analyze https://example.com/job --search-apollo --enrich-emails 0

# JSON output, no save, with Apollo.io search
./run_cli.sh analyze https://example.com/job --format json --no-save --search-apollo
```

**Email Enrichment:**

By default, when using `--search-apollo`, the tool automatically enriches the top 5 most relevant contacts to unlock their real email addresses. This:
- Prioritizes contacts based on role relevance (e.g., hiring managers first)
- Saves API credits by only enriching the most important contacts
- Gives you actionable email addresses to start your outreach immediately

### Search for Contacts

Use the `search-contacts` command to find contacts on Apollo.io:

**Search by saved job ID:**

```bash
./run_cli.sh search-contacts --job-id 1
```

**Manual search by domain and titles:**

```bash
./run_cli.sh search-contacts --domain acmecorp.com --title "Engineering Manager" --title "VP Engineering"
```

**Search and save contacts to database:**

```bash
./run_cli.sh search-contacts --job-id 1 --save
```

**Control email enrichment:**

```bash
# Enrich top 3 contacts only
./run_cli.sh search-contacts --job-id 1 --enrich-emails 3

# No email enrichment
./run_cli.sh search-contacts --domain acmecorp.com --title "Director" --enrich-emails 0
```

This will:
1. Search Apollo.io for people matching the suggested roles
2. Enrich top N contacts to unlock real email addresses (default: 5)
3. Display contact information (name, title, email, LinkedIn)
4. Optionally save contacts to the database for tracking

### Add Contacts to Sequences

Automatically add found contacts to Apollo.io email sequences for automated outreach campaigns.

**List available sequences:**

```bash
./run_cli.sh list-sequences
```

**Add contacts to a sequence during analysis:**

```bash
./run_cli.sh analyze <job_url> --search-apollo --add-to-sequence "Test auto sequencing"
```

**IMPORTANT SAFETY NOTES:**
- This ONLY adds contacts to the sequence (staging them)
- It does NOT automatically start the campaign
- You must manually review and start the sequence in Apollo.io UI
- Requires a **master API key** (not regular API key)
- Requires email account configuration in the sequence

**Setup Requirements:**
1. Create a master API key in Apollo.io (Settings -> API)
2. Create your sequence in Apollo.io web interface
3. Configure a sending email account for the sequence
4. Run the analyze command with `--add-to-sequence` flag

This ensures you can review contacts before starting any outreach campaign.

### Batch Processing Multiple Jobs

Process multiple job URLs automatically and add all contacts to your sequence:

**Method 1: Using the batch script**

```bash
./batch_process_jobs.sh "Test auto sequencing" \
  https://jobs.ashbyhq.com/company1/job1 \
  https://jobs.ashbyhq.com/company2/job2 \
  https://jobs.ashbyhq.com/company3/job3
```

**Method 2: Manual batch with --no-confirm flag**

```bash
# Process multiple URLs without confirmation prompts
./run_cli.sh analyze <job_url_1> --search-apollo --add-to-sequence "Test auto sequencing" --no-confirm
./run_cli.sh analyze <job_url_2> --search-apollo --add-to-sequence "Test auto sequencing" --no-confirm
./run_cli.sh analyze <job_url_3> --search-apollo --add-to-sequence "Test auto sequencing" --no-confirm
```

**Method 3: Process from a file**

Create a file `job_urls.txt` with one URL per line, then:

```bash
# Read URLs from file and process each one
while IFS= read -r url; do
  [[ "$url" =~ ^#.*$ ]] && continue  # Skip comments
  [[ -z "$url" ]] && continue         # Skip empty lines
  ./run_cli.sh analyze "$url" --search-apollo --add-to-sequence "Test auto sequencing" --no-confirm
done < job_urls.txt
```

**Workflow:**
1. Configure your sequence once in Apollo.io (email account, timing, templates)
2. Run the batch processing with all your job URLs
3. All contacts automatically added to the sequence
4. Go to Apollo.io, review all contacts in one place
5. Manually start the sequence when ready

## Project Structure

```
EmailRecruiters/
├── src/
│   └── email_recruiters/
│       ├── core/
│       │   ├── job_scraper.py      # Jina AI integration
│       │   ├── role_analyzer.py     # Gemini AI integration
│       │   └── apollo_search.py     # Apollo.io integration & sequences
│       ├── database/
│       │   ├── models.py           # SQLAlchemy models
│       │   └── db.py               # Database utilities
│       └── cli/
│           ├── main.py             # CLI entry point
│           ├── analyze.py          # Analyze command
│           ├── search_contacts.py  # Search contacts command
│           └── list_sequences.py   # List sequences command
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
