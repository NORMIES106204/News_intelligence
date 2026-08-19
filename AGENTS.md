# AGENTS.md

# News Intelligence

Repository:

https://github.com/NORMIES106204/News_intelligence

All commands are run from the **project root**:

```text
News_intelligence/
```

---

## 1. Environment Setup

### Clone

```bash
git clone https://github.com/NORMIES106204/News_intelligence.git
cd News_intelligence
```

### Create and activate venv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Verify

```bash
python --version
which python
```

Use Python 3.12+.

### Install project

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Never commit `.venv/` or `.env`.

---

## 2. Project Structure

```text
News_intelligence/
├── src/
│   └── news_intelligence/
│       ├── domain/
│       ├── collectors/
│       └── main.py
│
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   └── collectors/
│   └── integration/
│
├── config/
│   └── sources/
│
├── pyproject.toml
├── .env.example
├── .gitignore
└── AGENTS.md
```

Source code → `src/`

Tests → `tests/`

Source/feed configuration → `config/sources/`

---

## 3. Dependencies

Add dependencies to `pyproject.toml`.

Runtime:

```toml
[project]
dependencies = [
    "package-name",
]
```

Development:

```toml
[project.optional-dependencies]
dev = [
    "package-name",
]
```

After changing dependencies:

```bash
python -m pip install -e ".[dev]"
```

Do not only use `pip install package-name`.

---

## 4. Testing

Always run tests from the **project root**.

All tests:

```bash
python -m pytest
```

Unit tests:

```bash
python -m pytest tests/unit/
```

Domain tests:

```bash
python -m pytest tests/unit/domain/
```

Collector tests:

```bash
python -m pytest tests/unit/collectors/
```

Integration tests:

```bash
python -m pytest tests/integration/
```

Specific test:

```bash
python -m pytest tests/unit/domain/test_article.py
```

Tests must not normally depend on the public internet.

---

## 5. Code Quality

Run from the project root:

```bash
ruff check .
ruff format --check .
mypy src/
```

Format code when needed:

```bash
ruff format .
```

---

## 6. Development Rules

- Use Python 3.12+.
- Use type hints.
- Keep modules small and focused.
- Domain contains data/models.
- Collectors handle external data collection.
- Domain must not perform network/database operations.
- Use generic collectors instead of creating one Python file per news source.
- Add/update tests whenever behavior changes.
- Do not implement future features unless requested.

---

## 7. Development Phases

### Phase 1 — Domain

```text
src/news_intelligence/domain/
tests/unit/domain/
```

Implement:

```text
Source
Feed
Article
```

### Phase 2 — Collectors

```text
src/news_intelligence/collectors/
tests/unit/collectors/
```

Implement the collector interface and RSS/Atom collector.

### Phase 3 — Integration

```text
tests/integration/
```

Test:

```text
Source → Feed → Collector → Article
```

---

## 8. Git Workflow

Before working:

```bash
git status
git branch --show-current
```

Before committing:

```bash
python -m pytest
ruff check .
ruff format --check .
mypy src/
git diff
```

Commit one logical change at a time:

```bash
git add <files>
git commit -m "type(scope): description"
```

Examples:

```text
feat(domain): add Article model
feat(collectors): add RSS collector
test(collectors): add RSS tests
fix(domain): validate Article fields
```

After committing:

```bash
git status
```

Push:

```bash
git push
```

Do not force-push unless explicitly instructed.

---

## 9. Agent Rules

For every task:

1. Check `git status`.
2. Inspect existing code before changing it.
3. Make only the requested changes.
4. Add/update tests.
5. Run tests and quality checks.
6. Review `git diff`.
7. Commit one logical change.
8. Do not modify unrelated files.

Keep the project simple, reproducible, and easy to maintain.