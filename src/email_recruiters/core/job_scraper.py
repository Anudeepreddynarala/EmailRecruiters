"""
Job posting scraper using Jina AI Reader API.

This module handles fetching and parsing job postings from various job boards
using Jina AI's reader service to convert web pages to clean markdown.
"""

import os
import re
import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class JobPosting:
    """Represents a parsed job posting."""
    url: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    raw_content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "url": self.url,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "raw_content": self.raw_content
        }


class JobScraper:
    """Scrapes job postings using Jina AI Reader API."""

    JINA_READER_BASE_URL = "https://r.jina.ai/"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the job scraper.

        Args:
            api_key: Jina API key. If not provided, will try to load from JINA_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Jina API key not provided. Set JINA_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def scrape_job_posting(self, url: str) -> JobPosting:
        """
        Scrape a job posting from the given URL.

        Args:
            url: The URL of the job posting

        Returns:
            JobPosting object with extracted information

        Raises:
            requests.RequestException: If the request fails
        """
        # Use Jina Reader API to fetch clean markdown
        jina_url = f"{self.JINA_READER_BASE_URL}{url}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Return-Format": "markdown"
        }

        try:
            response = requests.get(jina_url, headers=headers, timeout=30)
            response.raise_for_status()

            content = response.text

            # Create job posting object
            job = JobPosting(
                url=url,
                raw_content=content
            )

            # Extract structured information
            job.title = self._extract_title(content, url)
            job.company = self._extract_company(content, url)
            job.location = self._extract_location(content)
            job.description = content  # The full content serves as description

            return job

        except requests.RequestException as e:
            raise Exception(f"Failed to scrape job posting: {str(e)}")

    def _extract_title(self, content: str, url: str) -> Optional[str]:
        """
        Extract job title from content.

        Looks for common patterns in job postings.
        """
        # Try to find title patterns
        patterns = [
            r"^#\s+(.+?)(?:\n|$)",  # First H1 heading
            r"Job Title:?\s*(.+?)(?:\n|$)",
            r"Position:?\s*(.+?)(?:\n|$)",
            r"Role:?\s*(.+?)(?:\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                # Clean up markdown artifacts
                title = re.sub(r'[#*\[\]()]', '', title).strip()
                if title and len(title) < 150:  # Reasonable title length
                    return title

        # Fallback: try to extract from URL
        if "linkedin.com" in url:
            match = re.search(r'/jobs/view/([^/]+)', url)
            if match:
                return match.group(1).replace('-', ' ').title()

        return None

    def _extract_company(self, content: str, url: str) -> Optional[str]:
        """
        Extract company name from content.
        """
        patterns = [
            r"Company:?\s*(.+?)(?:\n|$)",
            r"Organization:?\s*(.+?)(?:\n|$)",
            r"##\s*About\s+(.+?)(?:\n|$)",
            r"at\s+([A-Z][A-Za-z0-9\s&.,-]+?)(?:\n|Location:|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                company = match.group(1).strip()
                # Clean up
                company = re.sub(r'[#*\[\]()]', '', company).strip()
                if company and len(company) < 100:
                    return company

        # Try to extract from URL
        if "linkedin.com" in url:
            match = re.search(r'company/([^/]+)', url)
            if match:
                return match.group(1).replace('-', ' ').title()

        return None

    def _extract_location(self, content: str) -> Optional[str]:
        """
        Extract job location from content.
        """
        patterns = [
            r"Location:?\s*(.+?)(?:\n|$)",
            r"Based in:?\s*(.+?)(?:\n|$)",
            r"Office:?\s*(.+?)(?:\n|$)",
            # City, State pattern
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*[A-Z]{2}(?:\s+\d{5})?)",
            # City, Country pattern
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*[A-Z][a-z]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                location = match.group(1).strip()
                # Clean up
                location = re.sub(r'[#*\[\]()]', '', location).strip()
                if location and len(location) < 100:
                    return location

        # Check for remote work
        if re.search(r'\b(remote|hybrid|work from home)\b', content, re.IGNORECASE):
            return "Remote"

        return None


def scrape_job(url: str, api_key: Optional[str] = None) -> JobPosting:
    """
    Convenience function to scrape a job posting.

    Args:
        url: The URL of the job posting
        api_key: Optional Jina API key

    Returns:
        JobPosting object with extracted information
    """
    scraper = JobScraper(api_key=api_key)
    return scraper.scrape_job_posting(url)
