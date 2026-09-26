"""Guard the compiled workflow's token layout.

The write token must exist only in the safe_outputs job. If a gh-aw upgrade or a
frontmatter edit ever moves the broker mint or `id-token: write` into the agent
job, the agent container could reach a write-scoped GitHub token.
"""

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
    if "workflows: write" in LOCK.read_text():
        errors.append("no job may hold workflows: write")
    for e in errors:
        print(f"check_lock: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
