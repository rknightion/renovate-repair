"""Guard the compiled workflow's token layout.

The write token must exist only in the safe_outputs job. If a gh-aw upgrade or a
frontmatter edit ever moves the broker mint or `id-token: write` into the agent
job, the agent container could reach a write-scoped GitHub token.
"""

import json
import re
import sys
from pathlib import Path

LOCK = Path(".github/workflows/repair.lock.yml")


def jobs(text: str) -> dict[str, str]:
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"\n  ([A-Za-z_][A-Za-z0-9_-]*):\n", "\n" + body)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def main() -> int:
    j = jobs(LOCK.read_text())
    errors = []
    for name, body in j.items():
        has_mint = "broker-token@" in body
        has_oidc = "id-token: write" in body
        if name == "safe_outputs":
            if not (has_mint and has_oidc):
                errors.append("safe_outputs must mint the broker token with id-token: write")
        elif has_mint or has_oidc:
            errors.append(f"job {name!r} must not mint a broker token or hold id-token: write")
    text = LOCK.read_text()
    if "workflows: write" in text:
        errors.append("no job may hold workflows: write")
    # GITHUB_TOKEN with actions: write can dispatch workflows, including this one.
    if "actions: write" in text:
        errors.append("no job may hold actions: write")
    # Carrier mode (push-to-pull-request-branch) must stay pinned to the dispatched, held PR and
    # must never fall back to a new PR or an extra-commit token.
    # Both the tool config (agent side) and the handler config (what safe_outputs applies) must pin
    # the push to the dispatched, held PR. The target is `${{ inputs.pr }}` in the handler config
    # and env-substituted from GH_AW_INPUT_PR (= inputs.pr) in the tool config.
    pinned = {"${{ inputs.pr }}", "${GH_AW_INPUT_PR}"}
    for var in ("GH_AW_SAFE_OUTPUTS_CONFIG", "GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG"):
        raw = re.findall(var + r': ("(?:[^"\\]|\\.)*")', text)
        push = [c["push_to_pull_request_branch"] for c in map(lambda v: json.loads(json.loads(v)), raw)
                if "push_to_pull_request_branch" in c]
        if not push:
            errors.append(f"{var}: push_to_pull_request_branch config not found")
        for cfg in push:
            if cfg.get("target") not in pinned:
                errors.append(f"{var}: push target is {cfg.get('target')!r}, expected inputs.pr")
            want = {"fallback_as_pull_request": False, "required_labels": ["stop-updating"],
                    "protected_files_policy": "blocked", "max": 1}
            for k, v in want.items():
                if cfg.get(k) != v:
                    errors.append(f"{var}: push {k} is {cfg.get(k)!r}, expected {v!r}")
    if "GH_AW_CI_TRIGGER_TOKEN" in text:
        errors.append("the extra-empty-commit CI trigger token must stay out of the lock")
    if "Guard the held Renovate PR" not in j.get("safe_outputs", ""):
        errors.append("safe_outputs must run the held-PR guard before any write")
    for e in errors:
        print(f"check_lock: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
