from app.database.db import get_order_by_id, get_refund_details
from app.mcp_server.server import get_order, initiate_return, track_shipment


def run_order_agent(state):
    intent = state.get("intent")
    customer_id = state["customer_id"]
    order_id = state.get("order_id")
    actions = state.setdefault("actions_taken", [])

    if intent == "order_status":
        order = get_order(order_id=order_id, customer_id=customer_id)
        state["order_information"] = order
        if order.get("authorized") is False:
            state["final_response"] = "This order cannot be accessed from this customer account."
        else:
            state["final_response"] = (
                f"Order #{order['order_id']} is currently {order['status']}. "
                f"It was placed on {order['order_date']} and totals {order['total_amount']} {order['currency']}."
            )
        actions.append("Checked order status using the secure order tool.")
        return state

    if intent == "shipment_tracking":
        order = get_order(order_id=order_id, customer_id=customer_id)
        state["order_information"] = order
        shipment = track_shipment(order_id=order_id, customer_id=customer_id)
        state["shipment_information"] = shipment
        if order.get("authorized") is False:
            state["final_response"] = "This shipment cannot be accessed from this customer account."
        else:
            state["final_response"] = (
                f"Shipment for order #{order_id} is {shipment.get('shipment_status', 'unknown')}. "
                f"Current location: {shipment.get('current_location', 'not available')}. "
                f"Estimated delivery: {shipment.get('estimated_delivery', 'not available')}."
            )
        actions.append("Checked shipment tracking using the secure shipment tool.")
        return state

    if intent == "return":
        if state.get("policy_eligible") is True:
            result = initiate_return(
                order_id=order_id,
                item_id=state.get("item_id", "ITEM-0001"),
                reason=state.get("return_reason", "Customer requested return."),
                customer_id=customer_id,
            )
            state["order_information"] = get_order(order_id=order_id, customer_id=customer_id)
            if result.get("success"):
                state["final_response"] = (
                    f"Your return request for order #{order_id} has been created successfully. "
                    f"Return status: {result.get('status')}."
                )
            else:
                state["final_response"] = result.get("reason", "This return cannot be processed right now.")
            actions.append("Executed return after policy eligibility check.")
            return state
        state["final_response"] = "This return cannot proceed because it does not meet the policy requirements."
        return state

    if intent == "refund":
        order = get_order(order_id=order_id, customer_id=customer_id)
        state["order_information"] = order
        refund = get_refund_details(order_id) if order_id else None
        if order.get("authorized") is False:
            state["final_response"] = "This refund information cannot be accessed from this customer account."
        elif refund:
            state["final_response"] = (
                f"The refund for order #{order_id} is currently {refund.get('status')} and was processed on {refund.get('processed_on')}. "
                f"The expected date is {refund.get('expected_date')}."
            )
        else:
            state["final_response"] = (
                f"I checked the order and refund information for order #{order_id}. Based on the current policy, a refund is not yet available or has not been issued."
            )
        actions.append("Verified refund status and compared it to the policy timeline.")
        return state

    state["final_response"] = "I can help with order status, shipments, returns, or policy questions."
    return state
