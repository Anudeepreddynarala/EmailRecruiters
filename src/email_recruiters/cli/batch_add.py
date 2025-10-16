"""
Batch process multiple job URLs and add contacts to sequence.

Processes multiple job postings at once and automatically adds
found contacts to the configured default sequence.
"""

import click
import re
from ..config import is_configured, get_sequence_config, load_config
from ..core.job_scraper import JobScraper
from ..core.role_analyzer import RoleAnalyzer
from ..core.apollo_search import ApolloClient


@click.command(name="batch-add")
def batch_add():
    """
    Batch process multiple job URLs and add contacts to your configured sequence.

    Prompts for multiple job URLs and processes them automatically,
    adding all found contacts to your default sequence.
    """
    click.echo("=" * 80)
    click.echo("Batch Add Jobs to Sequence")
    click.echo("=" * 80)
    click.echo()

    # Check if configured
    if not is_configured():
        click.echo("⚠ Setup required!", err=True)
        click.echo()
        click.echo("You need to run the setup wizard first:")
        click.echo("  ./run_cli.sh setup")
        click.echo()
        raise click.Abort()

    # Load configuration
    seq_config = get_sequence_config()
    config = load_config()

    sequence_name = seq_config["sequence_name"]
    sequence_id = seq_config["sequence_id"]
    email_account_id = seq_config.get("email_account_id")

    click.echo(f"Using sequence: {sequence_name}")
    click.echo()

    # Prompt for job URLs
    click.echo("Enter job URLs (one per line, or comma-separated):")
    click.echo("Press Enter twice when done, or Ctrl+D")
    click.echo()

    # Read multiline input
    urls_input = []
    try:
        while True:
            line = input()
            if not line.strip() and urls_input:  # Empty line after some input
                break
            if line.strip():
                urls_input.append(line.strip())
    except EOFError:
        pass  # Ctrl+D pressed

    if not urls_input:
        click.echo("No URLs provided.", err=True)
        raise click.Abort()

    # Parse URLs (handle comma-separated, space-separated, and newline-separated)
    urls = []
    for line in urls_input:
        # Split by comma or whitespace
        parts = re.split(r'[,\s]+', line)
        urls.extend([url.strip() for url in parts if url.strip()])

    # Validate URLs (basic check)
    valid_urls = []
    for url in urls:
        if url.startswith('http://') or url.startswith('https://'):
            valid_urls.append(url)
        else:
            click.echo(f"⚠ Skipping invalid URL: {url}", err=True)

    if not valid_urls:
        click.echo("No valid URLs to process.", err=True)
        raise click.Abort()

    click.echo()
    click.echo(f"Processing {len(valid_urls)} job(s)...")
    click.echo()

    # Get defaults from config
    max_contacts_per_role = int(config.get("default_max_contacts_per_role", "3"))
    enrich_count = int(config.get("default_enrich_count", "5"))

    # Initialize clients
    scraper = JobScraper()
    analyzer = RoleAnalyzer()
    apollo_client = ApolloClient()

    # Track statistics
    stats = {
        "total_jobs": len(valid_urls),
        "successful": 0,
        "failed": 0,
        "total_contacts": 0,
        "contacts_added": 0,
    }

    # Process each URL
    for i, url in enumerate(valid_urls, 1):
        try:
            click.echo(f"[{i}/{len(valid_urls)}] Processing: {url}")

            # Step 1: Scrape job
            job = scraper.scrape_job_posting(url)

            # Step 2: Analyze with AI
            job_info, roles = analyzer.analyze_from_job_posting(job)

            # Update job with extracted info
            job.title = job_info.get("title")
            job.company = job_info.get("company")
            job.location = job_info.get("location")
            company_domain = job_info.get("company_domain")

            if not company_domain:
                click.echo(f"  ⚠ No company domain found, skipping", err=True)
                stats["failed"] += 1
                continue

            # Step 3: Search Apollo for contacts
            apollo_contacts = apollo_client.search_by_role_suggestions(
                domain=company_domain,
                role_suggestions=roles,
                max_per_role=max_contacts_per_role,
                enrich_top_n=enrich_count
            )

            total_found = sum(len(contacts) for contacts in apollo_contacts.values())
            stats["total_contacts"] += total_found

            # Step 4: Save contacts to user's account
            saved_count = 0
            all_contacts = []
            for role_title, contacts in apollo_contacts.items():
                for contact in contacts:
                    all_contacts.append(contact)
                    # Only save contacts with valid emails
                    if contact.email and contact.email != "email_not_unlocked@domain.com":
                        try:
                            # Parse name
                            name_parts = contact.name.split(' ', 1)
                            first_name = name_parts[0] if len(name_parts) > 0 else contact.name
                            last_name = name_parts[1] if len(name_parts) > 1 else ""

                            # Create contact in user's account
                            result = apollo_client.create_contact(
                                email=contact.email,
                                first_name=first_name,
                                last_name=last_name,
                                title=contact.title,
                                organization_name=contact.company
                            )

                            # Extract contact_id
                            contact_data = result.get("contact", {})
                            contact.contact_id = contact_data.get("id")

                            if contact.contact_id:
                                saved_count += 1
                        except Exception:
                            pass  # Continue with other contacts

            # Step 5: Add to sequence
            if saved_count > 0:
                contact_ids = [c.contact_id for c in all_contacts if c.contact_id]

                if contact_ids:
                    try:
                        apollo_client.add_contacts_to_sequence(
                            sequence_id=sequence_id,
                            contact_ids=contact_ids,
                            sequence_name=sequence_name,
                            email_account_id=email_account_id
                        )

                        stats["contacts_added"] += len(contact_ids)
                        click.echo(f"  ✓ Added {len(contact_ids)} contacts from {job.company} - {job.title}")
                    except Exception as e:
                        click.echo(f"  ✗ Failed to add to sequence: {str(e)}", err=True)
                        stats["failed"] += 1
                        continue
                else:
                    click.echo(f"  ⚠ No valid contacts to add", err=True)
            else:
                click.echo(f"  ⚠ No contacts with emails found", err=True)

            stats["successful"] += 1

        except Exception as e:
            click.echo(f"  ✗ Error: {str(e)}", err=True)
            stats["failed"] += 1
            continue

        click.echo()

    # Display summary
    click.echo("=" * 80)
    click.echo("Summary")
    click.echo("=" * 80)
    click.echo(f"Jobs processed: {stats['successful']}/{stats['total_jobs']}")
    if stats['failed'] > 0:
        click.echo(f"Jobs failed: {stats['failed']}")
    click.echo(f"Contacts found: {stats['total_contacts']}")
    click.echo(f"Contacts added to sequence: {stats['contacts_added']}")
    click.echo(f"Sequence: {sequence_name}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Log into Apollo.io")
    click.echo(f"  2. Go to Sequences → '{sequence_name}'")
    click.echo("  3. Review contacts and manually start the sequence")
    click.echo()


if __name__ == "__main__":
    batch_add()
