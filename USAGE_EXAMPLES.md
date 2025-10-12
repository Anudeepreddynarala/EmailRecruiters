# Usage Examples

## Quick Start

### 1. Analyze a LinkedIn Job Posting

```bash
./run_cli.sh analyze https://www.linkedin.com/jobs/view/123456789
```

### 2. Analyze an Indeed Job Posting

```bash
./run_cli.sh analyze https://www.indeed.com/viewjob?jk=abc123def456
```

### 3. Analyze a Company Career Page

```bash
./run_cli.sh analyze https://careers.company.com/jobs/senior-engineer
```

## Advanced Usage

### Get JSON Output (for scripting)

```bash
./run_cli.sh analyze <job_url> --format json > job_analysis.json
```

### Analyze Without Saving to Database

```bash
./run_cli.sh analyze <job_url> --no-save
```

## What You'll Get

For each job posting, the tool provides:

### 1. Basic Job Information
- Job title
- Company name
- Location (including remote/hybrid)
- Direct link to the posting

### 2. Suggested Contacts (Priority Ordered)

The tool analyzes the job and suggests 5-7 relevant roles to contact, such as:

**For Engineering Roles:**
- Engineering Manager
- Director of Engineering
- VP of Engineering
- Technical Recruiter
- Staff/Principal Engineer

**For Product Roles:**
- Product Manager
- Director of Product
- VP of Product
- Product Recruiter

**For Sales Roles:**
- Sales Manager
- Director of Sales
- VP of Sales
- Sales Operations
- Recruiting Manager

**For Marketing Roles:**
- Marketing Manager
- Director of Marketing
- CMO
- Marketing Recruiter

### 3. Search Keywords

For each suggested role, you get optimized keywords to use when searching on:
- LinkedIn
- Apollo.io
- ZoomInfo
- Company websites

### 4. Reasoning

Understanding WHY each role is suggested helps you:
- Prioritize your outreach
- Craft personalized messages
- Target the right decision-makers

## Workflow Example

### Step 1: Find a Job You're Interested In

Browse job boards and find relevant positions:
- LinkedIn Jobs
- Indeed
- Company career pages
- Greenhouse
- Lever

### Step 2: Analyze the Job

```bash
./run_cli.sh analyze <job_url>
```

### Step 3: Use the Suggested Roles

Take the suggested roles and keywords and search for contacts:

**On LinkedIn:**
1. Go to LinkedIn Search
2. Use filters: Company + Role keywords
3. Find 2nd and 3rd connections for warm intros

**On Apollo.io:**
1. Search by company and title keywords
2. Get verified email addresses
3. Export contact list

### Step 4: Reach Out

Use the insights to craft personalized cold emails:

```
Subject: [Your Name] - Interest in [Job Title] at [Company]

Hi [Contact Name],

I came across the [Job Title] position at [Company] and I'm very interested
in learning more. I have [relevant experience] that aligns well with what
you're looking for.

[Add 1-2 sentences about why you're interested in the company/role]

Would you have 15 minutes in the coming weeks for a quick call to discuss
the role and how I might be able to contribute to [specific team/project]?

Best regards,
[Your Name]
```

## Tips for Best Results

### 1. Analyze Multiple Jobs
Run the tool on 5-10 jobs to identify patterns in roles and keywords

### 2. Cross-Reference Contacts
Use multiple sources (LinkedIn, Apollo, company website) to verify contacts

### 3. Prioritize Quality Over Quantity
Focus on reaching out to the top 2-3 suggested roles for each job

### 4. Personalize Your Outreach
Use the job description and company info to customize each message

### 5. Track Your Outreach
Keep a spreadsheet of:
- Jobs analyzed
- Contacts reached out to
- Responses received
- Conversations scheduled

## Troubleshooting

### Issue: "Failed to scrape job posting"
- **Solution**: Check that the URL is accessible and not behind a login wall
- Some job boards may require authentication

### Issue: "Gemini API error"
- **Solution**: Check that your GEMINI_API_KEY is valid and has quota remaining
- You can check your quota at: https://aistudio.google.com/

### Issue: "Jina API error"
- **Solution**: Verify your JINA_API_KEY is correct
- Check Jina API status at: https://jina.ai/

## Need Help?

- Check the main README.md for setup instructions
- Run `./run_cli.sh --help` for CLI options
- Run `./run_cli.sh analyze --help` for analyze command options
