"""Manual test for RSSCollector, driven by news.yaml and space.yaml.

This is not a pytest/unittest suite. It is a small script that loads the
sources and feeds defined in ``news.yaml`` and ``space.yaml``, builds the
matching ``Source``/``Feed`` domain objects, runs the real ``RSSCollector``
against each enabled feed, and prints a human-readable report to the
terminal. It is meant to be run directly:

Because it performs real network requests, results depend on the feeds
being reachable at run time. Network or parsing failures are caught and
printed rather than raised, so one bad feed does not stop the others from
being tested.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.collectors.Rss import RSSCollectionError, RSSCollector
from news_intelligence.domain.source import Source

CONFIG_FILES = ("news.yaml", "space.yaml")


def load_sources_and_feeds(
    path: Path,
) -> list[tuple[Source, list[Feed]]]:
    """Parse one config file into Source/Feed domain objects.

    Args:
        path: Path to a YAML file shaped like news.yaml/space.yaml.

    Returns:
        A list of (Source, [Feed, ...]) pairs, one per source defined in
        the file.
    """
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    results: list[tuple[Source, list[Feed]]] = []

    for raw_source in data.get("sources", []):
        source = Source(
            id=raw_source["id"],
            name=raw_source["name"],
            website=raw_source["website"],
            country=raw_source.get("country"),
            language=raw_source.get("language"),
            categories=tuple(raw_source.get("categories", ())),
            enabled=raw_source.get("enabled", True),
        )

        feeds = [
            Feed(
                id=raw_feed["id"],
                source_id=source.id,
                name=raw_feed["name"],
                url=raw_feed["url"],
                type=FeedType(raw_feed["type"]),
                enabled=raw_feed.get("enabled", True),
            )
            for raw_feed in raw_source.get("feeds", [])
        ]

        results.append((source, feeds))

    return results


def print_header(text: str) -> None:
    """Print a section header framed with '=' characters."""
    print()
    print("=" * len(text))
    print(text)
    print("=" * len(text))


def run() -> None:
    """Load every config file and exercise RSSCollector against it."""
    collector = RSSCollector()
    base_dir = Path(__file__).parent

    total_feeds = 0
    total_articles = 0
    total_failures = 0

    for config_name in CONFIG_FILES:
        config_path = base_dir / config_name
        print_header(f"Config file: {config_name}")

        source_feed_pairs = load_sources_and_feeds(config_path)

        for source, feeds in source_feed_pairs:
            print(
                f"\nSource: {source.name} (id={source.id!r}, "
                f"language={source.language!r}, "
                f"categories={source.categories})"
            )

            if not source.enabled:
                print("  Source is disabled, skipping its feeds.")
                continue

            for feed in feeds:
                total_feeds += 1
                print(f"\n  Feed: {feed.name} (id={feed.id!r})")
                print(f"    URL:  {feed.url}")
                print(f"    Type: {feed.type}")

                if not feed.enabled:
                    print("    Feed is disabled, skipping collection.")
                    continue

                try:
                    articles = collector.collect(feed, source)
                except RSSCollectionError as exc:
                    total_failures += 1
                    print(f"    FAILED to collect: {exc}")
                    continue

                total_articles += len(articles)
                print(f"    Collected {len(articles)} article(s).")

                for article in articles[:3]:
                    print(f"      - [{article.id[:8]}] {article.title}")
                    print(f"        url:          {article.url}")
                    print(f"        published_at: {article.published_at}")
                    print(f"        language:     {article.language}")

                if len(articles) > 3:
                    print(f"      ... and {len(articles) - 3} more")

    print_header("Summary")
    print(f"Feeds attempted:   {total_feeds}")
    print(f"Feeds failed:      {total_failures}")
    print(f"Articles collected: {total_articles}")


if __name__ == "__main__":
    run()