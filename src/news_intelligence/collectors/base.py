# collectors/base.py

from abc import ABC, abstractmethod

from news_intelligence.domain.article import Article
from news_intelligence.domain.feed import Feed
from news_intelligence.domain.source import Source


class Collector(ABC):
    """Contract for all content collectors."""

    @abstractmethod
    def collect(
        self,
        feed: Feed,
        source: Source,
    ) -> list[Article]:
        """Collect and normalize content into Article objects."""
        raise NotImplementedError