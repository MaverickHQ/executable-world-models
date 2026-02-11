from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from services.core.broker.types import ExecutionEvent, OrderRequest


class Broker(ABC):
    @abstractmethod
    def execute(
        self, orders: List[OrderRequest], price_context: Dict[str, float]
    ) -> List[ExecutionEvent]:
        raise NotImplementedError