"""
Core functionality for job scraping and role analysis.
"""

from .job_scraper import JobScraper, JobPosting, scrape_job
from .role_analyzer import RoleAnalyzer, ContactRole, analyze_job

__all__ = [
    "JobScraper",
    "JobPosting",
    "scrape_job",
    "RoleAnalyzer",
    "ContactRole",
    "analyze_job",
]
