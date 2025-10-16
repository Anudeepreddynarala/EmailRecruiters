"""
Main CLI entry point for email-recruiters.
"""

import click
from dotenv import load_dotenv
from .analyze import analyze
from .search_contacts import search_contacts
from .list_sequences import list_sequences
from .setup_wizard import setup_wizard
from .batch_add import batch_add

# Load environment variables
load_dotenv()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    EmailRecruiters - Automated email outreach tool.

    Analyze job postings and find relevant contacts for cold emailing.
    """
    pass


# Register commands
cli.add_command(analyze)
cli.add_command(search_contacts)
cli.add_command(list_sequences)
cli.add_command(setup_wizard)
cli.add_command(batch_add)


if __name__ == "__main__":
    cli()
