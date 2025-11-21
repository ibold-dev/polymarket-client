"""Typed client for Polymarket API (read and write operations)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Literal, Optional

try:
    from py_clob_client.client import ClobClient
except ImportError:
    ClobClient = None  # type: ignore[assignment, misc]

try:
    from py_clob_client.clob_types import BookParams, OrderArgs, OrderType, PostOrdersArgs
    from py_clob_client.order_builder.constants import BUY, SELL
except ImportError:
    BookParams = None  # type: ignore[assignment, misc]
    OrderArgs = None  # type: ignore[assignment, misc]
    OrderType = None  # type: ignore[assignment, misc]
    PostOrdersArgs = None  # type: ignore[assignment, misc]
    BUY = "BUY"
    SELL = "SELL"

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment, misc]

try:
    from web3 import Web3
    from web3.types import EventData, LogReceipt
except ImportError:
    Web3 = None  # type: ignore[assignment, misc]
    EventData = None  # type: ignore[assignment, misc]
    LogReceipt = None  # type: ignore[assignment, misc]

from .base import (
    BaseMarket,
    BaseMarketClient,
    BaseOrder,
    BaseOrderBook,
    BatchOrderResponse,
    OrderRequest,
    OrderResponse,
)
from .types import (
    Activity,
    CancelMarketOrdersParams,
    CancelOrdersResponse,
    Category,
    ClosedPosition,
    Comment,
    DataTrade,
    Event,
    GetActiveOrdersParams,
    GetActivityParams,
    GetClosedPositionsParams,
    GetCommentsParams,
    GetDataTradesParams,
    GetEventsParams,
    GetMarketsParams,
    GetPositionsParams,
    GetRelatedTagsParams,
    GetSeriesParams,
    GetTagsParams,
    GetTeamsParams,
    GetTopHoldersParams,
    GetTotalValueParams,
    GetTradesParams,
    ImageOptimized,
    MakerOrder,
    Market,
    OpenOrder,
    OrderBook,
    OrderBookLevel,
    OrderFilled,
    OrderScoringParams,
    OrdersScoring,
    OrdersScoringBatch,
    OrdersScoringParams,
    Position,
    RelatedTag,
    SearchParams,
    SearchResult,
    Series,
    SportsMetadata,
    Tag,
    Team,
    TopHolder,
    TotalValue,
    Trade,
)


class PolymarketClientError(Exception):
    """Raised when the Polymarket API returns an error response."""


class PolymarketClient(BaseMarketClient):
    """Synchronous Polymarket API client for market data and trading."""

    def __init__(
        self,
        *,
        base_url: str = "https://clob.polymarket.com",
        private_key: Optional[str] = None,
        chain_id: int = 137,  # Polygon Mainnet
        funder: Optional[str] = None,
        signature_type: Optional[int] = None,
        timeout: int = 10,
        rpc_url: Optional[str] = None,
        exchange_contract_address: Optional[str] = None,
    ) -> None:
        """Initialize Polymarket client.

        Args:
            base_url: Base URL for the Polymarket CLOB API.
            private_key: Private key for authenticated operations (required for write ops).
            chain_id: Blockchain chain ID (137 for Polygon Mainnet, 80001 for Mumbai testnet).
            funder: Funder address (Polymarket Proxy address, optional).
            signature_type: Signature type (1 for email/Magic, 2 for browser wallet, None for EOA).
                If funder is provided and signature_type is None, defaults to 2.
            timeout: Request timeout in seconds.
            rpc_url: Optional RPC URL for blockchain queries (for OrderFilled event parsing).
                If not provided, defaults to public Polygon RPC.
            exchange_contract_address: Optional Exchange contract address for filtering OrderFilled events.
                If not provided, will attempt to detect from chain_id.

        Note:
            For read-only operations, private_key is optional.
            For write operations (placing orders, etc.), private_key is required.
            
            Signature types:
            - 1: Email/Magic Link account (with funder)
            - 2: Browser wallet (MetaMask, Coinbase Wallet, etc., with funder)
            - None/0: Direct EOA trading (no funder)
            
            For OrderFilled event parsing, web3 library and rpc_url are required.
        """
        if ClobClient is None:
            raise PolymarketClientError(
                "py-clob-client library is required. Install it with: pip install py-clob-client"
            )

        self._base_url = base_url
        self._timeout = timeout
        self._private_key = private_key
        self._chain_id = chain_id
        self._funder = funder
        # Default to signature_type=2 if funder is provided but signature_type is not
        if funder and signature_type is None:
            self._signature_type = 2
        else:
            self._signature_type = signature_type
        self._client: Optional[ClobClient] = None
        self._is_read_only = private_key is None
        
        # Web3 setup for onchain event parsing
        self._rpc_url = rpc_url or self._get_default_rpc_url(chain_id)
        self._exchange_contract_address = exchange_contract_address or self._get_default_exchange_address(chain_id)
        self._web3: Optional[Web3] = None

    @property
    def _clob_client(self) -> ClobClient:
        """Get or create CLOB client."""
        if self._client is None:
            kwargs: dict[str, Any] = {}
            if self._private_key:
                kwargs["key"] = self._private_key
            kwargs["chain_id"] = self._chain_id
            if self._funder:
                kwargs["funder"] = self._funder
            if self._signature_type is not None:
                kwargs["signature_type"] = self._signature_type

            self._client = ClobClient(self._base_url, **kwargs)
        return self._client
    
    @staticmethod
    def _get_default_rpc_url(chain_id: int) -> str:
        """Get default RPC URL for chain ID.
        
        Args:
            chain_id: Blockchain chain ID.
            
        Returns:
            Default RPC URL for the chain.
        """
        if chain_id == 137:  # Polygon Mainnet
            return "https://polygon-rpc.com"
        elif chain_id == 80001:  # Mumbai Testnet
            return "https://rpc-mumbai.maticvigil.com"
        else:
            # Default to Polygon Mainnet
            return "https://polygon-rpc.com"
    
    @staticmethod
    def _get_default_exchange_address(chain_id: int) -> str:
        """Get default Exchange contract address for chain ID.
        
        Args:
            chain_id: Blockchain chain ID.
            
        Returns:
            Default Exchange contract address for the chain.
        """
        # Polymarket Exchange contract addresses
        if chain_id == 137:  # Polygon Mainnet
            return "0x4bFb41d5B3570DeFd03C39a9A4D35d77Ee6a2697"
        elif chain_id == 80001:  # Mumbai Testnet
            return "0x4bFb41d5B3570DeFd03C39a9A4D35d77Ee6a2697"  # Same address on testnet
        else:
            # Default to Polygon Mainnet address
            return "0x4bFb41d5B3570DeFd03C39a9A4D35d77Ee6a2697"
    
    @property
    def _web3_client(self) -> Web3:
        """Get or create Web3 client for blockchain queries."""
        if Web3 is None:
            raise PolymarketClientError(
                "web3 library is required for onchain event parsing. Install it with: pip install web3"
            )
        
        if self._web3 is None:
            self._web3 = Web3(Web3.HTTPProvider(self._rpc_url))
            if not self._web3.is_connected():
                raise PolymarketClientError(f"Failed to connect to RPC: {self._rpc_url}")
        
        return self._web3

    # Read operations
    def get_ok(self) -> bool:
        """Check if the API is operational.

        Returns:
            True if the API is operational.

        Raises:
            PolymarketClientError: When the API check fails.
        """
        try:
            return self._clob_client.get_ok()
        except Exception as e:
            raise PolymarketClientError(f"Failed to check API status: {e}") from e

    def get_server_time(self) -> int:
        """Get the server timestamp.

        Returns:
            Server timestamp in milliseconds.

        Raises:
            PolymarketClientError: When fetching server time fails.
        """
        try:
            return self._clob_client.get_server_time()
        except Exception as e:
            raise PolymarketClientError(f"Failed to fetch server time: {e}") from e

    def get_markets(
        self,
        params: Optional[GetMarketsParams] = None,
    ) -> list[Market]:
        """Fetch markets from the Gamma API.
        
        Reference: https://docs.polymarket.com/developers/gamma-markets-api/get-markets

        Args:
            params: Optional query parameters for filtering and sorting markets.

        Returns:
            List of market data matching the Gamma API response schema.

        Raises:
            PolymarketClientError: When fetching markets fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/markets"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_markets = response.json()
                
                if not isinstance(raw_markets, list):
                    return []

                markets = [
                    Market.from_payload(market) 
                    for market in raw_markets 
                    if isinstance(market, dict)
                ]
                return markets
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch markets from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse markets: {e}") from e

    def get_market(self, market_id: str) -> Optional[BaseMarket]:
        """Fetch a specific market by token ID.

        Args:
            market_id: The market token ID.

        Returns:
            Market data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching the market fails.
        """
        try:
            raw_market = self._clob_client.get_market(market_id)
            if not isinstance(raw_market, dict):
                return None

            return Market.from_payload(raw_market)  # type: ignore[return-value]
        except Exception as e:
            raise PolymarketClientError(f"Failed to fetch market {market_id}: {e}") from e

    def get_order_book(self, market_id: str) -> BaseOrderBook:
        """Fetch order book for a specific market.

        Args:
            market_id: The market token ID.

        Returns:
            Order book snapshot.

        Raises:
            PolymarketClientError: When fetching the order book fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Use direct CLOB API endpoint: https://clob.polymarket.com/book?token_id=...
            url = f"https://clob.polymarket.com/book"
            params = {"token_id": market_id}
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=params, headers={"accept": "application/json"})
                response.raise_for_status()
                order_book_data = response.json()
                
                # Parse the response using OrderBook.from_payload
                order_book = OrderBook.from_payload(order_book_data)
                return order_book  # type: ignore[return-value]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch order book for {market_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse order book for {market_id}: {e}") from e

    def get_order_books(self, token_ids: list[str]) -> list[OrderBook]:
        """Fetch order books for multiple markets.

        Args:
            token_ids: List of market token IDs.

        Returns:
            List of order book snapshots.

        Raises:
            PolymarketClientError: When fetching order books fails.
        """
        try:
            if BookParams is None:
                # Fallback: fetch individually
                return [self.get_order_book(token_id) for token_id in token_ids]  # type: ignore[return-value]

            book_params = [BookParams(token_id=token_id) for token_id in token_ids]
            clob_books = self._clob_client.get_order_books(book_params)
            return [OrderBook.from_payload(book) for book in clob_books]
        except Exception as e:
            raise PolymarketClientError(f"Failed to fetch order books: {e}") from e

    def get_midpoint(self, token_id: str) -> float:
        """Fetch the midpoint price for a market.

        Args:
            token_id: The market token ID.

        Returns:
            Midpoint price.

        Raises:
            PolymarketClientError: When fetching the midpoint fails.
        """
        try:
            return float(self._clob_client.get_midpoint(token_id))
        except Exception as e:
            raise PolymarketClientError(f"Failed to fetch midpoint for {token_id}: {e}") from e

    def get_price(self, token_id: str, side: Literal["BUY", "SELL"] = "BUY") -> float:
        """Fetch the best price for a market on a specific side.

        Args:
            token_id: The market token ID.
            side: Order side ("BUY" or "SELL").

        Returns:
            Best price for the specified side.

        Raises:
            PolymarketClientError: When fetching the price fails.
        """
        try:
            return float(self._clob_client.get_price(token_id, side=side))
        except Exception as e:
            raise PolymarketClientError(f"Failed to fetch price for {token_id} (side={side}): {e}") from e

    def get_market_by_slug(self, slug: str) -> Optional[Market]:
        """Fetch market data from Gamma API by slug.
        
        Reference: https://docs.polymarket.com/api-reference/markets/get-market-by-slug

        Args:
            slug: Market slug (e.g., "bitcoin-up-or-down-november-13-12pm-et").

        Returns:
            Market data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching market fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/markets/slug/{slug}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_market = response.json()
                if not isinstance(raw_market, dict):
                    return None
                return Market.from_payload(raw_market)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch market by slug {slug}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse market: {e}") from e

    def get_market_by_id(self, market_id: int) -> Optional[Market]:
        """Fetch market data from Gamma API by ID.
        
        Reference: https://docs.polymarket.com/api-reference/markets/get-market-by-id

        Args:
            market_id: Market ID.

        Returns:
            Market data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching market fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/markets/{market_id}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_market = response.json()
                if not isinstance(raw_market, dict):
                    return None
                return Market.from_payload(raw_market)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch market by ID {market_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse market: {e}") from e

    def get_market_tags(self, market_id: int) -> list[Tag]:
        """Fetch tags for a market by ID.
        
        Reference: https://docs.polymarket.com/api-reference/markets/get-market-tags-by-id

        Args:
            market_id: Market ID.

        Returns:
            List of tags associated with the market.

        Raises:
            PolymarketClientError: When fetching tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/markets/{market_id}/tags"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                if not isinstance(raw_tags, list):
                    return []
                return [
                    Tag.from_payload(tag)
                    for tag in raw_tags
                    if isinstance(tag, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch tags for market {market_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse tags: {e}") from e

    def get_events(
        self,
        params: Optional[GetEventsParams] = None,
    ) -> list[Event]:
        """Fetch events from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/events/list-events

        Args:
            params: Optional query parameters for filtering and sorting events.

        Returns:
            List of event data.

        Raises:
            PolymarketClientError: When fetching events fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/events"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_events = response.json()
                
                if not isinstance(raw_events, list):
                    return []

                events = [
                    Event.from_payload(event) 
                    for event in raw_events 
                    if isinstance(event, dict)
                ]
                return events
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch events from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse events: {e}") from e

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Fetch event data from Gamma API by ID.
        
        Reference: https://docs.polymarket.com/api-reference/events/get-event-by-id

        Args:
            event_id: Event ID.

        Returns:
            Event data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching event fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/events/{event_id}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_event = response.json()
                if not isinstance(raw_event, dict):
                    return None
                return Event.from_payload(raw_event)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch event by ID {event_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse event: {e}") from e

    def get_event_by_slug(self, slug: str) -> Optional[Event]:
        """Fetch event data from Gamma API by slug.
        
        Reference: https://docs.polymarket.com/api-reference/events/get-event-by-slug

        Args:
            slug: Event slug.

        Returns:
            Event data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching event fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/events/slug/{slug}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_event = response.json()
                if not isinstance(raw_event, dict):
                    return None
                return Event.from_payload(raw_event)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch event by slug {slug}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse event: {e}") from e

    def get_event_tags(self, event_id: int) -> list[Tag]:
        """Fetch tags for an event by ID.
        
        Reference: https://docs.polymarket.com/api-reference/events/get-event-tags

        Args:
            event_id: Event ID.

        Returns:
            List of tags associated with the event.

        Raises:
            PolymarketClientError: When fetching tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/events/{event_id}/tags"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                if not isinstance(raw_tags, list):
                    return []
                return [
                    Tag.from_payload(tag)
                    for tag in raw_tags
                    if isinstance(tag, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch tags for event {event_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse tags: {e}") from e

    def get_tags(
        self,
        params: Optional[GetTagsParams] = None,
    ) -> list[Tag]:
        """Fetch tags from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/tags/list-tags

        Args:
            params: Optional query parameters for filtering and sorting tags.

        Returns:
            List of tag data.

        Raises:
            PolymarketClientError: When fetching tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/tags"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                
                if not isinstance(raw_tags, list):
                    return []

                tags = [
                    Tag.from_payload(tag) 
                    for tag in raw_tags 
                    if isinstance(tag, dict)
                ]
                return tags
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch tags from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse tags: {e}") from e

    def get_tag_by_id(self, tag_id: int, include_template: Optional[bool] = None) -> Optional[Tag]:
        """Fetch tag data from Gamma API by ID.
        
        Reference: https://docs.polymarket.com/api-reference/tags/get-tag-by-id

        Args:
            tag_id: Tag ID.
            include_template: Whether to include template data.

        Returns:
            Tag data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching tag fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/tags/{tag_id}"
            query_params: dict[str, Any] = {}
            if include_template is not None:
                query_params["include_template"] = include_template
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_tag = response.json()
                if not isinstance(raw_tag, dict):
                    return None
                return Tag.from_payload(raw_tag)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch tag by ID {tag_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse tag: {e}") from e

    def get_tag_by_slug(self, slug: str, include_template: Optional[bool] = None) -> Optional[Tag]:
        """Fetch tag data from Gamma API by slug.
        
        Reference: https://docs.polymarket.com/api-reference/tags/get-tag-by-slug

        Args:
            slug: Tag slug.
            include_template: Whether to include template data.

        Returns:
            Tag data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching tag fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/tags/slug/{slug}"
            query_params: dict[str, Any] = {}
            if include_template is not None:
                query_params["include_template"] = include_template
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_tag = response.json()
                if not isinstance(raw_tag, dict):
                    return None
                return Tag.from_payload(raw_tag)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch tag by slug {slug}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse tag: {e}") from e

    def get_related_tags_by_tag_id(
        self,
        tag_id: int,
        params: Optional[GetRelatedTagsParams] = None,
    ) -> list[RelatedTag]:
        """Fetch related tags by tag ID.
        
        Reference: https://docs.polymarket.com/api-reference/tags/get-related-tags-relationships-by-tag-id

        Args:
            tag_id: Tag ID.
            params: Optional query parameters.

        Returns:
            List of related tag relationships.

        Raises:
            PolymarketClientError: When fetching related tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/tags/{tag_id}/related-tags"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                if not isinstance(raw_tags, list):
                    return []
                return [
                    RelatedTag.from_payload(tag)
                    for tag in raw_tags
                    if isinstance(tag, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch related tags for tag {tag_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse related tags: {e}") from e

    def get_related_tags_by_tag_slug(
        self,
        slug: str,
        params: Optional[GetRelatedTagsParams] = None,
    ) -> list[RelatedTag]:
        """Fetch related tags by tag slug.
        
        Reference: https://docs.polymarket.com/api-reference/tags/get-related-tags-relationships-by-tag-slug

        Args:
            slug: Tag slug.
            params: Optional query parameters.

        Returns:
            List of related tag relationships.

        Raises:
            PolymarketClientError: When fetching related tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/tags/slug/{slug}/related-tags"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                if not isinstance(raw_tags, list):
                    return []
                return [
                    RelatedTag.from_payload(tag)
                    for tag in raw_tags
                    if isinstance(tag, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch related tags for tag {slug}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse related tags: {e}") from e

    def get_tags_related_to_tag_id(
        self,
        tag_id: int,
        params: Optional[GetRelatedTagsParams] = None,
    ) -> list[Tag]:
        """Fetch tags related to a tag by ID.
        
        Reference: https://docs.polymarket.com/api-reference/tags/get-tags-related-to-a-tag-id

        Args:
            tag_id: Tag ID.
            params: Optional query parameters.

        Returns:
            List of related tags.

        Raises:
            PolymarketClientError: When fetching related tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/tags/{tag_id}/related-tags/tags"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                if not isinstance(raw_tags, list):
                    return []
                return [
                    Tag.from_payload(tag)
                    for tag in raw_tags
                    if isinstance(tag, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch related tags for tag {tag_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse related tags: {e}") from e

    def get_tags_related_to_tag_slug(
        self,
        slug: str,
        params: Optional[GetRelatedTagsParams] = None,
    ) -> list[Tag]:
        """Fetch tags related to a tag by slug.
        
        Reference: https://docs.polymarket.com/api-reference/tags/get-tags-related-to-a-tag-slug

        Args:
            slug: Tag slug.
            params: Optional query parameters.

        Returns:
            List of related tags.

        Raises:
            PolymarketClientError: When fetching related tags fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/tags/slug/{slug}/related-tags/tags"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_tags = response.json()
                if not isinstance(raw_tags, list):
                    return []
                return [
                    Tag.from_payload(tag)
                    for tag in raw_tags
                    if isinstance(tag, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch related tags for tag {slug}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse related tags: {e}") from e

    def get_teams(
        self,
        params: Optional[GetTeamsParams] = None,
    ) -> list[Team]:
        """Fetch teams from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/sports/list-teams

        Args:
            params: Optional query parameters for filtering and sorting teams.

        Returns:
            List of team data.

        Raises:
            PolymarketClientError: When fetching teams fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/teams"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_teams = response.json()
                
                if not isinstance(raw_teams, list):
                    return []

                teams = [
                    Team.from_payload(team) 
                    for team in raw_teams 
                    if isinstance(team, dict)
                ]
                return teams
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch teams from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse teams: {e}") from e

    def get_sports_metadata(self) -> list[SportsMetadata]:
        """Fetch sports metadata information from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/sports/get-sports-metadata-information

        Returns:
            List of sports metadata.

        Raises:
            PolymarketClientError: When fetching sports metadata fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/sports"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_sports = response.json()
                
                if not isinstance(raw_sports, list):
                    return []

                sports = [
                    SportsMetadata.from_payload(sport) 
                    for sport in raw_sports 
                    if isinstance(sport, dict)
                ]
                return sports
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch sports metadata from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse sports metadata: {e}") from e

    def get_series(
        self,
        params: Optional[GetSeriesParams] = None,
    ) -> list[Series]:
        """Fetch series from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/series/list-series

        Args:
            params: Optional query parameters for filtering and sorting series.

        Returns:
            List of series data.

        Raises:
            PolymarketClientError: When fetching series fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/series"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_series = response.json()
                
                if not isinstance(raw_series, list):
                    return []

                series_list = [
                    Series.from_payload(series_item) 
                    for series_item in raw_series 
                    if isinstance(series_item, dict)
                ]
                return series_list
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch series from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse series: {e}") from e

    def get_series_by_id(self, series_id: int) -> Optional[Series]:
        """Fetch series data from Gamma API by ID.
        
        Reference: https://docs.polymarket.com/api-reference/series/get-series-by-id

        Args:
            series_id: Series ID.

        Returns:
            Series data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching series fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/series/{series_id}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_series = response.json()
                if not isinstance(raw_series, dict):
                    return None
                return Series.from_payload(raw_series)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch series by ID {series_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse series: {e}") from e

    def get_comments(
        self,
        params: Optional[GetCommentsParams] = None,
    ) -> list[Comment]:
        """Fetch comments from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/comments/list-comments

        Args:
            params: Optional query parameters for filtering and sorting comments.

        Returns:
            List of comment data.

        Raises:
            PolymarketClientError: When fetching comments fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/comments"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_comments = response.json()
                
                if not isinstance(raw_comments, list):
                    return []

                comments = [
                    Comment.from_payload(comment) 
                    for comment in raw_comments 
                    if isinstance(comment, dict)
                ]
                return comments
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch comments from Gamma API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse comments: {e}") from e

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        """Fetch comment data from Gamma API by ID.
        
        Reference: https://docs.polymarket.com/api-reference/comments/get-comments-by-comment-id

        Args:
            comment_id: Comment ID.

        Returns:
            Comment data if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching comment fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required for Gamma API. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/comments/{comment_id}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                raw_comment = response.json()
                if not isinstance(raw_comment, dict):
                    return None
                return Comment.from_payload(raw_comment)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch comment by ID {comment_id}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse comment: {e}") from e

    def get_comments_by_user_address(self, user_address: str) -> list[Comment]:
        """Fetch comments by user address from the Gamma API.
        
        Reference: https://docs.polymarket.com/api-reference/comments/get-comments-by-user-address

        Args:
            user_address: User wallet address.

        Returns:
            List of comments by the user.

        Raises:
            PolymarketClientError: When fetching comments fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = f"https://gamma-api.polymarket.com/comments/user/{user_address}"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_comments = response.json()
                if not isinstance(raw_comments, list):
                    return []
                return [
                    Comment.from_payload(comment)
                    for comment in raw_comments
                    if isinstance(comment, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch comments for user {user_address}: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse comments: {e}") from e

    def search(self, params: SearchParams) -> list[SearchResult]:
        """Search markets, events, and profiles.
        
        Reference: https://docs.polymarket.com/api-reference/search/search-markets-events-and-profiles

        Args:
            params: Search parameters including query string.

        Returns:
            List of search results.

        Raises:
            PolymarketClientError: When search fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://gamma-api.polymarket.com/search"
            query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_results = response.json()
                if not isinstance(raw_results, list):
                    return []
                return [
                    SearchResult.from_payload(result)
                    for result in raw_results
                    if isinstance(result, dict)
                ]
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to search: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse search results: {e}") from e

    def health_check(self) -> bool:
        """Check if the Data API is operational.
        
        Reference: https://docs.polymarket.com/api-reference/health/health-check

        Returns:
            True if the API is operational.

        Raises:
            PolymarketClientError: When the health check fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/"
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data") == "OK"
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to check health: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse health check response: {e}") from e

    def get_positions(self, params: GetPositionsParams) -> list[Position]:
        """Get current positions for a user.
        
        Reference: https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user

        Args:
            params: Query parameters including required user address.

        Returns:
            List of Position objects.

        Raises:
            PolymarketClientError: When fetching positions fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/positions"
            query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_positions = response.json()
                
                if not isinstance(raw_positions, list):
                    return []

                positions = [
                    Position.from_payload(position) 
                    for position in raw_positions 
                    if isinstance(position, dict)
                ]
                return positions
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch positions from Data API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse positions: {e}") from e

    def get_data_trades(self, params: Optional[GetDataTradesParams] = None) -> list[DataTrade]:
        """Get trades for a user or markets from Data API.
        
        Reference: https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets

        Args:
            params: Optional query parameters for filtering trades.

        Returns:
            List of DataTrade objects.

        Raises:
            PolymarketClientError: When fetching trades fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/trades"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_trades = response.json()
                
                if not isinstance(raw_trades, list):
                    return []

                trades = [
                    DataTrade.from_payload(trade) 
                    for trade in raw_trades 
                    if isinstance(trade, dict)
                ]
                return trades
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch trades from Data API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse trades: {e}") from e

    def get_activity(self, params: GetActivityParams) -> list[Activity]:
        """Get user activity from Data API.
        
        Reference: https://docs.polymarket.com/api-reference/core/get-user-activity

        Args:
            params: Query parameters including required user address.

        Returns:
            List of Activity objects.

        Raises:
            PolymarketClientError: When fetching activity fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/activity"
            query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_activities = response.json()
                
                if not isinstance(raw_activities, list):
                    return []

                activities = [
                    Activity.from_payload(activity) 
                    for activity in raw_activities 
                    if isinstance(activity, dict)
                ]
                return activities
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch activity from Data API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse activity: {e}") from e

    def get_top_holders(
        self,
        params: Optional[GetTopHoldersParams] = None,
    ) -> list[TopHolder]:
        """Get top holders for markets.
        
        Reference: https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets

        Args:
            params: Optional query parameters for filtering top holders.

        Returns:
            List of TopHolder objects.

        Raises:
            PolymarketClientError: When fetching top holders fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/top-holders"
            query_params: dict[str, Any] = {}
            
            if params is not None:
                query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_holders = response.json()
                
                if not isinstance(raw_holders, list):
                    return []

                holders = [
                    TopHolder.from_payload(holder) 
                    for holder in raw_holders 
                    if isinstance(holder, dict)
                ]
                return holders
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch top holders from Data API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse top holders: {e}") from e

    def get_total_value(self, params: GetTotalValueParams) -> TotalValue:
        """Get total value of a user's positions.
        
        Reference: https://docs.polymarket.com/api-reference/core/get-total-value-of-a-users-positions

        Args:
            params: Query parameters including required user address.

        Returns:
            TotalValue object with user address and total value.

        Raises:
            PolymarketClientError: When fetching total value fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/positions/total-value"
            query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_value = response.json()
                
                if not isinstance(raw_value, dict):
                    raise PolymarketClientError("Invalid response format from total value endpoint")
                
                return TotalValue.from_payload(raw_value)
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch total value from Data API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse total value: {e}") from e

    def get_closed_positions(self, params: GetClosedPositionsParams) -> list[ClosedPosition]:
        """Get closed positions for a user.
        
        Reference: https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user

        Args:
            params: Query parameters including required user address.

        Returns:
            List of ClosedPosition objects.

        Raises:
            PolymarketClientError: When fetching closed positions fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            url = "https://data-api.polymarket.com/positions/closed"
            query_params = params.to_query_params()
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(
                    url,
                    params=query_params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                raw_positions = response.json()
                
                if not isinstance(raw_positions, list):
                    return []

                positions = [
                    ClosedPosition.from_payload(position) 
                    for position in raw_positions 
                    if isinstance(position, dict)
                ]
                return positions
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch closed positions from Data API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse closed positions: {e}") from e

    # Write operations
    def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place a new order using the Polymarket CLOB API.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/create-order
        
        Supports all order types:
        - FOK (Fill-Or-Kill): Market order that must execute immediately in full or be cancelled
        - FAK (Fill-And-Kill): Market order executed immediately for available shares, remainder cancelled
        - GTC (Good-Till-Cancelled): Limit order active until fulfilled or cancelled
        - GTD (Good-Til-Date): Limit order active until specified expiration date

        Args:
            order: Order request parameters.

        Returns:
            OrderResponse with order details matching the API response format:
            - success: boolean indicating server-side error status
            - errorMsg: error message if placement failed
            - orderId: id of the placed order
            - orderHashes: array of settlement transaction hashes if matched
            - status: order status (matched, live, delayed, unmatched)

        Raises:
            PolymarketClientError: When placing order fails.
            ValueError: If client is read-only or order parameters are invalid.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot place order: client is read-only. Provide private_key to enable write operations.")

        if OrderArgs is None or OrderType is None:
            raise PolymarketClientError("py-clob-client types not available. Ensure py-clob-client is properly installed.")
        
        try:
            # Set API credentials (required for authenticated operations)
            # Reference: https://docs.polymarket.com/developers/CLOB/orders/create-order
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials: {e}") from e
            
            # Convert OrderRequest to OrderArgs
            side_value = BUY if order.side.upper() == "BUY" else SELL
            
            # For market orders (FOK/FAK), use the provided price (should be best available from order book)
            # For limit orders (GTC/GTD), use the specified price
            # Note: Polymarket API requires a valid price even for market orders (best available)
            order_price = order.price if order.price > 0 else 0.0

            # Handle expiration for GTD orders
            # GTD orders require expiration with 1 minute security threshold
            # If expiration is None, use 0 (which works for GTC/FOK/FAK)
            expiration = order.expiration if order.expiration is not None else 0

            order_args = OrderArgs(
                token_id=order.token_id,
                price=order_price,
                size=order.size,
                side=side_value,
                expiration=expiration,
            )

            # Create and sign the order
            # This handles the complex order preparation: structuring, hashing, and signing
            try:
                signed_order = self._clob_client.create_order(order_args)
            except Exception as e:
                raise PolymarketClientError(f"Failed to create/sign order: {e}") from e
            
            # Map order_type string to OrderType enum
            order_type_upper = order.order_type.upper()
            if order_type_upper == "FOK":
                order_type_enum = OrderType.FOK
            elif order_type_upper == "FAK":
                order_type_enum = OrderType.FAK
            elif order_type_upper == "GTC":
                order_type_enum = OrderType.GTC
            elif order_type_upper == "GTD":
                order_type_enum = OrderType.GTD
            else:
                raise PolymarketClientError(f"Invalid order_type: {order.order_type}. Must be FOK, FAK, GTC, or GTD")
            
            # Post the order to the CLOB API
            # Reference: POST /<clob-endpoint>/order
            try:
                response = self._clob_client.post_order(signed_order, order_type_enum)
            except Exception as e:
                raise PolymarketClientError(f"Failed to post order: {e}") from e

            # Parse response according to API documentation
            # Response format: { success, errorMsg, orderId, orderHashes, status }
            if isinstance(response, dict):
                success = bool(response.get("success", True))
                error_msg = str(response.get("errorMsg", response.get("error_msg", "")))
                order_id = str(response.get("orderId", response.get("orderID", response.get("order_id", ""))))
                order_hashes_raw = response.get("orderHashes", response.get("order_hashes", []))
                order_hashes = [str(hash_val) for hash_val in order_hashes_raw] if isinstance(order_hashes_raw, list) else []
                status = str(response.get("status", "unknown"))
            else:
                # Handle object response
                success = bool(getattr(response, "success", True))
                error_msg = str(getattr(response, "errorMsg", getattr(response, "error_msg", "")))
                order_id = str(getattr(response, "orderId", getattr(response, "orderID", getattr(response, "order_id", ""))))
                order_hashes_attr = getattr(response, "orderHashes", getattr(response, "order_hashes", []))
                order_hashes = [str(hash_val) for hash_val in order_hashes_attr] if isinstance(order_hashes_attr, list) else []
                status = str(getattr(response, "status", "unknown"))

            return OrderResponse(
                success=success,
                error_msg=error_msg,
                order_id=order_id,
                order_hashes=order_hashes,
                status=status,
                raw_response=response if isinstance(response, dict) else {"response": str(response)},
            )

        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is (already has good error message)
            raise
        except ValueError as e:
            # Re-raise ValueError from OrderRequest validation
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to place order: {e}") from e

    def place_orders(self, orders: list[OrderRequest]) -> BatchOrderResponse:
        """Place multiple orders in a single batch request.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/create-order-batch
        
        Polymarket's CLOB supports batch orders, allowing you to place up to 15 orders
        in a single request. This is more efficient than placing orders individually.

        Args:
            orders: List of order requests (maximum 15 orders per batch).

        Returns:
            List of OrderResponse objects, one for each order in the batch.
            Each response matches the API response format:
            - success: boolean indicating server-side error status
            - errorMsg: error message if placement failed
            - orderId: id of the placed order
            - orderHashes: array of settlement transaction hashes if matched
            - status: order status (matched, live, delayed, unmatched)

        Raises:
            PolymarketClientError: When placing orders fails.
            ValueError: If client is read-only, batch size exceeds 15, or order parameters are invalid.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot place orders: client is read-only. Provide private_key to enable write operations.")

        if OrderArgs is None or OrderType is None or PostOrdersArgs is None:
            raise PolymarketClientError("py-clob-client types not available. Ensure py-clob-client is properly installed.")
        
        # Validate batch size (max 15 orders per batch)
        if len(orders) > 15:
            raise ValueError(f"Batch size exceeds maximum of 15 orders. Received {len(orders)} orders.")
        
        if len(orders) == 0:
            raise ValueError("Cannot place empty batch. Provide at least one order.")
        
        try:
            # Set API credentials (required for authenticated operations)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials: {e}") from e
            
            # Convert each OrderRequest to PostOrdersArgs
            post_orders_args: list[PostOrdersArgs] = []
            
            for order in orders:
                # Convert OrderRequest to OrderArgs
                side_value = BUY if order.side.upper() == "BUY" else SELL
                order_price = order.price if order.price > 0 else 0.0
                expiration = order.expiration if order.expiration is not None else 0

                order_args = OrderArgs(
                    token_id=order.token_id,
                    price=order_price,
                    size=order.size,
                    side=side_value,
                    expiration=expiration,
                )

                # Create and sign the order
                try:
                    signed_order = self._clob_client.create_order(order_args)
                except Exception as e:
                    raise PolymarketClientError(f"Failed to create/sign order for token {order.token_id}: {e}") from e
                
                # Map order_type string to OrderType enum
                order_type_upper = order.order_type.upper()
                if order_type_upper == "FOK":
                    order_type_enum = OrderType.FOK
                elif order_type_upper == "FAK":
                    order_type_enum = OrderType.FAK
                elif order_type_upper == "GTC":
                    order_type_enum = OrderType.GTC
                elif order_type_upper == "GTD":
                    order_type_enum = OrderType.GTD
                else:
                    raise PolymarketClientError(f"Invalid order_type: {order.order_type}. Must be FOK, FAK, GTC, or GTD")
                
                # Create PostOrdersArgs for batch
                post_order_arg = PostOrdersArgs(
                    order=signed_order,
                    orderType=order_type_enum,
                )
                post_orders_args.append(post_order_arg)
            
            # Post all orders in batch to the CLOB API
            # Reference: POST /<clob-endpoint>/orders
            try:
                response = self._clob_client.post_orders(post_orders_args)
            except Exception as e:
                raise PolymarketClientError(f"Failed to post batch orders: {e}") from e

            # Parse response - batch endpoint returns a list of responses
            if not isinstance(response, list):
                raise PolymarketClientError(f"Expected list response from batch order endpoint, got {type(response)}")
            
            # Ensure response length matches request length
            if len(response) != len(orders):
                raise PolymarketClientError(
                    f"Response length ({len(response)}) does not match request length ({len(orders)})"
                )
            
            # Parse each response in the batch
            batch_responses: BatchOrderResponse = []
            for i, resp_item in enumerate(response):
                # Parse response according to API documentation
                if isinstance(resp_item, dict):
                    success = bool(resp_item.get("success", True))
                    error_msg = str(resp_item.get("errorMsg", resp_item.get("error_msg", "")))
                    order_id = str(resp_item.get("orderId", resp_item.get("orderID", resp_item.get("order_id", ""))))
                    order_hashes_raw = resp_item.get("orderHashes", resp_item.get("order_hashes", []))
                    order_hashes = [str(hash_val) for hash_val in order_hashes_raw] if isinstance(order_hashes_raw, list) else []
                    status = str(resp_item.get("status", "unknown"))
                else:
                    # Handle object response
                    success = bool(getattr(resp_item, "success", True))
                    error_msg = str(getattr(resp_item, "errorMsg", getattr(resp_item, "error_msg", "")))
                    order_id = str(getattr(resp_item, "orderId", getattr(resp_item, "orderID", getattr(resp_item, "order_id", ""))))
                    order_hashes_attr = getattr(resp_item, "orderHashes", getattr(resp_item, "order_hashes", []))
                    order_hashes = [str(hash_val) for hash_val in order_hashes_attr] if isinstance(order_hashes_attr, list) else []
                    status = str(getattr(resp_item, "status", "unknown"))
                
                batch_responses.append(
                    OrderResponse(
                        success=success,
                        error_msg=error_msg,
                        order_id=order_id,
                        order_hashes=order_hashes,
                        status=status,
                        raw_response=resp_item if isinstance(resp_item, dict) else {"response": str(resp_item)},
                    )
                )
            
            return batch_responses

        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is (already has good error message)
            raise
        except ValueError as e:
            # Re-raise ValueError from validation
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to place batch orders: {e}") from e

    def cancel_order(self, order_id: str) -> CancelOrdersResponse:
        """Cancel a single order.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/cancel-orders
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            order_id: The order identifier to cancel.

        Returns:
            CancelOrdersResponse with:
            - canceled: list of canceled order IDs
            - not_canceled: dictionary mapping order IDs to reason strings

        Raises:
            PolymarketClientError: When cancellation fails.
            ValueError: If client is read-only.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot cancel order: client is read-only. Provide private_key to enable write operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for cancel_order: {e}") from e
            
            # Cancel order from CLOB API
            # Reference: DELETE /<clob-endpoint>/order
            url = f"{self._base_url}/order"
            request_body = {"orderID": order_id}
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json", "content-type": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.delete(url, json=request_body, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response
            if not isinstance(response_data, dict):
                raise PolymarketClientError(f"Unexpected response format from cancel order endpoint: {type(response_data)}")
            
            return CancelOrdersResponse.from_payload(response_data)

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to cancel order {order_id}: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to cancel order {order_id}: {e}") from e

    def cancel_orders(self, order_ids: list[str]) -> CancelOrdersResponse:
        """Cancel multiple orders.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/cancel-orders
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            order_ids: List of order identifiers to cancel.

        Returns:
            CancelOrdersResponse with:
            - canceled: list of canceled order IDs
            - not_canceled: dictionary mapping order IDs to reason strings

        Raises:
            PolymarketClientError: When cancellation fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot cancel orders: client is read-only. Provide private_key to enable write operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        if not order_ids:
            raise ValueError("order_ids cannot be empty")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for cancel_orders: {e}") from e
            
            # Cancel orders from CLOB API
            # Reference: DELETE /<clob-endpoint>/orders
            url = f"{self._base_url}/orders"
            request_body = order_ids  # API expects array directly in request body
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json", "content-type": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.delete(url, json=request_body, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response
            if not isinstance(response_data, dict):
                raise PolymarketClientError(f"Unexpected response format from cancel orders endpoint: {type(response_data)}")
            
            return CancelOrdersResponse.from_payload(response_data)

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to cancel orders: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to cancel orders: {e}") from e

    def cancel_all(self) -> CancelOrdersResponse:
        """Cancel all open orders posted by the user.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/cancel-orders
        
        This endpoint requires a L2 Header (API credentials).

        Returns:
            CancelOrdersResponse with:
            - canceled: list of canceled order IDs
            - not_canceled: dictionary mapping order IDs to reason strings

        Raises:
            PolymarketClientError: When cancellation fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot cancel all orders: client is read-only. Provide private_key to enable write operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for cancel_all: {e}") from e
            
            # Cancel all orders from CLOB API
            # Reference: DELETE /<clob-endpoint>/cancel-all
            url = f"{self._base_url}/cancel-all"
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.delete(url, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response
            if not isinstance(response_data, dict):
                raise PolymarketClientError(f"Unexpected response format from cancel-all endpoint: {type(response_data)}")
            
            return CancelOrdersResponse.from_payload(response_data)

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to cancel all orders: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to cancel all orders: {e}") from e

    def cancel_market_orders(
        self,
        params: CancelMarketOrdersParams,
    ) -> CancelOrdersResponse:
        """Cancel orders from a specific market.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/cancel-orders
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            params: Parameters containing market and/or asset_id to filter orders:
                - market: condition id of the market (optional)
                - asset_id: id of the asset/token (optional)
                
            At least one of market or asset_id must be provided.

        Returns:
            CancelOrdersResponse with:
            - canceled: list of canceled order IDs
            - not_canceled: dictionary mapping order IDs to reason strings

        Raises:
            PolymarketClientError: When cancellation fails.
            ValueError: If neither market nor asset_id is provided.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot cancel market orders: client is read-only. Provide private_key to enable write operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        if params.market is None and params.asset_id is None:
            raise ValueError("At least one of market or asset_id must be provided")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for cancel_market_orders: {e}") from e
            
            # Cancel market orders from CLOB API
            # Reference: DELETE /<clob-endpoint>/cancel-market-orders
            url = f"{self._base_url}/cancel-market-orders"
            query_params = params.to_query_params()
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.delete(url, params=query_params, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response
            if not isinstance(response_data, dict):
                raise PolymarketClientError(f"Unexpected response format from cancel-market-orders endpoint: {type(response_data)}")
            
            return CancelOrdersResponse.from_payload(response_data)

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to cancel market orders: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to cancel market orders: {e}") from e

    def get_order(self, order_id: str) -> Optional[OpenOrder]:
        """Get information about a single order by ID.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/get-order
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            order_id: The order ID (hash) to retrieve information about.

        Returns:
            OpenOrder object if the order exists, None otherwise.
            The OpenOrder contains:
            - id: order id
            - status: order current status
            - market: market id (condition id)
            - original_size: original order size at placement
            - outcome: human readable outcome the order is for
            - maker_address: maker address (funder)
            - owner: api key
            - price: price
            - side: buy or sell
            - size_matched: size of order that has been matched/filled
            - asset_id: token id
            - expiration: unix timestamp when order expired (0 if doesn't expire)
            - type: order type (GTC, FOK, GTD, FAK)
            - created_at: unix timestamp when order was created
            - associate_trades: list of Trade IDs the order has been partially included in

        Raises:
            PolymarketClientError: When fetching the order fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get order: client is read-only. Provide private_key to enable authenticated operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for get_order: {e}") from e
            
            # Get order from CLOB API
            # Reference: GET /<clob-endpoint>/data/order/<order_hash>
            url = f"{self._base_url}/data/order/{order_id}"
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, headers=headers)
                
                # 404 means order doesn't exist
                if response.status_code == 404:
                    return None
                
                response.raise_for_status()
                response_data = response.json()

            # Parse response - API returns { "order": OpenOrder } or just OpenOrder
            if response_data is None:
                return None
            
            # Response might be wrapped in "order" key or be the order directly
            if isinstance(response_data, dict):
                order_data = response_data.get("order", response_data)
                if not order_data or not isinstance(order_data, dict):
                    return None
                return OpenOrder.from_payload(order_data)
            else:
                # Handle non-dict response
                return None

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None and e.response.status_code == 404:
                return None
            raise PolymarketClientError(f"Failed to fetch order {order_id}: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to get order {order_id}: {e}") from e

    def get_active_orders(
        self,
        params: Optional[GetActiveOrdersParams] = None,
    ) -> list[OpenOrder]:
        """Get active orders for a specific market.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/get-active-order
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            params: Optional query parameters to filter active orders:
                - id: id of order to get information about
                - market: condition id of market
                - asset_id: id of the asset/token
                
            If params is None, returns all active orders.

        Returns:
            List of OpenOrder objects filtered by the query parameters.
            Each OpenOrder contains:
            - id: order id
            - status: order current status
            - market: market id (condition id)
            - original_size: original order size at placement
            - outcome: human readable outcome the order is for
            - maker_address: maker address (funder)
            - owner: api key
            - price: price
            - side: buy or sell
            - size_matched: size of order that has been matched/filled
            - asset_id: token id
            - expiration: unix timestamp when order expired (0 if doesn't expire)
            - type: order type (GTC, FOK, GTD, FAK)
            - created_at: unix timestamp when order was created
            - associate_trades: list of Trade IDs the order has been partially included in

        Raises:
            PolymarketClientError: When fetching active orders fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get active orders: client is read-only. Provide private_key to enable authenticated operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for get_active_orders: {e}") from e
            
            # Get active orders from CLOB API
            # Reference: GET /<clob-endpoint>/data/orders
            url = f"{self._base_url}/data/orders"
            
            # Build query parameters
            query_params: dict[str, str] = {}
            if params is not None:
                query_params = params.to_query_params()
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=query_params, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response - API returns OpenOrder[] (list of open orders)
            if not isinstance(response_data, list):
                # Handle case where response might be wrapped or empty
                if response_data is None:
                    return []
                if isinstance(response_data, dict) and "orders" in response_data:
                    response_data = response_data["orders"]
                else:
                    return []
            
            # Parse each order in the list
            active_orders: list[OpenOrder] = []
            for order_data in response_data:
                if isinstance(order_data, dict):
                    try:
                        active_orders.append(OpenOrder.from_payload(order_data))
                    except Exception as e:
                        # Skip invalid order entries but continue processing others
                        continue
            
            return active_orders

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch active orders: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to get active orders: {e}") from e

    def is_order_scoring(self, params: OrderScoringParams) -> OrdersScoring:
        """Check if a single order is eligible or scoring for Rewards purposes.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/check-scoring
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            params: Parameters containing the order ID to check.

        Returns:
            OrdersScoring object with:
            - scoring: boolean indicating if the order is scoring or not

        Raises:
            PolymarketClientError: When checking order scoring fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot check order scoring: client is read-only. Provide private_key to enable authenticated operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for is_order_scoring: {e}") from e
            
            # Check order scoring from CLOB API
            # Reference: GET /<clob-endpoint>/order-scoring?order_id={...}
            url = f"{self._base_url}/order-scoring"
            query_params = {"order_id": params.order_id}
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=query_params, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response - API returns OrdersScoring object
            if not isinstance(response_data, dict):
                raise PolymarketClientError(f"Unexpected response format from order-scoring endpoint: {type(response_data)}")
            
            return OrdersScoring.from_payload(response_data)

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to check order scoring: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to check order scoring: {e}") from e

    def are_orders_scoring(self, params: OrdersScoringParams) -> OrdersScoringBatch:
        """Check if multiple orders are eligible or scoring for Rewards purposes.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/check-scoring
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            params: Parameters containing the list of order IDs to check.

        Returns:
            Dictionary mapping order IDs to boolean values indicating if each order is scoring.
            Format: { "order_id": bool, ... }

        Raises:
            PolymarketClientError: When checking orders scoring fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot check orders scoring: client is read-only. Provide private_key to enable authenticated operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        if not params.order_ids:
            raise ValueError("order_ids cannot be empty")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for are_orders_scoring: {e}") from e
            
            # Check orders scoring from CLOB API
            # Reference: POST /<clob-endpoint>/orders-scoring
            url = f"{self._base_url}/orders-scoring"
            request_body = {"orderIds": params.order_ids}
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json", "content-type": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, json=request_body, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response - API returns OrdersScoring (dictionary mapping order IDs to booleans)
            if not isinstance(response_data, dict):
                raise PolymarketClientError(f"Unexpected response format from orders-scoring endpoint: {type(response_data)}")
            
            # Convert response to typed dictionary
            # Response format: { "order_id": bool, ... }
            scoring_batch: OrdersScoringBatch = {}
            for order_id, scoring_value in response_data.items():
                if isinstance(order_id, str):
                    scoring_batch[order_id] = bool(scoring_value)
            
            return scoring_batch

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to check orders scoring: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to check orders scoring: {e}") from e

    def get_orders(self, market_id: Optional[str] = None) -> list[BaseOrder]:
        """Fetch user's orders.

        Args:
            market_id: Optional market ID to filter orders.

        Returns:
            List of user's orders.

        Raises:
            PolymarketClientError: When fetching orders fails.
            ValueError: If client is read-only.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get orders: client is read-only. Provide private_key to enable write operations.")

        try:
            # Set API credentials (required for Level 2 authentication)
            # get_orders() requires API credentials, not just private key
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for get_orders: {e}") from e
            
            # Get all orders or filter by market
            if market_id:
                orders = self._clob_client.get_orders(market_id=market_id)
            else:
                orders = self._clob_client.get_orders()

            if not isinstance(orders, list):
                return []

            # Parse orders - this is a simplified version, adjust based on actual API response
            parsed_orders: list[BaseOrder] = []
            for order in orders:
                if isinstance(order, dict):
                    parsed_orders.append(
                        BaseOrder(
                            order_id=str(order.get("orderID", order.get("order_id", ""))),
                            token_id=str(order.get("tokenID", order.get("token_id", ""))),
                            side=str(order.get("side", "")),
                            price=float(order.get("price", 0.0)),
                            size=float(order.get("size", 0.0)),
                            filled=float(order.get("filled", 0.0)),
                            status=str(order.get("status", "PENDING")),
                        )
                    )

            return parsed_orders

        except Exception as e:
            raise PolymarketClientError(f"Failed to fetch orders: {e}") from e

    def merge_orders(self, order_ids: list[str]) -> dict[str, Any]:
        """Merge multiple orders into a single order.

        Args:
            order_ids: List of order IDs to merge.

        Returns:
            Dictionary with merge result information.

        Raises:
            PolymarketClientError: When merge fails.
            ValueError: If client is read-only.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot merge orders: client is read-only. Provide private_key to enable write operations.")

        try:
            # Check if merge method exists in py-clob-client
            if hasattr(self._clob_client, "merge_orders"):
                response = self._clob_client.merge_orders(order_ids)
                return response if isinstance(response, dict) else {"response": str(response)}
            else:
                # Fallback: cancel old orders and create new combined order
                # This is a simplified implementation
                raise PolymarketClientError("Merge orders not directly supported. Consider canceling and recreating orders.")
        except Exception as e:
            raise PolymarketClientError(f"Failed to merge orders: {e}") from e

    def get_balance_allowance(self) -> dict[str, Any]:
        """Get balance and allowance information for the wallet address.
        
        Uses the CLOB API endpoint: /balance-allowance
        
        Returns:
            Dictionary with balance and allowance information.
            
        Raises:
            PolymarketClientError: When fetching balance fails.
            ValueError: If client is read-only (no private key).
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get balance: client is read-only. Provide private_key to enable authenticated operations.")
        
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")
        
        try:
            # Set API credentials first (required for authenticated endpoints)
            api_creds = self._clob_client.create_or_derive_api_creds()
            self._clob_client.set_api_creds(api_creds)
            
            # Get wallet address from private key
            from eth_account import Account
            account = Account.from_key(self._private_key)
            wallet_address = account.address
            
            # Call the balance-allowance endpoint
            url = f"{self._base_url}/balance-allowance"
            params = {"address": wallet_address}
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"{error_msg} - {error_detail}"
                except Exception:
                    error_msg = f"{error_msg} - Status: {e.response.status_code}"
            raise PolymarketClientError(f"Failed to fetch balance-allowance: {error_msg}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to get balance-allowance: {e}") from e
    
    @dataclass
    class Position:
        """Polymarket position data structure from Data API.
        
        Represents a user's position in a Polymarket market.
        """
        proxy_wallet: str
        asset: str
        condition_id: str
        size: float
        avg_price: float
        initial_value: float
        current_value: float
        cash_pnl: float
        percent_pnl: float
        total_bought: float
        realized_pnl: float
        percent_realized_pnl: float
        cur_price: float
        redeemable: bool
        mergeable: bool
        title: str
        slug: str
        icon: str
        event_id: str
        event_slug: str
        outcome: str  # "YES" or "NO"
        outcome_index: int  # 0 or 1
        opposite_outcome: str
        opposite_asset: str
        end_date: str  # "YYYY-MM-DD" or empty string
        negative_risk: bool
        
        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "PolymarketClient.Position":
            """Create Position from API response dictionary.
            
            Args:
                data: Dictionary from Polymarket Data API response.
                
            Returns:
                Position instance.
            """
            return cls(
                proxy_wallet=data.get("proxyWallet", ""),
                asset=data.get("asset", ""),
                condition_id=data.get("conditionId", ""),
                size=float(data.get("size", 0)),
                avg_price=float(data.get("avgPrice", 0)),
                initial_value=float(data.get("initialValue", 0)),
                current_value=float(data.get("currentValue", 0)),
                cash_pnl=float(data.get("cashPnl", 0)),
                percent_pnl=float(data.get("percentPnl", 0)),
                total_bought=float(data.get("totalBought", 0)),
                realized_pnl=float(data.get("realizedPnl", 0)),
                percent_realized_pnl=float(data.get("percentRealizedPnl", 0)),
                cur_price=float(data.get("curPrice", 0)),
                redeemable=bool(data.get("redeemable", False)),
                mergeable=bool(data.get("mergeable", False)),
                title=data.get("title", ""),
                slug=data.get("slug", ""),
                icon=data.get("icon", ""),
                event_id=data.get("eventId", ""),
                event_slug=data.get("eventSlug", ""),
                outcome=data.get("outcome", ""),
                outcome_index=int(data.get("outcomeIndex", 0)),
                opposite_outcome=data.get("oppositeOutcome", ""),
                opposite_asset=data.get("oppositeAsset", ""),
                end_date=data.get("endDate", ""),
                negative_risk=bool(data.get("negativeRisk", False)),
            )
        
        def to_dict(self) -> dict[str, Any]:
            """Convert Position to dictionary (matches API response format).
            
            Returns:
                Dictionary matching API response format.
            """
            return {
                "proxyWallet": self.proxy_wallet,
                "asset": self.asset,
                "conditionId": self.condition_id,
                "size": self.size,
                "avgPrice": self.avg_price,
                "initialValue": self.initial_value,
                "currentValue": self.current_value,
                "cashPnl": self.cash_pnl,
                "percentPnl": self.percent_pnl,
                "totalBought": self.total_bought,
                "realizedPnl": self.realized_pnl,
                "percentRealizedPnl": self.percent_realized_pnl,
                "curPrice": self.cur_price,
                "redeemable": self.redeemable,
                "mergeable": self.mergeable,
                "title": self.title,
                "slug": self.slug,
                "icon": self.icon,
                "eventId": self.event_id,
                "eventSlug": self.event_slug,
                "outcome": self.outcome,
                "outcomeIndex": self.outcome_index,
                "oppositeOutcome": self.opposite_outcome,
                "oppositeAsset": self.opposite_asset,
                "endDate": self.end_date,
                "negativeRisk": self.negative_risk,
            }
    
    def get_positions(
        self,
        user_address: Optional[str] = None,
        market: Optional[list[str]] = None,
        size_threshold: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> list["PolymarketClient.Position"]:
        """Fetch current positions from Polymarket Data API.
        
        Uses the Polymarket Data API endpoint: GET /positions
        Matches curl: curl -X GET "https://data-api.polymarket.com/positions?user=0xADDRESS" -H "accept: application/json"
        
        Reference: https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
        
        Args:
            user_address: User wallet address (0x-prefixed). If None, auto-derives from private_key.
            market: Optional list of condition IDs to filter by (comma-separated in API).
            size_threshold: Optional minimum position size to include. If None, not sent to API.
            limit: Optional maximum number of results. If None, not sent to API.
            
        Returns:
            List of Position objects.
            
        Raises:
            PolymarketClientError: When fetching positions fails.
        """
        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")
        
        # Get user address - try from private key if not provided
        if not user_address:
            if self._private_key:
                try:
                    from eth_account import Account
                    account = Account.from_key(self._private_key)
                    user_address = account.address
                except Exception as e:
                    raise PolymarketClientError(f"user_address is required or private_key must be set: {e}")
            else:
                raise PolymarketClientError("user_address is required (or provide private_key to auto-derive)")
        
        # Validate address format (0x-prefixed, 40 hex chars)
        if not user_address.startswith("0x") or len(user_address) != 42:
            raise PolymarketClientError(f"Invalid address format: {user_address}. Expected 0x-prefixed 40 hex characters.")
        
        try:
            # Use Data API endpoint: https://data-api.polymarket.com/positions
            # Match curl command exactly: only send 'user' parameter by default
            url = "https://data-api.polymarket.com/positions"
            params = {
                "user": user_address,  # Required: User address (0x-prefixed)
            }
            
            # Only add optional parameters if explicitly provided (to match curl command)
            if size_threshold is not None:
                params["sizeThreshold"] = size_threshold
            
            if limit is not None:
                params["limit"] = limit
            
            # Add market filter if provided (condition IDs)
            # API expects comma-separated list, but we accept list and convert
            if market:
                if isinstance(market, list):
                    # Convert list to comma-separated string for API
                    params["market"] = ",".join(market)
                else:
                    params["market"] = market
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=params, headers={"accept": "application/json"})
                response.raise_for_status()
                positions_data = response.json()
                
                # Convert dictionaries to Position objects
                positions = [
                    self.Position.from_dict(pos) for pos in positions_data
                ]
                
                # Filter out positions with size < threshold if threshold was provided
                if size_threshold is not None:
                    filtered_positions = [
                        pos for pos in positions
                        if pos.size >= size_threshold
                    ]
                    return filtered_positions
                else:
                    # Return all positions if no threshold specified
                    return positions
        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch positions from Polymarket API: {e}") from e
        except Exception as e:
            raise PolymarketClientError(f"Failed to parse positions: {e}") from e

    def get_usdc_balance(self) -> float:
        """Get USDC balance for the wallet.
        
        Returns:
            USDC balance as float.
            
        Raises:
            PolymarketClientError: When fetching balance fails.
        """
        try:
            balance_data = self.get_balance_allowance()
            # The response structure may vary - try common field names
            usdc_balance = balance_data.get("usdc_balance") or balance_data.get("balance") or balance_data.get("available")
            if usdc_balance is None:
                # Try nested structure
                if "balances" in balance_data:
                    usdc_balance = balance_data["balances"].get("USDC") or balance_data["balances"].get("usdc")
                elif "balance" in balance_data and isinstance(balance_data["balance"], dict):
                    usdc_balance = balance_data["balance"].get("USDC") or balance_data["balance"].get("usdc")
            
            if usdc_balance is None:
                raise PolymarketClientError("Could not find USDC balance in response")
            
            return float(usdc_balance)
        except Exception as e:
            if isinstance(e, PolymarketClientError):
                raise
            raise PolymarketClientError(f"Failed to get USDC balance: {e}") from e
    
    def get_token_balance(self, token_id: str) -> float:
        """Get balance for a specific token.
        
        Args:
            token_id: Token identifier.
            
        Returns:
            Token balance as float.
            
        Raises:
            PolymarketClientError: When fetching balance fails.
        """
        try:
            balance_data = self.get_balance_allowance()
            # The response may contain token balances in various formats
            # Try different possible structures
            if "balances" in balance_data:
                token_balance = balance_data["balances"].get(token_id)
                if token_balance is not None:
                    return float(token_balance)
            
            if "token_balances" in balance_data:
                for token_bal in balance_data["token_balances"]:
                    if isinstance(token_bal, dict) and token_bal.get("token_id") == token_id:
                        return float(token_bal.get("balance", 0.0))
            
            # If token not found, return 0.0 (no balance)
            return 0.0
        except Exception as e:
            if isinstance(e, PolymarketClientError):
                raise
            raise PolymarketClientError(f"Failed to get token balance for {token_id}: {e}") from e

    # Onchain event parsing methods
    def get_order_filled_events_from_tx(
        self,
        transaction_hash: str,
    ) -> list[OrderFilled]:
        """Get OrderFilled events from a transaction hash.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/onchain-order-info
        
        Parses OrderFilled events emitted by the Exchange contract in a transaction.
        This is useful when you have transaction hashes from order placement responses.

        Args:
            transaction_hash: Transaction hash to parse events from.

        Returns:
            List of OrderFilled events found in the transaction.

        Raises:
            PolymarketClientError: When parsing events fails.
        """
        if Web3 is None:
            raise PolymarketClientError(
                "web3 library is required for onchain event parsing. Install it with: pip install web3"
            )

        try:
            web3 = self._web3_client
            tx_receipt = web3.eth.get_transaction_receipt(transaction_hash)
            
            if tx_receipt is None:
                raise PolymarketClientError(f"Transaction {transaction_hash} not found")
            
            # OrderFilled event signature: OrderFilled(bytes32 orderHash, address maker, address taker, uint256 makerAssetId, uint256 takerAssetId, uint256 makerAmountFilled, uint256 takerAmountFilled, uint256 fee)
            event_signature = web3.keccak(text="OrderFilled(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")
            
            order_filled_events: list[OrderFilled] = []
            
            for log in tx_receipt["logs"]:
                # Check if log is from Exchange contract
                if log["address"].lower() != self._exchange_contract_address.lower():
                    continue
                
                # Check if this is an OrderFilled event (first topic is event signature)
                if len(log["topics"]) > 0 and log["topics"][0] == event_signature:
                    # Decode the event
                    # Topics: [event_signature, orderHash, maker, taker]
                    # Data: [makerAssetId, takerAssetId, makerAmountFilled, takerAmountFilled, fee]
                    
                    order_hash = log["topics"][1].hex() if isinstance(log["topics"][1], bytes) else log["topics"][1]
                    maker = web3.to_checksum_address(log["topics"][2].hex()[-40:] if isinstance(log["topics"][2], bytes) else log["topics"][2].hex()[-40:])
                    taker = web3.to_checksum_address(log["topics"][3].hex()[-40:] if isinstance(log["topics"][3], bytes) else log["topics"][3].hex()[-40:])
                    
                    # Decode data (5 uint256 values)
                    data = log["data"]
                    if isinstance(data, str):
                        data = bytes.fromhex(data[2:] if data.startswith("0x") else data)
                    
                    # Each uint256 is 32 bytes
                    maker_asset_id = str(int.from_bytes(data[0:32], byteorder="big"))
                    taker_asset_id = str(int.from_bytes(data[32:64], byteorder="big"))
                    maker_amount_filled = str(int.from_bytes(data[64:96], byteorder="big"))
                    taker_amount_filled = str(int.from_bytes(data[96:128], byteorder="big"))
                    fee = str(int.from_bytes(data[128:160], byteorder="big"))
                    
                    order_filled_events.append(
                        OrderFilled(
                            order_hash=order_hash,
                            maker=maker,
                            taker=taker,
                            maker_asset_id=maker_asset_id,
                            taker_asset_id=taker_asset_id,
                            maker_amount_filled=maker_amount_filled,
                            taker_amount_filled=taker_amount_filled,
                            fee=fee,
                            transaction_hash=transaction_hash,
                            block_number=tx_receipt["blockNumber"],
                            log_index=log["logIndex"],
                        )
                    )
            
            return order_filled_events

        except Exception as e:
            raise PolymarketClientError(f"Failed to parse OrderFilled events from transaction {transaction_hash}: {e}") from e

    def get_order_filled_events(
        self,
        order_hash: str,
        from_block: Optional[int] = None,
        to_block: Optional[int] = None,
    ) -> list[OrderFilled]:
        """Get OrderFilled events for a specific order hash.
        
        Reference: https://docs.polymarket.com/developers/CLOB/orders/onchain-order-info
        
        Searches for OrderFilled events matching a specific order hash across blocks.
        This is useful for tracking all fills of a specific order.

        Args:
            order_hash: Order hash to search for (from OrderResponse.order_hashes or OpenOrder.id).
            from_block: Starting block number to search from (optional).
            to_block: Ending block number to search to (optional, defaults to latest).

        Returns:
            List of OrderFilled events matching the order hash.

        Raises:
            PolymarketClientError: When searching for events fails.
        """
        if Web3 is None:
            raise PolymarketClientError(
                "web3 library is required for onchain event parsing. Install it with: pip install web3"
            )

        try:
            web3 = self._web3_client
            
            # OrderFilled event signature
            event_signature = web3.keccak(text="OrderFilled(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")
            
            # Prepare order hash topic (orderHash is bytes32, so it's already 32 bytes)
            # The order hash should be used directly as a topic (padded to 32 bytes)
            if order_hash.startswith("0x"):
                order_hash_hex = order_hash[2:]
            else:
                order_hash_hex = order_hash
            
            # Pad to 64 hex characters (32 bytes)
            if len(order_hash_hex) < 64:
                order_hash_hex = "0" * (64 - len(order_hash_hex)) + order_hash_hex
            elif len(order_hash_hex) > 64:
                order_hash_hex = order_hash_hex[-64:]
            
            # Convert to bytes32 topic
            order_hash_topic = bytes.fromhex(order_hash_hex)
            
            # Build filter
            filter_params: dict[str, Any] = {
                "address": self._exchange_contract_address,
                "topics": [event_signature, order_hash_topic],
            }
            
            if from_block is not None:
                filter_params["fromBlock"] = from_block
            if to_block is not None:
                filter_params["toBlock"] = to_block
            
            # Get events
            events = web3.eth.get_logs(filter_params)
            
            order_filled_events: list[OrderFilled] = []
            
            for event_log in events:
                # Get transaction receipt to get full event data
                tx_receipt = web3.eth.get_transaction_receipt(event_log["transactionHash"].hex())
                
                # Find the matching log
                for log in tx_receipt["logs"]:
                    if log["logIndex"] == event_log["logIndex"]:
                        # Decode the event (same logic as get_order_filled_events_from_tx)
                        order_hash_decoded = log["topics"][1].hex() if isinstance(log["topics"][1], bytes) else log["topics"][1]
                        maker = web3.to_checksum_address(log["topics"][2].hex()[-40:] if isinstance(log["topics"][2], bytes) else log["topics"][2].hex()[-40:])
                        taker = web3.to_checksum_address(log["topics"][3].hex()[-40:] if isinstance(log["topics"][3], bytes) else log["topics"][3].hex()[-40:])
                        
                        data = log["data"]
                        if isinstance(data, str):
                            data = bytes.fromhex(data[2:] if data.startswith("0x") else data)
                        
                        maker_asset_id = str(int.from_bytes(data[0:32], byteorder="big"))
                        taker_asset_id = str(int.from_bytes(data[32:64], byteorder="big"))
                        maker_amount_filled = str(int.from_bytes(data[64:96], byteorder="big"))
                        taker_amount_filled = str(int.from_bytes(data[96:128], byteorder="big"))
                        fee = str(int.from_bytes(data[128:160], byteorder="big"))
                        
                        order_filled_events.append(
                            OrderFilled(
                                order_hash=order_hash_decoded,
                                maker=maker,
                                taker=taker,
                                maker_asset_id=maker_asset_id,
                                taker_asset_id=taker_asset_id,
                                maker_amount_filled=maker_amount_filled,
                                taker_amount_filled=taker_amount_filled,
                                fee=fee,
                                transaction_hash=event_log["transactionHash"].hex(),
                                block_number=event_log["blockNumber"],
                                log_index=event_log["logIndex"],
                            )
                        )
                        break
            
            return order_filled_events

        except Exception as e:
            raise PolymarketClientError(f"Failed to get OrderFilled events for order {order_hash}: {e}") from e

    def get_address(self) -> str:
        """Get the wallet address associated with this client.
        
        Returns:
            Ethereum address (checksummed) of the wallet.
            
        Raises:
            PolymarketClientError: When address cannot be determined.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get address: client is read-only. Provide private_key to enable address derivation.")
        
        try:
            # Try to get address from clob client
            if hasattr(self._clob_client, "get_address"):
                return self._clob_client.get_address()
            
            # Fallback: derive from private key using eth-account
            try:
                from eth_account import Account
                account = Account.from_key(self._private_key)
                return account.address
            except ImportError:
                raise PolymarketClientError("eth-account library is required. Install it with: pip install eth-account")
        except Exception as e:
            raise PolymarketClientError(f"Failed to get address: {e}") from e

    # Trade methods
    def get_trades(
        self,
        params: Optional[GetTradesParams] = None,
    ) -> list[Trade]:
        """Get trades for the authenticated user based on provided filters.
        
        Reference: https://docs.polymarket.com/developers/CLOB/trades/trades
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            params: Optional query parameters to filter trades:
                - id: id of trade to fetch
                - taker: address to get trades for where it is included as a taker
                - maker: address to get trades for where it is included as a maker
                - market: market for which to get the trades (condition ID)
                - before: unix timestamp representing cutoff up to which trades happened before
                - after: unix timestamp representing cutoff for which trades happened after
                
            If params is None, returns all trades for the authenticated user.

        Returns:
            List of Trade objects filtered by the query parameters.
            Each Trade contains:
            - id: trade id
            - taker_order_id: hash of taker order that catalyzed the trade
            - market: market id (condition id)
            - asset_id: asset id (token id) of taker order
            - side: buy or sell
            - size: size
            - fee_rate_bps: fees paid expressed in basic points
            - price: limit price of taker order
            - status: trade status (MATCHED, MINED, CONFIRMED, RETRYING, FAILED)
            - match_time: time at which the trade was matched
            - last_update: timestamp of last status update
            - outcome: human readable outcome
            - maker_address: funder address of the taker
            - owner: api key of taker
            - transaction_hash: hash of transaction where trade was executed
            - bucket_index: index of bucket for multi-transaction trades
            - maker_orders: list of maker orders the taker trade was filled against
            - type: side of the trade (TAKER or MAKER)

        Raises:
            PolymarketClientError: When fetching trades fails.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get trades: client is read-only. Provide private_key to enable authenticated operations.")

        if httpx is None:
            raise PolymarketClientError("httpx library is required. Install it with: pip install httpx")

        try:
            # Set API credentials (required for L2 Header)
            try:
                api_creds = self._clob_client.create_or_derive_api_creds()
                self._clob_client.set_api_creds(api_creds)
            except Exception as e:
                raise PolymarketClientError(f"Failed to set API credentials for get_trades: {e}") from e
            
            # Get trades from CLOB API
            # Reference: GET /<clob-endpoint>/data/trades
            url = f"{self._base_url}/data/trades"
            
            # Build query parameters
            query_params: dict[str, str] = {}
            if params is not None:
                query_params = params.to_query_params()
            
            # Get auth headers from clob client if available
            headers = {"accept": "application/json"}
            if hasattr(self._clob_client, "get_auth_headers"):
                auth_headers = self._clob_client.get_auth_headers()
                headers.update(auth_headers)
            elif hasattr(self._clob_client, "_get_headers"):
                auth_headers = self._clob_client._get_headers()
                headers.update(auth_headers)
            
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(url, params=query_params, headers=headers)
                response.raise_for_status()
                response_data = response.json()

            # Parse response - API returns Trade[] (list of trades)
            if not isinstance(response_data, list):
                # Handle case where response might be wrapped or empty
                if response_data is None:
                    return []
                if isinstance(response_data, dict) and "trades" in response_data:
                    response_data = response_data["trades"]
                else:
                    return []
            
            # Parse each trade in the list
            trades: list[Trade] = []
            for trade_data in response_data:
                if isinstance(trade_data, dict):
                    try:
                        trades.append(Trade.from_payload(trade_data))
                    except Exception as e:
                        # Skip invalid trade entries but continue processing others
                        continue
            
            return trades

        except httpx.HTTPError as e:
            raise PolymarketClientError(f"Failed to fetch trades: {e}") from e
        except PolymarketClientError:
            # Re-raise PolymarketClientError as-is
            raise
        except Exception as e:
            raise PolymarketClientError(f"Failed to get trades: {e}") from e

    def get_trade(self, trade_id: str) -> Optional[Trade]:
        """Get a single trade by ID.
        
        Reference: https://docs.polymarket.com/developers/CLOB/trades/trades
        
        This endpoint requires a L2 Header (API credentials).

        Args:
            trade_id: The trade ID to retrieve.

        Returns:
            Trade object if found, None otherwise.

        Raises:
            PolymarketClientError: When fetching the trade fails.
        """
        params = GetTradesParams(id=trade_id)
        trades = self.get_trades(params=params)
        
        if not trades:
            return None
        
        # Should only be one trade when filtering by ID
        return trades[0] if trades else None

    @staticmethod
    def reconcile_trades(trades: list[Trade]) -> list[Trade]:
        """Reconcile multi-transaction trades into single trade objects.
        
        Reference: https://docs.polymarket.com/developers/CLOB/trades/trades-overview
        
        When trades are broken into multiple transactions due to gas limitations,
        they share the same market_order_id, match_time, and have incrementing bucket_index.
        This method combines such trades into a single trade object.
        
        Args:
            trades: List of trades to reconcile.

        Returns:
            List of reconciled trades. Trades with same market_order_id and match_time
            are combined, with maker_orders aggregated and sizes summed.
        """
        if not trades:
            return []
        
        # Group trades by (taker_order_id, match_time)
        # Note: The docs mention market_order_id, but the API uses taker_order_id
        trade_groups: dict[tuple[str, str], list[Trade]] = {}
        
        for trade in trades:
            key = (trade.taker_order_id, trade.match_time)
            if key not in trade_groups:
                trade_groups[key] = []
            trade_groups[key].append(trade)
        
        reconciled: list[Trade] = []
        
        for group_trades in trade_groups.values():
            if len(group_trades) == 1:
                # Single trade, no reconciliation needed
                reconciled.append(group_trades[0])
            else:
                # Multiple trades to reconcile
                # Sort by bucket_index
                sorted_trades = sorted(group_trades, key=lambda t: t.bucket_index)
                
                # Use the first trade as the base
                base_trade = sorted_trades[0]
                
                # Aggregate maker orders from all trades
                all_maker_orders: list[MakerOrder] = []
                for trade in sorted_trades:
                    all_maker_orders.extend(trade.maker_orders)
                
                # Sum sizes (convert to float, sum, convert back to string)
                total_size = sum(float(trade.size) for trade in sorted_trades)
                
                # Create reconciled trade
                reconciled_trade = Trade(
                    id=base_trade.id,  # Use first trade's ID
                    taker_order_id=base_trade.taker_order_id,
                    market=base_trade.market,
                    asset_id=base_trade.asset_id,
                    side=base_trade.side,
                    size=str(total_size),
                    fee_rate_bps=base_trade.fee_rate_bps,
                    price=base_trade.price,
                    status=base_trade.status,  # Use most recent status
                    match_time=base_trade.match_time,
                    last_update=max(trade.last_update for trade in sorted_trades),
                    outcome=base_trade.outcome,
                    maker_address=base_trade.maker_address,
                    owner=base_trade.owner,
                    transaction_hash=base_trade.transaction_hash,  # First transaction
                    bucket_index=0,  # Reset to 0 for reconciled trade
                    maker_orders=all_maker_orders,
                    type=base_trade.type,
                )
                
                reconciled.append(reconciled_trade)
        
        return reconciled

    def get_api_credentials(self) -> dict[str, str]:
        """Get API credentials for WebSocket authentication.
        
        Reference: https://docs.polymarket.com/developers/CLOB/websocket/wss-auth
        
        Derives API credentials (apiKey, secret, passphrase) from the client's private key.
        These credentials are required for USER channel WebSocket connections.
        
        Returns:
            Dictionary with apiKey, secret, and passphrase.
            
        Raises:
            PolymarketClientError: When credentials cannot be derived.
        """
        if self._is_read_only:
            raise PolymarketClientError("Cannot get API credentials: client is read-only. Provide private_key to enable authentication.")
        
        try:
            # Derive API credentials from clob client
            api_creds = self._clob_client.create_or_derive_api_creds()
            
            # Extract credentials
            # The structure may vary, try common field names
            if isinstance(api_creds, dict):
                api_key = api_creds.get("apiKey") or api_creds.get("api_key") or api_creds.get("key", "")
                secret = api_creds.get("secret") or api_creds.get("api_secret", "")
                passphrase = api_creds.get("passphrase") or api_creds.get("api_passphrase", "")
            else:
                # Try to get from attributes
                api_key = getattr(api_creds, "apiKey", getattr(api_creds, "api_key", getattr(api_creds, "key", "")))
                secret = getattr(api_creds, "secret", getattr(api_creds, "api_secret", ""))
                passphrase = getattr(api_creds, "passphrase", getattr(api_creds, "api_passphrase", ""))
            
            if not api_key or not secret or not passphrase:
                raise PolymarketClientError("Failed to extract API credentials. Ensure client is properly authenticated.")
            
            return {
                "apiKey": str(api_key),
                "secret": str(secret),
                "passphrase": str(passphrase),
            }
        except Exception as e:
            raise PolymarketClientError(f"Failed to get API credentials: {e}") from e

    def create_websocket_client(
        self,
        message_callback: Optional[Callable[[str, dict[str, Any]], None]] = None,
        user_message_callback: Optional[Callable[[Any], None]] = None,
        market_message_callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        close_callback: Optional[Callable[[int, str], None]] = None,
        verbose: bool = False,
    ) -> Any:  # PolymarketWebSocketClient
        """Create a WebSocket client with authentication from this client.
        
        Reference: https://docs.polymarket.com/developers/CLOB/websocket/wss-overview
        
        Creates a WebSocket client pre-configured with authentication credentials
        derived from this client. This allows easy access to USER channel updates.
        
        Args:
            message_callback: Optional callback for received messages.
                Signature: callback(channel: str, message: dict[str, Any]) -> None
            error_callback: Optional callback for errors.
                Signature: callback(error: Exception) -> None
            close_callback: Optional callback for connection close.
                Signature: callback(status_code: int, message: str) -> None
            verbose: Enable verbose logging.
        
        Returns:
            PolymarketWebSocketClient instance with authentication configured.
            
        Raises:
            PolymarketClientError: When client is read-only or credentials cannot be derived.
        """
        from .websocket import PolymarketWebSocketClient, WebSocketAuth
        
        # Get API credentials
        creds = self.get_api_credentials()
        auth = WebSocketAuth(
            api_key=creds["apiKey"],
            secret=creds["secret"],
            passphrase=creds["passphrase"],
        )
        
        return PolymarketWebSocketClient(
            auth=auth,
            message_callback=message_callback,
            user_message_callback=user_message_callback,
            market_message_callback=market_message_callback,
            error_callback=error_callback,
            close_callback=close_callback,
            verbose=verbose,
        )

    def close(self) -> None:
        """Close the client (cleanup if needed)."""
        self._client = None
        self._web3 = None


__all__ = [
    "Category",
    "Event",
    "ImageOptimized",
    "Market",
    "OrderBook",
    "OrderBookLevel",
    "PolymarketClient",
    "PolymarketClientError",
    "Tag",
]

