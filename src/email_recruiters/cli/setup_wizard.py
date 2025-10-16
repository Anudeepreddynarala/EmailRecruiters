"""
Interactive setup wizard for EmailRecruiters.

Guides users through API key validation, sequence selection,
and configuration setup.
"""

import click
import os
from dotenv import load_dotenv
from ..config import (
    load_config,
    save_config,
    validate_apollo_key,
    fuzzy_match_sequence,
)
from ..core.apollo_search import ApolloClient


@click.command(name="setup")
def setup_wizard():
    """
    Interactive setup wizard for first-time configuration.

    Validates API keys, helps select default sequence, and saves preferences.
    """
    click.echo("=" * 80)
    click.echo("EmailRecruiters Setup Wizard")
    click.echo("=" * 80)
    click.echo()

    # Load existing config
    config = load_config()

    # Step 1: Check API Keys
    click.echo("Step 1: Checking API Keys")
    click.echo("-" * 80)

    missing_keys = []

    # Check each required key
    keys_to_check = [
        ("APOLLO_API_KEY", "Apollo.io", "https://app.apollo.io/#/settings/integrations/api"),
        ("GEMINI_API_KEY", "Google Gemini", "https://makersuite.google.com/app/apikey"),
        ("JINA_API_KEY", "Jina AI", "https://jina.ai/"),
    ]

    for key_name, service_name, url in keys_to_check:
        if config.get(key_name.lower()):
            click.echo(f"✓ {service_name} API key found")
        else:
            click.echo(f"✗ {service_name} API key missing", err=True)
            missing_keys.append((key_name, service_name, url))

    click.echo()

    if missing_keys:
        click.echo("Missing API keys detected!", err=True)
        click.echo()
        click.echo("Please add the following keys to your .env file:")
        click.echo()
        for key_name, service_name, url in missing_keys:
            click.echo(f"  {key_name}=your_key_here")
            click.echo(f"  Get it from: {url}")
            click.echo()
        click.echo("After adding keys, run this setup again.")
        raise click.Abort()

    # Step 2: Validate Apollo API Key
    click.echo("Step 2: Validating Apollo.io API Key")
    click.echo("-" * 80)

    apollo_key = config["apollo_api_key"]
    click.echo("Testing Apollo.io connection...")

    if not validate_apollo_key(apollo_key):
        click.echo("✗ Apollo.io API key is invalid!", err=True)
        click.echo()
        click.echo("Please check your APOLLO_API_KEY in .env file.")
        click.echo("Note: Sequence operations require a MASTER API key.")
        raise click.Abort()

    click.echo("✓ Apollo.io API key is valid")
    click.echo()

    # Step 3: Select Default Sequence
    click.echo("Step 3: Select Default Sequence")
    click.echo("-" * 80)

    try:
        apollo_client = ApolloClient(api_key=apollo_key)

        # Fetch sequences
        click.echo("Fetching your Apollo.io sequences...")
        sequences = apollo_client.list_sequences()

        if not sequences:
            click.echo("No sequences found in your Apollo.io account.", err=True)
            click.echo("Please create a sequence in Apollo.io first.")
            raise click.Abort()

        click.echo(f"Found {len(sequences)} sequence(s):")
        click.echo()

        # Display sequences
        for i, seq in enumerate(sequences, 1):
            name = seq.get("name", "Unnamed")
            status = seq.get("active", False)
            status_str = "Active" if status else "Inactive"
            num_steps = seq.get("num_steps", 0)

            click.echo(f"  {i}. {name}")
            click.echo(f"     Status: {status_str} | Steps: {num_steps}")

        click.echo()

        # Prompt for selection
        selection = click.prompt(
            "Which sequence would you like to use for job applications?\n"
            "(Enter number or name)",
            type=str
        )

        # Try to parse as number first
        selected_sequence = None
        try:
            idx = int(selection) - 1
            if 0 <= idx < len(sequences):
                selected_sequence = sequences[idx]
        except ValueError:
            # Not a number, try fuzzy matching
            matches = fuzzy_match_sequence(selection, sequences)

            if not matches:
                click.echo(f"No sequences found matching '{selection}'", err=True)
                raise click.Abort()

            if len(matches) == 1:
                selected_sequence = matches[0]
            else:
                # Multiple matches, show top 3
                click.echo()
                click.echo("Multiple matches found:")
                for i, seq in enumerate(matches[:3], 1):
                    click.echo(f"  {i}. {seq.get('name')}")

                choice = click.prompt("Select one (1-3)", type=int)
                if 1 <= choice <= min(3, len(matches)):
                    selected_sequence = matches[choice - 1]

        if not selected_sequence:
            click.echo("Invalid selection", err=True)
            raise click.Abort()

        # Confirm selection
        seq_name = selected_sequence.get("name")
        seq_id = selected_sequence.get("id")

        click.echo()
        click.echo(f"You selected: {seq_name}")
        click.echo(f"Sequence ID: {seq_id}")

        # Check email account
        click.echo()
        click.echo("Checking email account configuration...")
        email_accounts = apollo_client.get_email_accounts()

        if not email_accounts:
            click.echo("⚠ Warning: No email accounts found", err=True)
            click.echo("  You'll need to configure an email account in Apollo.io")
            click.echo("  Go to: Settings → Email Accounts")
            email_account_id = ""
        else:
            email_account_id = email_accounts[0]
            click.echo(f"✓ Found {len(email_accounts)} email account(s)")
            click.echo(f"  Using: {email_account_id}")

        click.echo()

        if not click.confirm(f"Save '{seq_name}' as your default sequence?", default=True):
            click.echo("Setup cancelled.")
            raise click.Abort()

        # Step 4: Save Configuration
        click.echo()
        click.echo("Step 4: Saving Configuration")
        click.echo("-" * 80)

        save_config("DEFAULT_SEQUENCE_NAME", seq_name, user_config=True)
        save_config("DEFAULT_SEQUENCE_ID", seq_id, user_config=True)
        save_config("DEFAULT_EMAIL_ACCOUNT_ID", email_account_id, user_config=True)

        click.echo()
        click.echo("=" * 80)
        click.echo("✓ Setup Complete!")
        click.echo("=" * 80)
        click.echo()
        click.echo("Configuration saved:")
        click.echo(f"  Sequence: {seq_name}")
        click.echo(f"  Sequence ID: {seq_id}")
        if email_account_id:
            click.echo(f"  Email Account: {email_account_id}")
        click.echo()
        click.echo("You can now use the batch processing command:")
        click.echo("  ./run_cli.sh batch-add")
        click.echo()

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    setup_wizard()
