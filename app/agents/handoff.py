def run_handoff(state):
    issue = state.get("issue", state.get("user_message", "Customer concern"))
    customer_id = state.get("customer_id", "UNKNOWN")
    order_id = state.get("order_id")
    history = state.get("history", [])
    actions = state.get("actions_taken", [])
    reasons = []
    if state.get("repeated_complaint"):
        reasons.append("Repeated complaint.")
    if state.get("manager_request"):
        reasons.append("Explicit manager request.")
    if state.get("explicit_human_request"):
        reasons.append("Explicit human request.")
    if state.get("sentiment") == "negative":
        reasons.append("Negative sentiment.")
    if not reasons:
        reasons.append("Escalation required by policy and support workflow.")

    summary = (
        "HUMAN HANDOFF\n\n"
        "Issue:\n"
        f"{issue}\n\n"
        "Customer:\n"
        f"{customer_id}\n\n"
        "Order:\n"
        f"{order_id if order_id else 'N/A'}\n\n"
        "History:\n"
        + ("\n".join(f"- {entry}" for entry in history) if history else "- No prior history recorded.")
        + "\n\nActions Taken:\n"
        + ("\n".join(f"- {entry}" for entry in actions) if actions else "- No automated actions taken.")
        + "\n\nEscalation Reason:\n"
        + ("\n".join(f"- {reason}" for reason in reasons))
        + "\n"
    )
    state["handoff_summary"] = summary
    state["final_response"] = (
        "I’m transferring this to a human support agent for review. "
        "A structured summary has been prepared so the next team member can continue without repeating your information."
    )
    return state
