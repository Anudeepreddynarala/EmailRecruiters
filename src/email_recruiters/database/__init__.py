"""
Database models and utilities.
"""

from .models import Base, AnalyzedJob, SuggestedRole, Contact
from .db import Database, get_database, save_analyzed_job

__all__ = [
    "Base",
    "AnalyzedJob",
    "SuggestedRole",
    "Contact",
    "Database",
    "get_database",
    "save_analyzed_job",
]
