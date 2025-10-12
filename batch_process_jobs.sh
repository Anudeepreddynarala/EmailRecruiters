#!/bin/bash

# Batch process multiple job URLs and add contacts to sequence
# Usage: ./batch_process_jobs.sh "Sequence Name" url1 url2 url3 ...

SEQUENCE_NAME="$1"
shift  # Remove first argument (sequence name)

if [ -z "$SEQUENCE_NAME" ]; then
    echo "Usage: ./batch_process_jobs.sh \"Sequence Name\" <job_url1> <job_url2> ..."
    echo ""
    echo "Example:"
    echo "  ./batch_process_jobs.sh \"Test auto sequencing\" \\"
    echo "    https://jobs.ashbyhq.com/company1/job1 \\"
    echo "    https://jobs.ashbyhq.com/company2/job2 \\"
    echo "    https://jobs.ashbyhq.com/company3/job3"
    exit 1
fi

echo "=================================================="
echo "Batch Processing Jobs"
echo "Sequence: $SEQUENCE_NAME"
echo "Number of jobs: $#"
echo "=================================================="
echo ""

TOTAL_JOBS=$#
CURRENT_JOB=0
SUCCESS_COUNT=0
FAILED_COUNT=0

for JOB_URL in "$@"; do
    CURRENT_JOB=$((CURRENT_JOB + 1))

    echo ""
    echo "[$CURRENT_JOB/$TOTAL_JOBS] Processing: $JOB_URL"
    echo "=================================================="

    # Run the analyze command with --no-confirm for automatic processing
    if ./run_cli.sh analyze "$JOB_URL" \
        --search-apollo \
        --add-to-sequence "$SEQUENCE_NAME" \
        --no-confirm; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo "✓ Success!"
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo "✗ Failed!"
    fi

    # Add a small delay between jobs to avoid rate limiting
    if [ $CURRENT_JOB -lt $TOTAL_JOBS ]; then
        echo ""
        echo "Waiting 5 seconds before next job..."
        sleep 5
    fi
done

echo ""
echo "=================================================="
echo "Batch Processing Complete!"
echo "=================================================="
echo "Total jobs: $TOTAL_JOBS"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $FAILED_COUNT"
echo ""
echo "Next steps:"
echo "  1. Log into Apollo.io"
echo "  2. Go to Sequences -> '$SEQUENCE_NAME'"
echo "  3. Review all contacts that were added"
echo "  4. Manually start/resume the sequence"
echo "=================================================="
