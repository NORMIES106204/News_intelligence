from psycopg import Connection

from news_intelligence.domain.feed import Feed, FeedType


class FeedRepository:
    """Repository for persisting Feed domain objects."""

    def __init__(self, connection: Connection):
        self.connection = connection

    def save(self, feed: Feed) -> None:
        """Insert or update a feed."""

        query = """
            INSERT INTO feeds (
                id,
                source_id,
                name,
                url,
                type,
                enabled
            )
            VALUES (
                %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                source_id = EXCLUDED.source_id,
                name = EXCLUDED.name,
                url = EXCLUDED.url,
                type = EXCLUDED.type,
                enabled = EXCLUDED.enabled
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    feed.id,
                    feed.source_id,
                    feed.name,
                    feed.url,
                    feed.type.value,
                    feed.enabled,
                ),
            )

    def get_by_id(self, feed_id: str) -> Feed | None:
        """Retrieve a feed by ID."""

        query = """
            SELECT
                id,
                source_id,
                name,
                url,
                type,
                enabled
            FROM feeds
            WHERE id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (feed_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return Feed(
            id=row[0],
            source_id=row[1],
            name=row[2],
            url=row[3],
            type=FeedType(row[4]),
            enabled=row[5],
        )