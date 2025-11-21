"""Polymarket-specific data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .base import BaseMarket, BaseOrderBook, BaseOrderBookLevel


@dataclass
class GetMarketsParams:
    """Query parameters for the GET /markets endpoint.
    
    Reference: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
    """
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: Optional[str] = None  # Comma-separated list of fields to order by
    ascending: Optional[bool] = None
    id: Optional[list[int]] = None
    slug: Optional[list[str]] = None
    clob_token_ids: Optional[list[str]] = None
    condition_ids: Optional[list[str]] = None
    market_maker_address: Optional[list[str]] = None
    liquidity_num_min: Optional[float] = None
    liquidity_num_max: Optional[float] = None
    volume_num_min: Optional[float] = None
    volume_num_max: Optional[float] = None
    start_date_min: Optional[datetime] = None
    start_date_max: Optional[datetime] = None
    end_date_min: Optional[datetime] = None
    end_date_max: Optional[datetime] = None
    tag_id: Optional[int] = None
    related_tags: Optional[bool] = None
    cyom: Optional[bool] = None
    uma_resolution_status: Optional[str] = None
    game_id: Optional[str] = None
    sports_market_types: Optional[list[str]] = None
    rewards_min_size: Optional[float] = None
    question_ids: Optional[list[str]] = None
    include_tag: Optional[bool] = None
    closed: Optional[bool] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.order is not None:
            params["order"] = self.order
        if self.ascending is not None:
            params["ascending"] = self.ascending
        if self.id is not None:
            params["id"] = self.id
        if self.slug is not None:
            params["slug"] = self.slug
        if self.clob_token_ids is not None:
            params["clob_token_ids"] = self.clob_token_ids
        if self.condition_ids is not None:
            params["condition_ids"] = self.condition_ids
        if self.market_maker_address is not None:
            params["market_maker_address"] = self.market_maker_address
        if self.liquidity_num_min is not None:
            params["liquidity_num_min"] = self.liquidity_num_min
        if self.liquidity_num_max is not None:
            params["liquidity_num_max"] = self.liquidity_num_max
        if self.volume_num_min is not None:
            params["volume_num_min"] = self.volume_num_min
        if self.volume_num_max is not None:
            params["volume_num_max"] = self.volume_num_max
        if self.start_date_min is not None:
            params["start_date_min"] = self.start_date_min.isoformat()
        if self.start_date_max is not None:
            params["start_date_max"] = self.start_date_max.isoformat()
        if self.end_date_min is not None:
            params["end_date_min"] = self.end_date_min.isoformat()
        if self.end_date_max is not None:
            params["end_date_max"] = self.end_date_max.isoformat()
        if self.tag_id is not None:
            params["tag_id"] = self.tag_id
        if self.related_tags is not None:
            params["related_tags"] = self.related_tags
        if self.cyom is not None:
            params["cyom"] = self.cyom
        if self.uma_resolution_status is not None:
            params["uma_resolution_status"] = self.uma_resolution_status
        if self.game_id is not None:
            params["game_id"] = self.game_id
        if self.sports_market_types is not None:
            params["sports_market_types"] = self.sports_market_types
        if self.rewards_min_size is not None:
            params["rewards_min_size"] = self.rewards_min_size
        if self.question_ids is not None:
            params["question_ids"] = self.question_ids
        if self.include_tag is not None:
            params["include_tag"] = self.include_tag
        if self.closed is not None:
            params["closed"] = self.closed
        
        return params


@dataclass(slots=True)
class ImageOptimized:
    """Optimized image data structure."""

    id: str
    image_url_source: str
    image_url_optimized: str
    image_size_kb_source: float
    image_size_kb_optimized: float
    image_optimized_complete: bool
    image_optimized_last_updated: Optional[str]
    rel_id: Optional[int]
    field: Optional[str]
    relname: Optional[str]

    @staticmethod
    def from_payload(payload: dict[str, Any] | None) -> Optional["ImageOptimized"]:
        """Parse image optimized data from payload."""
        if payload is None:
            return None

        return ImageOptimized(
            id=str(payload.get("id", "")),
            image_url_source=str(payload.get("imageUrlSource", "")),
            image_url_optimized=str(payload.get("imageUrlOptimized", "")),
            image_size_kb_source=float(payload.get("imageSizeKbSource", 0.0)),
            image_size_kb_optimized=float(payload.get("imageSizeKbOptimized", 0.0)),
            image_optimized_complete=bool(payload.get("imageOptimizedComplete", False)),
            image_optimized_last_updated=payload.get("imageOptimizedLastUpdated"),
            rel_id=payload.get("relID"),
            field=payload.get("field"),
            relname=payload.get("relname"),
        )


@dataclass(slots=True)
class Category:
    """Category data structure."""

    id: str
    label: str
    parent_category: Optional[str]
    slug: str
    published_at: Optional[str]
    created_by: Optional[str]
    updated_by: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Category":
        """Parse category data from payload."""
        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError, TypeError):
                return None

        return Category(
            id=str(payload.get("id", "")),
            label=str(payload.get("label", "")),
            parent_category=payload.get("parentCategory"),
            slug=str(payload.get("slug", "")),
            published_at=payload.get("publishedAt"),
            created_by=payload.get("createdBy"),
            updated_by=payload.get("updatedBy"),
            created_at=parse_datetime(payload.get("createdAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
        )


@dataclass(slots=True)
class Tag:
    """Tag data structure."""

    id: str
    label: str
    slug: str
    force_show: Optional[bool]
    published_at: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    force_hide: Optional[bool]
    is_carousel: Optional[bool]

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Tag":
        """Parse tag data from payload."""
        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError, TypeError):
                return None

        return Tag(
            id=str(payload.get("id", "")),
            label=str(payload.get("label", "")),
            slug=str(payload.get("slug", "")),
            force_show=payload.get("forceShow"),
            published_at=payload.get("publishedAt"),
            created_by=payload.get("createdBy"),
            updated_by=payload.get("updatedBy"),
            created_at=parse_datetime(payload.get("createdAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
            force_hide=payload.get("forceHide"),
            is_carousel=payload.get("isCarousel"),
        )


@dataclass(slots=True)
class Event:
    """Event data structure (simplified - includes most important fields)."""

    id: str
    ticker: str
    slug: str
    title: str
    subtitle: Optional[str]
    description: Optional[str]
    resolution_source: Optional[str]
    start_date: Optional[datetime]
    creation_date: Optional[datetime]
    end_date: Optional[datetime]
    image: Optional[str]
    icon: Optional[str]
    active: bool
    closed: bool
    archived: bool
    new: bool
    featured: bool
    restricted: bool
    liquidity: float
    volume: float
    open_interest: Optional[float]
    category: Optional[str]
    subcategory: Optional[str]
    volume_24hr: Optional[float]
    volume_1wk: Optional[float]
    volume_1mo: Optional[float]
    volume_1yr: Optional[float]
    competitive: Optional[float]
    image_optimized: Optional[ImageOptimized]
    icon_optimized: Optional[ImageOptimized]

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Event":
        """Parse event data from payload."""
        start_date = payload.get("startDate")
        creation_date = payload.get("creationDate")
        end_date = payload.get("endDate")

        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError, TypeError):
                return None

        def parse_float(value: Any) -> Optional[float]:
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        return Event(
            id=str(payload.get("id", "")),
            ticker=str(payload.get("ticker", "")),
            slug=str(payload.get("slug", "")),
            title=str(payload.get("title", "")),
            subtitle=payload.get("subtitle"),
            description=payload.get("description"),
            resolution_source=payload.get("resolutionSource"),
            start_date=parse_datetime(start_date),
            creation_date=parse_datetime(creation_date),
            end_date=parse_datetime(end_date),
            image=payload.get("image"),
            icon=payload.get("icon"),
            active=bool(payload.get("active", False)),
            closed=bool(payload.get("closed", False)),
            archived=bool(payload.get("archived", False)),
            new=bool(payload.get("new", False)),
            featured=bool(payload.get("featured", False)),
            restricted=bool(payload.get("restricted", False)),
            liquidity=parse_float(payload.get("liquidity")) or 0.0,
            volume=parse_float(payload.get("volume")) or 0.0,
            open_interest=parse_float(payload.get("openInterest")),
            category=payload.get("category"),
            subcategory=payload.get("subcategory"),
            volume_24hr=parse_float(payload.get("volume24hr")),
            volume_1wk=parse_float(payload.get("volume1wk")),
            volume_1mo=parse_float(payload.get("volume1mo")),
            volume_1yr=parse_float(payload.get("volume1yr")),
            competitive=parse_float(payload.get("competitive")),
            image_optimized=ImageOptimized.from_payload(payload.get("imageOptimized")),
            icon_optimized=ImageOptimized.from_payload(payload.get("iconOptimized")),
        )


@dataclass(slots=True)
class Market(BaseMarket):
    """Market data structure matching the Gamma API response.
    
    Reference: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
    """

    # Core fields
    condition_id: Optional[str] = None
    slug: Optional[str] = None
    twitter_card_image: Optional[str] = None
    resolution_source: Optional[str] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    amm_type: Optional[str] = None
    liquidity_str: Optional[str] = None
    sponsor_name: Optional[str] = None
    sponsor_image: Optional[str] = None
    start_date: Optional[datetime] = None
    x_axis_value: Optional[str] = None
    y_axis_value: Optional[str] = None
    denomination_token: Optional[str] = None
    fee: Optional[str] = None
    image: Optional[str] = None
    icon: Optional[str] = None
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    description: Optional[str] = None
    outcomes: Optional[str] = None
    outcome_prices: Optional[str] = None
    volume_str: Optional[str] = None
    market_type: Optional[str] = None
    format_type: Optional[str] = None
    lower_bound_date: Optional[str] = None
    upper_bound_date: Optional[str] = None
    wide_format: Optional[bool] = None
    new: Optional[bool] = None
    featured: Optional[bool] = None
    archived: Optional[bool] = None
    resolved_by: Optional[str] = None
    restricted: Optional[bool] = None
    market_maker_address: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_time: Optional[str] = None
    mailchimp_tag: Optional[str] = None
    market_group: Optional[int] = None
    group_item_title: Optional[str] = None
    group_item_threshold: Optional[str] = None
    question_id: Optional[str] = None
    uma_end_date: Optional[str] = None
    enable_order_book: Optional[bool] = None
    order_price_min_tick_size: Optional[float] = None
    order_min_size: Optional[float] = None
    uma_resolution_status: Optional[str] = None
    curation_order: Optional[int] = None
    
    # Numeric fields
    volume_num: Optional[float] = None
    liquidity_num: Optional[float] = None
    end_date_iso: Optional[str] = None
    start_date_iso: Optional[str] = None
    uma_end_date_iso: Optional[str] = None
    has_reviewed_dates: Optional[bool] = None
    ready_for_cron: Optional[bool] = None
    comments_enabled: Optional[bool] = None
    
    # Volume fields
    volume_24hr: Optional[float] = None
    volume_1wk: Optional[float] = None
    volume_1mo: Optional[float] = None
    volume_1yr: Optional[float] = None
    volume_24hr_amm: Optional[float] = None
    volume_1wk_amm: Optional[float] = None
    volume_1mo_amm: Optional[float] = None
    volume_1yr_amm: Optional[float] = None
    volume_24hr_clob: Optional[float] = None
    volume_1wk_clob: Optional[float] = None
    volume_1mo_clob: Optional[float] = None
    volume_1yr_clob: Optional[float] = None
    volume_amm: Optional[float] = None
    volume_clob: Optional[float] = None
    liquidity_amm: Optional[float] = None
    liquidity_clob: Optional[float] = None
    
    # Trading fields
    maker_base_fee: Optional[int] = None  # API returns integer
    taker_base_fee: Optional[int] = None  # API returns integer
    custom_liveness: Optional[int] = None
    accepting_orders: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    score: Optional[int] = None
    last_trade_price: Optional[float] = None
    best_bid: Optional[float] = None
    best_ask: Optional[float] = None
    
    # Additional fields from API
    creator: Optional[str] = None
    ready: Optional[bool] = None
    funded: Optional[bool] = None
    past_slugs: Optional[str] = None
    ready_timestamp: Optional[datetime] = None
    funded_timestamp: Optional[datetime] = None
    accepting_orders_timestamp: Optional[datetime] = None
    competitive: Optional[float] = None
    rewards_min_size: Optional[float] = None
    rewards_max_spread: Optional[float] = None
    spread: Optional[float] = None
    automatically_resolved: Optional[bool] = None
    one_day_price_change: Optional[float] = None
    one_hour_price_change: Optional[float] = None
    one_week_price_change: Optional[float] = None
    one_month_price_change: Optional[float] = None
    one_year_price_change: Optional[float] = None
    automatically_active: Optional[bool] = None
    clear_book_on_start: Optional[bool] = None
    chart_color: Optional[str] = None
    series_color: Optional[str] = None
    show_gmp_series: Optional[bool] = None
    show_gmp_outcome: Optional[bool] = None
    manual_activation: Optional[bool] = None
    neg_risk_other: Optional[bool] = None
    game_id: Optional[str] = None
    group_item_range: Optional[str] = None
    sports_market_type: Optional[str] = None
    line: Optional[float] = None
    uma_resolution_statuses: Optional[str] = None
    pending_deployment: Optional[bool] = None
    deploying: Optional[bool] = None
    deploying_timestamp: Optional[datetime] = None
    scheduled_deployment_timestamp: Optional[datetime] = None
    rfq_enabled: Optional[bool] = None
    event_start_time: Optional[datetime] = None
    game_start_time: Optional[str] = None
    seconds_delay: Optional[int] = None
    clob_token_ids: Optional[str] = None  # JSON string in API
    disqus_thread: Optional[str] = None
    short_outcomes: Optional[str] = None
    team_a_id: Optional[str] = None
    team_b_id: Optional[str] = None
    uma_bond: Optional[str] = None
    uma_reward: Optional[str] = None
    fpmm_live: Optional[bool] = None
    
    # Related objects
    events: list[Event] = field(default_factory=list)
    categories: list[Category] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    image_optimized: Optional[ImageOptimized] = None
    icon_optimized: Optional[ImageOptimized] = None

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Market":
        """Parse market data from Gamma API payload.
        
        Reference: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
        """
        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None

        def parse_float(value: Any) -> Optional[float]:
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        def parse_int(value: Any) -> Optional[int]:
            if value is None:
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        def parse_bool(value: Any) -> Optional[bool]:
            if value is None:
                return None
            return bool(value)

        events_payload = payload.get("events", [])
        events = [Event.from_payload(event) for event in events_payload if isinstance(event, dict)]

        categories_payload = payload.get("categories", [])
        categories = [Category.from_payload(cat) for cat in categories_payload if isinstance(cat, dict)]

        tags_payload = payload.get("tags", [])
        tags = [Tag.from_payload(tag) for tag in tags_payload if isinstance(tag, dict)]

        volume_num = parse_float(payload.get("volumeNum"))
        liquidity_num = parse_float(payload.get("liquidityNum"))

        return Market(
            # BaseMarket fields
            id=str(payload.get("id", "")),
            question=payload.get("question"),  # API can return null
            active=parse_bool(payload.get("active")) or False,
            closed=parse_bool(payload.get("closed")) or False,
            volume=volume_num if volume_num is not None else 0.0,
            liquidity=liquidity_num if liquidity_num is not None else 0.0,
            
            # Core fields
            condition_id=payload.get("conditionId"),
            slug=payload.get("slug"),
            twitter_card_image=payload.get("twitterCardImage"),
            resolution_source=payload.get("resolutionSource"),
            end_date=parse_datetime(payload.get("endDate")),
            category=payload.get("category"),
            amm_type=payload.get("ammType"),
            liquidity_str=payload.get("liquidity"),
            sponsor_name=payload.get("sponsorName"),
            sponsor_image=payload.get("sponsorImage"),
            start_date=parse_datetime(payload.get("startDate")),
            x_axis_value=payload.get("xAxisValue"),
            y_axis_value=payload.get("yAxisValue"),
            denomination_token=payload.get("denominationToken"),
            fee=payload.get("fee"),
            image=payload.get("image"),
            icon=payload.get("icon"),
            lower_bound=payload.get("lowerBound"),
            upper_bound=payload.get("upperBound"),
            description=payload.get("description"),
            outcomes=payload.get("outcomes"),
            outcome_prices=payload.get("outcomePrices"),
            volume_str=payload.get("volume"),
            market_type=payload.get("marketType"),
            format_type=payload.get("formatType"),
            lower_bound_date=payload.get("lowerBoundDate"),
            upper_bound_date=payload.get("upperBoundDate"),
            wide_format=parse_bool(payload.get("wideFormat")),
            new=parse_bool(payload.get("new")),
            featured=parse_bool(payload.get("featured")),
            archived=parse_bool(payload.get("archived")),
            resolved_by=payload.get("resolvedBy"),
            restricted=parse_bool(payload.get("restricted")),
            market_maker_address=payload.get("marketMakerAddress"),
            created_by=parse_int(payload.get("createdBy")),
            updated_by=parse_int(payload.get("updatedBy")),
            created_at=parse_datetime(payload.get("createdAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
            closed_time=payload.get("closedTime"),
            mailchimp_tag=payload.get("mailchimpTag"),
            market_group=parse_int(payload.get("marketGroup")),
            group_item_title=payload.get("groupItemTitle"),
            group_item_threshold=payload.get("groupItemThreshold"),
            question_id=payload.get("questionID"),
            uma_end_date=payload.get("umaEndDate"),
            enable_order_book=parse_bool(payload.get("enableOrderBook")),
            order_price_min_tick_size=parse_float(payload.get("orderPriceMinTickSize")),
            order_min_size=parse_float(payload.get("orderMinSize")),
            uma_resolution_status=payload.get("umaResolutionStatus"),
            curation_order=parse_int(payload.get("curationOrder")),
            
            # Numeric and date fields
            volume_num=volume_num,
            liquidity_num=liquidity_num,
            end_date_iso=payload.get("endDateIso"),
            start_date_iso=payload.get("startDateIso"),
            uma_end_date_iso=payload.get("umaEndDateIso"),
            has_reviewed_dates=parse_bool(payload.get("hasReviewedDates")),
            ready_for_cron=parse_bool(payload.get("readyForCron")),
            comments_enabled=parse_bool(payload.get("commentsEnabled")),
            
            # Volume fields
            volume_24hr=parse_float(payload.get("volume24hr")),
            volume_1wk=parse_float(payload.get("volume1wk")),
            volume_1mo=parse_float(payload.get("volume1mo")),
            volume_1yr=parse_float(payload.get("volume1yr")),
            volume_24hr_amm=parse_float(payload.get("volume24hrAmm")),
            volume_1wk_amm=parse_float(payload.get("volume1wkAmm")),
            volume_1mo_amm=parse_float(payload.get("volume1moAmm")),
            volume_1yr_amm=parse_float(payload.get("volume1yrAmm")),
            volume_24hr_clob=parse_float(payload.get("volume24hrClob")),
            volume_1wk_clob=parse_float(payload.get("volume1wkClob")),
            volume_1mo_clob=parse_float(payload.get("volume1moClob")),
            volume_1yr_clob=parse_float(payload.get("volume1yrClob")),
            volume_amm=parse_float(payload.get("volumeAmm")),
            volume_clob=parse_float(payload.get("volumeClob")),
            liquidity_amm=parse_float(payload.get("liquidityAmm")),
            liquidity_clob=parse_float(payload.get("liquidityClob")),
            
            # Trading fields
            maker_base_fee=parse_int(payload.get("makerBaseFee")),
            taker_base_fee=parse_int(payload.get("takerBaseFee")),
            custom_liveness=parse_int(payload.get("customLiveness")),
            accepting_orders=parse_bool(payload.get("acceptingOrders")),
            notifications_enabled=parse_bool(payload.get("notificationsEnabled")),
            score=parse_int(payload.get("score")),
            last_trade_price=parse_float(payload.get("lastTradePrice")),
            best_bid=parse_float(payload.get("bestBid")),
            best_ask=parse_float(payload.get("bestAsk")),
            
            # Additional fields
            creator=payload.get("creator"),
            ready=parse_bool(payload.get("ready")),
            funded=parse_bool(payload.get("funded")),
            past_slugs=payload.get("pastSlugs"),
            ready_timestamp=parse_datetime(payload.get("readyTimestamp")),
            funded_timestamp=parse_datetime(payload.get("fundedTimestamp")),
            accepting_orders_timestamp=parse_datetime(payload.get("acceptingOrdersTimestamp")),
            competitive=parse_float(payload.get("competitive")),
            rewards_min_size=parse_float(payload.get("rewardsMinSize")),
            rewards_max_spread=parse_float(payload.get("rewardsMaxSpread")),
            spread=parse_float(payload.get("spread")),
            automatically_resolved=parse_bool(payload.get("automaticallyResolved")),
            one_day_price_change=parse_float(payload.get("oneDayPriceChange")),
            one_hour_price_change=parse_float(payload.get("oneHourPriceChange")),
            one_week_price_change=parse_float(payload.get("oneWeekPriceChange")),
            one_month_price_change=parse_float(payload.get("oneMonthPriceChange")),
            one_year_price_change=parse_float(payload.get("oneYearPriceChange")),
            automatically_active=parse_bool(payload.get("automaticallyActive")),
            clear_book_on_start=parse_bool(payload.get("clearBookOnStart")),
            chart_color=payload.get("chartColor"),
            series_color=payload.get("seriesColor"),
            show_gmp_series=parse_bool(payload.get("showGmpSeries")),
            show_gmp_outcome=parse_bool(payload.get("showGmpOutcome")),
            manual_activation=parse_bool(payload.get("manualActivation")),
            neg_risk_other=parse_bool(payload.get("negRiskOther")),
            game_id=payload.get("gameId"),
            group_item_range=payload.get("groupItemRange"),
            sports_market_type=payload.get("sportsMarketType"),
            line=parse_float(payload.get("line")),
            uma_resolution_statuses=payload.get("umaResolutionStatuses"),
            pending_deployment=parse_bool(payload.get("pendingDeployment")),
            deploying=parse_bool(payload.get("deploying")),
            deploying_timestamp=parse_datetime(payload.get("deployingTimestamp")),
            scheduled_deployment_timestamp=parse_datetime(payload.get("scheduledDeploymentTimestamp")),
            rfq_enabled=parse_bool(payload.get("rfqEnabled")),
            event_start_time=parse_datetime(payload.get("eventStartTime")),
            game_start_time=payload.get("gameStartTime"),
            seconds_delay=parse_int(payload.get("secondsDelay")),
            clob_token_ids=payload.get("clobTokenIds"),
            disqus_thread=payload.get("disqusThread"),
            short_outcomes=payload.get("shortOutcomes"),
            team_a_id=payload.get("teamAID"),
            team_b_id=payload.get("teamBID"),
            uma_bond=payload.get("umaBond"),
            uma_reward=payload.get("umaReward"),
            fpmm_live=parse_bool(payload.get("fpmmLive")),
            
            # Related objects
            events=events,
            categories=categories,
            tags=tags,
            image_optimized=ImageOptimized.from_payload(payload.get("imageOptimized")),
            icon_optimized=ImageOptimized.from_payload(payload.get("iconOptimized")),
        )


@dataclass(slots=True)
class OrderBookLevel(BaseOrderBookLevel):
    """Single level in the order book."""

    @staticmethod
    def from_payload(entry: list[float] | list[str] | dict[str, Any]) -> "OrderBookLevel":
        """Parse order book level from payload.
        
        Handles both formats:
        - List/tuple: [price, size] or (price, size)
        - Dict: {"price": "...", "size": "..."}
        """
        if isinstance(entry, dict):
            # Handle dict format: {"price": "0.01", "size": "3662.67"}
            price = float(entry.get("price", 0))
            quantity = float(entry.get("size", entry.get("quantity", entry.get("qty", 0))))
        elif isinstance(entry, (list, tuple)) and len(entry) >= 2:
            # Handle list/tuple format: [price, size]
            price = float(entry[0])
            quantity = float(entry[1])
        else:
            raise ValueError(f"Invalid order book level format: {entry}")
        
        return OrderBookLevel(
            price=price,
            quantity=quantity,
        )


@dataclass(slots=True)
class OrderBook(BaseOrderBook):
    """Order book snapshot."""

    market: str = ""
    bids: list[OrderBookLevel] = None  # type: ignore[assignment]
    asks: list[OrderBookLevel] = None  # type: ignore[assignment]
    timestamp: datetime = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Initialize default values for lists and timestamp."""
        if self.bids is None:
            self.bids = []
        if self.asks is None:
            self.asks = []
        if self.timestamp is None:
            from datetime import timezone
            self.timestamp = datetime.now(timezone.utc)

    @staticmethod
    def from_payload(payload: dict[str, Any] | Any) -> "OrderBook":
        """Parse order book from payload (dict or object from py-clob-client)."""
        # Handle both dict and object responses
        if isinstance(payload, dict):
            # Try 'market' first, fall back to 'symbol' if not present
            market = payload.get("market") or payload.get("symbol", "")
            bids_raw = payload.get("bids", [])
            asks_raw = payload.get("asks", [])
        else:
            # If it's an object, get attributes
            market = getattr(payload, "market", None) or getattr(payload, "symbol", "")
            bids_raw = getattr(payload, "bids", []) or []
            asks_raw = getattr(payload, "asks", []) or []

        # Parse bids and asks - handle both list and dict formats
        bids = []
        for bid in bids_raw:
            try:
                bids.append(OrderBookLevel.from_payload(bid))
            except (ValueError, KeyError, IndexError, TypeError):
                continue  # Skip invalid entries
        
        asks = []
        for ask in asks_raw:
            try:
                asks.append(OrderBookLevel.from_payload(ask))
            except (ValueError, KeyError, IndexError, TypeError):
                continue  # Skip invalid entries

        # Sort bids descending (best bid = highest price first)
        # Sort asks ascending (best ask = lowest price first)
        bids.sort(key=lambda x: x.price, reverse=True)
        asks.sort(key=lambda x: x.price, reverse=False)

        from datetime import timezone

        return OrderBook(
            market=market or "",  # Fixed: use 'market' not 'symbol'
            bids=bids,
            asks=asks,
            timestamp=datetime.now(timezone.utc),
        )


@dataclass
class GetActiveOrdersParams:
    """Query parameters for the GET /data/orders endpoint.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/get-active-order
    """
    
    id: Optional[str] = None  # id of order to get information about
    market: Optional[str] = None  # condition id of market
    asset_id: Optional[str] = None  # id of the asset/token
    
    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, str] = {}
        
        if self.id is not None:
            params["id"] = self.id
        if self.market is not None:
            params["market"] = self.market
        if self.asset_id is not None:
            params["asset_id"] = self.asset_id
        
        return params


@dataclass
class OrderScoringParams:
    """Parameters for checking if a single order is scoring.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/check-scoring
    """
    
    order_id: str  # id of order to get information about


@dataclass
class OrdersScoringParams:
    """Parameters for checking if multiple orders are scoring.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/check-scoring
    """
    
    order_ids: list[str]  # ids of the orders to get information about


@dataclass
class OrdersScoring:
    """Order scoring data for a single order.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/check-scoring
    """
    
    scoring: bool  # indicates if the order is scoring or not
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "OrdersScoring":
        """Parse OrdersScoring from API response payload.
        
        Args:
            payload: Raw API response dictionary.
            
        Returns:
            OrdersScoring instance.
        """
        return OrdersScoring(
            scoring=bool(payload.get("scoring", False))
        )


# Type alias for batch orders scoring response
# Dictionary mapping order IDs to boolean scoring status
OrdersScoringBatch = dict[str, bool]


@dataclass
class CancelMarketOrdersParams:
    """Parameters for canceling orders from a market.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/cancel-orders
    """
    
    market: Optional[str] = None  # condition id of the market
    asset_id: Optional[str] = None  # id of the asset/token
    
    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, str] = {}
        
        if self.market is not None:
            params["market"] = self.market
        if self.asset_id is not None:
            params["asset_id"] = self.asset_id
        
        return params


@dataclass(slots=True)
class OrderFilled:
    """OrderFilled onchain event data.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/onchain-order-info
    
    This represents an OrderFilled event emitted on-chain when an order is executed.
    """
    
    order_hash: str  # unique hash for the Order being filled
    maker: str  # user generating the order and source of funds
    taker: str  # user filling the order OR Exchange contract if fills multiple limit orders
    maker_asset_id: str  # id of asset given out (0 = BUY order, non-zero = SELL order)
    taker_asset_id: str  # id of asset received (0 = SELL order, non-zero = BUY order)
    maker_amount_filled: str  # amount of asset given out
    taker_amount_filled: str  # amount of asset received
    fee: str  # fees paid by the order maker
    transaction_hash: str  # transaction hash that emitted this event
    block_number: int  # block number where event was emitted
    log_index: int  # log index of the event
    
    @property
    def is_buy_order(self) -> bool:
        """Determine if this was a BUY order based on asset IDs.
        
        Returns:
            True if makerAssetId is 0 (BUY order), False if SELL order.
        """
        return self.maker_asset_id == "0" or self.maker_asset_id == "0x0"
    
    @property
    def is_sell_order(self) -> bool:
        """Determine if this was a SELL order based on asset IDs.
        
        Returns:
            True if makerAssetId is non-zero (SELL order), False if BUY order.
        """
        return not self.is_buy_order
    
    @staticmethod
    def from_event_log(
        event_log: dict[str, Any],
        transaction_hash: str,
        block_number: int,
        log_index: int,
    ) -> "OrderFilled":
        """Parse OrderFilled from web3 event log.
        
        Args:
            event_log: Decoded event log from web3.
            transaction_hash: Transaction hash that emitted this event.
            block_number: Block number where event was emitted.
            log_index: Log index of the event.
            
        Returns:
            OrderFilled instance.
        """
        # Handle both dict with 'args' and direct args
        if isinstance(event_log, dict) and "args" in event_log:
            args = event_log["args"]
        else:
            args = event_log
        
        # Extract values, handling both hex strings and integers
        def to_str(value: Any) -> str:
            if isinstance(value, (int, float)):
                return str(value)
            if isinstance(value, str):
                return value
            return str(value)
        
        return OrderFilled(
            order_hash=to_str(args.get("orderHash", args.get("order_hash", ""))),
            maker=to_str(args.get("maker", "")),
            taker=to_str(args.get("taker", "")),
            maker_asset_id=to_str(args.get("makerAssetId", args.get("makerAssetId", "0"))),
            taker_asset_id=to_str(args.get("takerAssetId", args.get("takerAssetId", "0"))),
            maker_amount_filled=to_str(args.get("makerAmountFilled", args.get("makerAmountFilled", "0"))),
            taker_amount_filled=to_str(args.get("takerAmountFilled", args.get("takerAmountFilled", "0"))),
            fee=to_str(args.get("fee", "0")),
            transaction_hash=transaction_hash,
            block_number=block_number,
            log_index=log_index,
        )


@dataclass(slots=True)
class MakerOrder:
    """Maker order information within a trade.
    
    Reference: https://docs.polymarket.com/developers/CLOB/trades/trades
    """
    
    order_id: str  # id of maker order
    maker_address: str  # maker address of the order
    owner: str  # api key of the owner of the order
    matched_amount: str  # size of maker order consumed with this trade
    fee_rate_bps: str  # fees paid for the taker order expressed in basic points
    price: str  # price of maker order
    asset_id: str  # token/asset id
    outcome: str  # human readable outcome of the maker order
    side: str  # the side of the maker order. Can be buy or sell
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "MakerOrder":
        """Parse MakerOrder from API response payload.
        
        Args:
            payload: Raw API response dictionary.
            
        Returns:
            MakerOrder instance.
        """
        return MakerOrder(
            order_id=str(payload.get("order_id", payload.get("orderId", ""))),
            maker_address=str(payload.get("maker_address", payload.get("makerAddress", ""))),
            owner=str(payload.get("owner", "")),
            matched_amount=str(payload.get("matched_amount", payload.get("matchedAmount", "0"))),
            fee_rate_bps=str(payload.get("fee_rate_bps", payload.get("feeRateBps", "0"))),
            price=str(payload.get("price", "0")),
            asset_id=str(payload.get("asset_id", payload.get("assetId", ""))),
            outcome=str(payload.get("outcome", "")),
            side=str(payload.get("side", "")),
        )


@dataclass(slots=True)
class Trade:
    """Trade information from the CLOB API.
    
    Reference: https://docs.polymarket.com/developers/CLOB/trades/trades
    
    A trade is initiated by a "taker" who creates a marketable limit order.
    This limit order can be matched against one or more resting limit orders.
    
    Trade statuses:
    - MATCHED: trade has been matched and sent to executor service
    - MINED: trade is observed to be mined into the chain
    - CONFIRMED: trade has achieved strong probabilistic finality (terminal)
    - RETRYING: trade transaction has failed and is being retried
    - FAILED: trade has failed and is not being retried (terminal)
    
    Note: Trades can be broken into multiple transactions due to gas limitations.
    Trades with the same market_order_id, match_time, and incrementing bucket_index
    should be combined into a single trade client-side.
    """
    
    id: str  # trade id
    taker_order_id: str  # hash of taker order (market order) that catalyzed the trade
    market: str  # market id (condition id)
    asset_id: str  # asset id (token id) of taker order (market order)
    side: str  # buy or sell
    size: str  # size
    fee_rate_bps: str  # fees paid for the taker order expressed in basic points
    price: str  # limit price of taker order
    status: str  # trade status (MATCHED, MINED, CONFIRMED, RETRYING, FAILED)
    match_time: str  # time at which the trade was matched
    last_update: str  # timestamp of last status update
    outcome: str  # human readable outcome of the trade
    maker_address: str  # funder address of the taker of the trade
    owner: str  # api key of taker of the trade
    transaction_hash: str  # hash of the transaction where the trade was executed
    bucket_index: int  # index of bucket for trade in case trade is executed in multiple transactions
    maker_orders: list[MakerOrder] = field(default_factory=list)  # list of maker orders the taker trade was filled against
    type: str = "TAKER"  # side of the trade: TAKER or MAKER
    
    @property
    def is_terminal(self) -> bool:
        """Check if trade status is terminal (CONFIRMED or FAILED).
        
        Returns:
            True if trade status is terminal, False otherwise.
        """
        return self.status.upper() in ("CONFIRMED", "FAILED")
    
    @property
    def is_confirmed(self) -> bool:
        """Check if trade is confirmed.
        
        Returns:
            True if trade status is CONFIRMED, False otherwise.
        """
        return self.status.upper() == "CONFIRMED"
    
    @property
    def is_failed(self) -> bool:
        """Check if trade has failed.
        
        Returns:
            True if trade status is FAILED, False otherwise.
        """
        return self.status.upper() == "FAILED"
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Trade":
        """Parse Trade from API response payload.
        
        Args:
            payload: Raw API response dictionary.
            
        Returns:
            Trade instance.
        """
        maker_orders_raw = payload.get("maker_orders", payload.get("makerOrders", []))
        maker_orders = (
            [MakerOrder.from_payload(mo) for mo in maker_orders_raw]
            if isinstance(maker_orders_raw, list)
            else []
        )
        
        return Trade(
            id=str(payload.get("id", "")),
            taker_order_id=str(payload.get("taker_order_id", payload.get("takerOrderId", ""))),
            market=str(payload.get("market", "")),
            asset_id=str(payload.get("asset_id", payload.get("assetId", ""))),
            side=str(payload.get("side", "")),
            size=str(payload.get("size", "0")),
            fee_rate_bps=str(payload.get("fee_rate_bps", payload.get("feeRateBps", "0"))),
            price=str(payload.get("price", "0")),
            status=str(payload.get("status", "")),
            match_time=str(payload.get("match_time", payload.get("matchTime", "0"))),
            last_update=str(payload.get("last_update", payload.get("lastUpdate", "0"))),
            outcome=str(payload.get("outcome", "")),
            maker_address=str(payload.get("maker_address", payload.get("makerAddress", ""))),
            owner=str(payload.get("owner", "")),
            transaction_hash=str(payload.get("transaction_hash", payload.get("transactionHash", ""))),
            bucket_index=int(payload.get("bucket_index", payload.get("bucketIndex", 0))),
            maker_orders=maker_orders,
            type=str(payload.get("type", "TAKER")),
        )


@dataclass
class GetTradesParams:
    """Query parameters for the GET /data/trades endpoint.
    
    Reference: https://docs.polymarket.com/developers/CLOB/trades/trades
    """
    
    id: Optional[str] = None  # id of trade to fetch
    taker: Optional[str] = None  # address to get trades for where it is included as a taker
    maker: Optional[str] = None  # address to get trades for where it is included as a maker
    market: Optional[str] = None  # market for which to get the trades (condition ID)
    before: Optional[str] = None  # unix timestamp representing cutoff up to which trades happened before
    after: Optional[str] = None  # unix timestamp representing cutoff for which trades happened after
    
    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, str] = {}
        
        if self.id is not None:
            params["id"] = self.id
        if self.taker is not None:
            params["taker"] = self.taker
        if self.maker is not None:
            params["maker"] = self.maker
        if self.market is not None:
            params["market"] = self.market
        if self.before is not None:
            params["before"] = self.before
        if self.after is not None:
            params["after"] = self.after
        
        return params


@dataclass
class CancelOrdersResponse:
    """Response from canceling orders.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/cancel-orders
    
    All cancel order endpoints return this format:
    - canceled: list of canceled order IDs
    - not_canceled: dictionary mapping order IDs to reason strings explaining why they couldn't be canceled
    """
    
    canceled: list[str]
    not_canceled: dict[str, str]
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "CancelOrdersResponse":
        """Parse CancelOrdersResponse from API response payload.
        
        Args:
            payload: Raw API response dictionary.
            
        Returns:
            CancelOrdersResponse instance.
        """
        canceled_raw = payload.get("canceled", payload.get("cancelled", []))
        canceled = [str(order_id) for order_id in canceled_raw] if isinstance(canceled_raw, list) else []
        
        not_canceled_raw = payload.get("not_canceled", payload.get("notCanceled", payload.get("not_cancelled", {})))
        not_canceled: dict[str, str] = {}
        if isinstance(not_canceled_raw, dict):
            for order_id, reason in not_canceled_raw.items():
                not_canceled[str(order_id)] = str(reason)
        
        return CancelOrdersResponse(
            canceled=canceled,
            not_canceled=not_canceled,
        )


@dataclass(slots=True)
class OpenOrder:
    """Open order information from the CLOB API.
    
    Reference: https://docs.polymarket.com/developers/CLOB/orders/get-order
    """

    id: str
    status: str
    market: str  # condition id
    original_size: str
    outcome: str
    maker_address: str
    owner: str
    price: str
    side: str
    size_matched: str
    asset_id: str  # token id
    expiration: str  # unix timestamp, 0 if doesn't expire
    type: str  # order type: GTC, FOK, GTD, FAK
    created_at: str  # unix timestamp
    associate_trades: list[str] = field(default_factory=list)

    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "OpenOrder":
        """Parse OpenOrder from API response payload.
        
        Args:
            payload: Raw API response dictionary.
            
        Returns:
            OpenOrder instance.
        """
        associate_trades_raw = payload.get("associate_trades", payload.get("associateTrades", []))
        associate_trades = (
            [str(trade) for trade in associate_trades_raw]
            if isinstance(associate_trades_raw, list)
            else []
        )

        return OpenOrder(
            id=str(payload.get("id", "")),
            status=str(payload.get("status", "")),
            market=str(payload.get("market", "")),
            original_size=str(payload.get("original_size", payload.get("originalSize", "0"))),
            outcome=str(payload.get("outcome", "")),
            maker_address=str(payload.get("maker_address", payload.get("makerAddress", ""))),
            owner=str(payload.get("owner", "")),
            price=str(payload.get("price", "0")),
            side=str(payload.get("side", "")),
            size_matched=str(payload.get("size_matched", payload.get("sizeMatched", "0"))),
            asset_id=str(payload.get("asset_id", payload.get("assetId", ""))),
            expiration=str(payload.get("expiration", "0")),
            type=str(payload.get("type", "")),
            created_at=str(payload.get("created_at", payload.get("createdAt", "0"))),
            associate_trades=associate_trades,
        )


@dataclass(slots=True)
class WebSocketMakerOrder:
    """Maker order information in WebSocket trade messages.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/user-channel
    
    This is a simplified version of MakerOrder used in WebSocket messages.
    """
    
    asset_id: str  # asset of the maker order
    matched_amount: str  # amount of maker order matched in trade
    order_id: str  # maker order ID
    outcome: str  # outcome
    owner: str  # owner of maker order
    price: str  # price of maker order
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketMakerOrder":
        """Parse WebSocketMakerOrder from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketMakerOrder instance.
        """
        return WebSocketMakerOrder(
            asset_id=str(payload.get("asset_id", "")),
            matched_amount=str(payload.get("matched_amount", "0")),
            order_id=str(payload.get("order_id", "")),
            outcome=str(payload.get("outcome", "")),
            owner=str(payload.get("owner", "")),
            price=str(payload.get("price", "0")),
        )


@dataclass(slots=True)
class WebSocketTradeMessage:
    """Trade message from User Channel WebSocket.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/user-channel
    
    Emitted when:
    - A market order is matched ("MATCHED")
    - A limit order for the user is included in a trade ("MATCHED")
    - Subsequent status changes for trade ("MINED", "CONFIRMED", "RETRYING", "FAILED")
    """
    
    asset_id: str  # asset id (token ID) of order (market order)
    event_type: str  # "trade"
    id: str  # trade id
    last_update: str  # time of last update to trade
    maker_orders: list[WebSocketMakerOrder]  # array of maker order details
    market: str  # market identifier (condition ID)
    matchtime: str  # time trade was matched
    outcome: str  # outcome
    owner: str  # api key of event owner
    price: str  # price
    side: str  # BUY/SELL
    size: str  # size
    status: str  # trade status
    taker_order_id: str  # id of taker order
    timestamp: str  # time of event
    trade_owner: str  # api key of trade owner
    type: str  # "TRADE"
    
    @property
    def is_terminal(self) -> bool:
        """Check if trade status is terminal (CONFIRMED or FAILED).
        
        Returns:
            True if trade status is terminal, False otherwise.
        """
        return self.status.upper() in ("CONFIRMED", "FAILED")
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketTradeMessage":
        """Parse WebSocketTradeMessage from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketTradeMessage instance.
        """
        maker_orders_raw = payload.get("maker_orders", [])
        maker_orders = (
            [WebSocketMakerOrder.from_payload(mo) for mo in maker_orders_raw]
            if isinstance(maker_orders_raw, list)
            else []
        )
        
        return WebSocketTradeMessage(
            asset_id=str(payload.get("asset_id", "")),
            event_type=str(payload.get("event_type", "trade")),
            id=str(payload.get("id", "")),
            last_update=str(payload.get("last_update", "0")),
            maker_orders=maker_orders,
            market=str(payload.get("market", "")),
            matchtime=str(payload.get("matchtime", "0")),
            outcome=str(payload.get("outcome", "")),
            owner=str(payload.get("owner", "")),
            price=str(payload.get("price", "0")),
            side=str(payload.get("side", "")),
            size=str(payload.get("size", "0")),
            status=str(payload.get("status", "")),
            taker_order_id=str(payload.get("taker_order_id", "")),
            timestamp=str(payload.get("timestamp", "0")),
            trade_owner=str(payload.get("trade_owner", "")),
            type=str(payload.get("type", "TRADE")),
        )


@dataclass(slots=True)
class WebSocketOrderMessage:
    """Order message from User Channel WebSocket.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/user-channel
    
    Emitted when:
    - An order is placed (PLACEMENT)
    - An order is updated (some of it is matched) (UPDATE)
    - An order is canceled (CANCELLATION)
    """
    
    asset_id: str  # asset ID (token ID) of order
    associate_trades: list[str]  # array of ids referencing trades that the order has been included in
    event_type: str  # "order"
    id: str  # order id
    market: str  # condition ID of market
    order_owner: str  # owner of order
    original_size: str  # original order size
    outcome: str  # outcome
    owner: str  # owner of orders
    price: str  # price of order
    side: str  # BUY/SELL
    size_matched: str  # size of order that has been matched
    timestamp: str  # time of event
    type: str  # PLACEMENT/UPDATE/CANCELLATION
    
    @property
    def is_placement(self) -> bool:
        """Check if this is a PLACEMENT event.
        
        Returns:
            True if type is PLACEMENT, False otherwise.
        """
        return self.type.upper() == "PLACEMENT"
    
    @property
    def is_update(self) -> bool:
        """Check if this is an UPDATE event.
        
        Returns:
            True if type is UPDATE, False otherwise.
        """
        return self.type.upper() == "UPDATE"
    
    @property
    def is_cancellation(self) -> bool:
        """Check if this is a CANCELLATION event.
        
        Returns:
            True if type is CANCELLATION, False otherwise.
        """
        return self.type.upper() == "CANCELLATION"
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketOrderMessage":
        """Parse WebSocketOrderMessage from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketOrderMessage instance.
        """
        associate_trades_raw = payload.get("associate_trades")
        associate_trades = (
            [str(trade_id) for trade_id in associate_trades_raw]
            if isinstance(associate_trades_raw, list)
            else []
        )
        
        return WebSocketOrderMessage(
            asset_id=str(payload.get("asset_id", "")),
            associate_trades=associate_trades,
            event_type=str(payload.get("event_type", "order")),
            id=str(payload.get("id", "")),
            market=str(payload.get("market", "")),
            order_owner=str(payload.get("order_owner", "")),
            original_size=str(payload.get("original_size", "0")),
            outcome=str(payload.get("outcome", "")),
            owner=str(payload.get("owner", "")),
            price=str(payload.get("price", "0")),
            side=str(payload.get("side", "")),
            size_matched=str(payload.get("size_matched", "0")),
            timestamp=str(payload.get("timestamp", "0")),
            type=str(payload.get("type", "")),
        )


# Union type for WebSocket messages
WebSocketUserMessage = WebSocketTradeMessage | WebSocketOrderMessage


@dataclass(slots=True)
class OrderSummary:
    """Order summary for Market Channel book messages.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/market-channel
    """
    
    price: str  # price of the orderbook level
    size: str  # size available at that price level
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "OrderSummary":
        """Parse OrderSummary from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            OrderSummary instance.
        """
        return OrderSummary(
            price=str(payload.get("price", "0")),
            size=str(payload.get("size", "0")),
        )


@dataclass(slots=True)
class WebSocketBookMessage:
    """Book message from Market Channel WebSocket.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/market-channel
    
    Emitted when:
    - First subscribed to a market
    - When there is a trade that affects the book
    """
    
    event_type: str  # "book"
    asset_id: str  # asset ID (token ID)
    market: str  # condition ID of market
    timestamp: str  # unix timestamp in milliseconds
    hash: str  # hash summary of the orderbook content
    buys: list[OrderSummary]  # list of aggregate book levels for buys
    sells: list[OrderSummary]  # list of aggregate book levels for sells
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketBookMessage":
        """Parse WebSocketBookMessage from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketBookMessage instance.
        """
        buys_raw = payload.get("buys", payload.get("bids", []))
        sells_raw = payload.get("sells", payload.get("asks", []))
        
        buys = (
            [OrderSummary.from_payload(b) for b in buys_raw]
            if isinstance(buys_raw, list)
            else []
        )
        sells = (
            [OrderSummary.from_payload(s) for s in sells_raw]
            if isinstance(sells_raw, list)
            else []
        )
        
        return WebSocketBookMessage(
            event_type=str(payload.get("event_type", "book")),
            asset_id=str(payload.get("asset_id", "")),
            market=str(payload.get("market", "")),
            timestamp=str(payload.get("timestamp", "0")),
            hash=str(payload.get("hash", "")),
            buys=buys,
            sells=sells,
        )


@dataclass(slots=True)
class PriceChange:
    """Price change object in Market Channel price_change messages.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/market-channel
    """
    
    asset_id: str  # asset ID (token ID)
    price: str  # price level affected
    size: str  # new aggregate size for price level
    side: str  # "BUY" or "SELL"
    hash: str  # hash of the order
    best_bid: str  # current best bid price
    best_ask: str  # current best ask price
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "PriceChange":
        """Parse PriceChange from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            PriceChange instance.
        """
        return PriceChange(
            asset_id=str(payload.get("asset_id", "")),
            price=str(payload.get("price", "0")),
            size=str(payload.get("size", "0")),
            side=str(payload.get("side", "")),
            hash=str(payload.get("hash", "")),
            best_bid=str(payload.get("best_bid", "0")),
            best_ask=str(payload.get("best_ask", "0")),
        )


@dataclass(slots=True)
class WebSocketPriceChangeMessage:
    """Price change message from Market Channel WebSocket.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/market-channel
    
    Emitted when:
    - A new order is placed
    - An order is cancelled
    """
    
    event_type: str  # "price_change"
    market: str  # condition ID of market
    price_changes: list[PriceChange]  # array of price change objects
    timestamp: str  # unix timestamp in milliseconds
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketPriceChangeMessage":
        """Parse WebSocketPriceChangeMessage from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketPriceChangeMessage instance.
        """
        price_changes_raw = payload.get("price_changes", [])
        price_changes = (
            [PriceChange.from_payload(pc) for pc in price_changes_raw]
            if isinstance(price_changes_raw, list)
            else []
        )
        
        return WebSocketPriceChangeMessage(
            event_type=str(payload.get("event_type", "price_change")),
            market=str(payload.get("market", "")),
            price_changes=price_changes,
            timestamp=str(payload.get("timestamp", "0")),
        )


@dataclass(slots=True)
class WebSocketTickSizeChangeMessage:
    """Tick size change message from Market Channel WebSocket.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/market-channel
    
    Emitted when:
    - The minimum tick size of the market changes
    - This happens when the book's price reaches the limits: price > 0.96 or price < 0.04
    """
    
    event_type: str  # "tick_size_change"
    asset_id: str  # asset ID (token ID)
    market: str  # condition ID of market
    old_tick_size: str  # previous minimum tick size
    new_tick_size: str  # current minimum tick size
    side: str  # buy/sell
    timestamp: str  # time of event
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketTickSizeChangeMessage":
        """Parse WebSocketTickSizeChangeMessage from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketTickSizeChangeMessage instance.
        """
        return WebSocketTickSizeChangeMessage(
            event_type=str(payload.get("event_type", "tick_size_change")),
            asset_id=str(payload.get("asset_id", "")),
            market=str(payload.get("market", "")),
            old_tick_size=str(payload.get("old_tick_size", "0")),
            new_tick_size=str(payload.get("new_tick_size", "0")),
            side=str(payload.get("side", "")),
            timestamp=str(payload.get("timestamp", "0")),
        )


@dataclass(slots=True)
class WebSocketLastTradePriceMessage:
    """Last trade price message from Market Channel WebSocket.
    
    Reference: https://docs.polymarket.com/developers/CLOB/websocket/market-channel
    
    Emitted when:
    - A maker and taker order is matched creating a trade event
    """
    
    event_type: str  # "last_trade_price"
    asset_id: str  # asset ID (token ID)
    fee_rate_bps: str  # fee rate in basis points
    market: str  # condition ID of market
    price: str  # trade price
    side: str  # BUY/SELL
    size: str  # trade size
    timestamp: str  # unix timestamp in milliseconds
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "WebSocketLastTradePriceMessage":
        """Parse WebSocketLastTradePriceMessage from message payload.
        
        Args:
            payload: Raw message dictionary.
            
        Returns:
            WebSocketLastTradePriceMessage instance.
        """
        return WebSocketLastTradePriceMessage(
            event_type=str(payload.get("event_type", "last_trade_price")),
            asset_id=str(payload.get("asset_id", "")),
            fee_rate_bps=str(payload.get("fee_rate_bps", "0")),
            market=str(payload.get("market", "")),
            price=str(payload.get("price", "0")),
            side=str(payload.get("side", "")),
            size=str(payload.get("size", "0")),
            timestamp=str(payload.get("timestamp", "0")),
        )


# Union type for Market Channel messages
WebSocketMarketMessage = (
    WebSocketBookMessage
    | WebSocketPriceChangeMessage
    | WebSocketTickSizeChangeMessage
    | WebSocketLastTradePriceMessage
)


@dataclass
class GetEventsParams:
    """Query parameters for the GET /events endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/events/list-events
    """
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: Optional[str] = None  # Comma-separated list of fields to order by
    ascending: Optional[bool] = None
    tag_id: Optional[int] = None
    related_tags: Optional[bool] = None
    closed: Optional[bool] = None
    exclude_tag_id: Optional[int] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.order is not None:
            params["order"] = self.order
        if self.ascending is not None:
            params["ascending"] = self.ascending
        if self.tag_id is not None:
            params["tag_id"] = self.tag_id
        if self.related_tags is not None:
            params["related_tags"] = self.related_tags
        if self.closed is not None:
            params["closed"] = self.closed
        if self.exclude_tag_id is not None:
            params["exclude_tag_id"] = self.exclude_tag_id
        
        return params


@dataclass
class GetTagsParams:
    """Query parameters for the GET /tags endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/tags/list-tags
    """
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: Optional[str] = None
    ascending: Optional[bool] = None
    include_template: Optional[bool] = None
    is_carousel: Optional[bool] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.order is not None:
            params["order"] = self.order
        if self.ascending is not None:
            params["ascending"] = self.ascending
        if self.include_template is not None:
            params["include_template"] = self.include_template
        if self.is_carousel is not None:
            params["is_carousel"] = self.is_carousel
        
        return params


@dataclass
class GetTeamsParams:
    """Query parameters for the GET /teams endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/sports/list-teams
    """
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: Optional[str] = None
    ascending: Optional[bool] = None
    league: Optional[list[str]] = None
    name: Optional[list[str]] = None
    abbreviation: Optional[list[str]] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.order is not None:
            params["order"] = self.order
        if self.ascending is not None:
            params["ascending"] = self.ascending
        if self.league is not None:
            params["league"] = self.league
        if self.name is not None:
            params["name"] = self.name
        if self.abbreviation is not None:
            params["abbreviation"] = self.abbreviation
        
        return params


@dataclass
class GetRelatedTagsParams:
    """Query parameters for related tags endpoints.
    
    Reference: https://docs.polymarket.com/api-reference/tags/get-related-tags-relationships-by-tag-id
    """
    
    omit_empty: Optional[bool] = None
    status: Optional[str] = None  # "active", "closed", "all"
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.omit_empty is not None:
            params["omit_empty"] = self.omit_empty
        if self.status is not None:
            params["status"] = self.status
        
        return params


@dataclass
class GetSeriesParams:
    """Query parameters for the GET /series endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/series/list-series
    """
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: Optional[str] = None
    ascending: Optional[bool] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.order is not None:
            params["order"] = self.order
        if self.ascending is not None:
            params["ascending"] = self.ascending
        
        return params


@dataclass
class GetCommentsParams:
    """Query parameters for the GET /comments endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/comments/list-comments
    """
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    order: Optional[str] = None
    ascending: Optional[bool] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.order is not None:
            params["order"] = self.order
        if self.ascending is not None:
            params["ascending"] = self.ascending
        
        return params


@dataclass
class SearchParams:
    """Query parameters for the GET /search endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/search/search-markets-events-and-profiles
    """
    
    q: str  # Search query (required)
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {"q": self.q}
        
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        
        return params


@dataclass(slots=True)
class Team:
    """Team data structure.
    
    Reference: https://docs.polymarket.com/api-reference/sports/list-teams
    """
    
    id: int
    name: Optional[str] = None
    league: Optional[str] = None
    record: Optional[str] = None
    logo: Optional[str] = None
    abbreviation: Optional[str] = None
    alias: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Team":
        """Parse Team from API response payload."""
        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        
        return Team(
            id=int(payload.get("id", 0)),
            name=payload.get("name"),
            league=payload.get("league"),
            record=payload.get("record"),
            logo=payload.get("logo"),
            abbreviation=payload.get("abbreviation"),
            alias=payload.get("alias"),
            created_at=parse_datetime(payload.get("createdAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
        )


@dataclass(slots=True)
class SportsMetadata:
    """Sports metadata information.
    
    Reference: https://docs.polymarket.com/api-reference/sports/get-sports-metadata-information
    """
    
    sport: str  # The sport identifier or abbreviation
    image: Optional[str] = None  # URL to the sport's logo or image asset
    resolution: Optional[str] = None  # URL to the official resolution source
    ordering: Optional[str] = None  # Preferred ordering (typically "home" or "away")
    tags: Optional[str] = None  # Comma-separated list of tag IDs
    series: Optional[str] = None  # Series identifier
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "SportsMetadata":
        """Parse SportsMetadata from API response payload."""
        return SportsMetadata(
            sport=str(payload.get("sport", "")),
            image=payload.get("image"),
            resolution=payload.get("resolution"),
            ordering=payload.get("ordering"),
            tags=payload.get("tags"),
            series=payload.get("series"),
        )


@dataclass(slots=True)
class RelatedTag:
    """Related tag relationship.
    
    Reference: https://docs.polymarket.com/api-reference/tags/get-related-tags-relationships-by-tag-id
    """
    
    id: str
    tag_id: Optional[int] = None
    related_tag_id: Optional[int] = None
    rank: Optional[int] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "RelatedTag":
        """Parse RelatedTag from API response payload."""
        return RelatedTag(
            id=str(payload.get("id", "")),
            tag_id=payload.get("tagID"),
            related_tag_id=payload.get("relatedTagID"),
            rank=payload.get("rank"),
        )


@dataclass(slots=True)
class Series:
    """Series data structure.
    
    Reference: https://docs.polymarket.com/api-reference/series/list-series
    """
    
    id: str
    ticker: Optional[str] = None
    slug: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    series_type: Optional[str] = None
    recurrence: Optional[str] = None
    image: Optional[str] = None
    icon: Optional[str] = None
    layout: Optional[str] = None
    active: Optional[bool] = None
    closed: Optional[bool] = None
    archived: Optional[bool] = None
    new: Optional[bool] = None
    featured: Optional[bool] = None
    restricted: Optional[bool] = None
    published_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    comments_enabled: Optional[bool] = None
    competitive: Optional[str] = None
    volume_24hr: Optional[float] = None
    volume: Optional[float] = None
    liquidity: Optional[float] = None
    start_date: Optional[datetime] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Series":
        """Parse Series from API response payload."""
        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError, TypeError):
                return None

        def parse_float(value: Any) -> Optional[float]:
            if value is None:
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        
        return Series(
            id=str(payload.get("id", "")),
            ticker=payload.get("ticker"),
            slug=payload.get("slug"),
            title=payload.get("title"),
            subtitle=payload.get("subtitle"),
            series_type=payload.get("seriesType"),
            recurrence=payload.get("recurrence"),
            image=payload.get("image"),
            icon=payload.get("icon"),
            layout=payload.get("layout"),
            active=payload.get("active"),
            closed=payload.get("closed"),
            archived=payload.get("archived"),
            new=payload.get("new"),
            featured=payload.get("featured"),
            restricted=payload.get("restricted"),
            published_at=parse_datetime(payload.get("publishedAt")),
            created_by=payload.get("createdBy"),
            updated_by=payload.get("updatedBy"),
            created_at=parse_datetime(payload.get("createdAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
            comments_enabled=payload.get("commentsEnabled"),
            competitive=payload.get("competitive"),
            volume_24hr=parse_float(payload.get("volume24hr")),
            volume=parse_float(payload.get("volume")),
            liquidity=parse_float(payload.get("liquidity")),
            start_date=parse_datetime(payload.get("startDate")),
        )


@dataclass(slots=True)
class Comment:
    """Comment data structure.
    
    Reference: https://docs.polymarket.com/api-reference/comments/list-comments
    """
    
    id: str
    content: Optional[str] = None
    user_address: Optional[str] = None
    market_id: Optional[str] = None
    event_id: Optional[str] = None
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Comment":
        """Parse Comment from API response payload."""
        def parse_datetime(dt_str: str | None) -> Optional[datetime]:
            if dt_str is None:
                return None
            try:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        
        return Comment(
            id=str(payload.get("id", "")),
            content=payload.get("content"),
            user_address=payload.get("userAddress"),
            market_id=payload.get("marketId"),
            event_id=payload.get("eventId"),
            parent_id=payload.get("parentId"),
            created_at=parse_datetime(payload.get("createdAt")),
            updated_at=parse_datetime(payload.get("updatedAt")),
        )


@dataclass(slots=True)
class SearchResult:
    """Search result data structure.
    
    Reference: https://docs.polymarket.com/api-reference/search/search-markets-events-and-profiles
    """
    
    type: str  # "market", "event", "profile", etc.
    id: str
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)  # Additional result-specific data
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "SearchResult":
        """Parse SearchResult from API response payload."""
        return SearchResult(
            type=str(payload.get("type", "")),
            id=str(payload.get("id", "")),
            title=payload.get("title"),
            slug=payload.get("slug"),
            description=payload.get("description"),
            data=payload.get("data", {}),
        )


@dataclass
class GetPositionsParams:
    """Query parameters for the GET /positions endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
    """
    
    user: str  # Required: User address
    market: Optional[list[str]] = None  # Comma-separated list of condition IDs
    event_id: Optional[list[int]] = None  # Comma-separated list of event IDs
    size_threshold: Optional[float] = None  # Minimum size threshold (default: 1)
    redeemable: Optional[bool] = None  # Filter by redeemable positions (default: false)
    mergeable: Optional[bool] = None  # Filter by mergeable positions (default: false)
    limit: Optional[int] = None  # Maximum: 500, default: 100
    offset: Optional[int] = None  # Maximum: 10000, default: 0
    sort_by: Optional[str] = None  # CURRENT, INITIAL, TOKENS, CASHPNL, PERCENTPNL, TITLE, RESOLVING, PRICE, AVGPRICE (default: TOKENS)
    sort_direction: Optional[str] = None  # ASC, DESC (default: DESC)
    title: Optional[str] = None  # Filter by title (maxLength: 100)
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {"user": self.user}
        
        if self.market is not None:
            params["market"] = self.market
        if self.event_id is not None:
            params["eventId"] = self.event_id
        if self.size_threshold is not None:
            params["sizeThreshold"] = self.size_threshold
        if self.redeemable is not None:
            params["redeemable"] = self.redeemable
        if self.mergeable is not None:
            params["mergeable"] = self.mergeable
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.sort_by is not None:
            params["sortBy"] = self.sort_by
        if self.sort_direction is not None:
            params["sortDirection"] = self.sort_direction
        if self.title is not None:
            params["title"] = self.title
        
        return params


@dataclass
class GetDataTradesParams:
    """Query parameters for the GET /trades endpoint (Data API).
    
    Reference: https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets
    """
    
    user: Optional[str] = None  # User Profile Address
    market: Optional[list[str]] = None  # Comma-separated list of condition IDs
    event_id: Optional[list[int]] = None  # Comma-separated list of event IDs
    limit: Optional[int] = None  # Maximum: 10000, default: 100
    offset: Optional[int] = None  # Maximum: 10000, default: 0
    taker_only: Optional[bool] = None  # Filter for taker trades (default: true)
    filter_type: Optional[str] = None  # CASH or TOKENS (must be provided with filter_amount)
    filter_amount: Optional[float] = None  # Amount for filtering (must be provided with filter_type)
    side: Optional[str] = None  # BUY or SELL
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.user is not None:
            params["user"] = self.user
        if self.market is not None:
            params["market"] = self.market
        if self.event_id is not None:
            params["eventId"] = self.event_id
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.taker_only is not None:
            params["takerOnly"] = self.taker_only
        if self.filter_type is not None:
            params["filterType"] = self.filter_type
        if self.filter_amount is not None:
            params["filterAmount"] = self.filter_amount
        if self.side is not None:
            params["side"] = self.side
        
        return params


@dataclass
class GetActivityParams:
    """Query parameters for the GET /activity endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-user-activity
    """
    
    user: str  # Required: User Profile Address
    market: Optional[list[str]] = None  # Comma-separated list of condition IDs
    event_id: Optional[list[int]] = None  # Comma-separated list of event IDs
    type: Optional[list[str]] = None  # TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION
    start: Optional[int] = None  # Start timestamp
    end: Optional[int] = None  # End timestamp
    limit: Optional[int] = None  # Maximum: 500, default: 100
    offset: Optional[int] = None  # Maximum: 10000, default: 0
    sort_by: Optional[str] = None  # TIMESTAMP, TOKENS, CASH (default: TIMESTAMP)
    sort_direction: Optional[str] = None  # ASC, DESC (default: DESC)
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {"user": self.user}
        
        if self.market is not None:
            params["market"] = self.market
        if self.event_id is not None:
            params["eventId"] = self.event_id
        if self.type is not None:
            params["type"] = self.type
        if self.start is not None:
            params["start"] = self.start
        if self.end is not None:
            params["end"] = self.end
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        if self.sort_by is not None:
            params["sortBy"] = self.sort_by
        if self.sort_direction is not None:
            params["sortDirection"] = self.sort_direction
        
        return params


@dataclass
class GetTopHoldersParams:
    """Query parameters for the GET /top-holders endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets
    """
    
    market: Optional[list[str]] = None  # Comma-separated list of condition IDs
    event_id: Optional[list[int]] = None  # Comma-separated list of event IDs
    limit: Optional[int] = None  # Maximum: 500, default: 100
    offset: Optional[int] = None  # Maximum: 10000, default: 0
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {}
        
        if self.market is not None:
            params["market"] = self.market
        if self.event_id is not None:
            params["eventId"] = self.event_id
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        
        return params


@dataclass
class GetClosedPositionsParams:
    """Query parameters for the GET /positions/closed endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
    """
    
    user: str  # Required: User address
    market: Optional[list[str]] = None  # Comma-separated list of condition IDs
    event_id: Optional[list[int]] = None  # Comma-separated list of event IDs
    title: Optional[str] = None  # Filter by market title
    limit: Optional[int] = None  # Default: 10
    offset: Optional[int] = None  # Default: 0
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {"user": self.user}
        
        if self.market is not None:
            params["market"] = self.market
        if self.event_id is not None:
            params["eventId"] = self.event_id
        if self.title is not None:
            params["title"] = self.title
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset
        
        return params


@dataclass
class GetTotalValueParams:
    """Query parameters for the GET /positions/total-value endpoint.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-total-value-of-a-users-positions
    """
    
    user: str  # Required: User address
    market: Optional[list[str]] = None  # Comma-separated list of condition IDs
    
    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dict for HTTP request."""
        params: dict[str, Any] = {"user": self.user}
        
        if self.market is not None:
            params["market"] = self.market
        
        return params


@dataclass(slots=True)
class Position:
    """Position data structure from Data API.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-current-positions-for-a-user
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
    cur_price: float
    redeemable: bool
    mergeable: bool
    realized_pnl: Optional[float] = None
    percent_realized_pnl: Optional[float] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    event_slug: Optional[str] = None
    outcome: Optional[str] = None
    outcome_index: Optional[int] = None
    opposite_outcome: Optional[str] = None
    opposite_asset: Optional[str] = None
    end_date: Optional[str] = None
    negative_risk: Optional[bool] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Position":
        """Parse Position from API response payload."""
        return Position(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            asset=str(payload.get("asset", "")),
            condition_id=str(payload.get("conditionId", "")),
            size=float(payload.get("size", 0.0)),
            avg_price=float(payload.get("avgPrice", 0.0)),
            initial_value=float(payload.get("initialValue", 0.0)),
            current_value=float(payload.get("currentValue", 0.0)),
            cash_pnl=float(payload.get("cashPnl", 0.0)),
            percent_pnl=float(payload.get("percentPnl", 0.0)),
            total_bought=float(payload.get("totalBought", 0.0)),
            cur_price=float(payload.get("curPrice", 0.0)),
            redeemable=bool(payload.get("redeemable", False)),
            mergeable=bool(payload.get("mergeable", False)),
            realized_pnl=float(payload.get("realizedPnl", 0.0)) if payload.get("realizedPnl") is not None else None,
            percent_realized_pnl=float(payload.get("percentRealizedPnl", 0.0)) if payload.get("percentRealizedPnl") is not None else None,
            title=payload.get("title"),
            slug=payload.get("slug"),
            icon=payload.get("icon"),
            event_slug=payload.get("eventSlug"),
            outcome=payload.get("outcome"),
            outcome_index=payload.get("outcomeIndex"),
            opposite_outcome=payload.get("oppositeOutcome"),
            opposite_asset=payload.get("oppositeAsset"),
            end_date=payload.get("endDate"),
            negative_risk=payload.get("negativeRisk"),
        )


@dataclass(slots=True)
class DataTrade:
    """Trade data structure from Data API (different from CLOB Trade).
    
    Reference: https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets
    """
    
    proxy_wallet: str
    side: str  # BUY or SELL
    asset: str
    condition_id: str
    size: float
    price: float
    timestamp: int
    title: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    event_slug: Optional[str] = None
    outcome: Optional[str] = None
    outcome_index: Optional[int] = None
    name: Optional[str] = None
    pseudonym: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    profile_image_optimized: Optional[str] = None
    transaction_hash: Optional[str] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "DataTrade":
        """Parse DataTrade from API response payload."""
        return DataTrade(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            side=str(payload.get("side", "")),
            asset=str(payload.get("asset", "")),
            condition_id=str(payload.get("conditionId", "")),
            size=float(payload.get("size", 0.0)),
            price=float(payload.get("price", 0.0)),
            timestamp=int(payload.get("timestamp", 0)),
            title=payload.get("title"),
            slug=payload.get("slug"),
            icon=payload.get("icon"),
            event_slug=payload.get("eventSlug"),
            outcome=payload.get("outcome"),
            outcome_index=payload.get("outcomeIndex"),
            name=payload.get("name"),
            pseudonym=payload.get("pseudonym"),
            bio=payload.get("bio"),
            profile_image=payload.get("profileImage"),
            profile_image_optimized=payload.get("profileImageOptimized"),
            transaction_hash=payload.get("transactionHash"),
        )


@dataclass(slots=True)
class Activity:
    """User activity data structure from Data API.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-user-activity
    """
    
    proxy_wallet: str
    timestamp: int
    condition_id: str
    type: str  # TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION
    size: Optional[float] = None
    usdc_size: Optional[float] = None
    transaction_hash: Optional[str] = None
    price: Optional[float] = None
    asset: Optional[str] = None
    side: Optional[str] = None  # BUY or SELL
    outcome_index: Optional[int] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    event_slug: Optional[str] = None
    outcome: Optional[str] = None
    name: Optional[str] = None
    pseudonym: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    profile_image_optimized: Optional[str] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "Activity":
        """Parse Activity from API response payload."""
        return Activity(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            timestamp=int(payload.get("timestamp", 0)),
            condition_id=str(payload.get("conditionId", "")),
            type=str(payload.get("type", "")),
            size=float(payload.get("size", 0.0)) if payload.get("size") is not None else None,
            usdc_size=float(payload.get("usdcSize", 0.0)) if payload.get("usdcSize") is not None else None,
            transaction_hash=payload.get("transactionHash"),
            price=float(payload.get("price", 0.0)) if payload.get("price") is not None else None,
            asset=payload.get("asset"),
            side=payload.get("side"),
            outcome_index=payload.get("outcomeIndex"),
            title=payload.get("title"),
            slug=payload.get("slug"),
            icon=payload.get("icon"),
            event_slug=payload.get("eventSlug"),
            outcome=payload.get("outcome"),
            name=payload.get("name"),
            pseudonym=payload.get("pseudonym"),
            bio=payload.get("bio"),
            profile_image=payload.get("profileImage"),
            profile_image_optimized=payload.get("profileImageOptimized"),
        )


@dataclass(slots=True)
class TopHolder:
    """Top holder data structure.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets
    """
    
    proxy_wallet: str
    asset: str
    condition_id: str
    size: float
    name: Optional[str] = None
    pseudonym: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    profile_image_optimized: Optional[str] = None
    title: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    event_slug: Optional[str] = None
    outcome: Optional[str] = None
    outcome_index: Optional[int] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "TopHolder":
        """Parse TopHolder from API response payload."""
        return TopHolder(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            asset=str(payload.get("asset", "")),
            condition_id=str(payload.get("conditionId", "")),
            size=float(payload.get("size", 0.0)),
            name=payload.get("name"),
            pseudonym=payload.get("pseudonym"),
            bio=payload.get("bio"),
            profile_image=payload.get("profileImage"),
            profile_image_optimized=payload.get("profileImageOptimized"),
            title=payload.get("title"),
            slug=payload.get("slug"),
            icon=payload.get("icon"),
            event_slug=payload.get("eventSlug"),
            outcome=payload.get("outcome"),
            outcome_index=payload.get("outcomeIndex"),
        )


@dataclass(slots=True)
class ClosedPosition:
    """Closed position data structure.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user
    """
    
    proxy_wallet: str
    asset: str
    condition_id: str
    avg_price: float
    total_bought: float
    realized_pnl: float
    cur_price: float
    timestamp: int
    title: Optional[str] = None
    slug: Optional[str] = None
    icon: Optional[str] = None
    event_slug: Optional[str] = None
    outcome: Optional[str] = None
    outcome_index: Optional[int] = None
    opposite_outcome: Optional[str] = None
    opposite_asset: Optional[str] = None
    end_date: Optional[str] = None
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "ClosedPosition":
        """Parse ClosedPosition from API response payload."""
        return ClosedPosition(
            proxy_wallet=str(payload.get("proxyWallet", "")),
            asset=str(payload.get("asset", "")),
            condition_id=str(payload.get("conditionId", "")),
            avg_price=float(payload.get("avgPrice", 0.0)),
            total_bought=float(payload.get("totalBought", 0.0)),
            realized_pnl=float(payload.get("realizedPnl", 0.0)),
            cur_price=float(payload.get("curPrice", 0.0)),
            timestamp=int(payload.get("timestamp", 0)),
            title=payload.get("title"),
            slug=payload.get("slug"),
            icon=payload.get("icon"),
            event_slug=payload.get("eventSlug"),
            outcome=payload.get("outcome"),
            outcome_index=payload.get("outcomeIndex"),
            opposite_outcome=payload.get("oppositeOutcome"),
            opposite_asset=payload.get("oppositeAsset"),
            end_date=payload.get("endDate"),
        )


@dataclass(slots=True)
class TotalValue:
    """Total value of user positions.
    
    Reference: https://docs.polymarket.com/api-reference/core/get-total-value-of-a-users-positions
    """
    
    user: str
    value: float
    
    @staticmethod
    def from_payload(payload: dict[str, Any]) -> "TotalValue":
        """Parse TotalValue from API response payload."""
        return TotalValue(
            user=str(payload.get("user", "")),
            value=float(payload.get("value", 0.0)),
        )


__all__ = [
    "Activity",
    "CancelMarketOrdersParams",
    "CancelOrdersResponse",
    "Category",
    "ClosedPosition",
    "Comment",
    "DataTrade",
    "Event",
    "GetActiveOrdersParams",
    "GetActivityParams",
    "GetClosedPositionsParams",
    "GetCommentsParams",
    "GetDataTradesParams",
    "GetEventsParams",
    "GetMarketsParams",
    "GetPositionsParams",
    "GetRelatedTagsParams",
    "GetSeriesParams",
    "GetTagsParams",
    "GetTeamsParams",
    "GetTopHoldersParams",
    "GetTotalValueParams",
    "GetTradesParams",
    "ImageOptimized",
    "MakerOrder",
    "Market",
    "OpenOrder",
    "OrderBook",
    "OrderBookLevel",
    "OrderFilled",
    "OrderScoringParams",
    "OrdersScoring",
    "OrdersScoringBatch",
    "OrdersScoringParams",
    "OrderSummary",
    "Position",
    "PriceChange",
    "RelatedTag",
    "SearchParams",
    "SearchResult",
    "Series",
    "SportsMetadata",
    "Tag",
    "Team",
    "TopHolder",
    "TotalValue",
    "Trade",
    "WebSocketMakerOrder",
    "WebSocketOrderMessage",
    "WebSocketTradeMessage",
    "WebSocketUserMessage",
    "OrderSummary",
    "PriceChange",
    "WebSocketBookMessage",
    "WebSocketLastTradePriceMessage",
    "WebSocketMarketMessage",
    "WebSocketPriceChangeMessage",
    "WebSocketTickSizeChangeMessage",
]

