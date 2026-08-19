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


# 22. Testing Philosophy

Tests should verify behavior, not implementation details.

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


# 24. Dependencies


Every dependency added to the project must have a purpose.

Update `pyproject.toml` when adding dependencies.

Never install project dependencies manually without recording them in the project configuration.