from psycopg import Connection

from news_intelligence.domain.article import Article


class ArticleRepository:
    """Repository for persisting Article domain objects."""

    def __init__(self, connection: Connection):
        self.connection = connection

    def save(self, article: Article) -> None:
        """Insert an article or update an existing article with the same ID."""

        query = """
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
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                source_id = EXCLUDED.source_id,
                feed_id = EXCLUDED.feed_id,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                url = EXCLUDED.url,
                published_at = EXCLUDED.published_at,
                collected_at = EXCLUDED.collected_at,
                language = EXCLUDED.language
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
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

    def get_by_id(self, article_id: str) -> Article | None:
        """Retrieve an article by ID."""

        query = """
            SELECT
                id,
                source_id,
                feed_id,
                title,
                description,
                url,
                published_at,
                collected_at,
                language
            FROM articles
            WHERE id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (article_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return Article(
            id=row[0],
            source_id=row[1],
            feed_id=row[2],
            title=row[3],
            description=row[4],
            url=row[5],
            published_at=row[6],
            collected_at=row[7],
            language=row[8],
        )
