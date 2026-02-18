from __future__ import annotations

import subprocess


def _run(args: list[str], home: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "-m", "services.cli.main", *args],
        text=True,
        capture_output=True,
        env={"HOME": home},
        check=False,
    )


def test_mode_show_and_set_persists(tmp_path) -> None:
    home = str(tmp_path)

    show = _run(["mode", "show"], home)
    assert show.returncode == 0
    assert show.stdout.strip() == "local"

    set_mode = _run(["mode", "set", "aws"], home)
    assert set_mode.returncode == 0
    assert set_mode.stdout.strip() == "aws"

    show_after = _run(["mode", "show"], home)
    assert show_after.returncode == 0
    assert show_after.stdout.strip() == "aws"


def test_env_show_and_set_persists(tmp_path) -> None:
    home = str(tmp_path)

    show = _run(["env", "show"], home)
    assert show.returncode == 0
    assert show.stdout.strip() == "paper"

    set_env = _run(["env", "set", "prod"], home)
    assert set_env.returncode == 0
    assert set_env.stdout.strip() == "prod"

    show_after = _run(["env", "show"], home)
    assert show_after.returncode == 0
    assert show_after.stdout.strip() == "prod"


def test_invalid_mode_and_env_return_nonzero(tmp_path) -> None:
    home = str(tmp_path)

    bad_mode = _run(["mode", "set", "invalid"], home)
    assert bad_mode.returncode != 0

    bad_env = _run(["env", "set", "invalid"], home)
    assert bad_env.returncode != 0
