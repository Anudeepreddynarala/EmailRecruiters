#!/bin/bash
# Wrapper script to run email-recruiters CLI

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH=/Users/anudeepnarala/Projects/EmailRecruiters/src:$PYTHONPATH

# Run the CLI
python -m email_recruiters.cli.main "$@"
