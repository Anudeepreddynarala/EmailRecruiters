"""
CLI command for listing Apollo.io sequences.
"""

import click
from dotenv import load_dotenv
from ..core.apollo_search import ApolloClient

# Load environment variables
load_dotenv()


@click.command()
def list_sequences():
    """
    List all sequences (email campaigns) in your Apollo.io account.

    This command shows all available sequences that you can add contacts to.
    Note: Requires a master API key, not a regular API key.

    Example:
        email-recruiters list-sequences
    """
    try:
        click.echo("Fetching sequences from Apollo.io...")
        click.echo()

        # Initialize Apollo client
        apollo_client = ApolloClient()

        # Get sequences
        sequences = apollo_client.list_sequences()

        if not sequences:
            click.echo("No sequences found in your Apollo.io account.")
            click.echo()
            click.echo("Create a sequence in Apollo.io web interface first, then run this command again.")
            return

        click.echo(f"Found {len(sequences)} sequence(s):")
        click.echo("=" * 80)

        for seq in sequences:
            seq_id = seq.get("id", "N/A")
            name = seq.get("name", "Unnamed")
            active = seq.get("active", False)
            num_steps = seq.get("num_steps", 0)

            status = "Active" if active else "Inactive"

            click.echo(f"\nID: {seq_id}")
            click.echo(f"Name: {name}")
            click.echo(f"Status: {status}")
            click.echo(f"Steps: {num_steps}")

        click.echo()
        click.echo("=" * 80)
        click.echo()
        click.echo("To add contacts to a sequence, use:")
        click.echo('  ./run_cli.sh analyze <job_url> --search-apollo --add-to-sequence "Sequence Name"')

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

        if "403" in str(e):
            click.echo()
            click.echo("Note: Sequences API requires a MASTER API key, not a regular API key.", err=True)
            click.echo("Please create a master API key in Apollo.io settings.", err=True)

        raise click.Abort()


if __name__ == "__main__":
    list_sequences()
