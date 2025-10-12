"""
Database connection and session management.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator, Optional

from .models import Base


# Default database location
DEFAULT_DB_PATH = Path.home() / ".email_recruiters" / "data.db"


class Database:
    """Database connection manager."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If not provided, uses default location.
        """
        if db_path is None:
            db_path = os.getenv("DATABASE_URL")
            if db_path is None:
                db_path = f"sqlite:///{DEFAULT_DB_PATH}"
                # Ensure directory exists
                DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            elif not db_path.startswith("sqlite:///"):
                # Assume it's a file path
                db_path = f"sqlite:///{db_path}"

        self.engine = create_engine(db_path, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            db = Database()
            with db.session() as session:
                session.add(obj)
                session.commit()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
_db_instance = None


def get_database(db_path: Optional[str] = None) -> Database:
    """
    Get the global database instance.

    Args:
        db_path: Optional database path. Only used if database hasn't been initialized yet.

    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
        _db_instance.create_tables()
    return _db_instance


def save_analyzed_job(
    url: str,
    title: Optional[str],
    company: Optional[str],
    location: Optional[str],
    company_domain: Optional[str],
    linkedin_company_url: Optional[str],
    description: Optional[str],
    raw_content: Optional[str],
    suggested_roles: list,
    db: Optional[Database] = None
) -> int:
    """
    Save an analyzed job posting to the database.

    Args:
        url: Job posting URL
        title: Job title
        company: Company name
        location: Job location
        company_domain: Company website domain
        linkedin_company_url: LinkedIn company page URL
        description: Job description
        raw_content: Raw content from scraper
        suggested_roles: List of ContactRole objects
        db: Optional Database instance

    Returns:
        ID of the saved job
    """
    from .models import AnalyzedJob, SuggestedRole

    if db is None:
        db = get_database()

    with db.session() as session:
        # Check if job already exists
        existing_job = session.query(AnalyzedJob).filter_by(url=url).first()
        if existing_job:
            # Update existing job
            existing_job.title = title
            existing_job.company = company
            existing_job.location = location
            existing_job.company_domain = company_domain
            existing_job.linkedin_company_url = linkedin_company_url
            existing_job.description = description
            existing_job.raw_content = raw_content

            # Remove old suggested roles
            for role in existing_job.suggested_roles:
                session.delete(role)

            job = existing_job
        else:
            # Create new job
            job = AnalyzedJob(
                url=url,
                title=title,
                company=company,
                location=location,
                company_domain=company_domain,
                linkedin_company_url=linkedin_company_url,
                description=description,
                raw_content=raw_content
            )
            session.add(job)

        # Flush to get the job ID
        session.flush()

        # Add suggested roles
        for role in suggested_roles:
            suggested_role = SuggestedRole(
                job_id=job.id,
                title=role.title,
                priority=role.priority,
                keywords=role.keywords,
                reasoning=role.reasoning
            )
            session.add(suggested_role)

        session.commit()
        return job.id
