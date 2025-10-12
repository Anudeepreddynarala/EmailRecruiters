"""
Basic test to verify the modules can be imported and instantiated.
"""

import sys
sys.path.insert(0, '/Users/anudeepnarala/Projects/EmailRecruiters/src')

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
try:
    from email_recruiters.core.job_scraper import JobScraper, JobPosting
    from email_recruiters.core.role_analyzer import RoleAnalyzer, ContactRole
    from email_recruiters.database.models import AnalyzedJob, SuggestedRole
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test JobScraper instantiation
try:
    scraper = JobScraper()
    print("✓ JobScraper instantiated successfully")
except Exception as e:
    print(f"✗ JobScraper error: {e}")
    sys.exit(1)

# Test RoleAnalyzer instantiation
try:
    analyzer = RoleAnalyzer()
    print("✓ RoleAnalyzer instantiated successfully")
except Exception as e:
    print(f"✗ RoleAnalyzer error: {e}")
    sys.exit(1)

# Test with mock job data
try:
    test_job = JobPosting(
        url="https://example.com/job/123",
        title="Senior Software Engineer",
        company="Tech Corp",
        location="San Francisco, CA",
        description="We are looking for a senior software engineer..."
    )
    print(f"✓ Created test JobPosting: {test_job.title} at {test_job.company}")
except Exception as e:
    print(f"✗ JobPosting creation error: {e}")
    sys.exit(1)

print("\n✓ All basic tests passed!")
print("\nReady to use!")
print("\nTo analyze a job posting, run:")
print("  ./run_cli.sh analyze <job_url>")
print("\nExample:")
print("  ./run_cli.sh analyze https://www.linkedin.com/jobs/view/123456789")
