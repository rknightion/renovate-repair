"""Keep the repair workflow's `repo` choice list in step with repos.txt.

repos.txt is the single list of enrolled target repositories. `sync` rewrites the
generated block in repair.md; `--check` fails if the block has drifted.
"""

import re
import sys
from pathlib import Path

REPOS = Path("repos.txt")
WORKFLOW = Path(".github/workflows/repair.md")
BEGIN = "          # BEGIN repos (generated from repos.txt by `just sync-repos`)\n"
END = "          # END repos\n"
NAME = re.compile(r"^(rknightion|BroTEK-Solutions)/[A-Za-z0-9._-]+$")


def render() -> str:
    names = [ln.strip() for ln in REPOS.read_text().splitlines() if ln.strip()]
    bad = [n for n in names if not NAME.match(n)]
    if bad:
        raise SystemExit(f"sync_repos: invalid entries in repos.txt: {bad}")
    if len(set(n.split("/")[1] for n in names)) != len(names):
        raise SystemExit("sync_repos: repo names must be unique across owners (permission sets key on the name)")
    return BEGIN + "".join(f"          - {n}\n" for n in sorted(names)) + END


def main() -> int:
    text = WORKFLOW.read_text()
    start, end = text.index(BEGIN), text.index(END) + len(END)
    new = text[:start] + render() + text[end:]
    if "--check" in sys.argv:
        if new != text:
            print("sync_repos: repair.md choice list differs from repos.txt; run `just sync-repos`", file=sys.stderr)
            return 1
        return 0
    WORKFLOW.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
