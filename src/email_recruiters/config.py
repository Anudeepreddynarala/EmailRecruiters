"""
Configuration management for EmailRecruiters.

Handles loading, saving, and validating user configuration including
Apollo API key, default sequence, and email account settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv, set_key, find_dotenv

# Config file location
CONFIG_DIR = Path.home() / ".email_recruiters"
CONFIG_FILE = CONFIG_DIR / "config.env"


def ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Optional[str]]:
    """
    Load configuration from .env files.

    Priority order:
    1. Project .env file (for API keys)
    2. User config file ~/.email_recruiters/config.env (for preferences)

    Returns:
        Dictionary with configuration values
    """
    # Load project .env first
    project_env = find_dotenv()
    if project_env:
        load_dotenv(project_env)

    # Load user config if it exists
    if CONFIG_FILE.exists():
        load_dotenv(CONFIG_FILE)

    return {
        "apollo_api_key": os.getenv("APOLLO_API_KEY"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "jina_api_key": os.getenv("JINA_API_KEY"),
        "default_sequence_name": os.getenv("DEFAULT_SEQUENCE_NAME"),
        "default_sequence_id": os.getenv("DEFAULT_SEQUENCE_ID"),
        "default_email_account_id": os.getenv("DEFAULT_EMAIL_ACCOUNT_ID"),
        "default_max_contacts_per_role": os.getenv("DEFAULT_MAX_CONTACTS_PER_ROLE", "3"),
        "default_enrich_count": os.getenv("DEFAULT_ENRICH_COUNT", "5"),
    }


def save_config(key: str, value: str, user_config: bool = True) -> bool:
    """
    Save a configuration value.

    Args:
        key: Configuration key
        value: Configuration value
        user_config: If True, saves to user config (~/.email_recruiters/config.env)
                    If False, saves to project .env

    Returns:
        True if successful, False otherwise
    """
    try:
        if user_config:
            ensure_config_dir()
            target_file = str(CONFIG_FILE)
        else:
            project_env = find_dotenv()
            if not project_env:
                # Create .env in project root
                target_file = ".env"
            else:
                target_file = project_env

        set_key(target_file, key, value)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def validate_apollo_key(api_key: str) -> bool:
    """
    Validate Apollo API key by making a test API call.

    Args:
        api_key: Apollo API key to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        from .core.apollo_search import ApolloClient
        client = ApolloClient(api_key=api_key)
        # Try to list sequences as a validation check
        client.list_sequences()
        return True
    except Exception:
        return False


def get_sequence_config() -> Optional[Dict[str, str]]:
    """
    Get configured sequence information.

    Returns:
        Dictionary with sequence_name, sequence_id, email_account_id or None
    """
    config = load_config()

    if config["default_sequence_name"] and config["default_sequence_id"]:
        return {
            "sequence_name": config["default_sequence_name"],
            "sequence_id": config["default_sequence_id"],
            "email_account_id": config["default_email_account_id"] or "",
        }

    return None


def clear_sequence_config():
    """Clear sequence configuration."""
    save_config("DEFAULT_SEQUENCE_NAME", "", user_config=True)
    save_config("DEFAULT_SEQUENCE_ID", "", user_config=True)
    save_config("DEFAULT_EMAIL_ACCOUNT_ID", "", user_config=True)


def fuzzy_match_sequence(query: str, sequences: list) -> list:
    """
    Fuzzy match a sequence name query against available sequences.

    Args:
        query: User's query string
        sequences: List of sequence dictionaries from Apollo API

    Returns:
        List of matching sequences, sorted by relevance
    """
    query_lower = query.lower()
    matches = []

    for seq in sequences:
        name = seq.get("name", "")
        name_lower = name.lower()

        # Calculate match score
        score = 0

        # Exact match
        if name_lower == query_lower:
            score = 100
        # Starts with query
        elif name_lower.startswith(query_lower):
            score = 80
        # Contains query
        elif query_lower in name_lower:
            score = 60
        # Contains all words from query
        else:
            query_words = query_lower.split()
            if all(word in name_lower for word in query_words):
                score = 40

        if score > 0:
            matches.append((score, seq))

    # Sort by score (highest first)
    matches.sort(key=lambda x: x[0], reverse=True)

    return [seq for score, seq in matches]


def is_configured() -> bool:
    """
    Check if the tool is fully configured.

    Returns:
        True if API key and sequence are configured
    """
    config = load_config()
    return bool(
        config["apollo_api_key"] and
        config["default_sequence_name"] and
        config["default_sequence_id"]
    )
