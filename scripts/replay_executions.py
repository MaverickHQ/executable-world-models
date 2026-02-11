from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.core.loop.formatting import render_execution_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay execution ledger.")
    parser.add_argument("--executions", required=True, help="Path to executions.json")
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format",
    )
    parser.add_argument("--max-rows", type=int, default=None, help="Limit rows")
    return parser.parse_args()


def render_table(rows: list[dict]) -> None:
    print(
        "step | symbol | side | qty | price | cash_before | cash_after | "
        "positions_before | positions_after | run_id | why"
    )
    print("-" * 120)
    for row in rows:
        print(render_execution_row(_row_to_execution(row)))


def _row_to_execution(row: dict):
    from services.core.loop.types import ExecutionRow

    return ExecutionRow(
        step_index=row["step_index"],
        run_id=row["run_id"],
        decision=row.get("decision", ""),
        symbol=row["symbol"],
        side=row["side"],
        quantity=row["quantity"],
        price=row["price"],
        cash_before=row["cash_before"],
        cash_after=row["cash_after"],
        positions_before=row.get("positions_before", {}),
        positions_after=row.get("positions_after", {}),
        reason=row.get("reason", row.get("why", "")),
        verification=row.get("verification", ""),
    )


def main() -> None:
    args = parse_args()
    path = Path(args.executions)
    rows = json.loads(path.read_text())
    if args.max_rows is not None:
        rows = rows[: args.max_rows]

    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return

    render_table(rows)


if __name__ == "__main__":
    main()