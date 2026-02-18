from __future__ import annotations

from services.cli.config import (
    VALID_ENVS,
    VALID_TARGETS,
    ensure_config,
    resolve_target,
    write_config,
)


def show_target() -> str:
    return resolve_target(ensure_config())


def set_target(value: str) -> str:
    if value not in VALID_TARGETS:
        raise ValueError(f"invalid target: {value}")
    cfg = ensure_config()
    cfg["target"] = value
    cfg["mode"] = value  # backward compatibility
    write_config(cfg)
    return value


def show_mode() -> str:
    return show_target()


def set_mode(value: str) -> str:
    return set_target(value)


def show_env() -> str:
    return str(ensure_config()["env"])


def set_env(value: str) -> str:
    if value not in VALID_ENVS:
        raise ValueError(f"invalid env: {value}")
    cfg = ensure_config()
    cfg["env"] = value
    write_config(cfg)
    return value
