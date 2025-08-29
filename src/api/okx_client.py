import base64
import datetime
import hmac
import json
import requests
import websocket
import threading
import time
from typing import Dict, List, Optional, Union
import urllib.parse

from src.config import (
    OKX_API_KEY,
    OKX_API_SECRET,
    OKX_API_PASSPHRASE
)
from src.utils.error_handler import error_handler, handle_errors

class OKXClient:
    """
    OKX API Client for both REST and WebSocket connections
    """
    # API Base URLs
    REST_API_URL = "https://www.okx.com"
    PUBLIC_WS_URL = "wss://ws.okx.com:8443/ws/v5/public"
    PRIVATE_WS_URL = "wss://ws.okx.com:8443/ws/v5/private"
    
    def __init__(self):
        self.api_key = OKX_API_KEY
        self.api_secret = OKX_API_SECRET
        self.passphrase = OKX_API_PASSPHRASE
        self.ws_public = None
        self.ws_private = None
        self.ws_callbacks = {}
        self.running = False
        self.connection_status = {
            'public_ws': False,
            'private_ws': False,
            'rest_api': False,
            'last_check': time.time()
        }
        
        # Register recovery strategies
        error_handler.register_recovery_strategy("ConnectionError", self._handle_connection_error)
        error_handler.register_recovery_strategy("TimeoutError", self._handle_timeout_error)
        error_handler.register_recovery_strategy("WebSocketConnectionClosedException", self._handle_ws_disconnect)
        
    def _get_timestamp(self):
        """Get ISO timestamp for API requests"""
        return datetime.datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    
    def _sign(self, timestamp, method, request_path, body=''):
        """Generate signature for API requests"""
        if not body:
            body = ''
            
        if isinstance(body, dict):
            body = json.dumps(body)
            
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf-8'),
            bytes(message, encoding='utf-8'),
            digestmod='sha256'
        )
        d = mac.digest()
        return base64.b64encode(d).decode('utf-8')
    
    def _build_headers(self, method, request_path, body=''):
        """Build headers for API requests"""
        timestamp = self._get_timestamp()
        sign = self._sign(timestamp, method, request_path, body)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    @handle_errors("OKX API request")
    def _request(self, method, request_path, params=None):
        """Make a REST API request"""
        url = self.REST_API_URL + request_path
        
        # Handle query parameters for GET requests
        if method == 'GET' and params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
            headers = self._build_headers(method, f"{request_path}?{query_string}")
            response = requests.get(url, headers=headers, timeout=10)
        else:
            # For POST, PUT, DELETE requests
            headers = self._build_headers(method, request_path, params)
            if method == 'POST':
                response = requests.post(url, headers=headers, json=params, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=params, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        # Update connection status
        self.connection_status['rest_api'] = True
        self.connection_status['last_check'] = time.time()
        
        return response.json()
    
    # REST API Methods
    @handle_errors("get_account_balance")
    def get_account_balance(self):
        """Get account balance"""
        return self._request('GET', '/api/v5/account/balance')
    
    @handle_errors("get_positions")
    def get_positions(self):
        """Get current positions"""
        return self._request('GET', '/api/v5/account/positions')
    
    @handle_errors("get_ticker")
    def get_ticker(self, instId):
        """Get ticker information for an instrument"""
        params = {'instId': instId}
        return self._request('GET', '/api/v5/market/ticker', params)
    
    @handle_errors("get_orderbook")
    def get_orderbook(self, instId, sz='20'):
        """Get orderbook for an instrument"""
        params = {'instId': instId, 'sz': sz}
        return self._request('GET', '/api/v5/market/books', params)
    
    @handle_errors("place_order")
    def place_order(self, instId, tdMode, side, ordType, sz, px=None):
        """Place a new order"""
        params = {
            'instId': instId,
            'tdMode': tdMode,  # 'cash', 'isolated', 'cross'
            'side': side,      # 'buy', 'sell'
            'ordType': ordType, # 'market', 'limit', 'post_only', 'fok', 'ioc'
            'sz': sz           # Size
        }
        
        if px and ordType != 'market':
            params['px'] = px  # Price, required for non-market orders
            
        return self._request('POST', '/api/v5/trade/order', params)
    
    @handle_errors("cancel_order")
    def cancel_order(self, instId, ordId=None, clOrdId=None):
        """Cancel an existing order"""
        params = {'instId': instId}
        
        if ordId:
            params['ordId'] = ordId
        elif clOrdId:
            params['clOrdId'] = clOrdId
        else:
            raise ValueError("Either ordId or clOrdId must be provided")
            
        return self._request('POST', '/api/v5/trade/cancel-order', params)
    
    @handle_errors("get_order_history")
    def get_order_history(self, instType, state='filled', limit='100'):
        """Get order history"""
        params = {
            'instType': instType,  # 'SPOT', 'MARGIN', 'SWAP', 'FUTURES', 'OPTION'
            'state': state,        # 'live', 'filled', 'canceled'
            'limit': limit
        }
        return self._request('GET', '/api/v5/trade/orders-history', params)
    
    # WebSocket Methods
    def _on_ws_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            
            # Handle ping messages
            if 'event' in data and data['event'] == 'ping':
                pong_msg = json.dumps({"event": "pong"})
                ws.send(pong_msg)
                return
                
            # Handle subscription responses
            if 'event' in data and data['event'] == 'subscribe':
                print(f"Successfully subscribed to {data.get('arg', {}).get('channel')}")
                return
                
            # Handle data messages
            if 'data' in data:
                channel = data.get('arg', {}).get('channel')
                if channel in self.ws_callbacks:
                    self.ws_callbacks[channel](data['data'])
        except Exception as e:
            error_handler.handle_error(e, "WebSocket message processing")
    
    def _on_ws_error(self, ws, error):
        """Handle WebSocket errors"""
        error_handler.handle_error(error, "WebSocket connection")
        
        # Update connection status
        if ws == self.ws_public:
            self.connection_status['public_ws'] = False
        elif ws == self.ws_private:
            self.connection_status['private_ws'] = False
    
    def _on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        print(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        
        # Update connection status
        if ws == self.ws_public:
            self.connection_status['public_ws'] = False
        elif ws == self.ws_private:
            self.connection_status['private_ws'] = False
        
        # Attempt to reconnect if we're still running
        if self.running:
            print("Attempting to reconnect in 5 seconds...")
            time.sleep(5)
            self._connect_websockets()
    
    def _on_ws_open(self, ws):
        """Handle WebSocket connection open"""
        print("WebSocket connection established")
        
        # Update connection status
        if ws == self.ws_public:
            self.connection_status['public_ws'] = True
        elif ws == self.ws_private:
            self.connection_status['private_ws'] = True
        
        # If this is the private WebSocket, we need to login
        if ws == self.ws_private:
            timestamp = self._get_timestamp()
            sign = self._sign(timestamp, 'GET', '/users/self/verify')
            
            login_msg = {
                "op": "login",
                "args": [{
                    "apiKey": self.api_key,
                    "passphrase": self.passphrase,
                    "timestamp": timestamp,
                    "sign": sign
                }]
            }
            ws.send(json.dumps(login_msg))
    
    @handle_errors("connect_websockets")
    def _connect_websockets(self):
        """Connect to WebSockets"""
        # Connect to public WebSocket
        self.ws_public = websocket.WebSocketApp(
            self.PUBLIC_WS_URL,
            on_open=self._on_ws_open,
            on_message=self._on_ws_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close
        )
        
        # Connect to private WebSocket
        self.ws_private = websocket.WebSocketApp(
            self.PRIVATE_WS_URL,
            on_open=self._on_ws_open,
            on_message=self._on_ws_message,
            on_error=self._on_ws_error,
            on_close=self._on_ws_close
        )
        
        # Start WebSocket threads
        threading.Thread(target=self.ws_public.run_forever, kwargs={'ping_interval': 30}).start()
        threading.Thread(target=self.ws_private.run_forever, kwargs={'ping_interval': 30}).start()
    
    def start_websockets(self):
        """Start WebSocket connections"""
        if not self.running:
            self.running = True
            self._connect_websockets()
            
            # Start connection monitor
            threading.Thread(target=self._monitor_connections, daemon=True).start()
    
    def stop_websockets(self):
        """Stop WebSocket connections"""
        self.running = False
        if self.ws_public:
            self.ws_public.close()
        if self.ws_private:
            self.ws_private.close()
    
    @handle_errors("subscribe_public")
    def subscribe_public(self, channel, instId, callback=None):
        """Subscribe to a public channel"""
        if not self.ws_public:
            raise Exception("Public WebSocket not connected. Call start_websockets() first.")
            
        sub_msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": channel,
                    "instId": instId
                }
            ]
        }
        
        if callback:
            self.ws_callbacks[channel] = callback
            
        self.ws_public.send(json.dumps(sub_msg))
    
    @handle_errors("subscribe_private")
    def subscribe_private(self, channel, callback=None):
        """Subscribe to a private channel"""
        if not self.ws_private:
            raise Exception("Private WebSocket not connected. Call start_websockets() first.")
            
        sub_msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": channel
                }
            ]
        }
        
        if callback:
            self.ws_callbacks[channel] = callback
            
        self.ws_private.send(json.dumps(sub_msg))
    
    def _monitor_connections(self):
        """Monitor connection status and reconnect if needed"""
        while self.running:
            try:
                # Check if connections are active
                current_time = time.time()
                if current_time - self.connection_status['last_check'] > 60:  # Check every minute
                    # Test REST API connection
                    try:
                        self._request('GET', '/api/v5/public/time')
                        self.connection_status['rest_api'] = True
                    except Exception:
                        self.connection_status['rest_api'] = False
                    
                    # Check WebSocket connections
                    if not self.connection_status['public_ws'] or not self.connection_status['private_ws']:
                        print("WebSocket connection lost. Reconnecting...")
                        self._connect_websockets()
                    
                    self.connection_status['last_check'] = current_time
                
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                error_handler.handle_error(e, "connection_monitor")
    
    # Recovery strategies
    def _handle_connection_error(self, error, context):
        """Handle connection errors"""
        print(f"Connection error in {context}: {error}. Attempting to reconnect...")
        time.sleep(5)  # Wait before reconnecting
        
        if "WebSocket" in context:
            self._connect_websockets()
        else:
            # For REST API, we'll retry on next request
            pass
    
    def _handle_timeout_error(self, error, context):
        """Handle timeout errors"""
        print(f"Timeout error in {context}: {error}. Will retry with increased timeout.")
        # The retry will be handled by the error_handler decorator
    
    def _handle_ws_disconnect(self, error, context):
        """Handle WebSocket disconnection"""
        print(f"WebSocket disconnected in {context}: {error}. Reconnecting...")
        self._connect_websockets()
    
    def get_connection_status(self):
        """Get the current connection status"""
        return {
            'public_ws': "Connected" if self.connection_status['public_ws'] else "Disconnected",
            'private_ws': "Connected" if self.connection_status['private_ws'] else "Disconnected",
            'rest_api': "Connected" if self.connection_status['rest_api'] else "Disconnected",
            'last_check': datetime.datetime.fromtimestamp(self.connection_status['last_check']).strftime('%Y-%m-%d %H:%M:%S')
        }