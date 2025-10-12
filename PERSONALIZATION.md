# Email Personalization Guide

This guide explains how to set up and use email personalization in your Apollo.io sequences.

## What Gets Personalized?

When you add contacts to a sequence using EmailRecruiters, the tool automatically sets:

1. **Contact's First Name** - Already available by default in Apollo.io
2. **Job Title You're Applying To** - Stored in a custom field called "Applied Role"

## One-Time Setup

### Step 1: Create Custom Field in Apollo.io

1. Log into Apollo.io
2. Go to **Settings → Custom Fields**
3. Click **Create Contact Custom Field**
4. Fill in the following:
   - **Field Name**: `Applied Role`
   - **Field Type**: Text
   - **Description**: "The job title/role the contact is being reached out for"
5. Click **Save**

### Step 2: Add Personalization to Your Sequence

Edit your sequence template and use these variables:

```
Hi {{first_name}},

I noticed you're hiring for a {{custom.applied_role}} at {{company}}.

I'm very interested in this {{custom.applied_role}} opportunity...
```

### Available Variables

| Variable | Description | Example Output |
|----------|-------------|----------------|
| `{{first_name}}` | Contact's first name (built-in) | "John" |
| `{{last_name}}` | Contact's last name (built-in) | "Doe" |
| `{{company}}` | Company name (built-in) | "Acme Corp" |
| `{{custom.applied_role}}` | Job title being applied for | "Senior Software Engineer" |
| `{{title}}` | Contact's job title (built-in) | "Engineering Manager" |

## How It Works

When you run:

```bash
./run_cli.sh analyze <job_url> --search-apollo --add-to-sequence "Sequence Name"
```

The tool automatically:

1. Analyzes the job posting and extracts the title (e.g., "Senior Software Engineer")
2. Finds relevant contacts at the company
3. **Updates each contact's "Applied Role" custom field** with the job title
4. Adds contacts to your sequence
5. Shows you the personalization variables to use

## Example Email Template

Here's a complete example of a personalized cold email:

```
Subject: {{custom.applied_role}} at {{company}}

Hi {{first_name}},

I hope this message finds you well. I noticed that {{company}} is hiring
for a {{custom.applied_role}}, and I'm very excited about this opportunity.

As a [your background], I believe I'd be a great fit for the
{{custom.applied_role}} role at {{company}} because:

- [Reason 1]
- [Reason 2]
- [Reason 3]

I'd love to learn more about the role and how I can contribute to
{{company}}'s mission.

Would you be open to a brief conversation?

Best regards,
[Your Name]
```

## Testing Personalization

Before running your sequence:

1. Go to your sequence in Apollo.io
2. Click on any contact
3. Click **Preview Email**
4. Verify that `{{custom.applied_role}}` shows the correct job title
5. Verify that `{{first_name}}` shows the contact's first name

If `{{custom.applied_role}}` shows as blank or highlighted in red:
- The custom field wasn't set (check that you created it correctly)
- Or the contact wasn't processed through EmailRecruiters

## Batch Processing with Personalization

When processing multiple jobs, each contact gets the appropriate job title:

```bash
./batch_process_jobs.sh "Sequence Name" \
  https://company1.com/software-engineer \
  https://company2.com/product-manager \
  https://company3.com/data-scientist
```

- Contacts from Company 1 will have "Applied Role" = "Software Engineer"
- Contacts from Company 2 will have "Applied Role" = "Product Manager"
- Contacts from Company 3 will have "Applied Role" = "Data Scientist"

## Troubleshooting

### "Warning: Custom field 'Applied Role' not found"

**Solution**: Create the custom field in Apollo.io Settings → Custom Fields

### Custom field shows as blank in preview

**Possible causes**:
1. Custom field wasn't created with exact name "Applied Role"
2. Contact was added before you ran EmailRecruiters
3. Job title extraction failed

**Solution**:
- Check custom field name matches exactly
- Re-run the analyze command to update contacts

### Using a different custom field name

If you want to use a different name (e.g., "Target Position"), you can modify it in the code or create the field with name "Applied Role" in Apollo.io.

## Best Practices

1. **Always preview before sending** - Check that personalization works correctly
2. **Test with yourself first** - Add your own email to test the sequence
3. **Keep it natural** - Don't over-use the job title variable
4. **Combine with other variables** - Use `{{company}}`, `{{title}}` for richer personalization
5. **Fallback text** - Apollo.io allows fallback text if a field is empty

## Advanced: Multiple Custom Fields

You can extend this system to add more custom fields:

- Company size
- Industry
- Technologies mentioned in job posting
- Salary range
- Location
- etc.

Just create additional custom fields in Apollo.io and modify the code to populate them.

## Summary

✅ **Person's Name**: Use `{{first_name}}` - always available
✅ **Job Role**: Use `{{custom.applied_role}}` - automatically set by EmailRecruiters
✅ **Company**: Use `{{company}}` - always available
✅ **Fully Automated**: Just create the custom field once, then it works for all future runs

This makes every email feel personally crafted while being completely automated!
