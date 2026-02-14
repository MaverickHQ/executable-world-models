from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

import boto3


class MemoryStoreError(RuntimeError):
    def __init__(self, message: str, code: str = "memory_error") -> None:
        super().__init__(message)
        self.code = code


class MemoryStore(Protocol):
    def put(self, key: str, value: Dict[str, Any]) -> None:
        ...

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        ...


@dataclass
class InMemoryMemoryStore:
    storage: Dict[str, Dict[str, Any]]

    def put(self, key: str, value: Dict[str, Any]) -> None:
        self.storage[key] = value

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self.storage.get(key)


class NoOpMemoryStore:
    def put(self, key: str, value: Dict[str, Any]) -> None:
        return None

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return None


class BedrockAgentCoreMemoryStore:
    """
    Placeholder adapter for AgentCore Memory.

    This uses AWS SDK calls only when ENABLE_AGENTCORE_MEMORY=1. If the
    integration is not configured, it returns a structured error.
    """

    def __init__(self) -> None:
        self.enabled = os.environ.get("ENABLE_AGENTCORE_MEMORY") == "1"
        self.region = os.environ.get("AWS_REGION", "")
        self._client = boto3.client("bedrock-agent-runtime") if self.enabled else None

    def _guard_enabled(self) -> None:
        if not self.enabled:
            raise MemoryStoreError("AgentCore memory disabled", code="memory_disabled")
        if not self._client:
            raise MemoryStoreError("AgentCore memory client unavailable", code="memory_unavailable")

    def put(self, key: str, value: Dict[str, Any]) -> None:
        self._guard_enabled()
        raise MemoryStoreError(
            "AgentCore memory integration not configured", code="memory_unavailable"
        )

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        self._guard_enabled()
        raise MemoryStoreError(
            "AgentCore memory integration not configured", code="memory_unavailable"
        )


def estimate_memory_bytes(payload: Dict[str, Any]) -> int:
    return len(json.dumps(payload, sort_keys=True).encode("utf-8"))