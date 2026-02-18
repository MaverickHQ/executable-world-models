from __future__ import annotations

import json

from services.cli import runs


def test_runs_latest_no_data_prints_help(monkeypatch, capsys, tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    monkeypatch.setattr(runs, "_repo_root", lambda _cwd=None: repo)

    rc = runs.runs_latest()
    out = capsys.readouterr().out
    assert rc == 0
    assert "No local runs found. Run scripts/demo_local_loop.py first." in out


def test_runs_latest_reads_runs_and_plan_summary(monkeypatch, capsys, tmp_path) -> None:
    repo = tmp_path / "repo"
    runs_dir = repo / "tmp" / "demo_local_loop"
    runs_dir.mkdir(parents=True)
    payload = [
        {
            "run_id": "r-1",
            "ok": True,
            "plan": {
                "meta": {"planner": "local"},
                "steps": [{"tool": "validate_request"}, {"tool": "run_loop"}],
            },
        }
    ]
    (runs_dir / "runs.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(runs, "_repo_root", lambda _cwd=None: repo)
    rc = runs.runs_latest()
    out = capsys.readouterr().out

    assert rc == 0
    assert "source:" in out
    assert '"run_id": "r-1"' in out
    assert "plan.meta:" in out
    assert "plan.step[1]: validate_request" in out


def test_runs_tail_respects_n(monkeypatch, capsys, tmp_path) -> None:
    repo = tmp_path / "repo"
    runs_dir = repo / "tmp" / "demo_local_loop"
    runs_dir.mkdir(parents=True)
    payload = [{"run_id": f"r-{i}"} for i in range(5)]
    (runs_dir / "runs.json").write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(runs, "_repo_root", lambda _cwd=None: repo)
    rc = runs.runs_tail(2)
    out = capsys.readouterr().out

    assert rc == 0
    assert '"run_id": "r-4"' in out
    assert '"run_id": "r-3"' in out
    assert '"run_id": "r-1"' not in out
