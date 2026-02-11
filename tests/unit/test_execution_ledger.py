from services.core.loop.formatting import render_execution_row
from services.core.loop.types import ExecutionRow


def test_execution_row_formatting() -> None:
    row = ExecutionRow(
        step_index=1,
        run_id="run-1",
        decision="APPROVED",
        symbol="AAPL",
        side="BUY",
        quantity=1.0,
        price=100.0,
        cash_before=1_000.0,
        cash_after=900.0,
        positions_before={"AAPL": 0.0},
        positions_after={"AAPL": 1.0},
        reason="AAPL: price < buy_below",
        verification="verified OK",
    )

    rendered = render_execution_row(row)
    assert "1 | AAPL | BUY" in rendered
    assert "1000.00" in rendered
    assert "900.00" in rendered
    assert "AAPL 0.00" in rendered
    assert "AAPL 1.00" in rendered