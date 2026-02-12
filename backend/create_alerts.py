"""
New Relic Alert Policy Creation Script

This script helps create alert policies programmatically using the New Relic API.
Requires: NEW_RELIC_API_KEY (User API key, not License key)

Get your User API Key from:
https://one.newrelic.com/api-keys → Create key → User type

Usage:
    export NEW_RELIC_API_KEY="your_api_key"
    export NEW_RELIC_ACCOUNT_ID="your_account_id"
    python create_alerts.py
"""

import os
import requests
import json

# Configuration
API_KEY = os.getenv("NEW_RELIC_API_KEY")
ACCOUNT_ID = os.getenv("NEW_RELIC_ACCOUNT_ID")
API_URL = "https://api.newrelic.com/graphql"

if not API_KEY or not ACCOUNT_ID:
    print("❌ Error: Set NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID environment variables")
    print("   Get your User API Key from: https://one.newrelic.com/api-keys")
    exit(1)

headers = {
    "Content-Type": "application/json",
    "API-Key": API_KEY
}

def create_alert_policy(policy_name, incident_preference="PER_CONDITION"):
    """Create an alert policy"""
    mutation = """
    mutation {
      alertsPolicyCreate(accountId: %s, policy: {name: "%s", incidentPreference: %s}) {
        id
        name
      }
    }
    """ % (ACCOUNT_ID, policy_name, incident_preference)
    
    response = requests.post(API_URL, json={"query": mutation}, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if "data" in result and result["data"]["alertsPolicyCreate"]:
            policy_id = result["data"]["alertsPolicyCreate"]["id"]
            print(f"✅ Created policy: {policy_name} (ID: {policy_id})")
            return policy_id
        else:
            print(f"❌ Failed to create policy: {result}")
            return None
    else:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None

def create_nrql_condition(policy_id, condition_name, nrql_query, threshold_duration, threshold_value, operator="ABOVE"):
    """Create a NRQL alert condition"""
    mutation = """
    mutation {
      alertsNrqlConditionStaticCreate(
        accountId: %s,
        policyId: "%s",
        condition: {
          name: "%s",
          enabled: true,
          nrql: {
            query: "%s"
          },
          signal: {
            aggregationWindow: 60,
            aggregationMethod: AVERAGE,
            aggregationDelay: 120
          },
          terms: [{
            threshold: %s,
            thresholdDuration: %s,
            thresholdOccurrences: AT_LEAST_ONCE,
            operator: %s,
            priority: CRITICAL
          }],
          violationTimeLimitSeconds: 86400
        }
      ) {
        id
        name
      }
    }
    """ % (ACCOUNT_ID, policy_id, condition_name, nrql_query, threshold_value, threshold_duration, operator)
    
    response = requests.post(API_URL, json={"query": mutation}, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if "data" in result and result["data"]["alertsNrqlConditionStaticCreate"]:
            print(f"  ✅ Created condition: {condition_name}")
            return True
        else:
            print(f"  ❌ Failed to create condition: {result}")
            return False
    else:
        print(f"  ❌ API Error: {response.status_code}")
        return False

def main():
    print("🚀 Creating New Relic Alert Policies for GoComet Leaderboard\n")
    
    # Policy 1: High Response Time
    print("📋 Creating Policy: High Response Time")
    policy_id = create_alert_policy("GoComet - High Response Time")
    if policy_id:
        create_nrql_condition(
            policy_id=policy_id,
            condition_name="Response Time > 500ms",
            nrql_query="SELECT average(duration) FROM Transaction WHERE appName = 'GoComet Leaderboard API'",
            threshold_duration=300,  # 5 minutes
            threshold_value=0.5,  # 500ms = 0.5 seconds
            operator="ABOVE"
        )
    
    # Policy 2: High Error Rate
    print("\n📋 Creating Policy: High Error Rate")
    policy_id = create_alert_policy("GoComet - High Error Rate")
    if policy_id:
        create_nrql_condition(
            policy_id=policy_id,
            condition_name="Error Rate > 5%",
            nrql_query="SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = 'GoComet Leaderboard API'",
            threshold_duration=180,  # 3 minutes
            threshold_value=5,  # 5%
            operator="ABOVE"
        )
    
    # Policy 3: Slow Database Queries
    print("\n📋 Creating Policy: Slow Database Queries")
    policy_id = create_alert_policy("GoComet - Slow Database Queries")
    if policy_id:
        create_nrql_condition(
            policy_id=policy_id,
            condition_name="Slow Query Count > 10",
            nrql_query="SELECT count(newrelic.timeslice.value) FROM Metric WHERE metricTimesliceName = 'Custom/SlowQuery/GetUserRank'",
            threshold_duration=300,  # 5 minutes
            threshold_value=10,
            operator="ABOVE"
        )
    
    # Policy 4: Low Cache Hit Rate
    print("\n📋 Creating Policy: Low Cache Hit Rate")
    policy_id = create_alert_policy("GoComet - Low Cache Hit Rate")
    if policy_id:
        create_nrql_condition(
            policy_id=policy_id,
            condition_name="Cache Hit Rate < 70%",
            nrql_query="SELECT (sum(Custom/Cache/TopUsers/Hit) / (sum(Custom/Cache/TopUsers/Hit) + sum(Custom/Cache/TopUsers/Miss))) * 100 FROM Metric",
            threshold_duration=300,  # 5 minutes
            threshold_value=70,
            operator="BELOW"
        )
    
    print("\n✅ Alert policy creation complete!")
    print("\n📊 View your policies at: https://one.newrelic.com/alerts")
    print("\n💡 Next steps:")
    print("   1. Add notification channels (email, Slack, etc.)")
    print("   2. Test alerts by simulating conditions")
    print("   3. Adjust thresholds based on your baseline metrics")

if __name__ == "__main__":
    main()
