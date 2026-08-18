"""         Domain model for the News source

This module defines the Source domain object. A Source represents an
organization, publisher, or website that produces news content.

The Source model contains only information that describes the publisher.
It does not know how news is collected, processed, stored, or analyzed.
Those responsibilities belong to other parts of the application."""

from dataclasses import dataclass, field
from urllib.parse import urlparse

class SourceValidationError (ValueError):
    """Raised when a Source is created with invalid data"""

def _normalize_categories(categories: tuple[str, ...]) -> tuple[str, ...]:
    """Clean and deduplicate source categories.

    Leading and trailing whitespace is removed, empty categories are
    discarded, and duplicate categories are removed while preserving
    their original order.

    Args:
        categories: Categories associated with the source.

    Returns:
        A tuple containing the cleaned and unique categories.
    """
    result = []

    for category in categories:
        category = category.strip()

        if category and category not in result:
            result.append(category)

    return tuple(result)


@dataclass(frozen=True, slots=True)
class Source:
    """Represent a publisher or organization that produces news.

    A Source is treated as an immutable domain object because the identity
    and basic metadata of a publisher should remain stable while the
    application is processing news.

    Attributes:
        id: Stable identifier used internally for the source.
        name: Human-readable name of the publisher.
        website: Canonical homepage URL of the publisher.
        country: Optional country code associated with the publisher.
        language: Optional primary language code used by the publisher.
        categories: Topics associated with the publisher.
        enabled: Whether this source is currently available for collection.

    Example:
        >>> source = Source(
        ...     id="reuters",
        ...     name="Reuters",
        ...     website="https://www.reuters.com",
        ...     country="US",
        ...     language="en",
        ...     categories=("world", "business"),
        ... )
    """

    id: str
    name: str
    website: str
    country: str | None = None
    language: str | None = None
    categories: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate and normalize the source after initialization.

        Because the dataclass is frozen, object.__setattr__ is used when
        storing the normalized categories.
        """
        self._validate_text(self.id, "id")
        self._validate_text(self.name, "name")
        self._validate_website(self.website)

        if self.country is not None:
            self._validate_text(self.country, "country")

        if self.language is not None:
            self._validate_text(self.language, "language")

        # Store categories as a cleaned, duplicate-free tuple.
        object.__setattr__(
            self,
            "categories",
            _normalize_categories(self.categories),
        )

    @staticmethod
    def _validate_text(value: str, field_name: str) -> None:
        """Ensure a required text field contains a non-empty string.

        Args:
            value: Value being validated.
            field_name: Name of the field, used in the error message.

        Raises:
            SourceValidationError: If the value is not a non-empty string.
        """
        if not isinstance(value, str) or not value.strip():
            raise SourceValidationError(
                f"{field_name} must be a non-empty string"
            )

    @staticmethod
    def _validate_website(website: str) -> None:
        """Ensure the website is an absolute HTTP or HTTPS URL.

        This validation checks only the URL structure. It does not make a
        network request to determine whether the website is reachable.

        Network availability is the responsibility of the collector layer.

        Args:
            website: URL to validate.

        Raises:
            SourceValidationError: If the URL is invalid.
        """
        Source._validate_text(website, "website")

        parsed = urlparse(website)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise SourceValidationError(
                f"website must be a valid HTTP(S) URL: {website!r}"
            )


"""Usage guidelines for the Source domain model.

Use Source to represent the identity and basic metadata of a news
publisher or organization.

Create Source objects in the domain/application layer when defining
known news sources:

    source = Source(
        id="reuters",
        name="Reuters",
        website="https://www.reuters.com",
        country="US",
        language="en",
        categories=("world", "business"),
    )

Source should be passed to collectors, processors, and repositories
when they need to know which publisher a piece of news belongs to.

Do not put collection-specific information in Source, such as:

    - RSS feed URLs
    - API endpoints
    - HTTP headers or authentication
    - Scraping settings
    - Database connections
    - AI or processing results

Those details belong to the appropriate collector, configuration,
storage, or processing modules.

The Source object is immutable. If source information needs to change,
create a new Source instance rather than modifying an existing one.

The `enabled` field indicates whether the source is currently intended
to be collected. Collection logic should check this value, but the
Source model itself should not perform or control the collection.

Source is a domain model and should remain independent of infrastructure.
It must not import or depend on PostgreSQL, Docker, HTTP clients,
RSS libraries, AI libraries, or framework-specific code.
"""