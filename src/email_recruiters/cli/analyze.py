"""
CLI command for analyzing job postings.
"""

import click
from dotenv import load_dotenv
from ..core.job_scraper import JobScraper
from ..core.role_analyzer import RoleAnalyzer
from ..database.db import save_analyzed_job

# Load environment variables
load_dotenv()


@click.command()
@click.argument("job_url")
@click.option(
    "--save/--no-save",
    default=True,
    help="Save the analysis to the database (default: yes)"
)
@click.option(
    "--format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)"
)
def analyze(job_url: str, save: bool, format: str):
    """
    Analyze a job posting and suggest relevant roles to contact.

    JOB_URL: The URL of the job posting to analyze

    Example:
        email-recruiters analyze https://www.linkedin.com/jobs/view/123456789
    """
    try:
        click.echo("Fetching job posting...")

        # Scrape the job posting
        scraper = JobScraper()
        job = scraper.scrape_job_posting(job_url)

        click.echo("Job posting fetched successfully!")
        click.echo()

        click.echo("Analyzing job posting with AI...")

        # Analyze the job posting (extracts info + suggests roles)
        analyzer = RoleAnalyzer()
        job_info, roles = analyzer.analyze_from_job_posting(job)

        # Update job object with LLM-extracted information
        job.title = job_info.get("title")
        job.company = job_info.get("company")
        job.location = job_info.get("location")
        company_domain = job_info.get("company_domain")
        linkedin_company = job_info.get("linkedin_company")

        click.echo(f"Analysis complete! Found {len(roles)} suggested roles.")
        click.echo()

        # Display basic info
        if format == "text":
            click.echo("=" * 80)
            click.echo(f"Job Title: {job.title or 'N/A'}")
            click.echo(f"Company: {job.company or 'N/A'}")
            if company_domain:
                click.echo(f"Domain: {company_domain}")
            if linkedin_company:
                click.echo(f"LinkedIn: https://{linkedin_company}")
            click.echo(f"Location: {job.location or 'N/A'}")
            click.echo(f"URL: {job.url}")
            click.echo("=" * 80)
            click.echo()

        # Display results
        if format == "text":
            _display_text_format(roles)

            # Show search tips if we have company domain
            if company_domain:
                click.echo()
                click.echo("=" * 80)
                click.echo("Search Tips:")
                click.echo(f"  On Apollo/LinkedIn, filter by domain: @{company_domain}")
                click.echo(f"  Example search: \"Product Manager @{company_domain}\"")
                if linkedin_company:
                    click.echo(f"  LinkedIn company page: https://{linkedin_company}")
                click.echo("=" * 80)
        elif format == "json":
            _display_json_format(job, roles)

        # Save to database
        if save:
            click.echo()
            click.echo("Saving to database...")
            job_id = save_analyzed_job(
                url=job.url,
                title=job.title,
                company=job.company,
                location=job.location,
                company_domain=company_domain,
                linkedin_company_url=linkedin_company,
                description=job.description,
                raw_content=job.raw_content,
                suggested_roles=roles
            )
            click.echo(f"Saved successfully! Job ID: {job_id}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


def _display_text_format(roles):
    """Display roles in human-readable text format."""
    click.echo("Suggested Contacts (in priority order):")
    click.echo()

    for role in roles:
        click.echo(f"{role.priority}. {role.title}")
        click.echo(f"   Keywords: {', '.join(role.keywords)}")
        click.echo(f"   Reasoning: {role.reasoning}")
        click.echo()


def _display_json_format(job, roles):
    """Display results in JSON format."""
    import json

    result = {
        "job": job.to_dict(),
        "suggested_roles": [role.to_dict() for role in roles]
    }

    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    analyze()
