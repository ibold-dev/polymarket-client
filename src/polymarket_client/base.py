"""Base interfaces and types for prediction market clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class BaseOrderBookLevel:
    """Base order book level data structure."""

    price: float
    quantity: float


@dataclass
class BaseOrderBook:
    """Base order book data structure."""

    bids: list[BaseOrderBookLevel]
    asks: list[BaseOrderBookLevel]
    timestamp: datetime


@dataclass
class BaseMarket:
    """Base market data structure.

    All market-specific market classes should inherit from this or match its structure.
    """

    id: str
    question: str | None  # API can return null for question
    active: bool
    closed: bool
    volume: float
    liquidity: float

    @staticmethod
    def from_payload(payload: Any) -> BaseMarket:
        """Parse market data from API payload.

        Args:
            payload: Raw API response (format depends on market).

        Returns:
            BaseMarket: Parsed market data.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement from_payload")


@dataclass
class BaseOrder:
    """Base order data structure."""

    order_id: str
    token_id: str
    side: str  # "BUY" or "SELL"
    price: float
    size: float
    filled: float
    status: str
    created_at: datetime | None = None

    @staticmethod
    def from_payload(payload: Any) -> BaseOrder:
        """Parse order data from API payload.

        Args:
            payload: Raw API response.

        Returns:
            BaseOrder: Parsed order data.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement from_payload")


@dataclass
class OrderRequest:
    """Request parameters for placing an order.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/create-order
    """

    token_id: str
    side: str  # "BUY" or "SELL"
    price: float
    size: float
    order_type: str = "GTC"  # "FOK", "FAK", "GTC", or "GTD"
    expiration: int | None = None  # Unix timestamp (required for GTD orders)
    
    def __post_init__(self) -> None:
        """Validate order request parameters."""
        if self.order_type.upper() not in ("FOK", "FAK", "GTC", "GTD"):
            raise ValueError(
                f"Invalid order_type: {self.order_type}. Must be one of: FOK, FAK, GTC, GTD"
            )
        if self.order_type.upper() == "GTD" and self.expiration is None:
            raise ValueError("expiration is required for GTD orders")
        if self.side.upper() not in ("BUY", "SELL"):
            raise ValueError(f"Invalid side: {self.side}. Must be BUY or SELL")


@dataclass
class OrderResponse:
    """Response from placing an order.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/create-order
    
    The response format matches the Polymarket CLOB API response:
    - success: boolean indicating if server-side error occurred
    - errorMsg: error message if placement failed
    - orderId: id of the placed order
    - orderHashes: array of settlement transaction hashes if order was matched
    - status: order status (matched, live, delayed, unmatched)
    """

    success: bool
    error_msg: str
    order_id: str
    order_hashes: list[str]
    status: str
    raw_response: dict[str, Any]


# Type alias for batch order responses
BatchOrderResponse = list[OrderResponse]


class BaseMarketClient(ABC):
    """Base interface for prediction market clients.

    All market-specific clients should inherit from this class.
    """

    # Read operations
    @abstractmethod
    def get_markets(self) -> list[BaseMarket]:
        """Fetch all markets.

        Returns:
            List of market data.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_markets")

    @abstractmethod
    def get_market(self, market_id: str) -> BaseMarket | None:
        """Fetch a specific market by ID.

        Args:
            market_id: The market identifier.

        Returns:
            Market data if found, None otherwise.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_market")

    @abstractmethod
    def get_order_book(self, market_id: str) -> BaseOrderBook:
        """Fetch order book for a specific market.

        Args:
            market_id: The market identifier.

        Returns:
            Order book snapshot.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_order_book")

    # Write operations (optional - some clients may be read-only)
    def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place a new order.

        Args:
            order: Order request parameters.

        Returns:
            OrderResponse with order details.

        Raises:
            NotImplementedError: If write operations are not supported.
        """
        raise NotImplementedError("Write operations not supported by this client")

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order.

        Args:
            order_id: The order identifier to cancel.

        Returns:
            True if cancellation was successful.

        Raises:
            NotImplementedError: If write operations are not supported.
        """
        raise NotImplementedError("Write operations not supported by this client")

    def get_orders(self, market_id: str | None = None) -> list[BaseOrder]:
        """Fetch user's orders.

        Args:
            market_id: Optional market ID to filter orders.

        Returns:
            List of user's orders.

        Raises:
            NotImplementedError: If write operations are not supported.
        """
        raise NotImplementedError("Write operations not supported by this client")

    def close(self) -> None:
        """Close the client and cleanup resources.

        Default implementation does nothing. Override if needed.
        """
        pass

    def __enter__(self) -> BaseMarketClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Context manager exit."""
        self.close()


__all__ = [
    "BaseMarket",
    "BaseMarketClient",
    "BaseOrder",
    "BaseOrderBook",
    "BaseOrderBookLevel",
    "BatchOrderResponse",
    "OrderRequest",
    "OrderResponse",
]

