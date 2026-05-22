# Reflections

## 1. Multi-Account Strategy

Running costctl against 100 AWS accounts would need some significant changes.

The cleanest approach is cross-account IAM roles. Set up a management account that can assume a `CostCtlReadOnlyRole` in each target account. Each account needs this role with permissions for EC2, RDS, S3, CloudWatch, and Cost Explorer.

Code-wise, you'd add `--account` or `--all-accounts` flags and store account configs in YAML. Wrap boto3 client creation in a session factory that handles the STS assume role process. For output with 100 accounts, CSV export makes sense - one row per account with a summary view. Use ThreadPoolExecutor to query accounts in parallel, otherwise it takes forever.

The config file could be simple:
```yaml
accounts:
  - id: "123456789012"
    name: "production"
  - id: "234567890123"
    name: "staging"
```

This gives centralized cost management while keeping security boundaries between accounts.

---

## 2. idle vs Trusted Advisor

The 24h vs 14-day window is an interesting tradeoff.

I'd use the 24h window (idle command) for:
- Dev/test environments where things change fast
- Investigating sudden cost spikes when you need answers now
- Right after deployment to verify new instances are actually working
- Workloads that should have steady CPU like web servers

The 14-day window (Trusted Advisor) makes more sense for:
- Production workloads with weekly patterns (batch jobs on weekends, quiet Mondays)
- Seasonal or periodic tasks
- When you need to justify termination to management
- Strategic planning and quarterly reviews

Honestly, the best approach is using both. If something shows up in both, it's definitely idle. If it's only in the 24h window, investigate before terminating.

Example: A database running nightly ETL would look idle during the day but the 14-day view would catch the nightly activity pattern.

---

## 3. clean --apply Blast Radius

If I accidentally ran `clean --tag Environment=dev --apply` in a shared account, here's what I wish was in place:

**IAM Tag Policies**
The strongest protection - tag-based policies that prevent touching resources unless your IAM user's Team tag matches the resource's Team tag. This should be standard in shared accounts.

**Mandatory Tagging**
Enforce Team, Owner, Environment tags on everything. Then costctl should require a `--team` flag and only touch resources matching your team.

**Hard Limits**
Cap the tool at maybe 20 resources per run. If someone tries to delete more, make them override with explicit confirmation.

**Better Confirmation**
Instead of just "y/N", show the first 10 resources and make them type "DELETE 47 RESOURCES" to proceed. Typos = abort.

**Monitoring**
CloudWatch alarm if >10 instances terminate in 5 minutes. Send to team Slack immediately. This catches accidents fast.

**Resource Protection**
Enable termination protection on critical instances. Use S3 bucket policies to prevent deletion. Turn on RDS deletion protection by default.

**The Real Solution**
Don't share AWS accounts between teams. Use AWS Organizations - each team gets their own account with consolidated billing. This eliminates the blast radius problem entirely.

If you must share accounts, IAM tag policies are your best defense.

---

## 4. AI Tools

I used Claude/Cursor for probably 70% of the code. The other 30% needed manual fixes.

What worked well:
- Standard boto3 patterns (describe_instances, list_buckets, etc)
- Using the helper functions correctly
- Basic error handling
- Output formatting

What needed fixing:

*S3 Exception Handling*
AI tried to catch `s3.exceptions.NoSuchTagSet` but moto doesn't expose that the same way. Switched to generic Exception handling which works for both testing and production.

*Clean Command Filtering*
AI forgot to filter out terminated instances and in-use volumes. Had to add state checks manually.

*Error Messages*
AI's error messages were bland. Added helpful hints like "Cost data lags 8-24h. Try --days 7 or more."

*S3 Tag Merging*
AI's version worked but was verbose. Cleaned it up with dict comprehension.

The pattern I noticed: AI is great for standard patterns and boilerplate. Humans are needed for edge cases, test quirks, and making things user-friendly. The docstrings in the starter code were detailed enough that AI could generate mostly correct implementations, but the polish required human judgment.

---

## 5. W7 Production Strategy

For W7 (production multi-account), I'd keep some commands and drop others.

**Keep:**

*list* - Essential. Need visibility into resources across accounts. Would add `--account`, `--all-accounts`, `--region` flags and JSON/CSV output options.

*cost* - Critical for production. Would add cross-account aggregation, budget alerts, and CSV export for finance team.

*tag* - Important for governance. Would add bulk tagging, tag validation against org policies, and audit trail.

**Modify Heavily:**

*terminate* - Too dangerous as-is. Would rename to `request-termination` and create approval workflows. Require manager approval for production resources. Add 24h cooling-off period. Or just keep it for dev/test accounts only and disable in production.

**Drop:**

*clean* - Bulk deletion is too risky in production. Would replace with `identify-cleanup-candidates` that only generates reports. If kept at all, require multiple approvals and MFA.

**Add for W7:**

*audit* - Check for untagged resources, missing owners, security policy violations. Generate compliance reports.

*snapshot* - Create backups before any destructive operation. Automated snapshot scheduling.

*report* - Weekly cost summary emails, utilization dashboards, anomaly detection.

The philosophy shift for W7: move from direct manipulation to observability + approval workflows. Production needs guardrails, audit trails, and human oversight for destructive operations.

Architecture changes: API-first design (convert CLI to library with REST API), RBAC (developers can list, only ops can terminate), centralized audit logging, dry-run by default for everything destructive, integration with Slack/PagerDuty/ServiceNow.
