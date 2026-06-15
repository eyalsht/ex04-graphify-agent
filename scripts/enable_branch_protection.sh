#!/usr/bin/env bash
# Enable enforced protection on `main` once the repo is PUBLIC or on GitHub Pro.
# (On a FREE private repo, GitHub rejects branch protection / rulesets with HTTP 403.)
# Requires the gh CLI authenticated with repo admin. Usage: bash scripts/enable_branch_protection.sh
set -euo pipefail

REPO="${1:-eyalsht/ex04-graphify-agent}"

# Repository ruleset: require a PR + the CI "quality" check to pass; block force-push & deletion.
gh api -X POST "repos/${REPO}/rulesets" --input - <<'JSON'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false
    } },
    { "type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "required_status_checks": [ { "context": "quality" } ]
    } },
    { "type": "non_fast_forward" },
    { "type": "deletion" }
  ]
}
JSON

echo "Branch protection ruleset 'protect-main' applied to ${REPO}."
