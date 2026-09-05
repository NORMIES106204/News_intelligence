"""API collector.

This module implements collection of :class:`Article` objects from
JSON-based HTTP APIs.

The collector is intentionally responsible only for:
    - fetching the API endpoint
    - parsing the JSON response
    - converting API records into Article objects

API endpoint URLs and collection settings are provided by the Feed
configuration and are not hard-coded here.
"""

from __future__ import annotations

import hashlib
import json
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from news_intelligence.collectors.base import Collector
from news_intelligence.domain.article import Article
from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.domain.source import Source


_USER_AGENT = "NewsCollector/1.0 (+api-collector)"
_DEFAULT_TIMEOUT = 15


class APICollectionError(Exception):
    """Raised when an API cannot be fetched or parsed."""


class APICollector(Collector):
    """Collect :class:`Article` objects from a JSON API.

    The collector has no knowledge of storage, scheduling, or processing.
    Its responsibility is turning an API Feed into Article objects.
    """

    def __init__(
        self,
        timeout: int = _DEFAULT_TIMEOUT,
        user_agent: str = _USER_AGENT,
    ) -> None:
        self._timeout = timeout
        self._user_agent = user_agent

    def collect(
        self,
        feed: Feed,
        source: Source,
    ) -> list[Article]:
        """Fetch an API and convert its records into articles.

        Args:
            feed: API feed to collect.
            source: Source that owns the feed.

        Returns:
            One Article per valid API record.

        Raises:
            ValueError:
                If the feed does not belong to the source or is not an API
                feed.
            APICollectionError:
                If the API cannot be fetched or parsed.
        """

        self._validate_feed(feed, source)

        payload = self._fetch(feed.url)

        records = self._extract_records(payload)

        collected_at = datetime.now(timezone.utc)

        articles: list[Article] = []

        for record in records:
            article = self._build_article(
                record=record,
                feed=feed,
                source=source,
                collected_at=collected_at,
            )

            if article is not None:
                articles.append(article)

        return articles

    def _fetch(
        self,
        url: str,
    ) -> dict[str, Any] | list[Any]:
        """Download and decode the JSON response."""

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": self._user_agent,
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                raw_content = response.read()

        except urllib.error.HTTPError as exc:
            raise APICollectionError(
                f"API request failed with HTTP {exc.code}: {url!r}"
            ) from exc

        except urllib.error.URLError as exc:
            raise APICollectionError(
                f"Failed to fetch API at {url!r}: {exc}"
            ) from exc

        except socket.timeout as exc:
            raise APICollectionError(
                f"Timed out fetching API at {url!r}: {exc}"
            ) from exc

        try:
            return json.loads(raw_content)

        except json.JSONDecodeError as exc:
            raise APICollectionError(
                f"API at {url!r} returned invalid JSON."
            ) from exc

    @staticmethod
    def _extract_records(
        payload: dict[str, Any] | list[Any],
    ) -> list[dict[str, Any]]:
        """Extract article records from the API response.

        The default implementation supports either:

            [
                {...},
                {...}
            ]

        or:

            {
                "articles": [
                    {...},
                    {...}
                ]
            }
        """

        if isinstance(payload, list):
            records = payload

        elif isinstance(payload, dict):
            records = payload.get("articles", [])

        else:
            raise APICollectionError(
                "API response must be a JSON object or array."
            )

        if not isinstance(records, list):
            raise APICollectionError(
                "API articles field must be a JSON array."
            )

        return [
            record
            for record in records
            if isinstance(record, dict)
        ]

    def _build_article(
        self,
        record: dict[str, Any],
        feed: Feed,
        source: Source,
        collected_at: datetime,
    ) -> Article | None:
        """Convert one API record into an Article."""

        title = record.get("title")
        url = record.get("url") or record.get("link")

        if not title or not url:
            return None

        description = (
            record.get("description")
            or record.get("summary")
        )

        language = (
            record.get("language")
            or source.language
        )

        published_at = self._parse_timestamp(
            record.get("published_at")
            or record.get("published")
            or record.get("publishedAt")
        )

        return Article(
            id=self._make_article_id(
                feed.id,
                record,
                url,
            ),
            source_id=source.id,
            feed_id=feed.id,
            title=title,
            description=description,
            url=url,
            published_at=published_at,
            collected_at=collected_at,
            language=language,
        )

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> datetime | None:
        """Convert an API timestamp into a UTC datetime."""

        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)

            return value.astimezone(timezone.utc)

        if isinstance(value, str):
            value = value.replace("Z", "+00:00")

            try:
                parsed = datetime.fromisoformat(value)
            except ValueError:
                return None

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        return None

    @staticmethod
    def _make_article_id(
        feed_id: str,
        record: dict[str, Any],
        url: str,
    ) -> str:
        """Build a deterministic identifier for an API article."""

        natural_key = (
            record.get("id")
            or record.get("guid")
            or url
        )

        digest_source = (
            f"{feed_id}:{natural_key}"
        ).encode("utf-8")

        return hashlib.sha256(
            digest_source
        ).hexdigest()

    @staticmethod
    def _validate_feed(
        feed: Feed,
        source: Source,
    ) -> None:
        """Validate that the feed can be collected by this collector."""

        if feed.source_id != source.id:
            raise ValueError(
                f"Feed {feed.id!r} does not belong to source "
                f"{source.id!r} "
                f"(feed.source_id={feed.source_id!r})."
            )

        if feed.type != FeedType.API:
            raise ValueError(
                f"APICollector cannot collect feed type "
                f"{feed.type!r}; only API is supported."
            )