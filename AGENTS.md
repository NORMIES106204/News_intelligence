# AGENTS.md

# News Intelligence — Development Guidelines

## 1. Project Overview

News Intelligence is a Python-based personal news intelligence system.

The system will eventually:

1. Collect news from multiple sources.
2. Normalize collected data.
3. Deduplicate articles.
4. Detect related news/events.
5. Cluster articles into events.
6. Evaluate relevance and impact.
7. Rank important/hot events.
8. Store historical data.
9. Send important notifications to the user.

The initial focus is ONLY on the domain model and collection system.

Current collection targets include:

- General/world news
- Science
- Scientific publications
- Space
- Technology
- Semiconductors
- Vietnam/local news

The system should eventually support approximately dozens of sources and potentially 50–100 feeds.

---

# 2. Core Development Philosophy

Build the project incrementally.

Do NOT implement the entire system at once.

Prefer:

    small component
        ↓
    tests
        ↓
    verify
        ↓
    integrate
        ↓
    next component

over:

    large implementation
        ↓
    many interconnected problems

Every component must have a clear responsibility.

Avoid premature abstraction.

Do not create classes, modules, or frameworks unless they solve an actual architectural problem.

---

# 3. Current Scope

The current development phase focuses on:

    domain/
    collectors/

Do NOT implement the following yet unless explicitly requested:

- PostgreSQL
- SQLAlchemy
- Alembic
- Database repositories
- AI models
- embeddings
- clustering
- event detection
- ranking
- hotness scoring
- impact scoring
- notifications
- Telegram
- scheduling
- background workers
- web dashboard
- full article scraping
- distributed processing

Future components must not leak into the current implementation.

---

# 4. Project Structure

The current project structure is:

    News_intelligence/
    │
    ├── src/
    │   └── news_intelligence/
    │       │
    │       ├── domain/
    │       │   ├── __init__.py
    │       │   ├── article.py
    │       │   ├── source.py
    │       │   └── feed.py
    │       │
    │       ├── collectors/
    │       │   ├── __init__.py
    │       │   ├── base.py
    │       │   └── rss.py
    │       │
    │       └── main.py
    │
    ├── tests/
    │   ├── unit/
    │   │   ├── domain/
    │   │   └── collectors/
    │   │
    │   └── integration/
    │
    ├── config/
    │   └── sources/
    │       ├── news.yaml
    │       ├── science.yaml
    │       ├── publications.yaml
    │       └── space.yaml
    │
    ├── .venv/
    ├── pyproject.toml
    ├── .gitignore
    ├── AGENTS.md
    └── README.md

Do not reorganize this structure without a strong architectural reason.

If a structural change is necessary, explain the reason before making it.

---

# 5. Architecture

The fundamental architecture is:

    Source
       │
       ▼
      Feed
       │
       ▼
    Collector
       │
       ▼
     Article
       │
       ▼
    Processing
       │
       ▼
    Intelligence
       │
       ▼
    Storage
       │
       ▼
    Notification

Only the first four components are currently being implemented.

---

# 6. Domain vs Infrastructure

The most important architectural boundary is:

    domain/
        What is the data?

    collectors/
        How do we obtain the data?

Domain objects must NOT know about external infrastructure.

The domain layer must not depend on:

- RSS libraries
- HTTP clients
- web scraping libraries
- PostgreSQL
- SQLAlchemy
- filesystem infrastructure
- notification systems
- AI libraries

Dependency direction:

    collectors
        │
        ▼
      domain

Never:

    domain
        │
        ▼
    collectors

---

# 7. Domain Model

The initial domain contains three objects:

    Source
    Feed
    Article

Their relationship is:

    Source
      │
      ├── Feed
      │     ├── Article
      │     ├── Article
      │     └── Article
      │
      └── Feed
            └── Article

---

# 8. Source

`domain/source.py`

A Source represents a publisher or organization.

Examples:

- Reuters
- NASA
- Nature
- ESA
- BBC
- Space.com

A Source answers:

    "Who publishes this information?"

Suggested fields:

    id
    name
    website
    country
    language
    categories
    enabled

Conceptually:

    Source(
        id: str,
        name: str,
        website: str,
        country: str | None,
        language: str | None,
        categories: list[str],
        enabled: bool = True
    )

A Source must NOT:

- perform HTTP requests
- parse RSS
- collect articles
- access databases
- perform AI analysis

---

# 9. Feed

`domain/feed.py`

A Feed represents a specific content stream belonging to a Source.

Examples:

    Reuters World
    Reuters Technology
    NASA News
    NASA Spaceflight

A Source may contain multiple feeds.

A Feed answers:

    "Which content stream are we collecting from this publisher?"

Suggested fields:

    id
    source_id
    name
    url
    type
    enabled

Conceptually:

    Feed(
        id: str,
        source_id: str,
        name: str,
        url: str,
        type: str,
        enabled: bool = True
    )

`source_id` establishes:

    Feed → Source

A Feed must NOT:

- perform network requests
- parse RSS
- create Articles
- access databases

---

# 10. Article

`domain/article.py`

An Article represents one canonical news item.

Initial fields:

    id
    source_id
    feed_id
    title
    description
    url
    published_at
    collected_at
    language

Conceptually:

    Article(
        id: str,
        source_id: str,
        feed_id: str,
        title: str,
        description: str | None,
        url: str,
        published_at: datetime | None,
        collected_at: datetime,
        language: str | None
    )

The initial Article represents ONLY collected source information.

Do NOT add:

- hotness score
- relevance score
- impact score
- cluster ID
- event ID
- embedding
- AI summary
- sentiment
- notification status

Those belong to future processing/intelligence layers.

---

# 11. Article ID

Article IDs should be deterministic when possible.

Preferred order:

1. Reliable source GUID/ID.
2. Stable canonical URL.
3. Deterministic hash of stable information.

Never use the article title alone as the identifier.

For example:

    source_id + canonical_url

can be hashed to produce a stable ID.

The same source and URL should produce the same ID.

The ID-generation logic should be isolated and independently testable.

---

# 12. Time Handling

All timestamps must be timezone-aware.

Use UTC internally.

Do not create naive datetimes.

Example:

    2026-08-18T08:30:00+00:00

`published_at`:

    When the publisher says the article was published.

`collected_at`:

    When our system obtained the article.

Both fields are important.

Do not replace one with the other.

---

# 13. Collector Architecture

Collectors are responsible for obtaining external data and converting it into domain objects.

Current collectors:

    base.py
    rss.py

Future collectors may include:

    api.py
    web.py

Do not implement future collectors until explicitly requested.

---

# 14. Base Collector

`collectors/base.py`

The base collector defines the common contract.

Conceptually:

    Collector.collect(feed: Feed) -> list[Article]

Every collector must follow this contract.

For example:

    RSSCollector
    APICollector
    WebCollector

should all eventually expose the same conceptual operation:

    collect(feed) -> list[Article]

The application should not care how the data was obtained.

---

# 15. RSS Collector

`collectors/rss.py`

RSSCollector is responsible for:

1. Receiving a Feed.
2. Validating the Feed.
3. Fetching the RSS/Atom document.
4. Parsing it.
5. Converting entries into Article objects.
6. Returning `list[Article]`.

RSSCollector must work with generic feeds.

Do NOT create:

    ReutersCollector
    NASACollector
    NatureCollector
    BBCCollector

Do not create one Python collector per website.

The source configuration determines the feed.

The generic collector determines how to retrieve it.

---

# 16. RSS and Atom

The RSS collector should support both:

- RSS
- Atom

where practical.

Do not manually parse XML unless there is a strong reason.

Use a mature feed parsing library.

Raw library-specific objects must NOT escape the collector layer.

The rest of the application should only see:

    Article

not:

    feedparser.FeedParserDict

or another library-specific type.

---

# 17. RSS Entry Mapping

Map external feed entries into Article objects.

Typical mapping:

    entry.title
        ↓
    Article.title

    entry.description / summary
        ↓
    Article.description

    entry.link
        ↓
    Article.url

    entry.published / updated
        ↓
    Article.published_at

    Feed.source_id
        ↓
    Article.source_id

    Feed.id
        ↓
    Article.feed_id

    current UTC time
        ↓
    Article.collected_at

    entry.guid / entry.id
        ↓
    Article.id

Handle missing fields explicitly.

Never invent information.

---

# 18. Missing Data Policy

Potential cases:

    Missing title
    Missing description
    Missing URL
    Missing publication date
    Missing GUID
    Missing language

Recommended behavior:

- Missing title:
  Article is generally invalid; skip it or raise a clear validation error.

- Missing URL:
  Skip the article if no canonical URL can be determined.

- Missing description:
  Allowed.

- Missing publication date:
  Allowed; use `None`.

- Missing GUID:
  Use deterministic fallback ID generation.

- Missing language:
  Allowed; use `None` or feed/source language where appropriate.

Do not silently fabricate values.

---

# 19. Network Handling

Network operations belong ONLY in collectors/infrastructure.

Collectors must:

- use a reasonable timeout
- handle connection failures
- handle HTTP failures
- handle malformed feeds
- avoid infinite retries
- produce useful error information

A single failed feed must not crash the entire collection process.

However, do not implement a complicated retry framework yet.

Keep the first implementation simple.

---

# 20. Error Handling

Use explicit collector errors where useful.

Possible errors:

    CollectorError
    FeedFetchError
    FeedParseError
    UnsupportedFeedTypeError
    InvalidFeedError

Errors should contain useful context:

    feed ID
    feed URL
    underlying error

Do not silently catch every exception.

Do not hide programming errors behind generic error handling.

---

# 21. Testing Requirements

Every component should have tests.

Domain tests:

    tests/unit/domain/

Collector tests:

    tests/unit/collectors/

Integration tests:

    tests/integration/

Unit tests must NOT depend on the public internet.

Use local fixtures.

Recommended fixtures:

    tests/unit/collectors/fixtures/
        rss_valid.xml
        atom_valid.xml
        rss_missing_description.xml
        rss_missing_date.xml
        rss_missing_guid.xml
        rss_missing_url.xml
        rss_malformed.xml

Test at minimum:

- valid RSS
- valid Atom
- multiple entries
- missing description
- missing publication date
- missing GUID
- deterministic ID generation
- missing URL
- malformed feed
- unsupported feed type
- network failure
- timeout handling

---

# 22. Testing Philosophy

Tests should verify behavior, not implementation details.

Prefer:

    Given a valid feed,
    when the RSS collector runs,
    then it returns valid Article objects.

Avoid tests that depend heavily on private implementation details.

Tests should remain valid if the internal implementation is refactored.

---

# 23. Configuration

Source configuration belongs under:

    config/sources/

Examples:

    news.yaml
    science.yaml
    publications.yaml
    space.yaml

Source configuration is DATA.

It should not be hardcoded into collector classes.

Bad:

    if source.name == "NASA":
        ...

Good:

    Feed(
        id="nasa-news",
        source_id="nasa",
        ...
    )

The same RSSCollector should work for NASA, Reuters, Nature, BBC, or any other valid RSS feed.

---

# 24. Dependencies

Keep dependencies minimal.

The domain layer should preferably use the Python standard library.

Potential collector dependency:

    feedparser

HTTP functionality may use a suitable HTTP client.

Do not add large frameworks without a clear reason.

Every dependency added to the project must have a purpose.

Update `pyproject.toml` when adding dependencies.

Never install project dependencies manually without recording them in the project configuration.

---

# 25. Python Version

Target:

    Python 3.12+

Use modern Python features where they improve clarity.

Use:

- type hints
- dataclasses where appropriate
- `datetime`
- `typing`
- clear exception types

Do not sacrifice readability for cleverness.

---

# 26. Code Style

Write simple, readable Python.

Prefer:

    small functions
    explicit types
    descriptive names
    clear boundaries

Avoid:

    giant functions
    global mutable state
    hidden side effects
    unnecessary metaprogramming
    excessive inheritance
    premature optimization

Use docstrings for public classes/functions when their purpose is not obvious.

---

# 27. Dependency Direction

Maintain this dependency direction:

    domain
       ↑
       │
    collectors

More explicitly:

    RSSCollector
        ↓
      Feed
        ↓
      Article

Never:

    Article
       ↓
    RSSCollector

Domain must remain independent.

---

# 28. No Database Yet

PostgreSQL is planned for a later phase.

Do not add:

- SQLAlchemy
- psycopg
- Alembic
- repositories
- database sessions
- database models

to the current implementation.

The domain objects should be designed so they can later be persisted, but they should not know that a database exists.

---

# 29. No Full Article Scraping

The initial collector system only needs metadata:

    title
    description
    URL
    source
    feed
    publication date
    collection date
    language
    identifier

Do not download or parse full article bodies unless explicitly requested later.

This keeps bandwidth, storage, complexity, and legal/copyright concerns lower.

---

# 30. Implementation Process

When asked to implement a component:

1. Inspect the existing code.
2. Understand existing interfaces.
3. Make the smallest appropriate change.
4. Add or update tests.
5. Run tests.
6. Run lint/type checks if configured.
7. Report what changed.
8. Report test results.
9. Do not modify unrelated components.

Do not rewrite working code unnecessarily.

---

# 31. Incremental Development Order

The recommended initial implementation order is:

### Phase 1

Implement:

    domain/source.py

Then:

    tests/unit/domain/test_source.py

---

### Phase 2

Implement:

    domain/feed.py

Then:

    tests/unit/domain/test_feed.py

---

### Phase 3

Implement:

    domain/article.py

Then:

    tests/unit/domain/test_article.py

---

### Phase 4

Implement:

    collectors/base.py

Then verify the interface.

---

### Phase 5

Implement:

    collectors/rss.py

---

### Phase 6

Add RSS/Atom fixtures.

---

### Phase 7

Add RSS collector unit tests.

---

### Phase 8

Add an integration test:

    Feed
      ↓
    RSSCollector
      ↓
    list[Article]

Only after these phases are stable should the project move toward processing.

---

# 32. Future Architecture

The future system is expected to evolve toward:

    collectors/
        ↓
    processing/
        ↓
    intelligence/
        ↓
    storage/
        ↓
    notifications/

Possible future structure:

    src/news_intelligence/
    │
    ├── domain/
    │
    ├── collectors/
    │
    ├── processing/
    │
    ├── intelligence/
    │
    ├── storage/
    │
    ├── notifications/
    │
    └── application/

Do NOT create or implement these components prematurely.

---

# 33. Important Rules

Always follow these rules:

1. Source represents the publisher.
2. Feed represents a content stream.
3. Article represents an individual news item.
4. Collector obtains external data.
5. Domain does not perform I/O.
6. Collectors convert external data into domain objects.
7. Never create a collector for every individual website.
8. Keep source configuration separate from collector code.
9. Do not hardcode source-specific behavior into generic collectors.
10. Keep timestamps timezone-aware.
11. Use UTC internally.
12. Do not silently fabricate missing data.
13. Unit tests must not depend on the internet.
14. Keep dependencies minimal.
15. Do not add database functionality yet.
16. Do not add AI functionality yet.
17. Do not add notification functionality yet.
18. Do not implement future components unless explicitly requested.
19. Prefer simple solutions over premature abstractions.
20. Preserve existing architecture unless there is a strong reason to change it.

---

# 34. Definition of Done

A component is considered complete only when:

- The implementation is complete.
- Types are correct.
- Invalid input is handled appropriately.
- Unit tests exist.
- Tests pass.
- No unrelated functionality was added.
- The architecture remains consistent.
- The code is understandable to another developer.

Do not mark a component as complete merely because it runs once.

---

# 35. Agent Behavior

Before making significant architectural changes:

    Explain the problem.
    Explain the proposed solution.
    Explain the affected files.
    Wait for approval if the change is outside the current task.

For normal implementation tasks:

    implement
    test
    report

Do not ask unnecessary questions when the existing architecture already provides the answer.

When uncertain about a design decision, prefer the simplest solution consistent with these guidelines.

The goal is to build a maintainable system incrementally, not to maximize the amount of code written.