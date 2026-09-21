from pathlib import Path

from news_intelligence.collectors.Rss import RSSCollector
from news_intelligence.config.loader import load_all_sources_and_feeds
from news_intelligence.database.connection import get_connection
from news_intelligence.database.db_repo.articles import ArticleRepository
from news_intelligence.database.db_repo.feeds import FeedRepository
from news_intelligence.database.db_repo.sources import SourceRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config" / "sources"


def main() -> None:
    sources_and_feeds = load_all_sources_and_feeds(CONFIG_DIR)

    collector = RSSCollector(timeout=15)

    with get_connection() as connection:
        source_repository = SourceRepository(connection)
        feed_repository = FeedRepository(connection)
        article_repository = ArticleRepository(connection)

        for source, feed in sources_and_feeds:

            source_repository.save(source)
            feed_repository.save(feed)

            articles = collector.collect(
                source=source,
                feed=feed,
            )

            for article in articles:
                article_repository.save(article)

            print(
                f"{source.name} / {feed.name}: "
                f"{len(articles)} articles"
            )


if __name__ == "__main__":
    main()