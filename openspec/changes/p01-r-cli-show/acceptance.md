# P01 Acceptance — R-CLI-SHOW

## Acceptance criteria

- [x] AC1: `ewm target show` default output is `target: <value>`.
- [x] AC2: `ewm mode show` default output is `mode: <value>`.
- [x] AC3: `ewm env show` default output is `env: <value>`.
- [x] AC4: `--raw` for all three commands prints only raw value.
- [x] AC5: Existing CLI behavior outside show-formatting remains unchanged.
- [x] AC6: Unit tests cover default and raw outputs for all three commands.

## Test evidence

Commands:
- [x] `pytest tests/unit/test_cli_mode_env.py -q`
- [x] `pytest tests/unit/test_cli_config_io.py -q`
- [x] `pytest tests/unit/test_cli_runs_latest.py -q`

Results:
- [x] All required tests passed
- [x] No relevant regressions observed

Recorded outputs:
- `pytest tests/unit/test_cli_mode_env.py -q` -> `5 passed in 1.67s`
- `pytest tests/unit/test_cli_config_io.py -q` -> `3 passed in 0.01s`
- `pytest tests/unit/test_cli_runs_latest.py -q` -> `3 passed in 0.01s`
- Combined regression check: `pytest tests/unit/test_cli_mode_env.py tests/unit/test_cli_config_io.py tests/unit/test_cli_runs_latest.py -q` -> `11 passed in 1.37s`

## Git evidence

- [ ] Branch verified pre/post commit
- [ ] Commit SHA recorded
- [ ] Push/upstream verified

## Notes

Release tasks are optional for this pilot unless explicitly requested.
