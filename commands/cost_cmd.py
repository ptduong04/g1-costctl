"""cost — show cost of resources matching a tag, over the last N days.

WHAT YOU MUST BUILD
-------------------
A function that:
  1. Queries Cost Explorer (`ce.get_cost_and_usage`) for the last N days
  2. Filters by a tag (e.g. Application=HealthBot)
  3. Groups by SERVICE dimension
  4. Sums per-service costs across the date range
  5. Prints services sorted descending by cost, plus a TOTAL row

HELPERS YOU CAN USE
-------------------
From commands._common:
  parse_kv(s) -> (k, v)             # "Application=HealthBot" -> tuple

AWS APIS YOU'LL NEED
--------------------
ce = boto3.client("ce")
ce.get_cost_and_usage(
    TimePeriod={"Start": "YYYY-MM-DD", "End": "YYYY-MM-DD"},
    Granularity="DAILY",
    Metrics=["UnblendedCost"],
    Filter={"Tags": {"Key": "<tag_key>", "Values": ["<tag_value>"]}},
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)

The response has `ResultsByTime` (one entry per day), each with `Groups` —
each group has `Keys=[service_name]` and `Metrics={"UnblendedCost":{"Amount":"1.23"}}`.

EXPECTED OUTPUT FORMAT
----------------------
    Cost for Application=HealthBot over last 7 days (2026-05-14 → 2026-05-21):
    ------------------------------------------------------------
      Amazon Elastic Compute Cloud - Compute        $    8.42
      Amazon Relational Database Service             $    5.18
      ...
    ------------------------------------------------------------
      TOTAL                                          $   13.80

GOTCHAS
-------
- Cost data lags 8–24h. If --days 1 returns nothing, try --days 7.
- Tag filter requires that you have ACTIVATED cost allocation tags in Billing.
- Amount field is a STRING in the response — cast to float before summing.

VERIFY MANUALLY (no test file for this command)
-----------------------------------------------
    ./costctl.py cost --tag Application=<your-app> --days 7

The first time you run this, double-check against the AWS Console
(Cost Management → Cost Explorer → filter by same tag + same range).
Output should match within a few cents.
"""
import boto3
from collections import defaultdict
from datetime import date, timedelta

from commands._common import parse_kv


def run(args):
    """Entry point.

    Args set by argparse:
        args.tag   — "key=value" string (REQUIRED)
        args.days  — int, default 7
    """
    tag_key, tag_val = parse_kv(args.tag)
    
    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=args.days)
    
    # Query Cost Explorer
    ce = boto3.client("ce")
    try:
        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start_date.strftime("%Y-%m-%d"),
                "End": end_date.strftime("%Y-%m-%d")
            },
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            Filter={"Tags": {"Key": tag_key, "Values": [tag_val]}},
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
        )
    except Exception as e:
        print(f"Error querying Cost Explorer: {e}")
        print("Note: Cost data lags 8-24h. Try --days 7 or more.")
        return
    
    # Aggregate costs by service
    service_costs = defaultdict(float)
    
    for day_result in response.get("ResultsByTime", []):
        for group in day_result.get("Groups", []):
            service_name = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            service_costs[service_name] += amount
    
    # Print results
    if not service_costs:
        print(f"No cost data found for {tag_key}={tag_val} over last {args.days} days.")
        print("Note: Cost data lags 8-24h, and tags must be activated in Billing.")
        return
    
    print(f"Cost for {tag_key}={tag_val} over last {args.days} days ({start_date} → {end_date}):")
    print("-" * 70)
    
    # Sort by cost descending
    sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
    total = 0.0
    
    for service, cost in sorted_services:
        print(f"  {service:50s} $ {cost:8.2f}")
        total += cost
    
    print("-" * 70)
    print(f"  {'TOTAL':50s} $ {total:8.2f}")
