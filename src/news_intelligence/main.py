"""Quick manual test: fetch one feed and print what Article objects come out.

Usage:
    python main.py                                  # uses the default feed below
    python main.py https://example.com/rss.xml       # or pass any feed URL
"""

import os
import sys
from pathlib import Path
from dataclasses import asdict
from datetime import datetime
from __future__ import annotations

from dataclasses import asdict, fields

import yaml

from news_intelligence.database.connection import get_connection
from news_intelligence.collectors.Rss import RSSCollector
from news_intelligence.domain.article import Article
from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.domain.source import Source

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = PROJECT_ROOT / "config" / "sources"

CONFIG_FILES = (
    "news.yaml",
    "space.yaml",
)

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


def insert_struct(cursor, table: str, obj) -> None:
    data = asdict(obj)
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))  # sqlite; use %s for Postgres/MySQL
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))

def upsert_source_and_feed(
    conn,
    source: Source,
    feed: Feed,
) -> None:
    """Synchronize source/feed metadata from YAML into PostgreSQL."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO sources
                (id, name, website, country, language, categories, enabled)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                website = EXCLUDED.website,
                country = EXCLUDED.country,
                language = EXCLUDED.language,
                categories = EXCLUDED.categories,
                enabled = EXCLUDED.enabled
            """,
            (
                source.id,
                source.name,
                source.website,
                source.country,
                source.language,
                list(source.categories),
                source.enabled,
            ),
        )

        cur.execute(
            """
            INSERT INTO feeds
                (id, source_id, name, url, type, enabled)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                source_id = EXCLUDED.source_id,
                name = EXCLUDED.name,
                url = EXCLUDED.url,
                type = EXCLUDED.type,
                enabled = EXCLUDED.enabled
            """,
            (
                feed.id,
                feed.source_id,
                feed.name,
                feed.url,
                feed.type.value,
                feed.enabled,
            ),
        )


def save_articles(conn, articles: list[Article]) -> int:
    """Insert new articles and ignore articles already stored by URL."""
    inserted = 0

    with conn.cursor() as cur:
        for article in articles:
            cur.execute(
                """
                INSERT INTO articles (
                    id,
                    source_id,
                    feed_id,
                    title,
                    description,
                    url,
                    published_at,
                    collected_at,
                    language
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
                """,
                (
                    article.id,
                    article.source_id,
                    article.feed_id,
                    article.title,
                    article.description,
                    article.url,
                    article.published_at,
                    article.collected_at,
                    article.language,
                ),
            )
            inserted += cur.rowcount

    return inserted





if __name__ == "__main__":
    pass