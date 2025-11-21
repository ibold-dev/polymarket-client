"""WebSocket client for Polymarket CLOB API real-time updates."""

from __future__ import annotations

import json
import threading
import time
from typing import Any, Callable, Optional, Union

try:
    import websocket
    from websocket import WebSocketApp
except ImportError:
    WebSocketApp = None  # type: ignore[assignment, misc]
    websocket = None  # type: ignore[assignment, misc]

from .client import PolymarketClientError
from .types import (
    WebSocketBookMessage,
    WebSocketLastTradePriceMessage,
    WebSocketMarketMessage,
    WebSocketOrderMessage,
    WebSocketPriceChangeMessage,
    WebSocketTickSizeChangeMessage,
    WebSocketTradeMessage,
    WebSocketUserMessage,
)


class WebSocketAuth:
    """WebSocket authentication credentials.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/wss-auth
    """
    
    api_key: str
    secret: str
    passphrase: str
    
    def __init__(self, api_key: str, secret: str, passphrase: str) -> None:
        """Initialize WebSocket authentication.
        
        Args:
            api_key: Polygon account's CLOB API key.
            secret: Polygon account's CLOB API secret.
            passphrase: Polygon account's CLOB API passphrase.
        """
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
    
    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary with apiKey, secret, and passphrase.
        """
        return {
            "apiKey": self.api_key,
            "secret": self.secret,
            "passphrase": self.passphrase,
        }


class PolymarketWebSocketClient:
    """WebSocket client for Polymarket CLOB API real-time updates.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/wss-overview
    
    Supports two channels:
    - user: Real-time updates for user's orders and trades (requires authentication)
    - market: Real-time updates for market order books (no authentication required)
    """
    
    MARKET_CHANNEL = "market"
    USER_CHANNEL = "user"
    
    def __init__(
        self,
        base_url: str = "wss://ws-subscriptions-clob.polymarket.com",
        auth: Optional[WebSocketAuth] = None,
        message_callback: Optional[Callable[[str, dict[str, Any]], None]] = None,
        user_message_callback: Optional[Callable[[WebSocketUserMessage], None]] = None,
        market_message_callback: Optional[Callable[[WebSocketMarketMessage], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        close_callback: Optional[Callable[[int, str], None]] = None,
        verbose: bool = False,
    ) -> None:
        """Initialize WebSocket client.
        
        Args:
            base_url: WebSocket base URL (default: wss://ws-subscriptions-clob.polymarket.com).
            auth: Authentication credentials (required for USER channel).
            message_callback: Callback function for received messages.
                Signature: callback(channel: str, message: dict[str, Any]) -> None
            error_callback: Callback function for errors.
                Signature: callback(error: Exception) -> None
            close_callback: Callback function for connection close.
                Signature: callback(status_code: int, message: str) -> None
            verbose: Enable verbose logging.
        """
        if WebSocketApp is None:
            raise PolymarketClientError(
                "websocket-client library is required. Install it with: pip install websocket-client"
            )
        
        self.base_url = base_url
        self.auth = auth
        self.message_callback = message_callback
        self.user_message_callback = user_message_callback
        self.market_message_callback = market_message_callback
        self.error_callback = error_callback
        self.close_callback = close_callback
        self.verbose = verbose
        
        self._market_ws: Optional[WebSocketApp] = None
        self._user_ws: Optional[WebSocketApp] = None
        self._ping_threads: dict[str, threading.Thread] = {}
        self._running = False
    
    def connect_market_channel(
        self,
        asset_ids: list[str],
    ) -> None:
        """Connect to the market channel for real-time order book updates.
        
        Reference: https://docs.polymarket.com/developers/CLOB/websocket/wss-overview
        
        The market channel provides real-time updates for order books.
        No authentication is required.
        
        Args:
            asset_ids: List of asset IDs (token IDs) to receive events for.
            
        Raises:
            PolymarketClientError: When connection fails.
        """
        if self._market_ws is not None:
            raise PolymarketClientError("Market channel is already connected. Close it first.")
        
        url = f"{self.base_url}/ws/{self.MARKET_CHANNEL}"
        
        def on_message(ws: WebSocketApp, message: str) -> None:
            try:
                data = json.loads(message)
                
                # Parse Market Channel messages into typed objects
                if isinstance(data, dict):
                    event_type = data.get("event_type", "")
                    
                    if event_type == "book":
                        # Parse as WebSocketBookMessage
                        try:
                            book_msg = WebSocketBookMessage.from_payload(data)
                            if self.market_message_callback:
                                self.market_message_callback(book_msg)
                            elif self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                            elif self.verbose:
                                print(f"[MARKET] Book: {book_msg.asset_id} - {len(book_msg.buys)} buys, {len(book_msg.sells)} sells")
                        except Exception as e:
                            if self.verbose:
                                print(f"[MARKET] Failed to parse book message: {e}")
                            if self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                    
                    elif event_type == "price_change":
                        # Parse as WebSocketPriceChangeMessage
                        try:
                            price_change_msg = WebSocketPriceChangeMessage.from_payload(data)
                            if self.market_message_callback:
                                self.market_message_callback(price_change_msg)
                            elif self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                            elif self.verbose:
                                print(f"[MARKET] Price Change: {price_change_msg.market} - {len(price_change_msg.price_changes)} changes")
                        except Exception as e:
                            if self.verbose:
                                print(f"[MARKET] Failed to parse price_change message: {e}")
                            if self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                    
                    elif event_type == "tick_size_change":
                        # Parse as WebSocketTickSizeChangeMessage
                        try:
                            tick_size_msg = WebSocketTickSizeChangeMessage.from_payload(data)
                            if self.market_message_callback:
                                self.market_message_callback(tick_size_msg)
                            elif self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                            elif self.verbose:
                                print(f"[MARKET] Tick Size Change: {tick_size_msg.asset_id} - {tick_size_msg.old_tick_size} → {tick_size_msg.new_tick_size}")
                        except Exception as e:
                            if self.verbose:
                                print(f"[MARKET] Failed to parse tick_size_change message: {e}")
                            if self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                    
                    elif event_type == "last_trade_price":
                        # Parse as WebSocketLastTradePriceMessage
                        try:
                            last_trade_msg = WebSocketLastTradePriceMessage.from_payload(data)
                            if self.market_message_callback:
                                self.market_message_callback(last_trade_msg)
                            elif self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                            elif self.verbose:
                                print(f"[MARKET] Last Trade: {last_trade_msg.asset_id} - {last_trade_msg.price} @ {last_trade_msg.size}")
                        except Exception as e:
                            if self.verbose:
                                print(f"[MARKET] Failed to parse last_trade_price message: {e}")
                            if self.message_callback:
                                self.message_callback(self.MARKET_CHANNEL, data)
                    
                    else:
                        # Unknown event type, use raw callback
                        if self.message_callback:
                            self.message_callback(self.MARKET_CHANNEL, data)
                        elif self.verbose:
                            print(f"[MARKET] Unknown event type: {message}")
                else:
                    # Non-dict message, use raw callback
                    if self.message_callback:
                        self.message_callback(self.MARKET_CHANNEL, data)
                    elif self.verbose:
                        print(f"[MARKET] {message}")
            except json.JSONDecodeError:
                if self.verbose:
                    print(f"[MARKET] Non-JSON message: {message}")
        
        def on_error(ws: WebSocketApp, error: Exception) -> None:
            if self.error_callback:
                self.error_callback(error)
            elif self.verbose:
                print(f"[MARKET] Error: {error}")
        
        def on_close(ws: WebSocketApp, close_status_code: int, close_msg: str) -> None:
            self._market_ws = None
            if self.MARKET_CHANNEL in self._ping_threads:
                self._ping_threads[self.MARKET_CHANNEL] = None
            if self.close_callback:
                self.close_callback(close_status_code, close_msg)
            elif self.verbose:
                print(f"[MARKET] Connection closed: {close_status_code} - {close_msg}")
        
        def on_open(ws: WebSocketApp) -> None:
            # Send subscription message
            subscription = {
                "assets_ids": asset_ids,
                "type": self.MARKET_CHANNEL.upper(),
            }
            ws.send(json.dumps(subscription))
            
            # Start ping thread
            def ping_loop() -> None:
                while self._market_ws is not None:
                    try:
                        ws.send("PING")
                        time.sleep(10)
                    except Exception:
                        break
            
            ping_thread = threading.Thread(target=ping_loop, daemon=True)
            ping_thread.start()
            self._ping_threads[self.MARKET_CHANNEL] = ping_thread
            
            if self.verbose:
                print(f"[MARKET] Connected and subscribed to {len(asset_ids)} assets")
        
        self._market_ws = WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        
        # Start connection in background thread
        def run_connection() -> None:
            self._market_ws.run_forever()
        
        thread = threading.Thread(target=run_connection, daemon=True)
        thread.start()
        self._running = True
    
    def connect_user_channel(
        self,
        markets: Optional[list[str]] = None,
    ) -> None:
        """Connect to the user channel for real-time order and trade updates.
        
        Reference: https://docs.polymarket.com/developers/CLOB/websocket/wss-overview
        
        The user channel provides real-time updates for user's orders and trades.
        Authentication is required.
        
        Args:
            markets: Optional list of market IDs (condition IDs) to filter events.
                If None, receives events for all markets.
            
        Raises:
            PolymarketClientError: When connection fails or auth is missing.
        """
        if self._user_ws is not None:
            raise PolymarketClientError("User channel is already connected. Close it first.")
        
        if self.auth is None:
            raise PolymarketClientError("Authentication is required for USER channel. Provide auth parameter.")
        
        url = f"{self.base_url}/ws/{self.USER_CHANNEL}"
        
        def on_message(ws: WebSocketApp, message: str) -> None:
            try:
                data = json.loads(message)
                
                # Parse User Channel messages into typed objects
                if isinstance(data, dict):
                    event_type = data.get("event_type", "")
                    
                    if event_type == "trade":
                        # Parse as WebSocketTradeMessage
                        try:
                            trade_msg = WebSocketTradeMessage.from_payload(data)
                            if self.user_message_callback:
                                self.user_message_callback(trade_msg)
                            elif self.message_callback:
                                self.message_callback(self.USER_CHANNEL, data)
                            elif self.verbose:
                                print(f"[USER] Trade: {trade_msg.id} - {trade_msg.status}")
                        except Exception as e:
                            if self.verbose:
                                print(f"[USER] Failed to parse trade message: {e}")
                            if self.message_callback:
                                self.message_callback(self.USER_CHANNEL, data)
                    
                    elif event_type == "order":
                        # Parse as WebSocketOrderMessage
                        try:
                            order_msg = WebSocketOrderMessage.from_payload(data)
                            if self.user_message_callback:
                                self.user_message_callback(order_msg)
                            elif self.message_callback:
                                self.message_callback(self.USER_CHANNEL, data)
                            elif self.verbose:
                                print(f"[USER] Order: {order_msg.id} - {order_msg.type}")
                        except Exception as e:
                            if self.verbose:
                                print(f"[USER] Failed to parse order message: {e}")
                            if self.message_callback:
                                self.message_callback(self.USER_CHANNEL, data)
                    
                    else:
                        # Unknown event type, use raw callback
                        if self.message_callback:
                            self.message_callback(self.USER_CHANNEL, data)
                        elif self.verbose:
                            print(f"[USER] Unknown event type: {message}")
                else:
                    # Non-dict message, use raw callback
                    if self.message_callback:
                        self.message_callback(self.USER_CHANNEL, data)
                    elif self.verbose:
                        print(f"[USER] {message}")
            except json.JSONDecodeError:
                if self.verbose:
                    print(f"[USER] Non-JSON message: {message}")
        
        def on_error(ws: WebSocketApp, error: Exception) -> None:
            if self.error_callback:
                self.error_callback(error)
            elif self.verbose:
                print(f"[USER] Error: {error}")
        
        def on_close(ws: WebSocketApp, close_status_code: int, close_msg: str) -> None:
            self._user_ws = None
            if self.USER_CHANNEL in self._ping_threads:
                self._ping_threads[self.USER_CHANNEL] = None
            if self.close_callback:
                self.close_callback(close_status_code, close_msg)
            elif self.verbose:
                print(f"[USER] Connection closed: {close_status_code} - {close_msg}")
        
        def on_open(ws: WebSocketApp) -> None:
            # Send subscription message with authentication
            subscription: dict[str, Any] = {
                "type": self.USER_CHANNEL.upper(),
                "auth": self.auth.to_dict(),
            }
            if markets is not None:
                subscription["markets"] = markets
            
            ws.send(json.dumps(subscription))
            
            # Start ping thread
            def ping_loop() -> None:
                while self._user_ws is not None:
                    try:
                        ws.send("PING")
                        time.sleep(10)
                    except Exception:
                        break
            
            ping_thread = threading.Thread(target=ping_loop, daemon=True)
            ping_thread.start()
            self._ping_threads[self.USER_CHANNEL] = ping_thread
            
            if self.verbose:
                market_count = len(markets) if markets else "all"
                print(f"[USER] Connected and subscribed to {market_count} markets")
        
        self._user_ws = WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        
        # Start connection in background thread
        def run_connection() -> None:
            self._user_ws.run_forever()
        
        thread = threading.Thread(target=run_connection, daemon=True)
        thread.start()
        self._running = True
    
    def close_market_channel(self) -> None:
        """Close the market channel connection."""
        if self._market_ws is not None:
            self._market_ws.close()
            self._market_ws = None
    
    def close_user_channel(self) -> None:
        """Close the user channel connection."""
        if self._user_ws is not None:
            self._user_ws.close()
            self._user_ws = None
    
    def close_all(self) -> None:
        """Close all WebSocket connections."""
        self.close_market_channel()
        self.close_user_channel()
        self._running = False
    
    def is_market_connected(self) -> bool:
        """Check if market channel is connected.
        
        Returns:
            True if market channel is connected, False otherwise.
        """
        return self._market_ws is not None
    
    def is_user_connected(self) -> bool:
        """Check if user channel is connected.
        
        Returns:
            True if user channel is connected, False otherwise.
        """
        return self._user_ws is not None

