from app.rag.policy_rag import LocalPolicyRAG, build_policy_query


rag = LocalPolicyRAG()


def run_policy_agent(state):
    message = state["user_message"]
    intent = state.get("intent", "policy_question")
    results = rag.retrieve(build_policy_query(state), k=3)
    state["retrieved_policy_info"] = [
        f"{item['section']}: {item['text']}" for item in results
    ]
    if intent == "return":
        state["policy_eligible"] = "30 days" in " ".join([item["text"].lower() for item in results]).lower() and (
            "shoes" in message.lower() or "footwear" in message.lower() or "item" in message.lower()
        )
        if state["policy_eligible"]:
            state["final_response"] = (
                f"According to the Return Policy, the item is eligible for return within 30 days of delivery if it is in saleable condition. "
                f"Relevant policy: {results[0]['section']} - {results[0]['text'][:200]}"
            )
        else:
            policy_text = results[0]["text"] if results else "The policy does not support this request."
            state["final_response"] = (
                f"The return does not meet the current policy requirements. "
                f"According to the relevant policy: {policy_text[:220]}"
            )
            state["policy_eligible"] = False
        return state

    if intent == "refund":
        policy_text = results[0]["text"] if results else "No policy record found."
        state["final_response"] = (
            f"Refund timing is governed by policy. {policy_text[:220]}"
        )
        return state

    if intent == "policy_question":
        policy_text = results[0]["text"] if results else "No matching policy found."
        state["final_response"] = (
            f"I checked the local policy knowledge base. {policy_text[:220]}"
        )
        return state

    policy_text = results[0]["text"] if results else "No policy record found."
    state["final_response"] = policy_text[:220]
    return state
