# EmailRecruiters - Complete Feature Summary

This document provides a comprehensive overview of all features implemented in EmailRecruiters.

## Project Purpose

EmailRecruiters automates the process of finding and contacting relevant people at companies when applying for jobs. It analyzes job postings, finds the right people to contact, gets their email addresses, and sets up personalized email campaigns.

## Complete Workflow

### 1. Analyze Job Posting
```bash
./run_cli.sh analyze <job_url> --search-apollo --add-to-sequence "Sequence Name"
```

**What happens:**
1. ✅ Fetches job posting from any job board (LinkedIn, Indeed, Greenhouse, etc.)
2. ✅ Extracts job title, company, location, domain
3. ✅ AI analyzes and suggests 5-7 relevant roles to contact
4. ✅ Finds actual people at the company matching those roles
5. ✅ Unlocks real email addresses for top 5 contacts
6. ✅ Updates each contact with job title for personalization
7. ✅ Adds all contacts to your Apollo.io sequence
8. ✅ Saves everything to database

**Result:** Ready-to-start email campaign with personalized contact data

### 2. Review and Start Campaign
1. Log into Apollo.io
2. Go to your sequence
3. Review contacts (all have personalized data)
4. Click "Start" to begin outreach

## Core Features

### 🎯 Job Analysis (AI-Powered)
- **Technology:** Jina AI + Google Gemini
- **Input:** Any job posting URL
- **Output:**
  - Job details (title, company, location)
  - Company domain and LinkedIn URL
  - 5-7 prioritized contact roles to reach out to
  - Search keywords for each role
  - Reasoning for why each role is relevant

**Example Output:**
```
1. Engineering Manager
   Keywords: Engineering Manager, Backend, Platform
   Reasoning: Direct hiring manager who would oversee this role

2. Director of Engineering
   Keywords: Director Engineering, Engineering Lead
   Reasoning: Senior decision maker for engineering hires
```

### 🔍 Contact Discovery (Apollo.io)
- **Searches by:** Company domain + job titles
- **Finds:** Actual people at the company
- **Returns:** Name, title, email (if unlocked), LinkedIn URL
- **Smart filtering:** Focuses on most relevant roles first

**Example Result:**
```
Found 15 contacts across 6 roles:
- Engineering Manager: 3 people
- Director of Engineering: 2 people
- VP Engineering: 2 people
- etc.
```

### 📧 Email Enrichment
- **Automatically unlocks:** Top 5 most relevant contacts
- **Prioritization:** Hiring managers and decision-makers first
- **Credit saving:** Only enriches the most important contacts
- **Result:** Real email addresses ready to use

**Example:**
```
✓ Enriched 5/5 contacts
- john.doe@company.com (Engineering Manager)
- jane.smith@company.com (Director of Engineering)
- bob.jones@company.com (VP Engineering)
```

### 🎭 Email Personalization
- **Automatic:** No manual data entry required
- **Sets custom fields:** Job title for each contact
- **Available variables:**
  - `{{first_name}}` - Contact's first name (e.g., "John")
  - `{{custom.applied_role}}` - Job title (e.g., "Senior Engineer")
  - `{{company}}` - Company name (e.g., "Acme Corp")
  - `{{title}}` - Contact's job title (e.g., "Engineering Manager")

**Example Template:**
```
Hi {{first_name}},

I noticed you're hiring for a {{custom.applied_role}} at {{company}}.

I'm very interested in this {{custom.applied_role}} opportunity...
```

**Example Result:**
```
Hi John,

I noticed you're hiring for a Senior Engineer at Acme Corp.

I'm very interested in this Senior Engineer opportunity...
```

### 🔄 Sequence Integration
- **Automatically adds contacts** to Apollo.io sequences
- **Updates custom fields** for personalization
- **Safety first:** Only stages contacts, never auto-starts
- **Manual control:** You review and start campaigns manually

**Features:**
- Find sequence by name
- Batch add contacts
- Confirmation prompts (can be disabled for automation)
- Helpful error messages

### 📦 Batch Processing
Process multiple job postings in one go:

**Method 1: Batch Script**
```bash
./batch_process_jobs.sh "Sequence Name" \
  https://company1.com/job1 \
  https://company2.com/job2 \
  https://company3.com/job3
```

**Method 2: From File**
```bash
while IFS= read -r url; do
  ./run_cli.sh analyze "$url" --search-apollo --add-to-sequence "Sequence" --no-confirm
done < job_urls.txt
```

**What happens:**
- Each job analyzed separately
- Contacts found for each company
- Each contact gets the appropriate job title
- All contacts added to sequence
- Progress shown for each job

### 💾 Database Storage
- **Location:** `~/.email_recruiters/data.db`
- **Stores:**
  - All analyzed jobs
  - Suggested roles per job
  - Found contacts (name, email, LinkedIn, company)
  - Links between jobs and contacts

**Benefits:**
- Track all applications
- Re-search for saved jobs
- Historical record
- Analytics potential

## API Integrations

### 1. Jina AI
- **Purpose:** Web scraping and content extraction
- **Use:** Fetches job postings from any URL
- **Output:** Clean markdown of job posting

### 2. Google Gemini
- **Purpose:** AI-powered analysis
- **Use:** Analyzes job descriptions to suggest contacts
- **Model:** gemini-2.5-pro
- **Output:** Structured contact suggestions with reasoning

### 3. Apollo.io
- **Purpose:** Contact discovery and email enrichment
- **APIs Used:**
  - People Search - Find contacts by domain/title
  - People Enrichment - Unlock email addresses
  - Sequences - Add contacts to campaigns
  - Custom Fields - Set personalization data
- **Requirements:** Master API key for sequences and custom fields

## Configuration Requirements

### API Keys (in `.env`)
```
JINA_API_KEY=your_jina_key
GEMINI_API_KEY=your_gemini_key
APOLLO_API_KEY=your_apollo_master_key
```

### Apollo.io Setup
1. **Master API Key:** Required for sequences and custom fields
2. **Custom Field:** Create "Applied Role" contact field
3. **Email Account:** Connect sending email to sequence
4. **Sequence:** Create sequence with email templates

## Command Reference

### Main Commands

**Analyze Job:**
```bash
./run_cli.sh analyze <job_url> [options]
```

**Search Contacts:**
```bash
./run_cli.sh search-contacts [--job-id ID | --domain DOMAIN --title TITLE] [options]
```

**List Sequences:**
```bash
./run_cli.sh list-sequences
```

### Key Options

| Option | Description | Default |
|--------|-------------|---------|
| `--search-apollo` | Search for contacts | no |
| `--enrich-emails N` | Unlock N top emails | 5 |
| `--add-to-sequence "Name"` | Add to sequence | none |
| `--no-confirm` | Skip prompts (batch mode) | false |
| `--save` / `--no-save` | Save to database | true |
| `--format json` | JSON output | text |
| `--max-contacts-per-role N` | Max contacts per role | 3 |

## Use Cases

### Use Case 1: Single Job Application
```bash
# Find contacts and add to sequence
./run_cli.sh analyze https://company.com/job \
  --search-apollo \
  --add-to-sequence "Job Applications"

# Review in Apollo.io, then start sequence
```

### Use Case 2: Batch Applications
```bash
# Process 10 jobs at once
./batch_process_jobs.sh "Job Applications" \
  url1 url2 url3 url4 url5 url6 url7 url8 url9 url10

# All contacts added with personalized job titles
# Review all in Apollo.io, then start sequence
```

### Use Case 3: Research Only
```bash
# Analyze without Apollo.io
./run_cli.sh analyze https://company.com/job

# Get suggested roles and keywords
# Manual outreach on LinkedIn
```

### Use Case 4: Find Contacts Later
```bash
# Analyze and save
./run_cli.sh analyze https://company.com/job

# Search contacts later
./run_cli.sh search-contacts --job-id 1 --save
```

## Safety Features

### 1. Campaign Control
- ✅ Contacts only staged, never auto-started
- ✅ Manual review required before sending
- ✅ Confirmation prompts for all additions
- ✅ Clear safety messages throughout

### 2. Credit Management
- ✅ Only enriches top N contacts
- ✅ Customizable enrichment count
- ✅ Can disable enrichment entirely
- ✅ Smart prioritization saves credits

### 3. Error Handling
- ✅ Clear error messages
- ✅ Helpful troubleshooting tips
- ✅ Graceful degradation
- ✅ Detailed logging

## File Structure

```
EmailRecruiters/
├── README.md                   # User documentation
├── CLAUDE.md                   # Developer documentation
├── PERSONALIZATION.md          # Personalization guide
├── SUMMARY.md                  # This file
├── batch_process_jobs.sh       # Batch processing script
├── job_urls_example.txt        # Example input file
├── run_cli.sh                  # CLI wrapper
├── requirements.txt            # Python dependencies
├── .env                        # API keys (gitignored)
└── src/email_recruiters/
    ├── core/
    │   ├── job_scraper.py      # Jina AI integration
    │   ├── role_analyzer.py    # Gemini AI integration
    │   └── apollo_search.py    # Apollo.io integration
    ├── database/
    │   ├── models.py           # Database models
    │   └── db.py               # Database utilities
    └── cli/
        ├── main.py             # CLI entry point
        ├── analyze.py          # Analyze command
        ├── search_contacts.py  # Search command
        └── list_sequences.py   # List sequences command
```

## Getting Started

### Quick Start (5 minutes)

1. **Install:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Apollo.io:**
   - Create master API key
   - Create "Applied Role" custom field
   - Create a sequence
   - Connect email account to sequence

3. **Test:**
```bash
./run_cli.sh analyze <job_url> --search-apollo --add-to-sequence "Sequence Name"
```

4. **Review in Apollo.io and start campaign**

### Full Workflow

1. **Collect job URLs** you want to apply to
2. **Run batch processing** to add all contacts
3. **Review contacts** in Apollo.io sequence
4. **Start sequence** to begin outreach
5. **Track responses** in Apollo.io

## Best Practices

### 1. Email Templates
- Use {{first_name}} for personalization
- Use {{custom.applied_role}} to mention the job
- Keep it concise and genuine
- A/B test different approaches

### 2. Contact Selection
- Focus on hiring managers and decision-makers
- Include recruiters for visibility
- Consider team members for referrals
- Don't spam entire company

### 3. Sequence Design
- 3-5 touchpoints over 2 weeks
- Mix of email, LinkedIn, and calls
- Provide value in each touchpoint
- Respect unsubscribes

### 4. Batch Processing
- Process 10-20 jobs at a time
- Review before starting campaigns
- Monitor for API rate limits
- Track which jobs get responses

## Troubleshooting

See README.md and PERSONALIZATION.md for detailed troubleshooting guides.

## Future Enhancements

Potential additions:
- Response tracking and analytics
- Email template library
- A/B testing framework
- Multi-sequence campaigns
- Integration with job boards
- Chrome extension for one-click analysis

## Support

- Documentation: README.md, CLAUDE.md, PERSONALIZATION.md
- Issues: Create GitHub issue
- Questions: Check documentation first

## Summary

EmailRecruiters provides a complete, automated solution for job application outreach:

✅ **Analyzes** job postings with AI
✅ **Finds** the right people to contact
✅ **Unlocks** their email addresses
✅ **Personalizes** emails automatically
✅ **Adds** to sequences for automation
✅ **Saves** everything for tracking

**Result:** Professional, personalized cold email campaigns at scale, while maintaining full control and safety.
