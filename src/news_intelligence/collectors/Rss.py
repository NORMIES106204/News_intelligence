"""RSS/Atom collector.

This module implements collection of :class:`Article` objects from a
:class:`Feed` whose ``type`` is ``FeedType.RSS`` or ``FeedType.ATOM``.

The collector is intentionally the only place in the application that
performs a network request and parses feed markup. It depends on the
domain layer (``Article``, ``Feed``, ``Source``) but the domain layer does
not depend on it, keeping the dependency direction one-way as described in
feed.py and article.py.

Parsing is delegated to the third-party ``feedparser`` library, which
tolerates the many small deviations from the RSS/Atom specs found in the
wild. Network access is done with the standard library so no extra HTTP
client dependency is required.
"""

from __future__ import annotations

import hashlib
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from time import struct_time


import feedparser

from news_intelligence.domain.article import Article
from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.domain.source import Source


#: Identifies this collector to remote servers. Some publishers reject
#: requests that do not send a User-Agent header at all.
_USER_AGENT = "NewsCollector/1.0 (+rss-collector)"

#: Default socket timeout, in seconds, for a single feed request.
_DEFAULT_TIMEOUT = 15


class RSSCollectionError(Exception):
    """Raised when a feed cannot be fetched or parsed.

    This wraps lower level failures (network errors, malformed documents)
    behind a single collector-specific exception so callers do not need to
    know about ``urllib`` or ``feedparser`` internals.
    """


class RSSCollector:
    """Collect :class:`Article` objects from an RSS or Atom feed.

    The collector has no knowledge of storage, scheduling, or processing.
    Its only responsibility is turning a ``Feed`` into a list of
    ``Article`` instances.
    """

    def __init__(
        self,
        timeout: int = _DEFAULT_TIMEOUT,
        user_agent: str = _USER_AGENT,
    ) -> None:
        """Initialize the collector.

        Args:
            timeout: Number of seconds to wait for the feed to respond
                before giving up.
            user_agent: Value sent as the ``User-Agent`` header.
        """
        self._timeout = timeout
        self._user_agent = user_agent

    def collect(self, feed: Feed, source: Source) -> list[Article]:
        """Fetch a feed and convert its entries into articles.

        Args:
            feed: Feed to collect. Must belong to ``source``
                (``feed.source_id == source.id``) and have a type of
                ``FeedType.RSS`` or ``FeedType.ATOM``.
            source: Source that owns the feed.

        Returns:
            One ``Article`` per entry found in the feed, in the order
            returned by the feed itself. Entries that are missing a title
            or a link are skipped, since ``Article`` requires both.

        Raises:
            ValueError: If ``feed`` does not belong to ``source`` or is
                not an RSS/Atom feed.
            RSSCollectionError: If the feed cannot be downloaded or
                contains no parseable content.
        """
        self._validate_feed(feed, source)

        raw_content = self._fetch(feed.url)
        parsed = feedparser.parse(raw_content)

        if parsed.bozo and not parsed.entries:
            raise RSSCollectionError(
                f"Feed at {feed.url!r} could not be parsed: "
                f"{parsed.bozo_exception!r}"
            )

        collected_at = datetime.now(timezone.utc)
        feed_language = parsed.feed.get("language")

        articles: list[Article] = []
        for entry in parsed.entries:
            article = self._build_article(
                entry=entry,
                feed=feed,
                source=source,
                collected_at=collected_at,
                feed_language=feed_language,
            )
            if article is not None:
                articles.append(article)

        return articles

    def _fetch(self, url: str) -> bytes:
        """Download the raw bytes of a feed.

        Args:
            url: HTTP(S) URL of the feed.

        Returns:
            Raw response body, still encoded as sent by the server.
            ``feedparser`` handles character-encoding detection itself.

        Raises:
            RSSCollectionError: If the request fails or times out.
        """
        request = urllib.request.Request(
            url,
            headers={"User-Agent": self._user_agent},
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self._timeout
            ) as response:
                return response.read()
        except urllib.error.URLError as exc:
            raise RSSCollectionError(
                f"Failed to fetch feed at {url!r}: {exc}"
            ) from exc
        except socket.timeout as exc:
            raise RSSCollectionError(
                f"Timed out fetching feed at {url!r}: {exc}"
            ) from exc

    def _build_article(
        self,
        entry,
        feed: Feed,
        source: Source,
        collected_at: datetime,
        feed_language: str | None,
    ) -> Article | None:
        """Convert one ``feedparser`` entry into an ``Article``.

        Args:
            entry: Single entry object produced by ``feedparser.parse``.
            feed: Feed the entry was collected from.
            source: Source that owns the feed.
            collected_at: Timestamp shared by all articles from this
                collection run.
            feed_language: Language reported at the feed level, used as a
                fallback when the entry itself does not specify one.

        Returns:
            A new ``Article``, or ``None`` if the entry lacks the minimum
            information (title and link) required to build one.
        """
        title = entry.get("title")
        url = entry.get("link")

        if not title or not url:
            return None

        description = entry.get("summary") or None
        language = entry.get("language") or feed_language or source.language

        published_at = self._parse_timestamp(
            entry.get("published_parsed")
            or entry.get("updated_parsed")
        )

        return Article(
            id=self._make_article_id(feed.id, entry, url),
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
        time_struct: struct_time | None,
    ) -> datetime | None:
        """Convert a ``feedparser`` time struct into a UTC datetime.

        ``feedparser`` already normalizes ``*_parsed`` fields to UTC, so
        this only needs to attach timezone information.

        Args:
            time_struct: A ``time.struct_time`` as produced by
                ``feedparser``, or ``None`` if the entry had no usable
                date.

        Returns:
            A timezone-aware UTC datetime, or ``None``.
        """
        if time_struct is None:
            return None

        return datetime(*time_struct[:6], tzinfo=timezone.utc)

    @staticmethod
    def _make_article_id(feed_id: str, entry, url: str) -> str:
        """Build a deterministic identifier for an article.

        The identifier is derived from the feed id together with the
        entry's ``guid`` when available, falling back to the article URL.
        Hashing keeps identifiers a fixed, filesystem/DB-safe length
        regardless of how long the source's own identifiers are.

        Args:
            feed_id: Identifier of the feed the entry came from.
            entry: ``feedparser`` entry.
            url: Article URL, used as a fallback identifier source.

        Returns:
            A stable, deterministic hex string.
        """
        natural_key = entry.get("id") or entry.get("guid") or url
        digest_source = f"{feed_id}:{natural_key}".encode("utf-8")
        return hashlib.sha256(digest_source).hexdigest()

    @staticmethod
    def _validate_feed(feed: Feed, source: Source) -> None:
        """Validate that a feed can be collected by this collector.

        Args:
            feed: Feed to validate.
            source: Source expected to own the feed.

        Raises:
            ValueError: If the feed does not belong to the source or is
                not an RSS/Atom feed.
        """
        if feed.source_id != source.id:
            raise ValueError(
                f"Feed {feed.id!r} does not belong to source "
                f"{source.id!r} (feed.source_id={feed.source_id!r})."
            )

        if feed.type not in (FeedType.RSS, FeedType.ATOM):
            raise ValueError(
                f"RSSCollector cannot collect feed type {feed.type!r}; "
                "only RSS and ATOM are supported."
            )