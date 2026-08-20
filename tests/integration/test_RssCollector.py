"""Pytest integration tests for RSSCollector.

These tests load the real feed definitions from config/sources and make real
network requests. They are therefore integration/live tests, not unit tests.

Run from the project root:

    python -m pytest tests/integration/test_RssCollector.py -v -s

The `-s` option displays the RSS article information printed by the test.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from news_intelligence.collectors.Rss import RSSCollector
from news_intelligence.domain.article import Article
from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.domain.source import Source


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = PROJECT_ROOT / "config" / "sources"

CONFIG_FILES = (
    "news.yaml",
    "space.yaml",
)


# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------

def load_sources_and_feeds(
    path: Path,
) -> list[tuple[Source, Feed]]:
    """Load enabled Source/Feed pairs from one YAML configuration file."""

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    pairs: list[tuple[Source, Feed]] = []

    for raw_source in data.get("sources", []):
        source = Source(
            id=raw_source["id"],
            name=raw_source["name"],
            website=raw_source["website"],
            country=raw_source.get("country"),
            language=raw_source.get("language"),
            categories=tuple(
                raw_source.get("categories", ())
            ),
            enabled=raw_source.get("enabled", True),
        )

        # Ignore disabled sources.
        if not source.enabled:
            continue

        for raw_feed in raw_source.get("feeds", []):
            feed = Feed(
                id=raw_feed["id"],
                source_id=source.id,
                name=raw_feed["name"],
                url=raw_feed["url"],
                type=FeedType(raw_feed["type"]),
                enabled=raw_feed.get("enabled", True),
            )

            # Ignore disabled feeds.
            if feed.enabled:
                pairs.append((source, feed))

    return pairs


def get_live_feeds() -> list[tuple[Source, Feed]]:
    """Return all enabled RSS/Atom feeds from the configured YAML files."""

    pairs: list[tuple[Source, Feed]] = []

    for config_name in CONFIG_FILES:
        config_path = CONFIG_DIR / config_name

        assert config_path.is_file(), (
            f"Missing config file: {config_path}"
        )

        pairs.extend(
            load_sources_and_feeds(config_path)
        )

    return pairs


# ---------------------------------------------------------------------------
# RSS integration test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "source,feed",
    get_live_feeds(),
    ids=lambda item: item.id,
)
def test_enabled_rss_feed_description(
    source: Source,
    feed: Feed,
) -> None:
    """Collect real RSS/Atom data and inspect Article descriptions."""

    collector = RSSCollector(timeout=15)

    articles = collector.collect(
        feed=feed,
        source=source,
    )

    # -----------------------------------------------------------------------
    # Basic result validation
    # -----------------------------------------------------------------------

    assert isinstance(articles, list)

    print("\n" + "=" * 80)
    print(f"Source:             {source.name}")
    print(f"Feed:               {feed.name}")
    print(f"Feed ID:            {feed.id}")
    print(f"Feed URL:           {feed.url}")
    print(f"Articles received:  {len(articles)}")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # Display first three articles
    #
    # We only print the first three so a feed with 50+ articles does not
    # flood the terminal.
    # -----------------------------------------------------------------------

    for index, article in enumerate(articles[:3], start=1):
        print(f"\nARTICLE {index}")
        print("-" * 80)

        print("ID:")
        print(article.id)

        print("\nTitle:")
        print(article.title)

        print("\nDescription:")
        print(article.description)

        print("\nURL:")
        print(article.url)

        print("\nPublished:")
        print(article.published_at)

        print("\nCollected:")
        print(article.collected_at)

        print("\nLanguage:")
        print(article.language)

        print("-" * 80)

    # -----------------------------------------------------------------------
    # Validate every Article returned by the collector
    # -----------------------------------------------------------------------

    for article in articles:

        assert isinstance(article, Article)

        # The article must belong to the source/feed that produced it.
        assert article.source_id == source.id
        assert article.feed_id == feed.id

        # Required article fields.
        assert article.title
        assert article.url

        # Description is optional in the Article domain model.
        assert (
            article.description is None
            or isinstance(article.description, str)
        )

        # If a description exists, it should not be empty/whitespace only.
        if article.description is not None:
            assert article.description.strip() != ""

        # collected_at should contain timezone information.
        assert article.collected_at.tzinfo is not None


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------

def test_feed_configuration_files_exist() -> None:
    """Verify that all configured feed YAML files exist."""

    for config_name in CONFIG_FILES:
        config_path = CONFIG_DIR / config_name

        assert config_path.is_file(), (
            f"Expected feed configuration at {config_path}"
        )


def test_configured_feeds_match_their_sources() -> None:
    """Verify configured feeds correctly reference their Source."""

    pairs = get_live_feeds()

    assert pairs, (
        "No enabled RSS/Atom feeds were found "
        "in the configuration."
    )

    for source, feed in pairs:

        # Feed must belong to the Source that loaded it.
        assert feed.source_id == source.id

        # RSSCollector currently supports RSS and Atom feeds.
        assert feed.type in (
            FeedType.RSS,
            FeedType.ATOM,
        )

        # Feed URL must be an HTTP(S) URL.
        assert feed.url.startswith(
            ("http://", "https://")
        )