"""
Main CLI entry point for email-recruiters.
"""

import click
from dotenv import load_dotenv
from .analyze import analyze

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


if __name__ == "__main__":
    cli()
