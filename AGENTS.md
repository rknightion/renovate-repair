# renovate-repair

A GitHub Agentic Workflows (gh-aw) workflow that repairs the CI failure blocking one Renovate pull
request in a public rknightion or BroTEK-Solutions repository and proposes the fix as a PR (auto-merge off).
Dispatched by the n8n workflow "GitHub — Renovate Repair Dispatcher", which also decides merges
(`~/repos/chat-personal/n8n/renovate-repair.md`). Nothing in this repo merges anything.

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
- Enrolled repos live in `repos.txt` only. `just fmt` regenerates the `repo` choice list in
  `repair.md` from it and `just check` fails on drift. Names must be unique across owners because
  the permission set keys on the bare name.
- Tokens: one OpenBao permission set, policy and JWT role per target repo,
  `renovate-repair-<repo>`, each role pinned to this repo's id, `main`, `workflow_dispatch` and
  `repair.lock.yml`. The `Resolve permission set` pre-step maps the input to the set name; an
  unknown name resolves to `renovate-repair-none`, which does not exist and fails closed. Enrolling a
  repo = a `repos.txt` line plus the OpenBao set, policy and role. Runbook:
  `~/repos/chat-personal/camden/openbao/runbooks/CI-SECRETS.md`.
- `run-name` is `Renovate repair <owner>/<repo>#<pr>`; the dispatcher parses it back. Keep the format.
- Kill switch: repository variable `REPAIR_ENABLED` must equal `true` or every run skips at activation.
- No job may hold `actions: write` either (a token with it could dispatch workflows here).
- gh-aw merges the agent's own `labels` into the PR's, so a label on a repair PR proves nothing.
  The dispatcher identifies its PRs by run correlation, never by label.
- `AI_GATEWAY_TOKEN` is a Cloudflare token with Account AI Gateway Run only; the model is
  DeepSeek `deepseek-flash` via `https://ai.m7kni.com/deepseek` (Copilot BYOK, completions wire).
- Plans: `~/repos/chat-personal/docs/superpowers/plans/2026-09-26-renovate-repair-gh-aw-pilot.md` (pilot) and `2026-09-26-renovate-repair-phase2.md` (dispatch and merge tiers).
