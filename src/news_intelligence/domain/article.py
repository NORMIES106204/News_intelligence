"""Domain model for collected articles.

This module defines the :class:`Article` entity, which represents a single
canonical piece of published information collected from a feed.

The Article model contains only source-provided and collection metadata.
It intentionally does not contain AI-generated summaries, embeddings,
clustering information, relevance scores, notification state, or other
processing results.

The domain layer is independent of the collectors and infrastructure
layers. An Article can therefore be created by an RSS collector, an API
collector, or a future web collector without changing this model.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Article:
    """Represent one canonical article collected from a feed.

    An Article belongs to both a Source and a Feed. The relationships are
    represented using identifiers rather than direct object references,
    keeping the domain model simple and avoiding unnecessary coupling.

    All timestamps must be timezone-aware. The application should normally
    use UTC for both publication and collection timestamps.

    Attributes:
        id: Deterministic identifier for the article.
        source_id: Identifier of the source that published the article.
        feed_id: Identifier of the feed from which the article was collected.
        title: Title of the published article.
        description: Optional article description or feed-provided summary.
        url: Canonical URL of the article.
        published_at: Publication timestamp when provided by the source.
        collected_at: UTC timestamp indicating when the application
            collected the article.
        language: Optional language code associated with the article.
    """

    id: str
    source_id: str
    feed_id: str
    title: str
    description: str | None
    url: str
    published_at: datetime | None
    collected_at: datetime
    language: str | None

    def __post_init__(self) -> None:
        """Validate the structural integrity of the article.

        Validation is limited to information that can be verified from the
        Article itself. This method does not verify that the URL is reachable
        or that the article actually exists at that URL.

        Raises:
            ValueError: If a required string field is empty.
            ValueError: If the article URL is empty.
            ValueError: If a timestamp is timezone-naive.
        """
        self._validate_required_field(self.id, "id")
        self._validate_required_field(self.source_id, "source_id")
        self._validate_required_field(self.feed_id, "feed_id")
        self._validate_required_field(self.title, "title")
        self._validate_required_field(self.url, "url")

        self._validate_timezone_aware(
            self.published_at,
            "published_at",
        )
        self._validate_timezone_aware(
            self.collected_at,
            "collected_at",
        )

    @staticmethod
    def _validate_required_field(
        value: str,
        field_name: str,
    ) -> None:
        """Validate that a required string field contains a value.

        Args:
            value: Field value to validate.
            field_name: Name of the field used in the error message.

        Raises:
            ValueError: If the value is not a non-empty string.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Article {field_name} must not be empty."
            )

    @staticmethod
    def _validate_timezone_aware(
        value: datetime | None,
        field_name: str,
    ) -> None:
        """Validate that a timestamp is timezone-aware.

        A timezone-aware datetime has enough information to identify an
        absolute point in time. Naive datetimes are rejected because the
        application uses UTC internally and should not have ambiguous
        timestamps.

        Args:
            value: Datetime to validate. ``None`` is accepted for optional
                publication timestamps.
            field_name: Name of the field used in the error message.

        Raises:
            ValueError: If the datetime is timezone-naive.
        """
        if value is not None and value.tzinfo is None:
            raise ValueError(
                f"Article {field_name} must be timezone-aware."
            )