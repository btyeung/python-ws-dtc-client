import logging
import traceback

from dtc_client.dtc_client import DTCClient
from dtc.message_types.market_data_request import MarketDataRequest
from dtc.enums.request_action_enum import RequestActionEnum
from dtc.message_types.market_data_snapshot import MarketDataSnapshot
from dtc.message_types.order_update import OrderUpdate
from lib.symbol_util import get_symbol_id
from lib.util import Util, CONSOLE_LOGGING

_NAME = 'name'
_ID = 'ID'


if __name__ == '__main__':
    # Symbols to monitor
    SYMBOL_LIST = [
        {_NAME: "ESH25_FUT_CME"},
        #{_NAME: "CLH25_FUT_NYMEX"},
        #{_NAME: "NQH25_FUT_CME"},
    ]
    # Generate symbol IDs
    for ix, symbol in enumerate(SYMBOL_LIST):
        SYMBOL_LIST[ix][_ID] = get_symbol_id(symbol[_NAME])

    class ExampleDTCClient(DTCClient):
        def __init__(self):
            super().__init__(on_message_handler=self.on_message_thread, post_login_thread=self.post_login_thread)

        def post_login_thread(self):
            for ix, symbol in enumerate(SYMBOL_LIST):
                self.send(
                    MarketDataRequest(
                        request_action=RequestActionEnum.SUBSCRIBE,
                        symbol_id=SYMBOL_LIST[ix][_ID],
                        symbol=symbol[_NAME]))

        def on_message_thread(self, message):
            if isinstance(message, MarketDataSnapshot):
                marketDataSnapshot = MarketDataSnapshot()
                # do something with market data
                #marketDepthSnapshot = MarketDepthSnapshot()

                #TODO: post this to redis, or stream this somewhere


    try:
        logger = Util.setup_logging("DTC_Client", console=CONSOLE_LOGGING)
        dtc_client = ExampleDTCClient()
        dtc_client.start()
    except BaseException as e:
        logging.error(e.__str__())
        logging.debug(traceback.format_exc())
