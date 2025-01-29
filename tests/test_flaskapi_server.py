import pytest
import requests
import time
import threading
import logging
from unittest.mock import MagicMock
from rest.rest_server import RESTServer
from rest.api import API

TEST_PORT = 8081
BASE_URL = f"http://localhost:{TEST_PORT}{API.API_PREFIX}"

class MockDTCClient:
    def __init__(self, handler):
        self.rest_server = None
        
    def request_response(self, request_id, request):
        # Return empty list for all requests in test
        return []

@pytest.fixture(scope="session")
def server():
    # Use mock DTC client for testing
    client = MockDTCClient(lambda x: None)
    server = RESTServer()
    
    # Start server in a separate thread
    thread = threading.Thread(
        target=server.start,
        args=(client, TEST_PORT),
        daemon=True
    )
    thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield server
    
    # Cleanup not needed as thread is daemon

def test_account_balance(server):
    response = requests.get(f"{BASE_URL}{API.ACCOUNT_BALANCE}")
    assert response.status_code == 200

def test_current_positions(server):
    response = requests.get(f"{BASE_URL}{API.CURRENT_POSITIONS}")
    assert response.status_code == 200

def test_exchange_list(server):
    response = requests.get(f"{BASE_URL}{API.EXCHANGE_LIST}")
    assert response.status_code == 200

def test_historical_account_balances(server):
    params = {
        'TradeAccount': 'test_account',
        'StartDateTime': '2024-01-01'
    }
    response = requests.get(f"{BASE_URL}{API.HISTORICAL_ACCOUNT_BALANCES}", params=params)
    assert response.status_code == 200

def test_historical_order_fills(server):
    params = {
        'TradeAccount': 'test_account',
        'NumberOfDays': 7
    }
    response = requests.get(f"{BASE_URL}{API.HISTORICAL_ORDER_FILLS}", params=params)
    assert response.status_code == 200

def test_security_definition(server):
    params = {
        'Symbol': 'AAPL',
        'Exchange': 'NASDAQ'
    }
    response = requests.get(f"{BASE_URL}{API.SECURITY_DEFINITION}", params=params)
    assert response.status_code == 200

def test_trade_accounts(server):
    response = requests.get(f"{BASE_URL}{API.TRADE_ACCOUNTS}")
    assert response.status_code == 200

# Test invalid requests
def test_historical_order_fills_missing_required_params(server):
    response = requests.get(f"{BASE_URL}{API.HISTORICAL_ORDER_FILLS}")
    assert response.status_code == 400  # Flask validation error

def test_security_definition_missing_required_params(server):
    response = requests.get(f"{BASE_URL}{API.SECURITY_DEFINITION}")
    assert response.status_code == 400  # Flask validation error

def test_nonexistent_endpoint(server):
    response = requests.get(f"{BASE_URL}/nonexistent")
    assert response.status_code == 404