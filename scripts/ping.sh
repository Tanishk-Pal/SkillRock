#!/usr/bin/env bash
#
# Keep-Alive Ping Script for Render Free-Tier Web Services
# Pings target URL(s) to prevent cold starts / instance spin-downs.
#
# Usage:
#   ./scripts/ping.sh [TARGET_URL]
#   TARGET_URL="https://skillrock.onrender.com/healthz" ./scripts/ping.sh
#

set -o pipefail

TARGET_URL="${1:-${TARGET_URL:-https://skillrock.onrender.com/healthz}}"
HTTP_METHOD="${HTTP_METHOD:-GET}"
EXPECTED_STATUS="${EXPECTED_STATUS:-200}"
FAIL_ON_ERROR="${FAIL_ON_ERROR:-false}"

if [ -z "$TARGET_URL" ]; then
  echo "❌ Error: TARGET_URL is not set and no URL argument was provided."
  exit 1
fi

echo "=========================================================="
echo "🚀 Keep Render Instance Alive — HTTP Ping"
echo "🕒 Timestamp: $(date -u +"%Y-%m-%d %H:%M:%SZ")"
echo "🔧 Method:    $HTTP_METHOD"
echo "🎯 Targets:   $TARGET_URL"
echo "=========================================================="

HAD_FAILURE=0

# Support comma-separated URLs
IFS=',' read -ra ADDR <<< "$TARGET_URL"
for raw_url in "${ADDR[@]}"; do
  # Trim whitespace
  url="$(echo "$raw_url" | xargs)"
  if [ -z "$url" ]; then
    continue
  fi

  echo ""
  echo "➡️ Pinging: $url"

  # Run curl with timing and response code extraction
  CURL_CMD=(
    curl
    -s
    -S
    -L
    --max-time 30
    -A "SkillRock-KeepAlive/1.0 (+https://skillrock.onrender.com)"
    -w "%{http_code} %{time_total}"
  )

  if [ "$HTTP_METHOD" = "HEAD" ]; then
    CURL_CMD+=( -I )
  else
    CURL_CMD+=( -X GET -o /dev/null )
  fi

  OUTPUT="$("${CURL_CMD[@]}" "$url" 2>&1)"
  CURL_EXIT=$?

  if [ $CURL_EXIT -ne 0 ]; then
    echo "❌ [FAILED] curl error (exit code $CURL_EXIT): $OUTPUT"
    HAD_FAILURE=1
    continue
  fi

  HTTP_CODE=$(echo "$OUTPUT" | awk '{print $1}')
  TIME_TOTAL=$(echo "$OUTPUT" | awk '{print $2}')

  echo "⏱️ Response Time: ${TIME_TOTAL}s"
  echo "📊 HTTP Status:   $HTTP_CODE"

  if [ -n "$EXPECTED_STATUS" ] && [ "$EXPECTED_STATUS" != "" ]; then
    if [ "$HTTP_CODE" -eq "$EXPECTED_STATUS" ]; then
      echo "✅ Instance is WARM & healthy (matches expected status $EXPECTED_STATUS)."
    else
      echo "⚠️ [WARNING] Status $HTTP_CODE does not match expected $EXPECTED_STATUS."
      if [ "$FAIL_ON_ERROR" = "true" ]; then
        HAD_FAILURE=1
      fi
    fi
  else
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 400 ]; then
      echo "✅ Instance is WARM & reachable."
    else
      echo "⚠️ [WARNING] Unexpected HTTP Status $HTTP_CODE."
      if [ "$FAIL_ON_ERROR" = "true" ]; then
        HAD_FAILURE=1
      fi
    fi
  fi
done

echo ""
echo "=========================================================="
if [ $HAD_FAILURE -eq 1 ]; then
  echo "❌ One or more ping checks failed."
  if [ "$FAIL_ON_ERROR" = "true" ]; then
    exit 1
  fi
else
  echo "🎉 All pings completed successfully. Render instance is warm."
fi
echo "=========================================================="
