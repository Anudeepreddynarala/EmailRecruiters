"""
CLI command for analyzing job postings.
"""

import click
from dotenv import load_dotenv
from ..core.job_scraper import JobScraper
from ..core.role_analyzer import RoleAnalyzer
from ..core.apollo_search import ApolloClient
from ..database.db import save_analyzed_job, save_contacts

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
@click.option(
    "--search-apollo/--no-search-apollo",
    default=False,
    help="Search for contacts on Apollo.io (default: no)"
)
@click.option(
    "--max-contacts-per-role",
    default=3,
    type=int,
    help="Maximum contacts to find per role on Apollo.io (default: 3)"
)
@click.option(
    "--enrich-emails",
    default=5,
    type=int,
    help="Number of top contacts to enrich/unlock emails for (default: 5, requires --search-apollo)"
)
def analyze(job_url: str, save: bool, format: str, search_apollo: bool, max_contacts_per_role: int, enrich_emails: int):
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

        # Search Apollo.io if requested
        apollo_contacts = {}
        if search_apollo:
            if not company_domain:
                click.echo()
                click.echo("Warning: Cannot search Apollo.io - company domain not found", err=True)
            else:
                click.echo()
                click.echo("Searching for contacts on Apollo.io...")
                try:
                    apollo_client = ApolloClient()
                    apollo_contacts = apollo_client.search_by_role_suggestions(
                        domain=company_domain,
                        role_suggestions=roles,
                        max_per_role=max_contacts_per_role,
                        enrich_top_n=enrich_emails if enrich_emails > 0 else None
                    )

                    total_found = sum(len(contacts) for contacts in apollo_contacts.values())
                    click.echo(f"Found {total_found} contacts across {len(apollo_contacts)} roles!")
                    click.echo()

                    if format == "text":
                        _display_apollo_contacts(apollo_contacts)

                except Exception as e:
                    click.echo(f"Error searching Apollo.io: {str(e)}", err=True)

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

            # Save Apollo contacts if any were found
            if apollo_contacts:
                click.echo("Saving Apollo.io contacts to database...")
                all_contacts = []
                for role_title, contacts in apollo_contacts.items():
                    all_contacts.extend(contacts)

                saved_count = save_contacts(job_id, all_contacts)
                click.echo(f"Saved {saved_count} contacts to database!")

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


def _display_apollo_contacts(apollo_contacts):
    """Display Apollo.io contacts in human-readable format."""
    click.echo("=" * 80)
    click.echo("Apollo.io Contacts Found:")
    click.echo("=" * 80)
    click.echo()

    for role_title, contacts in apollo_contacts.items():
        click.echo(f"Role: {role_title}")
        click.echo("-" * 80)

        for i, contact in enumerate(contacts, 1):
            click.echo(f"  {i}. {contact.name}")
            if contact.title:
                click.echo(f"     Title: {contact.title}")
            if contact.email:
                click.echo(f"     Email: {contact.email}")
            if contact.linkedin_url:
                click.echo(f"     LinkedIn: {contact.linkedin_url}")
            click.echo()

        click.echo()


if __name__ == "__main__":
    analyze()
