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
@click.option(
    "--add-to-sequence",
    type=str,
    default=None,
    help="Add contacts to Apollo.io sequence (e.g., 'Test auto sequencing'). ONLY stages contacts, does NOT start campaign."
)
@click.option(
    "--no-confirm",
    is_flag=True,
    default=False,
    help="Skip confirmation prompts when adding to sequence (for batch processing)"
)
@click.option(
    "--test-emails",
    type=str,
    default=None,
    help="Comma-separated test emails to use instead of Apollo search (e.g., 'email1@test.com,email2@test.com')"
)
def analyze(job_url: str, save: bool, format: str, search_apollo: bool, max_contacts_per_role: int, enrich_emails: int, add_to_sequence: str, no_confirm: bool, test_emails: str):
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

        # Handle test emails if provided
        apollo_contacts = {}
        if test_emails:
            click.echo()
            click.echo("=" * 80)
            click.echo("TEST MODE: Creating test contacts in Apollo.io")
            click.echo("=" * 80)

            # Parse comma-separated emails
            email_list = [email.strip() for email in test_emails.split(",") if email.strip()]

            if not email_list:
                click.echo("Error: No valid emails provided in --test-emails", err=True)
            else:
                click.echo(f"Creating {len(email_list)} test contacts...")
                click.echo()

                try:
                    apollo_client = ApolloClient()
                    test_contacts = []

                    for i, email in enumerate(email_list, 1):
                        click.echo(f"  Creating contact {i}: {email}")

                        # Create contact in Apollo.io
                        result = apollo_client.create_contact(
                            email=email,
                            first_name=f"Test",
                            last_name=f"Contact {i}",
                            title="Test Contact",
                            organization_name="Test Organization"
                        )

                        # Extract contact info from response
                        contact_data = result.get("contact", {})
                        person_id = contact_data.get("id")

                        # Create ApolloContact object
                        from ..core.apollo_search import ApolloContact
                        contact = ApolloContact(
                            name=f"Test Contact {i}",
                            title="Test Contact",
                            email=email,
                            linkedin_url=None,
                            company="Test Organization",
                            organization_id=None,
                            person_id=person_id
                        )

                        test_contacts.append(contact)
                        click.echo(f"    ✓ Created with ID: {person_id}")

                    click.echo()
                    click.echo(f"✓ Successfully created {len(test_contacts)} test contacts!")

                    # Store contacts in the same format as Apollo search
                    if test_contacts:
                        apollo_contacts["Test Contacts"] = test_contacts

                    if format == "text":
                        _display_apollo_contacts(apollo_contacts)

                except Exception as e:
                    click.echo(f"Error creating test contacts: {str(e)}", err=True)

        # Search Apollo.io if requested (skip if test emails provided)
        elif search_apollo:
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

                    # Save contacts to user's Apollo account to get contact_ids
                    click.echo("Saving contacts to your Apollo account...")
                    saved_count = 0
                    for role_title, contacts in apollo_contacts.items():
                        for contact in contacts:
                            # Only save contacts with valid emails
                            if contact.email and contact.email != "email_not_unlocked@domain.com":
                                try:
                                    # Parse name into first and last
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

                                    # Extract contact_id from response
                                    contact_data = result.get("contact", {})
                                    contact.contact_id = contact_data.get("id")

                                    if contact.contact_id:
                                        saved_count += 1
                                except Exception as e:
                                    # Log error but continue with other contacts
                                    click.echo(f"  Warning: Failed to save {contact.name}: {str(e)}", err=True)

                    click.echo(f"✓ Saved {saved_count}/{total_found} contacts to your account")
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

        # Add contacts to sequence if requested
        if add_to_sequence and apollo_contacts:
            click.echo()
            click.echo("=" * 80)
            click.echo(f"Adding contacts to sequence: '{add_to_sequence}'")
            click.echo("=" * 80)

            # Collect all contacts
            all_contacts = []
            for role_title, contacts in apollo_contacts.items():
                all_contacts.extend(contacts)

            # Get contact IDs (use contact_id if available, fallback to person_id for test contacts)
            contact_ids = [c.contact_id or c.person_id for c in all_contacts if (c.contact_id or c.person_id)]

            if not contact_ids:
                click.echo("Warning: No contacts have saved to your account. Cannot add to sequence.", err=True)
            else:
                click.echo(f"Found {len(contact_ids)} contacts with Apollo.io IDs")
                click.echo()

                # Show confirmation prompt (unless --no-confirm is set)
                should_add = no_confirm

                if not no_confirm:
                    click.echo("IMPORTANT: This will ADD contacts to the sequence but NOT start the campaign.")
                    click.echo("You will need to manually start/resume the sequence in Apollo.io UI.")
                    click.echo()
                    should_add = click.confirm(f"Add {len(contact_ids)} contacts to '{add_to_sequence}'?", default=True)
                else:
                    click.echo(f"Auto-adding {len(contact_ids)} contacts to sequence (--no-confirm enabled)...")

                if should_add:
                    try:
                        apollo_client = ApolloClient()

                        # Find sequence by name
                        sequence = apollo_client.find_sequence_by_name(add_to_sequence)

                        if not sequence:
                            click.echo(f"Error: Sequence '{add_to_sequence}' not found.", err=True)
                            click.echo("Run './run_cli.sh list-sequences' to see available sequences.", err=True)
                        else:
                            sequence_id = sequence.get("id")
                            click.echo(f"Found sequence: {sequence.get('name')} (ID: {sequence_id})")
                            click.echo()

                            # Update contacts with job title for personalization
                            click.echo("Updating contacts with job title for email personalization...")
                            updated_count = 0
                            for contact in all_contacts:
                                # Use contact_id if available, fallback to person_id for test contacts
                                contact_id = contact.contact_id or contact.person_id
                                if contact_id and job.title:
                                    if apollo_client.update_contact_with_job_title(contact_id, job.title):
                                        updated_count += 1

                            if updated_count > 0:
                                click.echo(f"✓ Updated {updated_count}/{len(all_contacts)} contacts with job title: '{job.title}'")
                                click.echo("  (You can now use {{first_name}} and {{custom.applied_role}} in your sequence emails)")
                            else:
                                click.echo("⚠ Warning: Could not update contacts with job title.")
                                click.echo("  Make sure you have created a custom field named 'Applied Role' in Apollo.io")
                                click.echo("  (Settings -> Custom Fields -> Create Contact Custom Field)")

                            click.echo()

                            # Try to fetch email accounts automatically
                            email_account_id = None
                            try:
                                click.echo("Fetching email accounts...")
                                email_accounts = apollo_client.get_email_accounts()
                                if email_accounts:
                                    email_account_id = str(email_accounts[0])
                                    click.echo(f"Using email account ID: {email_account_id}")
                                else:
                                    click.echo("Warning: No email accounts found")
                            except Exception as e:
                                click.echo(f"Warning: Could not fetch email accounts: {str(e)}")

                            click.echo()

                            # Add contacts to sequence
                            result = apollo_client.add_contacts_to_sequence(
                                sequence_id=sequence_id,
                                contact_ids=contact_ids,
                                sequence_name=add_to_sequence,
                                email_account_id=email_account_id
                            )

                            click.echo()
                            click.echo(f"✓ Successfully added {len(contact_ids)} contacts to sequence!")
                            click.echo()
                            click.echo("Next steps:")
                            click.echo(f"  1. Log into Apollo.io")
                            click.echo(f"  2. Go to Sequences -> '{add_to_sequence}'")
                            click.echo(f"  3. Review contacts and manually start/resume the sequence")
                            click.echo()
                            click.echo("Email personalization:")
                            click.echo(f"  - Use {{{{first_name}}}} for the contact's first name")
                            click.echo(f"  - Use {{{{custom.applied_role}}}} for the job title: '{job.title}'")

                    except Exception as e:
                        click.echo(f"Error adding contacts to sequence: {str(e)}", err=True)

                        if "403" in str(e):
                            click.echo()
                            click.echo("Note: Sequences API requires a MASTER API key.", err=True)
                            click.echo("Please create a master API key in Apollo.io settings.", err=True)
                        elif "Email account ID required" in str(e):
                            click.echo()
                            click.echo("To fix this:", err=True)
                            click.echo("  1. Log into Apollo.io", err=True)
                            click.echo("  2. Go to Settings -> Email Accounts", err=True)
                            click.echo("  3. Connect your email account to the sequence", err=True)
                            click.echo("  4. OR configure a default sending mailbox for the sequence", err=True)
                else:
                    click.echo("Cancelled. Contacts were NOT added to sequence.")

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
