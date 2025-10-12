"""
Apollo.io API client for searching contacts.

This module provides integration with Apollo.io's People Search API
to find actual contacts at companies based on job titles and domains.
"""

import os
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ApolloContact:
    """Represents a contact found via Apollo.io."""
    name: str
    title: Optional[str]
    email: Optional[str]
    linkedin_url: Optional[str]
    company: Optional[str]
    organization_id: Optional[str]
    person_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "title": self.title,
            "email": self.email,
            "linkedin_url": self.linkedin_url,
            "company": self.company,
            "organization_id": self.organization_id,
            "person_id": self.person_id
        }


class ApolloClient:
    """Client for interacting with Apollo.io API."""

    API_BASE_URL = "https://api.apollo.io"
    PEOPLE_SEARCH_ENDPOINT = "/api/v1/mixed_people/search"
    PEOPLE_ENRICHMENT_ENDPOINT = "/api/v1/people/match"
    SEQUENCES_SEARCH_ENDPOINT = "/api/v1/emailer_campaigns/search"
    SEQUENCES_ADD_CONTACTS_ENDPOINT = "/api/v1/emailer_campaigns/{sequence_id}/add_contact_ids"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Apollo.io client.

        Args:
            api_key: Apollo.io API key. If not provided, will try to load from APOLLO_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("APOLLO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Apollo API key not provided. Set APOLLO_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def search_people(
        self,
        organization_domains: Optional[List[str]] = None,
        person_titles: Optional[List[str]] = None,
        per_page: int = 10,
        page: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search for people using Apollo.io API.

        Args:
            organization_domains: List of company domains to search (e.g., ["acmecorp.com"])
            person_titles: List of job titles to search for (e.g., ["Engineering Manager"])
            per_page: Number of results per page (1-100)
            page: Page number to retrieve
            **kwargs: Additional search parameters supported by Apollo.io API

        Returns:
            Dictionary containing search results and metadata

        Raises:
            Exception: If the API call fails
        """
        url = f"{self.API_BASE_URL}{self.PEOPLE_SEARCH_ENDPOINT}"

        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

        # Build request payload
        payload = {
            "per_page": min(per_page, 100),  # Cap at 100
            "page": page
        }

        # Add organization domains if provided
        if organization_domains:
            # Apollo expects newline-separated domains
            payload["q_organization_domains"] = "\n".join(organization_domains)

        # Add person titles if provided
        if person_titles:
            payload["person_titles"] = person_titles

        # Add any additional parameters
        payload.update(kwargs)

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Apollo.io API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Apollo.io API: {str(e)}")

    def enrich_person(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        email: Optional[str] = None,
        reveal_personal_emails: bool = True,
        reveal_phone_number: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich a person's data to get their email and other details.

        Args:
            first_name: Person's first name
            last_name: Person's last name
            name: Full name (alternative to first_name + last_name)
            domain: Company domain
            email: Person's email (if already known)
            reveal_personal_emails: Whether to reveal personal emails (default: True)
            reveal_phone_number: Whether to reveal phone number (default: False)

        Returns:
            Dictionary containing enriched person data

        Raises:
            Exception: If the API call fails
        """
        url = f"{self.API_BASE_URL}{self.PEOPLE_ENRICHMENT_ENDPOINT}"

        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

        # Build query parameters
        params = {
            "reveal_personal_emails": str(reveal_personal_emails).lower(),
            "reveal_phone_number": str(reveal_phone_number).lower()
        }

        # Add identification parameters
        if email:
            params["email"] = email
        if name:
            params["name"] = name
        elif first_name and last_name:
            params["first_name"] = first_name
            params["last_name"] = last_name

        if domain:
            params["domain"] = domain

        try:
            response = requests.post(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Apollo.io enrichment error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Apollo.io enrichment API: {str(e)}")

    def search_contacts(
        self,
        domain: str,
        titles: List[str],
        max_results: int = 10
    ) -> List[ApolloContact]:
        """
        Search for contacts at a company with specific titles.

        Args:
            domain: Company domain (e.g., "acmecorp.com")
            titles: List of job titles to search for
            max_results: Maximum number of results to return (default: 10)

        Returns:
            List of ApolloContact objects
        """
        contacts = []
        per_page = min(max_results, 100)

        # Make API request
        result = self.search_people(
            organization_domains=[domain],
            person_titles=titles,
            per_page=per_page
        )

        # Parse response
        people = result.get("people", [])

        for person in people[:max_results]:
            # Extract contact information
            name = person.get("name", "Unknown")
            title = person.get("title")
            email = person.get("email")
            linkedin_url = person.get("linkedin_url")

            # Organization info
            organization = person.get("organization", {})
            company = organization.get("name")
            org_id = organization.get("id")

            person_id = person.get("id")

            contact = ApolloContact(
                name=name,
                title=title,
                email=email,
                linkedin_url=linkedin_url,
                company=company,
                organization_id=org_id,
                person_id=person_id
            )

            contacts.append(contact)

        return contacts

    def enrich_contact(self, contact: ApolloContact, domain: str) -> ApolloContact:
        """
        Enrich a single contact to unlock their email.

        Args:
            contact: ApolloContact object to enrich
            domain: Company domain

        Returns:
            Updated ApolloContact with enriched data
        """
        try:
            # Try to enrich by name and domain
            enriched_data = self.enrich_person(
                name=contact.name,
                domain=domain,
                reveal_personal_emails=True
            )

            # Extract person data from response
            person = enriched_data.get("person", {})

            # Update contact with enriched email if available
            if person.get("email"):
                contact.email = person.get("email")

            # Update other fields if available
            if person.get("linkedin_url"):
                contact.linkedin_url = person.get("linkedin_url")

            return contact

        except Exception as e:
            # If enrichment fails, just return original contact
            print(f"Warning: Failed to enrich {contact.name}: {str(e)}")
            return contact

    def search_by_role_suggestions(
        self,
        domain: str,
        role_suggestions: List[Any],
        max_per_role: int = 3,
        enrich_top_n: Optional[int] = None
    ) -> Dict[str, List[ApolloContact]]:
        """
        Search for contacts based on suggested roles from job analysis.

        Args:
            domain: Company domain
            role_suggestions: List of ContactRole objects from role_analyzer
            max_per_role: Maximum contacts to find per role
            enrich_top_n: If specified, enriches the top N most relevant contacts to unlock emails

        Returns:
            Dictionary mapping role title to list of contacts found
        """
        results = {}
        all_contacts_with_priority = []

        for role in role_suggestions:
            # Use the role title and keywords for searching
            search_titles = [role.title] + role.keywords[:2]  # Role title + top 2 keywords

            try:
                contacts = self.search_contacts(
                    domain=domain,
                    titles=search_titles,
                    max_results=max_per_role
                )

                if contacts:
                    results[role.title] = contacts

                    # Track contacts with their priority for enrichment
                    for contact in contacts:
                        all_contacts_with_priority.append((role.priority, contact))

            except Exception as e:
                # Continue searching other roles even if one fails
                print(f"Warning: Failed to search for {role.title}: {str(e)}")
                continue

        # Enrich top N contacts if requested
        if enrich_top_n and all_contacts_with_priority:
            print(f"\nEnriching top {enrich_top_n} contacts to unlock emails...")

            # Sort by priority (lower number = higher priority)
            all_contacts_with_priority.sort(key=lambda x: x[0])

            # Get top N unique contacts
            seen_names = set()
            contacts_to_enrich = []

            for priority, contact in all_contacts_with_priority:
                if contact.name not in seen_names:
                    contacts_to_enrich.append(contact)
                    seen_names.add(contact.name)

                if len(contacts_to_enrich) >= enrich_top_n:
                    break

            # Enrich each contact
            enriched_count = 0
            for contact in contacts_to_enrich:
                enriched = self.enrich_contact(contact, domain)
                if enriched.email and enriched.email != "email_not_unlocked@domain.com":
                    enriched_count += 1

            print(f"Successfully enriched {enriched_count}/{len(contacts_to_enrich)} contacts")

        return results

    def list_sequences(self) -> List[Dict[str, Any]]:
        """
        List all sequences (email campaigns) in the Apollo.io account.

        Returns:
            List of sequence dictionaries with id, name, and other details

        Raises:
            Exception: If the API call fails (403 if not using master API key)
        """
        url = f"{self.API_BASE_URL}{self.SEQUENCES_SEARCH_ENDPOINT}"

        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

        try:
            response = requests.post(url, headers=headers, json={})
            response.raise_for_status()
            data = response.json()
            return data.get("emailer_campaigns", [])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception(
                    "403 Forbidden: Sequences API requires a master API key. "
                    "Regular API keys cannot access sequences. "
                    "Please create a master API key in Apollo.io settings."
                )
            raise Exception(f"Apollo.io sequences API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Apollo.io sequences API: {str(e)}")

    def add_contacts_to_sequence(
        self,
        sequence_id: str,
        contact_ids: List[str],
        sequence_name: Optional[str] = None,
        email_account_id: Optional[str] = None,
        mailbox_rotation: bool = False
    ) -> Dict[str, Any]:
        """
        Add contacts to an Apollo.io sequence (email campaign).

        IMPORTANT: This only ADDS contacts to the sequence. It does NOT start the campaign.
        You will need to manually start/resume the sequence in Apollo.io UI.

        Args:
            sequence_id: The ID of the sequence to add contacts to
            contact_ids: List of Apollo.io contact IDs (person_id from ApolloContact)
            sequence_name: Optional name for display purposes
            email_account_id: Email account ID to use for sending (optional, uses sequence default)
            mailbox_rotation: Whether to rotate mailboxes (default: False)

        Returns:
            Dictionary with response data

        Raises:
            Exception: If the API call fails
        """
        url = f"{self.API_BASE_URL}{self.SEQUENCES_ADD_CONTACTS_ENDPOINT.format(sequence_id=sequence_id)}"

        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

        payload = {
            "contact_ids": contact_ids,
            "mailbox_rotation": mailbox_rotation
        }

        # Add email account ID if provided, otherwise try to use a default
        # The API requires send_email_from_email_account_id parameter
        if email_account_id:
            payload["send_email_from_email_account_id"] = email_account_id

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception(
                    "403 Forbidden: Sequences API requires a master API key. "
                    "Regular API keys cannot access sequences."
                )
            elif e.response.status_code == 422 and "send_email_from_email_account_id" in e.response.text:
                raise Exception(
                    "Email account ID required. Please specify an email account to send from. "
                    "You can find your email account IDs in Apollo.io -> Settings -> Email Accounts. "
                    "Pass the email_account_id parameter or configure a default in the sequence."
                )
            raise Exception(f"Apollo.io sequences API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to add contacts to sequence: {str(e)}")

    def find_sequence_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a sequence by its name.

        Args:
            name: The name of the sequence to find

        Returns:
            Sequence dictionary if found, None otherwise
        """
        sequences = self.list_sequences()
        for seq in sequences:
            if seq.get("name", "").lower() == name.lower():
                return seq
        return None


def search_contacts(
    domain: str,
    titles: List[str],
    api_key: Optional[str] = None,
    max_results: int = 10
) -> List[ApolloContact]:
    """
    Convenience function to search for contacts.

    Args:
        domain: Company domain
        titles: List of job titles to search for
        api_key: Optional Apollo.io API key
        max_results: Maximum number of results

    Returns:
        List of ApolloContact objects
    """
    client = ApolloClient(api_key=api_key)
    return client.search_contacts(domain, titles, max_results)
