import re

from app.database.db import find_most_relevant_order

NEGATIVE_WORDS = {
    "terrible", "awful", "angry", "hate", "frustrated", "unacceptable", "late", "delay", "terrible",
    "not arrived", "never arrived", "bad", "disappointed", "horrible", "broken"
}
REPEATED_PATTERNS = ["third time", "again", "again and again", "multiple times", "this is the third"]
HUMAN_PATTERNS = ["human", "speak to a human", "manager", "speak to a manager", "live agent", "supervisor"]


def extract_order_id(message: str):
    match = re.search(r"(?:order\s*#?|order\s*)(\d{5,})", message, re.IGNORECASE)
    if match:
        return int(match.group(1))
    numbers = re.findall(r"\d{5,}", message)
    return int(numbers[0]) if numbers else None


def triage_node(state):
    message = state["user_message"].lower()
    order_id = extract_order_id(state["user_message"])
    state["order_id"] = order_id
    if state["order_id"] is None:
        guess = find_most_relevant_order(state["customer_id"], state["user_message"])
        if guess:
            state["order_id"] = guess.get("order_id")
            if guess.get("item_id"):
                state["item_id"] = guess.get("item_id")
            if "return" in state["user_message"].lower() and state.get("item_id"):
                state["return_reason"] = "Customer requested a return."
    state["intent"] = "other"
    state["sentiment"] = "neutral"
    state["explicit_human_request"] = any(pattern in message for pattern in HUMAN_PATTERNS)
    state["repeated_complaint"] = any(pattern in message for pattern in REPEATED_PATTERNS)
    state["manager_request"] = "manager" in message or "supervisor" in message

    if "where is my order" in message or "track my order" in message or "status" in message:
        state["intent"] = "order_status"
    elif "ship" in message or "delivery" in message or "tracking" in message:
        state["intent"] = "shipment_tracking"
    elif "return" in message or "exchange" in message:
        state["intent"] = "return"
    elif "refund" in message:
        state["intent"] = "refund"
    elif "warranty" in message:
        state["intent"] = "warranty"
    elif "policy" in message:
        state["intent"] = "policy_question"
    elif "complaint" in message or "terrible" in message or "late" in message or "manager" in message:
        state["intent"] = "complaint"

    if any(word in message for word in NEGATIVE_WORDS):
        state["sentiment"] = "negative"

    state["escalation_status"] = (
        state["sentiment"] == "negative"
        or state["repeated_complaint"]
        or state["explicit_human_request"]
        or state["manager_request"]
    )
    state["issue"] = state["user_message"]
    state["history"] = [state["user_message"]]
    return state
