"""
Database models for storing analyzed job postings and contact roles.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AnalyzedJob(Base):
    """Represents an analyzed job posting stored in the database."""

    __tablename__ = "analyzed_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False, unique=True)
    title = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    company_domain = Column(String(200), nullable=True)
    linkedin_company_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    raw_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to suggested roles
    suggested_roles = relationship(
        "SuggestedRole",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AnalyzedJob(id={self.id}, title='{self.title}', company='{self.company}')>"


class SuggestedRole(Base):
    """Represents a suggested contact role for a job posting."""

    __tablename__ = "suggested_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("analyzed_jobs.id"), nullable=False)
    title = Column(String(200), nullable=False)
    priority = Column(Integer, nullable=False)
    keywords = Column(JSON, nullable=False)  # List of search keywords
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to job
    job = relationship("AnalyzedJob", back_populates="suggested_roles")

    def __repr__(self):
        return f"<SuggestedRole(id={self.id}, title='{self.title}', priority={self.priority})>"


class Contact(Base):
    """Represents a contact found for outreach."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("analyzed_jobs.id"), nullable=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    title = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    source = Column(String(100), nullable=True)  # e.g., "apollo", "linkedin", "manual"
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="new")  # new, contacted, responded, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', title='{self.title}')>"
