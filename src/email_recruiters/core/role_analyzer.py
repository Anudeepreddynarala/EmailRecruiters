"""
Role analyzer using Google Gemini API.

This module analyzes job postings and suggests relevant roles to contact
for cold emailing purposes using Google's Gemini LLM.
"""

import os
import json
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import google.generativeai as genai


@dataclass
class ContactRole:
    """Represents a suggested contact role."""
    title: str
    priority: int  # 1 = highest priority
    keywords: List[str]
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "priority": self.priority,
            "keywords": self.keywords,
            "reasoning": self.reasoning
        }


class RoleAnalyzer:
    """Analyzes job postings to suggest contact roles using Gemini."""

    ANALYSIS_PROMPT = """
You are an expert career coach and networking strategist helping a job seeker.

CONTEXT: A job seeker is applying for this position and wants to reach out to people at the company who can:
- Provide employee referrals (which significantly boost application visibility)
- Advocate for their candidacy internally
- Actually influence or participate in the hiring process
- Move their application forward in a meaningful way

The goal is NOT to contact random executives, but to find people who would be willing and able to help a candidate succeed.

Job Posting Content:
{content}

Provide a JSON response with this exact structure:
{{
  "job_info": {{
    "title": "extracted job title",
    "company": "extracted company name",
    "location": "extracted location (city, state/country or 'Remote')",
    "company_domain": "company.com",
    "linkedin_company": "linkedin.com/company/company-name"
  }},
  "suggested_roles": [
    {{
      "title": "Engineering Manager, Backend",
      "priority": 1,
      "keywords": ["Engineering Manager", "Backend", "Platform"],
      "reasoning": "Direct hiring manager who interviews candidates and can advocate for strong applicants. Likely to respond to thoughtful outreach from qualified candidates."
    }}
  ]
}}

IMPORTANT: Infer the company's web presence:
- Extract or infer the company's official website domain from the job posting content or company name (return just the domain like "company.com", without https:// or www.)
- Infer the likely LinkedIn company page URL based on the company name (full path like "linkedin.com/company/company-name", using lowercase and hyphens)
- If the job posting contains links to the company website or LinkedIn, extract those
- If not present, make your best intelligent guess based on the company name (e.g., "Observe, Inc." -> "observeinc.com" and "linkedin.com/company/observe-inc")

For the suggested roles, provide a prioritized list of 5-7 roles/titles that would be most relevant to contact. Prioritize based on:

1. **Influence on hiring** - Can they actually affect hiring decisions?
2. **Referral ability** - Can they submit an employee referral?
3. **Accessibility** - Are they likely to respond to outreach from candidates?
4. **Relevance** - Would they care about this specific role?

For each role provide:
1. The exact role title
2. Priority (1 = highest priority, 7 = lowest)
3. A list of search keywords to use when finding these people on LinkedIn/Apollo
4. Brief reasoning explaining their influence AND why they'd be receptive to helping

Consider:
- Direct hiring managers (they interview and decide)
- Team members in the same/similar role (can refer and vouch for technical fit)
- Engineering/product managers who would work with this role (involved in interviews)
- Recruiters/talent partners (gatekeepers who can flag applications)
- Senior individual contributors (referrals carry weight, often help with hiring)

Avoid suggesting:
- C-suite executives who don't engage with individual applications
- People too far removed from the role's team/function
- Roles that have no involvement in hiring decisions

IMPORTANT: Return ONLY the JSON object, no additional text or markdown formatting.
"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-pro"):
        """
        Initialize the role analyzer.

        Args:
            api_key: Gemini API key. If not provided, will try to load from GEMINI_API_KEY env var.
            model: Gemini model to use (default: gemini-2.5-pro)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    def analyze_job_posting(
        self,
        content: str
    ) -> Tuple[Dict[str, str], List[ContactRole]]:
        """
        Analyze a job posting and extract info + suggest contact roles.

        Args:
            content: Full job posting content (markdown text)

        Returns:
            Tuple of (job_info dict, list of ContactRole objects)
            job_info contains: title, company, location

        Raises:
            Exception: If the API call fails or response parsing fails
        """
        # Build the prompt
        prompt = self.ANALYSIS_PROMPT.format(
            content=content[:8000]  # Limit content length for API
        )

        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)

            # Extract the response text
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                # Remove first line with ```json and last line with ```
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])

            # Parse JSON response
            data = json.loads(response_text)

            # Extract job info
            job_info = data.get("job_info", {
                "title": None,
                "company": None,
                "location": None
            })

            # Extract and convert suggested roles to ContactRole objects
            roles = []
            for role_data in data.get("suggested_roles", []):
                role = ContactRole(
                    title=role_data.get("title", ""),
                    priority=role_data.get("priority", 99),
                    keywords=role_data.get("keywords", []),
                    reasoning=role_data.get("reasoning", "")
                )
                roles.append(role)

            # Sort by priority
            roles.sort(key=lambda x: x.priority)

            return job_info, roles

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}\nResponse: {response_text}")
        except Exception as e:
            raise Exception(f"Failed to analyze job posting with Gemini: {str(e)}")

    def analyze_from_job_posting(self, job_posting) -> Tuple[Dict[str, str], List[ContactRole]]:
        """
        Analyze a JobPosting object.

        Args:
            job_posting: JobPosting object from job_scraper

        Returns:
            Tuple of (job_info dict, list of ContactRole objects)
        """
        content = job_posting.description or job_posting.raw_content or ""
        return self.analyze_job_posting(content)


def analyze_job(
    content: str,
    api_key: Optional[str] = None
) -> Tuple[Dict[str, str], List[ContactRole]]:
    """
    Convenience function to analyze a job posting.

    Args:
        content: Full job posting content
        api_key: Optional Gemini API key

    Returns:
        Tuple of (job_info dict, list of ContactRole objects)
    """
    analyzer = RoleAnalyzer(api_key=api_key)
    return analyzer.analyze_job_posting(content)
