from app.mcp_server.server import initiate_return
from app.rag.policy_rag import LocalPolicyRAG


def test_eligible_return_policy_agent_confirms_and_initiates_return():
    rag = LocalPolicyRAG()
    policy = rag.retrieve('return shoes within 30 days in good condition')
    assert policy

    result = initiate_return(order_id=10245, item_id='ITEM-0001', reason='Changed my mind', customer_id='CUST001')
    assert result['success'] is True or result['status'] == 'created'


def test_ineligible_return_policy_rejects_and_blocks_return():
    result = initiate_return(order_id=10245, item_id='ITEM-9999', reason='No reason', customer_id='CUST001')
    assert result['success'] is False
    assert 'eligible' in str(result.get('reason', '')).lower() or 'cannot' in str(result.get('reason', '')).lower()
