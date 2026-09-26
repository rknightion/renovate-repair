# gh-aw is a public preview that changes fast; pin the compiler. Upgrading changes
# the compiled lock file and its security posture, so re-run `just check` and
# re-read the lock diff when bumping this.
gh_aw_version := "v0.89.21"

default:
    @just --list

# install the pinned gh-aw compiler as a gh extension
setup:
    gh extension install github/gh-aw --pin {{ gh_aw_version }} --force

# compile repair.md into repair.lock.yml
fmt:
    gh aw compile repair

# fail if the committed lock file is stale
fmt-check:
    gh aw compile repair
    git diff --exit-code -- .github/workflows/repair.lock.yml

# assert the write token lives only in the safe_outputs job
lint:
    python3 scripts/check_lock.py

test: lint

check: fmt-check lint
