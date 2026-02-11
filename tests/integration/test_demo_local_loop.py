import json
import subprocess
from pathlib import Path


def test_demo_local_loop_outputs(tmp_path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    monkeypatch.chdir(repo_root)

    result = subprocess.run(
        ["python3", "scripts/demo_local_loop.py", "--steps", "5"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Execution Ledger" in result.stdout
    assert "step | prices | signals" in result.stdout
    assert "step | symbol | side" in result.stdout

    data_dir = repo_root / "tmp" / "demo_local_loop"
    tape_path = data_dir / "tape.json"
    executions_path = data_dir / "executions.json"
    report_path = data_dir / "report.md"

    assert tape_path.exists()
    assert executions_path.exists()
    assert report_path.exists()

    payload = json.loads(tape_path.read_text())
    executions = json.loads(executions_path.read_text())

    assert payload
    assert any(row["decision"] == "APPROVED" for row in payload)
    assert all(row["decision"] == "APPROVED" for row in executions)

    replay_tape = subprocess.run(
        ["python3", "scripts/replay_tape.py", "--tape", str(tape_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "step | prices | signals" in replay_tape.stdout

    replay_executions = subprocess.run(
        [
            "python3",
            "scripts/replay_executions.py",
            "--executions",
            str(executions_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "step | symbol | side" in replay_executions.stdout