from datetime import datetime, timezone

from news_intelligence.domain.source import Source
from news_intelligence.domain.feed import Feed, FeedType
from news_intelligence.domain.article import Article


def test_source_feed_article_flow():
    print("\n--- Creating Source ---")

    source = Source(
        id="reuters",
        name="Reuters",
        website="https://www.reuters.com",
        country="US",
        language="en",
        categories=("world", "business"),
    )

    print(f"Source created: {source}")
    print(f"  ID: {source.id}")
    print(f"  Name: {source.name}")

    print("\n--- Creating Feed ---")

    feed = Feed(
        id="reuters-world",
        source_id=source.id,
        name="Reuters World",
        url="https://example.com/reuters-world.xml",
        type=FeedType.RSS,
    )

    print(f"Feed created: {feed}")
    print(f"  ID: {feed.id}")
    print(f"  Source ID: {feed.source_id}")
    print(f"  Type: {feed.type}")

    print("\n--- Creating Article ---")

    article = Article(
        id="article-001",
        source_id=source.id,
        feed_id=feed.id,
        title="Example news article",
        description="Example article description",
        url="https://example.com/article-001",
        published_at=datetime(
            2026, 8, 18, 12, 0, tzinfo=timezone.utc
        ),
        collected_at=datetime.now(timezone.utc),
        language="en",
    )

    print(f"Article created: {article}")
    print(f"  ID: {article.id}")
    print(f"  Source ID: {article.source_id}")
    print(f"  Feed ID: {article.feed_id}")
    print(f"  Title: {article.title}")

    print("\n--- Checking relationships ---")

    assert feed.source_id == source.id
    print("✓ Feed → Source relationship OK")

    assert article.source_id == source.id
    print("✓ Article → Source relationship OK")

    assert article.feed_id == feed.id
    print("✓ Article → Feed relationship OK")

    assert article.title == "Example news article"
    print("✓ Article data OK")

    print("\n✓ Source → Feed → Article flow PASSED")