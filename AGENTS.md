# renovate-repair

A GitHub Agentic Workflows (gh-aw) workflow that repairs the CI failure blocking one Renovate pull
request in a public rknightion or BroTEK-Solutions repository and proposes the fix as a draft PR.
Pilot stage: dispatched by hand, auto-merge off.

- Edit `.github/workflows/repair.md`, then `just fmt` to regenerate `repair.lock.yml`. Never edit
  the lock file by hand. `just check` must pass before a commit.
- The gh-aw compiler is pinned in the `justfile`. A bump changes the compiled security posture:
  re-read the lock diff.
- **The write token must exist only in the `safe_outputs` job.** `scripts/check_lock.py` enforces
  it. The agent job's `mint` step is a deliberate stub: the compiler requires a step with that id in
  every job that evaluates the PR token, and the stub keeps a real token out of the agent container.
- `protected-files: blocked` is deliberate. `request-review` still pushes the protected change,
  and a pushed workflow file runs with the target repo's own token. A self-authored PR cannot carry
  a REQUEST_CHANGES review either (GitHub refuses it; gh-aw falls back to COMMENT), so a review is
  never a merge gate here.
- No job may hold `workflows: write`, and the broker permission sets grant only `contents` and
  `pull_requests` write.
- Tokens: one OpenBao permission set, policy and JWT role per target repo,
  `renovate-repair-<repo>`, each role pinned to this repo's id, `main`, `workflow_dispatch` and
  `repair.lock.yml`. Adding a target repo means a new set, policy and role plus the `repo` choice
  list and the permission-set expression in `repair.md`. Runbook:
  `~/repos/chat-personal/camden/openbao/runbooks/CI-SECRETS.md`.
- `AI_GATEWAY_TOKEN` is a Cloudflare token with Account AI Gateway Run only; the model is
  DeepSeek `deepseek-flash` via `https://ai.m7kni.com/deepseek` (Copilot BYOK, completions wire).
- Plan and pilot record: `~/repos/chat-personal/docs/superpowers/plans/2026-09-26-renovate-repair-gh-aw-pilot.md`.
