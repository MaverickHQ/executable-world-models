from __future__ import annotations

import json
import os
import ssl
import sys
from pathlib import Path

import boto3
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.aws.utils.output_loader import load_outputs

OUTPUTS_PATH = Path(
    os.environ.get("AWS_OUTPUTS_PATH", ROOT / "infra" / "cdk" / "cdk-outputs.json")
)


def _sanitize(payload: dict) -> dict:
    if "artifact_dir" in payload:
        payload = dict(payload)
        payload["artifact_dir"] = "s3://<redacted>/artifacts/<run_id>/"
    return payload


def _invoke_api(api_url: str, body: dict) -> dict:
    url = api_url.rstrip("/") + "/agentcore/memory"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    context = ssl.create_default_context()
    if os.environ.get("ALLOW_INSECURE_HTTPS") == "1":
        context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=10, context=context) as response:
        return json.loads(response.read().decode("utf-8"))


def _invoke_lambda(function_name: str, body: dict) -> dict:
    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(body).encode("utf-8"),
    )
    return json.loads(response["Payload"].read().decode("utf-8"))


def _load_outputs() -> dict:
    if OUTPUTS_PATH.exists():
        return load_outputs(OUTPUTS_PATH)

    stack_name = os.environ.get("AWS_STACK_NAME", "BeyondTokensStack")
    client = boto3.client("cloudformation")
    response = client.describe_stacks(StackName=stack_name)
    stacks = response.get("Stacks", [])
    if not stacks:
        raise SystemExit("Missing stack outputs; deploy the stack first.")

    outputs = {}
    for output in stacks[0].get("Outputs", []):
        outputs[output["OutputKey"]] = output["OutputValue"]
    return outputs


def _run(api_url: str | None, function_name: str | None, body: dict) -> dict:
    if api_url:
        try:
            return _invoke_api(api_url, body)
        except Exception:
            return _invoke_lambda(function_name, body)
    return _invoke_lambda(function_name, body)


def _run_scenario(name: str, api_url: str | None, function_name: str | None, body: dict) -> None:
    payload = _run(api_url, function_name, body)
    print(f"\n== {name} ==")
    print(json.dumps(_sanitize(payload), indent=2))


def main() -> None:
    print("AgentCore Memory Demo")
    print("- Expect ok=true for memory_put/memory_get")
    print("- Expect ok=false with budget_exceeded for max_memory_ops=0")

    outputs = _load_outputs()
    api_url = outputs.get("AgentCoreMemoryApiUrl")
    function_name = outputs.get("AgentCoreMemoryFunctionName")

    if not api_url and not function_name:
        raise SystemExit("Missing AgentCore memory outputs. Run cdk deploy.")

    os.environ.setdefault("ENABLE_AGENTCORE_MEMORY", "1")

    put_body = {
        "mode": "agentcore-memory",
        "budget": {"max_steps": 1, "max_tool_calls": 0, "max_model_calls": 0, "max_memory_ops": 1, "max_memory_bytes": 512},
        "requests": [{"op": "memory_put", "key": "demo", "value": {"value": "hello"}}],
    }
    get_body = {
        "mode": "agentcore-memory",
        "budget": {"max_steps": 1, "max_tool_calls": 0, "max_model_calls": 0, "max_memory_ops": 1, "max_memory_bytes": 512},
        "requests": [{"op": "memory_get", "key": "demo"}],
    }
    fail_body = {
        "mode": "agentcore-memory",
        "budget": {"max_steps": 1, "max_tool_calls": 0, "max_model_calls": 0, "max_memory_ops": 0, "max_memory_bytes": 0},
        "requests": [{"op": "memory_get", "key": "demo"}],
    }

    _run_scenario("memory_put (expect ok=true)", api_url, function_name, put_body)
    _run_scenario("memory_get (expect ok=true)", api_url, function_name, get_body)
    _run_scenario("budget_exceeded (expect ok=false)", api_url, function_name, fail_body)


if __name__ == "__main__":
    main()