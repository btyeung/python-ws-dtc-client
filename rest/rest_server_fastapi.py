import json
import logging
from threading import Lock

from fastapi import FastAPI, WebSocket, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from dtc.message_types.account_balance_request import AccountBalanceRequest
from dtc.message_types.current_positions_request import CurrentPositionsRequest
from dtc.message_types.exchange_list_request import ExchangeListRequest
from dtc.message_types.historical_account_balances_request import HistoricalAccountBalancesRequest
from dtc.message_types.historical_order_fills_request import HistoricalOrderFillsRequest
from dtc.message_types.historical_price_data_request import HistoricalPriceDataRequest
from dtc.message_types.security_definition_for_symbol_request import SecurityDefinitionForSymbolRequest
from dtc.message_types.trade_accounts_request import TradeAccountsRequest
from dtc_client.enums import SubscriptionDataType
from lib.error import MethodNotAllowedError, InvalidArgumentsError, RequestTimeoutError
from rest.api import API

app = FastAPI(title="DTC REST Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dtc_client = None
rest_server = None

# Constants
TRADE_ACCOUNT = 'TradeAccount'
NUMBER_OF_DAYS = 'NumberOfDays'
START_DATE_TIME = 'StartDateTime'
END_DATE_TIME = 'EndDateTime'
SYMBOL = 'Symbol'
EXCHANGE = 'Exchange'
RECORD_INTERVAL = 'RecordInterval'
MAX_DAYS_TO_RETURN = 'MaxDaysToReturn'

# Subscription keys
_ACTION = 'action'
_SUBSCRIBE = 'subscribe'
_UNSUBSCRIBE = 'unsubscribe'
_SYMBOL = 'symbol'
_SUCCESS = 'success'

async def handle_websocket(websocket: WebSocket, subscription_type: SubscriptionDataType):
    await websocket.accept()
    logging.info('ws connected')
    
    try:
        while True:
            try:
                data = await websocket.receive_json()
                action = data.get(_ACTION)

                if action in [_SUBSCRIBE, _UNSUBSCRIBE]:
                    symbol = data.get(_SYMBOL)
                    success = False
                    if action == _SUBSCRIBE:
                        if dtc_client.data_subscribe(websocket, symbol, subscription_type):
                            success = True
                    else:  # action == _UNSUBSCRIBE
                        if dtc_client.data_unsubscribe(websocket, symbol, subscription_type):
                            success = True

                    message = {_ACTION: action, _SYMBOL: symbol, _SUCCESS: success}
                    await websocket.send_json(message)
                else:
                    await websocket.send_json(
                        {'error': 'unknown_action', 'details': 'action=subscribe|unsubscribe, symbol=symbol'})
            except Exception as e:
                logging.debug(e)
                break
    finally:
        dtc_client.data_unsubscribe_all_for_socket(websocket)

@app.websocket(API.API_PREFIX + API.MARKET_DATA)
async def market_data(websocket: WebSocket):
    await handle_websocket(websocket, SubscriptionDataType.MARKET_DATA)

@app.websocket(API.API_PREFIX + API.MARKET_DEPTH)
async def market_depth(websocket: WebSocket):
    await handle_websocket(websocket, SubscriptionDataType.MARKET_DEPTH)

@app.exception_handler(InvalidArgumentsError)
async def invalid_arguments_handler(request, exc):
    logging.error(exc)
    return JSONResponse(
        status_code=400,
        content={
            'success': False,
            'error': {
                'type': 'InvalidArgumentsError',
                'message': str(exc),
                'status': 400
            }
        }
    )

@app.exception_handler(MethodNotAllowedError)
async def method_not_allowed_handler(request, exc):
    logging.error(exc)
    return JSONResponse(
        status_code=405,
        content={
            'success': False,
            'error': {
                'type': 'MethodNotAllowedError',
                'message': 'The request method is not allowed.',
                'status': 405
            }
        }
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    logging.error(exc)
    return JSONResponse(
        status_code=404,
        content={
            'success': False,
            'error': {
                'type': 'NotFoundError',
                'message': str(exc),
                'status': 404
            }
        }
    )

@app.exception_handler(RequestTimeoutError)
async def request_timeout_handler(request, exc):
    logging.error(exc)
    return JSONResponse(
        status_code=408,
        content={
            'success': False,
            'error': {
                'type': 'RequestTimeoutError',
                'message': 'The request timed out.',
                'status': 408
            }
        }
    )

@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    logging.error(exc)
    return JSONResponse(
        status_code=500,
        content={
            'success': False,
            'error': {
                'type': 'UnexpectedError',
                'message': 'An unexpected error has occurred.',
                'status': 500
            }
        }
    )

@app.get(API.API_PREFIX + API.ACCOUNT_BALANCE)
async def account_balance():
    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        AccountBalanceRequest(
            request_id=request_id
        )
    )
    return response

@app.get(API.API_PREFIX + API.CURRENT_POSITIONS)
async def current_positions():
    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        CurrentPositionsRequest(
            request_id=request_id
        )
    )
    return response

@app.get(API.API_PREFIX + API.EXCHANGE_LIST)
async def exchange_list():
    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        ExchangeListRequest(
            request_id=request_id
        )
    )
    return response

@app.get(API.API_PREFIX + API.HISTORICAL_ACCOUNT_BALANCES)
async def historical_account_balance(
    trade_account: str = Query(..., alias=TRADE_ACCOUNT),
    start_date_time: str | None = Query(None, alias=START_DATE_TIME)
):
    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        HistoricalAccountBalancesRequest(
            request_id=request_id,
            trade_account=trade_account,
            start_date_time=start_date_time
        )
    )
    return response

@app.get(API.API_PREFIX + API.HISTORICAL_ORDER_FILLS)
async def historical_order_fills(
    trade_account: str = Query(..., alias=TRADE_ACCOUNT),
    number_of_days: int | None = Query(None, alias=NUMBER_OF_DAYS),
    start_date_time: str | None = Query(None, alias=START_DATE_TIME)
):
    if not number_of_days and not start_date_time:
        raise InvalidArgumentsError(f'Either {NUMBER_OF_DAYS} or {START_DATE_TIME} must be specified')

    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        HistoricalOrderFillsRequest(
            request_id=request_id,
            trade_account=trade_account,
            number_of_days=number_of_days,
            start_date_time=start_date_time
        )
    )
    return response

@app.get(API.API_PREFIX + API.SECURITY_DEFINITION)
async def security_definition(
    symbol: str = Query(..., alias=SYMBOL),
    exchange: str | None = Query(None, alias=EXCHANGE)
):
    logging.info('Security definition request')
    logging.info('dtc_client: %s' % dtc_client)

    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        SecurityDefinitionForSymbolRequest(
            request_id=request_id,
            symbol=symbol,
            exchange=exchange
        )
    )
    return response

@app.get(API.API_PREFIX + API.TRADE_ACCOUNTS)
async def trade_accounts():
    request_id = rest_server.get_next_request_id()
    response = dtc_client.request_response(
        request_id,
        TradeAccountsRequest(
            request_id=request_id,
        )
    )
    return response

class RESTServer:
    def __init__(self):
        global rest_server
        rest_server = self
        self.request_id = 0
        self.request_id_lock = Lock()

    def get_next_request_id(self):
        self.request_id_lock.acquire()
        self.request_id += 1
        request_id = self.request_id
        self.request_id_lock.release()
        return request_id

    def start(self, _dtc_client, _rest_port):
        logging.info('Starting REST Server')
        global dtc_client
        dtc_client = _dtc_client

        uvicorn.run(app, host="0.0.0.0", port=_rest_port)