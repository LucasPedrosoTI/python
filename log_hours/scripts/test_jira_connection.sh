#!/bin/bash
# Script to test Jira API connection

echo "=== Testing Jira Connection ==="
echo ""

# Load environment variables
if [ -f /app/.env.cron ]; then
    echo "📁 Loading environment from /app/.env.cron (Docker)"
    . /app/.env.cron
elif [ -f .env ]; then
    echo "📁 Loading environment from .env (Local)"
    set -a
    source .env
    set +a
else
    echo "❌ No environment file found (.env or /app/.env.cron)"
    exit 1
fi

# Validate required environment variables
echo ""
echo "🔍 Checking required environment variables..."

missing_vars=()

if [ -z "$JIRA_URL" ]; then
    missing_vars+=("JIRA_URL")
fi

if [ -z "$JIRA_USERNAME" ]; then
    missing_vars+=("JIRA_USERNAME")
fi

if [ -z "$JIRA_SVC_ACCOUNT" ]; then
    missing_vars+=("JIRA_SVC_ACCOUNT")
fi

if [ -z "$JIRA_API_TOKEN" ]; then
    missing_vars+=("JIRA_API_TOKEN")
fi

if [ -z "$JIRA_PROJECT" ]; then
    missing_vars+=("JIRA_PROJECT")
fi

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    exit 1
fi

echo "✅ All required environment variables are set"
echo ""
echo "📋 Configuration:"
echo "   JIRA_URL:         $JIRA_URL"
echo "   JIRA_USERNAME:    $JIRA_USERNAME"
echo "   JIRA_SVC_ACCOUNT: $JIRA_SVC_ACCOUNT"
echo "   JIRA_PROJECT:     $JIRA_PROJECT"
echo "   JIRA_API_TOKEN:   ***${JIRA_API_TOKEN: -4}"
echo ""

# Test 1: Check Jira server connectivity
echo "=== Test 1: Server Connectivity ==="
echo "Testing connection to $JIRA_URL..."
echo ""

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$JIRA_URL")

if [ "$HTTP_STATUS" = "000" ]; then
    echo "❌ Could not connect to Jira server"
    echo "   Check if JIRA_URL is correct and the server is reachable"
    exit 1
elif [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
    echo "✅ Server is reachable (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Server responded with HTTP $HTTP_STATUS"
fi
echo ""

# Test 2: API Authentication
echo "=== Test 2: API Authentication ==="
echo "Testing API authentication..."
echo ""

API_URL="$JIRA_URL/rest/api/3/myself"
AUTH_STRING=$(echo -n "$JIRA_SVC_ACCOUNT:$JIRA_API_TOKEN" | base64)

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Basic $AUTH_STRING" \
    -H "Accept: application/json" \
    --connect-timeout 10 \
    "$API_URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API authentication successful!"
    DISPLAY_NAME=$(echo "$BODY" | grep -o '"displayName":"[^"]*"' | cut -d'"' -f4)
    ACCOUNT_ID=$(echo "$BODY" | grep -o '"accountId":"[^"]*"' | cut -d'"' -f4)
    echo "   Authenticated as: $DISPLAY_NAME"
    echo "   Account ID: $ACCOUNT_ID"
elif [ "$HTTP_CODE" = "401" ]; then
    echo "❌ Authentication failed (HTTP 401)"
    echo "   Check JIRA_SVC_ACCOUNT and JIRA_API_TOKEN"
    exit 1
elif [ "$HTTP_CODE" = "403" ]; then
    echo "❌ Access forbidden (HTTP 403)"
    echo "   The service account may not have the required permissions"
    exit 1
else
    echo "❌ API request failed with HTTP $HTTP_CODE"
    echo "   Response: $BODY"
    exit 1
fi
echo ""

# Test 3: Project Access
echo "=== Test 3: Project Access ==="
echo "Checking access to project $JIRA_PROJECT..."
echo ""

PROJECT_URL="$JIRA_URL/rest/api/3/project/$JIRA_PROJECT"
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Basic $AUTH_STRING" \
    -H "Accept: application/json" \
    --connect-timeout 10 \
    "$PROJECT_URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    PROJECT_NAME=$(echo "$BODY" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✅ Project access confirmed!"
    echo "   Project: $PROJECT_NAME ($JIRA_PROJECT)"
elif [ "$HTTP_CODE" = "404" ]; then
    echo "❌ Project not found (HTTP 404)"
    echo "   Check if JIRA_PROJECT is correct"
    exit 1
elif [ "$HTTP_CODE" = "403" ]; then
    echo "❌ Access to project forbidden (HTTP 403)"
    echo "   The service account may not have access to this project"
    exit 1
else
    echo "⚠️  Unexpected response (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
fi
echo ""

# Test 4: JQL Query (same query used by the app)
echo "=== Test 4: JQL Query ==="
echo "Testing the same query used by the application..."
echo ""

JQL="project = $JIRA_PROJECT AND assignee = \"$JIRA_USERNAME\" AND updated >= -5d AND type IN standardIssueTypes()"
echo "📋 JQL: $JQL"
echo ""

SEARCH_URL="$JIRA_URL/rest/api/3/search/jql"
ENCODED_JQL=$(echo -n "$JQL" | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read()))")

RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Basic $AUTH_STRING" \
    -H "Accept: application/json" \
    --connect-timeout 30 \
    "$SEARCH_URL?jql=$ENCODED_JQL&maxResults=10&fields=key,summary")

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    TOTAL=$(echo "$BODY" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "✅ JQL query successful!"
    echo "   Total issues found: $TOTAL"
    
    if [ "$TOTAL" = "0" ]; then
        echo ""
        echo "⚠️  No issues found for user $JIRA_USERNAME in the last 5 days"
        echo "   This is not an error, but the app needs assigned tickets to log hours"
    else
        echo ""
        echo "📋 Recent issues:"
        # Extract issue keys (simplified parsing)
        echo "$BODY" | grep -o '"key":"[^"]*"' | cut -d'"' -f4 | head -5 | while read -r key; do
            echo "   - $key"
        done
    fi
elif [ "$HTTP_CODE" = "400" ]; then
    echo "❌ Invalid JQL query (HTTP 400)"
    echo "   Response: $BODY"
    exit 1
else
    echo "❌ JQL query failed (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ All Jira connection tests passed!"
echo "========================================="
