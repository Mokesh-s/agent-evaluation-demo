import json
import os
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "orders.json"

def _load():
    return json.loads(DATA_FILE.read_text())

def _save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def get_order(order_id: str) -> str:
    """Retrieve an order by ID. Always use this before destructive actions."""
    order = _load().get(order_id)
    if not order:
        return f"ORDER_NOT_FOUND:{order_id}"
    return json.dumps({"order_id": order_id, **order})

def cancel_order(order_id: str) -> str:
    """Cancel an eligible order. Only PROCESSING orders can be cancelled."""
    data = _load()
    order = data.get(order_id)
    if not order:
        return f"ORDER_NOT_FOUND:{order_id}"
    if order["status"] != "PROCESSING":
        return f"CANCEL_REJECTED:{order_id}:status={order['status']}"
    order["status"] = "CANCELLED"
    _save(data)
    return f"CANCELLED:{order_id}"

def refund_order(order_id: str) -> str:
    """Refund an order only after it has been cancelled."""
    data = _load()
    order = data.get(order_id)
    if not order:
        return f"ORDER_NOT_FOUND:{order_id}"
    if order["status"] != "CANCELLED":
        return f"REFUND_REJECTED:{order_id}:status={order['status']}"
    return f"REFUNDED:{order_id}:amount={order['amount']}"

def reset_data():
    source = {
        "ORD-1001":{"status":"PROCESSING","amount":120.0,"customer":"Alice"},
        "ORD-1002":{"status":"SHIPPED","amount":80.0,"customer":"Bob"},
        "ORD-1003":{"status":"PROCESSING","amount":250.0,"customer":"Carol"},
        "ORD-1004":{"status":"CANCELLED","amount":50.0,"customer":"Dave"}
    }
    _save(source)
