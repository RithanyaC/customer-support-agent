import pytest

from app.database.db import get_order_by_id, get_customer_by_id


def test_valid_customer_can_access_own_order():
    order = get_order_by_id(10245, customer_id='CUST001')
    assert order is not None
    assert order['order_id'] == 10245
    assert order['customer_id'] == 'CUST001'


def test_customer_cannot_access_another_customers_order():
    order = get_order_by_id(10245, customer_id='CUST002')
    assert order is None or order.get('authorized') is False


def test_order_status_uses_get_order_mcp_tool():
    from app.mcp_server.server import get_order

    result = get_order(order_id=10245, customer_id='CUST001')
    assert result['authorized'] is True
    assert result['order_id'] == 10245
    assert 'status' in result


def test_shipment_query_uses_track_shipment_mcp_tool():
    from app.mcp_server.server import track_shipment

    result = track_shipment(order_id=10245, customer_id='CUST001')
    assert result['authorized'] is True
    assert 'shipment_status' in result or 'status' in result
