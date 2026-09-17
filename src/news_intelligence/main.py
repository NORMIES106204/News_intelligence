from datetime import datetime, timezone

from news_intelligence.database.connection import get_connection


TEST_SOURCE_ID = "connection-test-source"
TEST_FEED_ID = "connection-test-feed"
TEST_ARTICLE_ID = "connection-test-article"


def main() -> None:
    print("Connecting to PostgreSQL...")

    with get_connection() as conn:
        print("✓ PostgreSQL connection established")

        with conn.cursor() as cur:
            # Test PostgreSQL itself
            cur.execute("SELECT 1;")
            result = cur.fetchone()

            if result != (1,):
                raise RuntimeError(f"Unexpected result: {result}")

            print("✓ SELECT 1 succeeded")

            # Test writing to sources
            cur.execute(
                """
                INSERT INTO sources (
                    id,
                    name,
                    website,
                    country,
                    language,
                    categories,
                    enabled
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    name = EXCLUDED.name
                """,
                (
                    TEST_SOURCE_ID,
                    "Connection Test Source",
                    "https://example.com",
                    "test",
                    "en",
                    ["test"],
                    True,
                ),
            )

            print("✓ Source written")

            # Test writing to feeds
            cur.execute(
                """
                INSERT INTO feeds (
                    id,
                    source_id,
                    name,
                    url,
                    type,
                    enabled
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    name = EXCLUDED.name
                """,
                (
                    TEST_FEED_ID,
                    TEST_SOURCE_ID,
                    "Connection Test Feed",
                    "https://example.com/test.xml",
                    "rss",
                    True,
                ),
            )

            print("✓ Feed written")

            # Test writing to articles
            now = datetime.now(timezone.utc)

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
                    language,
                    processed
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    title = EXCLUDED.title
                """,
                (
                    TEST_ARTICLE_ID,
                    TEST_SOURCE_ID,
                    TEST_FEED_ID,
                    "Database Connection Test",
                    "Test article written by the collector container.",
                    "https://example.com/connection-test",
                    now,
                    now,
                    "en",
                    False,
                ),
            )

            print("✓ Article written")

            # Read it back
            cur.execute(
                """
                SELECT
                    a.id,
                    a.title,
                    s.name,
                    f.name
                FROM articles a
                JOIN sources s
                    ON s.id = a.source_id
                JOIN feeds f
                    ON f.id = a.feed_id
                WHERE a.id = %s;
                """,
                (TEST_ARTICLE_ID,),
            )

            row = cur.fetchone()

            if row is None:
                raise RuntimeError("Article was not found after INSERT")

            print("✓ Article read back")
            print(f"  id:     {row[0]}")
            print(f"  title:  {row[1]}")
            print(f"  source: {row[2]}")
            print(f"  feed:   {row[3]}")

    print("✓ DATABASE CONNECTION TEST PASSED")


if __name__ == "__main__":
    main()