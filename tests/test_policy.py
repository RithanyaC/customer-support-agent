from app.graph.workflow import run_customer_support


def test_refund_follows_policy():
    state = run_customer_support('CUST001', "My refund still hasn't arrived after 10 days.")
    text = state['final_response'].lower()
    assert 'policy' in text or 'refund' in text or 'next step' in text or 'delay' in text


def test_no_cross_customer_data_leakage():
    state = run_customer_support('CUST002', 'Where is my order #10245?')
    final = state['final_response'].lower()
    assert 'cannot be accessed' in final or 'order cannot be accessed' in final
    assert '10245' in final or 'cannot' in final
