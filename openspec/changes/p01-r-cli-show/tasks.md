# P01 Tasks — R-CLI-SHOW (Pilot)

## Phase 0 — Preflight (MANDATORY)
- [x] Check working branch
  - `git branch --show-current`
  - Expected: feature branch for this change
- [x] Check workspace cleanliness/intent
  - `git status`

## Phase 1 — Parser updates
- [x] Add `--raw` option to `target show`
- [x] Add `--raw` option to `mode show`
- [x] Add `--raw` option to `env show`

## Phase 2 — CLI output behavior
- [x] Implement default labeled output for `target show`
- [x] Implement default labeled output for `mode show`
- [x] Implement default labeled output for `env show`
- [x] Ensure `--raw` returns raw value with no label

## Phase 3 — Testing (MANDATORY)
- [x] Add/update tests for default output (`key: value`) for all three commands
- [x] Add/update tests for `--raw` output for all three commands
- [x] Confirm no regression in related CLI tests

Required test commands:
- [x] `pytest tests/unit/test_cli_mode_env.py -q`
- [x] `pytest tests/unit/test_cli_config_io.py -q`
- [x] `pytest tests/unit/test_cli_runs_latest.py -q`

## Phase 4 — Acceptance evidence
- [x] Update `openspec/changes/p01-r-cli-show/acceptance.md`
- [x] Record command outputs and test evidence

## Phase 5 — Commit/push gates (MANDATORY)
- [x] Re-check branch before commit
  - `git branch --show-current`
- [x] Review final diff
  - `git status`
- [ ] Commit with scoped message
  - Example: `cli: add labeled show output with --raw (p01-r-cli-show)`
- [ ] Verify commit on expected branch
  - `git log --oneline -n 1`
- [ ] Push branch
- [ ] Verify upstream tracking
  - `git rev-parse --abbrev-ref --symbolic-full-name @{u}`

## Phase 6 — Optional release tasks (ONLY if explicitly releasing)
- [ ] Merge/checkout `main` and pull latest
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] **Update `README.md` (mandatory for release)**
- [ ] Run verification (`make lint`, `make test`)
- [ ] Commit release and create annotated tag
- [ ] Push main and tag
- [ ] Verify remote tag exists
