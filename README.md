# renovate-repair

Agentic repair of CI failures that block Renovate dependency-update pull requests, built on
[GitHub Agentic Workflows](https://github.github.com/gh-aw/). The agent reproduces the failure with
the target repository's own `just check`, fixes the root cause without weakening any check, and
opens a draft pull request. Dependency manifests, lockfiles and anything under `.github/` are never
changed by the agent; those cases end with a written diagnosis instead.
