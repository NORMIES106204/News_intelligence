from pathlib import Path

import yaml

from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.domain.source import Source


def load_sources_and_feeds(
    path: Path,
) -> list[tuple[Source, Feed]]:
    """Load enabled Source/Feed pairs from one YAML file."""

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

            if feed.enabled:
                pairs.append((source, feed))

    return pairs


def load_all_sources_and_feeds(
    config_dir: Path,
) -> list[tuple[Source, Feed]]:
    """Load enabled sources and feeds from all YAML files."""

    pairs: list[tuple[Source, Feed]] = []

    for config_path in sorted(config_dir.glob("*.yaml")):
        pairs.extend(
            load_sources_and_feeds(config_path)
        )

    return pairs