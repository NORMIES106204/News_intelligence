"""Domain model for content feeds.

This module defines the :class:`Feed` entity, which represents a specific
content stream belonging to a :class:`Source`.

The domain layer intentionally knows nothing about how a feed is retrieved
or parsed. Network access and RSS/Atom parsing belong to the collectors
layer.
"""

from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse


class FeedType(StrEnum):
    """Supported feed formats.

    The enum intentionally contains only formats supported by the current
    implementation. Additional feed types can be introduced later without
    changing the structure of the Feed entity.
    """

    RSS = "rss"
    ATOM = "atom"
    API = "api"
    


@dataclass(frozen=True, slots=True)
class Feed:
    """Represent a content stream belonging to a source.

    Feed is a pure domain object. It does not perform network requests,
    parse RSS/Atom documents, or interact with persistence infrastructure.

    Attributes:
        id: Stable identifier for the feed.
        source_id: Identifier of the source that owns this feed.
        name: Human-readable name of the feed.
        url: HTTP or HTTPS URL from which the feed can be collected.
        type: Format of the feed, currently RSS or Atom.
        enabled: Whether the feed is currently enabled for collection.
    """

    id: str
    source_id: str
    name: str
    url: str
    type: FeedType
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate the structural integrity of the feed.

        Validation is intentionally limited to properties that can be
        determined from the Feed data itself. Whether the URL actually
        exists or contains a valid RSS/Atom document is the responsibility
        of the collectors layer.
        """
        self._validate_required_field(self.id, "id")
        self._validate_required_field(self.source_id, "source_id")
        self._validate_required_field(self.name, "name")
        self._validate_url(self.url)

        if not isinstance(self.type, FeedType):
            raise TypeError("Feed type must be a FeedType.")

    @staticmethod
    def _validate_required_field(value: str, field_name: str) -> None:
        """Validate that a required string field contains a value.

        Args:
            value: Field value to validate.
            field_name: Name of the field used in the error message.

        Raises:
            ValueError: If the value is not a non-empty string.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Feed {field_name} must not be empty.")

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate that a feed URL uses HTTP or HTTPS.

        This performs only basic URL structure validation. It does not make
        a network request or verify that the URL points to an actual feed.

        Args:
            url: Feed URL to validate.

        Raises:
            ValueError: If the URL is empty or structurally invalid.
        """
        if not isinstance(url, str) or not url.strip():
            raise ValueError("Feed URL must not be empty.")

        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid feed URL: {url}")