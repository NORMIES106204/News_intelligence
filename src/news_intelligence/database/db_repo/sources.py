from psycopg import Connection

from domain.source import Source


class SourceRepository:
    """Repository for persisting Source domain objects."""

    def __init__(self, connection: Connection):
        self.connection = connection

    def save(self, source: Source) -> None:
        """Insert or update a source."""

        query = """
            INSERT INTO sources (
                id,
                name,
                website,
                country,
                language,
                categories,
                enabled
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                name = EXCLUDED.name,
                website = EXCLUDED.website,
                country = EXCLUDED.country,
                language = EXCLUDED.language,
                categories = EXCLUDED.categories,
                enabled = EXCLUDED.enabled
        """

        with self.connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    source.id,
                    source.name,
                    source.website,
                    source.country,
                    source.language,
                    source.categories,
                    source.enabled,
                ),
            )

    def get_by_id(self, source_id: str) -> Source | None:
        """Retrieve a source by ID."""

        query = """
            SELECT
                id,
                name,
                website,
                country,
                language,
                categories,
                enabled
            FROM sources
            WHERE id = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (source_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return Source(
            id=row[0],
            name=row[1],
            website=row[2],
            country=row[3],
            language=row[4],
            categories=tuple(row[5] or ()),
            enabled=row[6],
        )