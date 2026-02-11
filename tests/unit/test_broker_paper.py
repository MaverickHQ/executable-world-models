from services.core.broker.paper import LocalPaperBroker
from services.core.broker.types import OrderRequest


def test_paper_broker_deterministic_events() -> None:
    broker = LocalPaperBroker()
    orders = [
        OrderRequest(
            run_id="run-1",
            step_index=2,
            action_index=0,
            symbol="AAPL",
            side="BUY",
            quantity=1.0,
            limit_price=99.0,
        ),
        OrderRequest(
            run_id="run-1",
            step_index=2,
            action_index=1,
            symbol="MSFT",
            side="SELL",
            quantity=2.0,
            limit_price=200.0,
        ),
    ]

    events = broker.execute(orders, {"AAPL": 101.0, "MSFT": 199.5})
    assert events[0].event_id == "run-1:2:0"
    assert events[0].price == 101.0
    assert events[1].event_id == "run-1:2:1"
    assert events[1].price == 199.5