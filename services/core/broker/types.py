from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class OrderRequest:
    run_id: str
    step_index: int
    action_index: int
    symbol: str
    side: str
    quantity: float
    limit_price: float

    def to_dict(self) -> Dict[str, object]:
        return {
            "run_id": self.run_id,
            "step_index": self.step_index,
            "action_index": self.action_index,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "limit_price": self.limit_price,
        }


@dataclass(frozen=True)
class OrderFill:
    fill_price: float
    filled_qty: float
    status: str = "FILLED"

    def to_dict(self) -> Dict[str, object]:
        return {
            "fill_price": self.fill_price,
            "filled_qty": self.filled_qty,
            "status": self.status,
        }


@dataclass(frozen=True)
class ExecutionEvent:
    event_id: str
    run_id: str
    step_index: int
    action_index: int
    symbol: str
    side: str
    quantity: float
    price: float
    status: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "event_id": self.event_id,
            "run_id": self.run_id,
            "step_index": self.step_index,
            "action_index": self.action_index,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status,
        }