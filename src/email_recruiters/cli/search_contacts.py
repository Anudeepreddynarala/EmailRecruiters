"""
CLI command for searching contacts on Apollo.io.
"""

import click
from dotenv import load_dotenv
from ..core.apollo_search import ApolloClient
from ..database.db import get_database, save_contacts
from ..database.models import AnalyzedJob

# Load environment variables
load_dotenv()


@click.command()
@click.option(
    "--job-id",
    type=int,
    help="Search contacts for a saved job by its ID"
)
@click.option(
    "--domain",
    type=str,
    help="Company domain to search (e.g., acmecorp.com)"
)
@click.option(
    "--title",
    "-t",
    "titles",
    multiple=True,
    help="Job title to search for (can specify multiple times)"
)
@click.option(
    "--max-results",
    default=10,
    type=int,
    help="Maximum number of results to return (default: 10)"
)
@click.option(
    "--save/--no-save",
    default=False,
    help="Save contacts to database (default: no, requires --job-id)"
)
@click.option(
    "--enrich-emails",
    default=5,
    type=int,
    help="Number of top contacts to enrich/unlock emails for (default: 5)"
)
def search_contacts(job_id, domain, titles, max_results, save, enrich_emails):
    """
    Search for contacts on Apollo.io.

    You can either search for contacts of a saved job using --job-id,
    or manually specify --domain and --title for a custom search.

    Examples:
        # Search contacts for a saved job
        email-recruiters search-contacts --job-id 1

        # Manual search by domain and title
        email-recruiters search-contacts --domain acmecorp.com --title "Engineering Manager" --title "VP Engineering"

        # Search and save to database (requires job-id)
        email-recruiters search-contacts --job-id 1 --save
    """
    try:
        # Initialize Apollo client
        apollo_client = ApolloClient()

        # Case 1: Search by job ID
        if job_id:
            click.echo(f"Loading job {job_id} from database...")

            db = get_database()
            with db.session() as session:
                job = session.query(AnalyzedJob).filter_by(id=job_id).first()

                if not job:
                    click.echo(f"Error: Job with ID {job_id} not found", err=True)
                    raise click.Abort()

                domain = job.company_domain
                if not domain:
                    click.echo("Error: Job has no company domain saved", err=True)
                    raise click.Abort()

                click.echo(f"Job: {job.title} at {job.company}")
                click.echo(f"Domain: {domain}")
                click.echo()

                # Get suggested roles from database
                if job.suggested_roles:
                    click.echo(f"Searching for {len(job.suggested_roles)} suggested roles...")
                    click.echo()

                    # Convert database models to objects that apollo_search expects
                    class RoleSuggestion:
                        def __init__(self, title, keywords):
                            self.title = title
                            self.keywords = keywords

                    role_suggestions = [
                        RoleSuggestion(role.title, role.keywords)
                        for role in job.suggested_roles
                    ]

                    apollo_contacts = apollo_client.search_by_role_suggestions(
                        domain=domain,
                        role_suggestions=role_suggestions,
                        max_per_role=3,
                        enrich_top_n=enrich_emails if enrich_emails > 0 else None
                    )
                else:
                    click.echo("No suggested roles found. Using generic search...")
                    titles = ["Manager", "Director", "VP"]
                    contacts = apollo_client.search_contacts(
                        domain=domain,
                        titles=titles,
                        max_results=max_results
                    )
                    apollo_contacts = {"General": contacts}

        # Case 2: Manual search by domain and titles
        elif domain and titles:
            click.echo(f"Searching for contacts at {domain}...")
            click.echo(f"Titles: {', '.join(titles)}")
            click.echo()

            contacts = apollo_client.search_contacts(
                domain=domain,
                titles=list(titles),
                max_results=max_results
            )

            # Enrich top N contacts if requested
            if enrich_emails and contacts and enrich_emails > 0:
                click.echo(f"\nEnriching top {min(enrich_emails, len(contacts))} contacts to unlock emails...")
                for i, contact in enumerate(contacts[:enrich_emails]):
                    apollo_client.enrich_contact(contact, domain)

            apollo_contacts = {"Custom Search": contacts}

        else:
            click.echo("Error: Must specify either --job-id OR both --domain and --title", err=True)
            raise click.Abort()

        # Display results
        total_found = sum(len(contacts) for contacts in apollo_contacts.values())
        click.echo(f"Found {total_found} contacts!")
        click.echo()

        _display_contacts(apollo_contacts)

        # Save contacts if requested
        if save:
            if not job_id:
                click.echo()
                click.echo("Error: --save requires --job-id to associate contacts with a job", err=True)
                raise click.Abort()

            click.echo()
            click.echo("Saving contacts to database...")
            all_contacts = []
            for role_contacts in apollo_contacts.values():
                all_contacts.extend(role_contacts)

            saved_count = save_contacts(job_id, all_contacts)
            click.echo(f"Saved {saved_count} new contacts to database!")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


def _display_contacts(apollo_contacts):
    """Display Apollo.io contacts in human-readable format."""
    click.echo("=" * 80)
    click.echo("Contacts Found:")
    click.echo("=" * 80)
    click.echo()

    for role_title, contacts in apollo_contacts.items():
        if not contacts:
            continue

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
    search_contacts()
