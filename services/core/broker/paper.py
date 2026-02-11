from __future__ import annotations

from typing import Dict, List

from services.core.broker.base import Broker
from services.core.broker.types import ExecutionEvent, OrderRequest


class LocalPaperBroker(Broker):
    def execute(
        self, orders: List[OrderRequest], price_context: Dict[str, float]
    ) -> List[ExecutionEvent]:
        events: List[ExecutionEvent] = []
        for order in orders:
            price = price_context.get(order.symbol, order.limit_price)
            event_id = f"{order.run_id}:{order.step_index}:{order.action_index}"
            events.append(
                ExecutionEvent(
                    event_id=event_id,
                    run_id=order.run_id,
                    step_index=order.step_index,
                    action_index=order.action_index,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    price=price,
                    status="FILLED",
                )
            )
        return events