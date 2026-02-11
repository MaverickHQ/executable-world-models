from __future__ import annotations

from typing import Dict, List

from services.core.loop.types import ExecutionRow


def render_execution_row(row: ExecutionRow) -> str:
    return (
        " | ".join(
            [
                str(row.step_index),
                row.symbol,
                row.side,
                f"{row.quantity:.2f}",
                f"{row.price:.2f}",
                f"{row.cash_before:.2f}",
                f"{row.cash_after:.2f}",
                _format_positions(row.positions_before),
                _format_positions(row.positions_after),
                row.run_id,
                row.reason,
            ]
        )
    )


def _format_positions(positions: Dict[str, float]) -> str:
    if not positions:
        return "-"
    parts = [
        f"{symbol} {qty:.2f}" for symbol, qty in sorted(positions.items())
    ]
    return "; ".join(parts)


def render_execution_table(rows: List[ExecutionRow]) -> List[str]:
    lines = [
        "step | symbol | side | qty | price | cash_before | cash_after | "
        "positions_before | positions_after | run_id | why",
        "-" * 120,
    ]
    lines.extend(render_execution_row(row) for row in rows)
    return lines