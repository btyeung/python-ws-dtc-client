import websocket
import json
import time

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Connection closed: {close_status_code} - {close_msg}")

def on_open(ws):
    print("Connection established")
    subscribe_message = {
        "action": "subscribe",
        "symbol": "NQH25_FUT_CME"
    }
    ws.send(json.dumps(subscribe_message))
    print(f"Sent subscription request: {subscribe_message}")

if __name__ == "__main__":
    print("Starting WebSocket client...")
    
    # WebSocket connection URL
    uri = "ws://localhost:8081/api/v1/marketdata"
    
    # Create WebSocket connection
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        uri,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        header={
            'Sec-WebSocket-Protocol': 'dtc',
            'Sec-WebSocket-Version': '8'
        }
    )
    
    # Run WebSocket client
    ws.run_forever(
        skip_utf8_validation=True,
        ping_interval=30,
        ping_timeout=10
    )
