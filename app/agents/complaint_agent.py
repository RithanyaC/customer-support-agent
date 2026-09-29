from app.database.db import get_order_by_id


def run_complaint_agent(state):
    customer_id = state["customer_id"]
    order_id = state.get("order_id")
    order = get_order_by_id(order_id, customer_id=customer_id) if order_id else None
    if order and order.get("authorized"):
        order_status = order.get("status")
    else:
        order_status = "unverified"

    state["final_response"] = (
        "I understand this is frustrating, and I appreciate you bringing it to our attention. "
        f"I can see the issue is related to order #{order_id if order_id else 'N/A'} and the current status is {order_status}. "
        "I am not able to promise a refund or replacement outside of policy, but I can help document the issue and escalate it for review."
    )
    state["complaint_context"] = state["user_message"]
    state["actions_taken"] = state.get("actions_taken", []) + ["Acknowledged the complaint and reviewed the order context."]
    return state
