from app.graph.workflow import run_customer_support


def test_negative_complaint_triggers_human_handoff():
    state = run_customer_support('CUST001', 'This order is terrible and I want a manager now.')
    assert state['escalation_status'] is True
    assert 'manager' in state['handoff_summary'].lower() or 'human' in state['handoff_summary'].lower()


def test_repeated_complaint_triggers_human_handoff():
    state = run_customer_support('CUST001', 'This is the third time my order is late. I want to speak to a manager.')
    assert state['escalation_status'] is True


def test_explicit_human_request_triggers_human_handoff():
    state = run_customer_support('CUST001', 'I want to speak to a human support agent.')
    assert state['escalation_status'] is True


def test_human_handoff_summary_contains_required_sections():
    state = run_customer_support('CUST001', 'This is the third time my order is late. I want to speak to a manager.')
    summary = state['handoff_summary']
    assert 'issue' in summary.lower()
    assert 'history' in summary.lower()
    assert 'actions taken' in summary.lower()
    assert 'escalation reason' in summary.lower()
