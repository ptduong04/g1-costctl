# Quick Start

## Setup

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Configure AWS
aws configure

# Run tests
python -m pytest tests/ -v
# Should see: 25 passed
```

## Common Commands

```bash
# List all EC2 instances
python costctl.py list ec2

# List with tag filter
python costctl.py list ec2 --tag Environment=dev

# List missing a tag
python costctl.py list ec2 --missing-tag Application

# Show cost for tagged resources
python costctl.py cost --tag Application=HealthBot --days 7

# Tag a resource
python costctl.py tag ec2 --id i-0abc123 --set Owner=alice

# Terminate (asks confirmation)
python costctl.py terminate ec2 --id i-0abc123

# Bulk cleanup (dry-run first!)
python costctl.py clean --tag purpose=practice
python costctl.py clean --tag purpose=practice --apply
```

## Useful Workflows

**Find and fix untagged resources:**
```bash
python costctl.py list ec2 --missing-tag Application
python costctl.py tag ec2 --id <id> --set Application=MyApp
```

**Cost optimization:**
```bash
python costctl.py list ec2 --tag purpose=practice
python costctl.py cost --tag purpose=practice --days 7
python costctl.py clean --tag purpose=practice --apply
```

## Safety Features

- All destructive commands ask for confirmation (use `--force` to skip)
- `clean` is dry-run by default (requires `--apply` to actually delete)
- S3 refuses to delete non-empty buckets

## Troubleshooting

**"No cost data found"**
Cost Explorer data lags 8-24 hours. Try `--days 7` or more. Also check that cost allocation tags are activated in AWS Billing console.

**"InvalidInstanceID.NotFound"**
Resource doesn't exist or is in a different region. Try `--region us-west-2`.

**"ModuleNotFoundError: No module named 'moto'"**
Run `pip install -r requirements-dev.txt`
