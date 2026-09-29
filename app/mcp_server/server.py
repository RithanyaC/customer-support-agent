import json
from typing import Optional

from mcp.server.fastmcp import FastMCP

from app.database.db import create_return_request, get_order_by_id, get_refund_details, get_shipment, get_return_eligibility

mcp = FastMCP("customer_support_mcp")


@mcp.tool()
def get_order(order_id: int, customer_id: Optional[str] = None) -> dict:
    """Return order details only when the customer owns the order."""
    result = get_order_by_id(order_id, customer_id=customer_id)
    if result is None:
        return {"authorized": False, "reason": "Order not found."}
    if result.get("authorized") is False:
        return {"authorized": False, "reason": "This order cannot be accessed."}
    return result


@mcp.tool()
def track_shipment(order_id: int, customer_id: Optional[str] = None) -> dict:
    """Return shipment details only when the customer owns the order."""
    allowed = get_order_by_id(order_id, customer_id=customer_id)
    if allowed is None or allowed.get("authorized") is False:
        return {"authorized": False, "reason": "This order cannot be accessed."}
    shipment = get_shipment(order_id)
    if shipment is None:
        return {"authorized": True, "order_id": order_id, "shipment_status": "not_found", "reason": "Shipment information is not available."}
    return {
        "authorized": True,
        "order_id": order_id,
        "shipment_status": shipment.get("shipment_status"),
        "current_location": shipment.get("current_location"),
        "estimated_delivery": shipment.get("estimated_delivery"),
        "carrier": shipment.get("carrier"),
        "tracking_number": shipment.get("tracking_number"),
    }


@mcp.tool()
def initiate_return(order_id: int, item_id: str, reason: str, customer_id: str) -> dict:
    """Create a return request only after checking eligibility."""
    return_result = create_return_request(order_id, item_id, reason, customer_id)
    if return_result.get("success"):
        refund_info = get_refund_details(order_id)
        return {
            "success": True,
            "status": "created",
            "order_id": order_id,
            "item_id": item_id,
            "reason": reason,
            "refund": refund_info,
        }
    eligible, _ = get_return_eligibility(order_id, item_id)
    if eligible:
        return {"success": False, "reason": "Return could not be created for an unknown reason."}
    return {
        "success": False,
        "reason": return_result.get("reason") or "This item is not eligible for return.",
    }


if __name__ == "__main__":
    mcp.run() 
