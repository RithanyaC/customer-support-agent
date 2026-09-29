from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class CustomerSupportState(TypedDict):
    customer_id: str
    user_message: str
    order_id: Optional[int]
    intent: str
    sentiment: str
    escalation_status: bool
    policy_eligible: Optional[bool]
    actions_taken: List[str]
    retrieved_policy_info: List[str]
    order_information: Optional[Dict[str, Any]]
    shipment_information: Optional[Dict[str, Any]]
    final_response: str
    handoff_summary: str
    complaint_context: Optional[str]
    issue: str
    history: List[str]
    explicit_human_request: bool
    repeated_complaint: bool
    manager_request: bool
