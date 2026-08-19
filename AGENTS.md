# AGENTS.md

# News Intelligence — Agent Development Guide

## 1. Project

**Repository:**

https://github.com/NORMIES106204/News_intelligence

**Project root:**

```text
News_intelligence/
```

All commands below are executed from the **project root** unless explicitly
stated otherwise.

The project uses:

- Python 3.12+
- Python `venv`
- `pyproject.toml`
- pytest
- Ruff
- mypy

---

# 2. Project Structure

```text
News_intelligence/
│
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
├── .venv/
├── pyproject.toml
├── .env
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

Do not change the project structure without a clear reason.

---

# 3. Fresh Environment Setup

## 3.1 Clone the Repository

**Run from the directory where the project should be created.**

```bash
git clone https://github.com/NORMIES106204/News_intelligence.git
cd News_intelligence
```

From this point onward, commands should be run from:

```text
News_intelligence/
```

Verify the repository:

```bash
pwd
git status
```

---

## 3.2 Check Python

**Run from the project root.**

```bash
python3 --version
```

Required:

```text
Python 3.12+
```

Correct:

```bash
python3 --version
```

Incorrect:

```bash
python 3 --version
```

`python 3 --version` is interpreted by Python as trying to execute a file
called `3`.

If Python 3.12+ is unavailable, do not silently use an older version.
Report the problem.

---

## 3.3 Create the Virtual Environment

**Run from the project root.**

```bash
python3 -m venv .venv
```

Activate the environment:

```bash
source .venv/bin/activate
```

Verify the environment:

```bash
which python
python --version
python -m pip --version
```

`which python` should point to:

```text
News_intelligence/.venv/bin/python
```

All Python development commands should use this virtual environment.

---

## 3.4 Install the Project

**Run from the project root with `.venv` activated.**

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

The project must be installed in **editable mode** during development.

Do not use:

```bash
PYTHONPATH=src
```

as a normal workaround.

---

# 4. Environment Variables

If `.env.example` exists, create the local environment file.

**Run from the project root.**

```bash
cp .env.example .env
```

Edit `.env` when required.

The `.env` file contains local configuration and secrets.

**Never commit `.env`.**

If a new environment variable is required:

1. Add it to `.env.example` with a placeholder value.
2. Add the actual value only to `.env`.
3. Never commit the actual secret.
4. Document the variable if its purpose is not obvious.

---

# 5. Daily Development

Before starting work, activate the environment.

**Run from the project root.**

```bash
source .venv/bin/activate
```

Check the Git state:

```bash
git status
```

Check the current branch:

```bash
git branch --show-current
```

Do not start modifying files until the current Git state is understood.

---

# 6. Source Code and Tests

Application code belongs under:

```text
src/news_intelligence/
```

Tests belong under:

```text
tests/
```

Never put application code inside `tests/`.

Never put tests inside `src/`.

Use the `src/` layout consistently.

---

# 7. Adding a New Dependency

When a new Python package is required, the dependency must be added to
`pyproject.toml`.

Do not install packages only into the current virtual environment.

## Step 1 — Add the Dependency

### Runtime dependency

Add it under:

```toml
[project]
dependencies = [
    "package-name",
]
```

### Development-only dependency

Add it under:

```toml
[project.optional-dependencies]
dev = [
    "package-name",
]
```

Do **not** only run:

```bash
pip install package-name
```

without updating `pyproject.toml`.

---

## Step 2 — Install the Updated Dependencies

**Run from the project root with `.venv` activated.**

```bash
python -m pip install -e ".[dev]"
```

---

## Step 3 — Verify the Dependency

**Run from the project root.**

```bash
python -m pip show package-name
```

Then run the tests:

```bash
python -m pytest
```

---

## Step 4 — Commit the Dependency Change

The dependency change and the code that uses it should normally be committed
together.

**Run from the project root.**

```bash
git add pyproject.toml src/ tests/
```

Then:

```bash
git commit -m "feat(scope): add package-name dependency"
```

Never commit:

```text
.venv/
```

---

# 8. Running Tests

All normal test commands are executed from the **project root**:

```text
News_intelligence/
```

Do not normally run pytest from:

```text
src/
tests/
tests/unit/
tests/unit/domain/
```

## Run the Complete Test Suite

**Run from the project root.**

```bash
python -m pytest
```

---

## Run Only Unit Tests

```bash
python -m pytest tests/unit/
```

---

## Run Domain Tests

```bash
python -m pytest tests/unit/domain/
```

---

## Run Collector Tests

```bash
python -m pytest tests/unit/collectors/
```

---

## Run Integration Tests

```bash
python -m pytest tests/integration/
```

---

## Run a Specific Test File

Example:

```bash
python -m pytest tests/unit/domain/test_article.py
```

---

## Run a Specific Test

Example:

```bash
python -m pytest tests/unit/domain/test_article.py::test_article_creation
```

---

## Run Tests with Verbose Output

```bash
python -m pytest -v
```

---

## Stop at the First Failure

```bash
python -m pytest -x
```

---

# 9. Testing Rules

Every new component must have tests.

For example, if implementing:

```text
src/news_intelligence/domain/article.py
```

create or update:

```text
tests/unit/domain/test_article.py
```

If implementing:

```text
src/news_intelligence/collectors/rss.py
```

create or update:

```text
tests/unit/collectors/test_rss.py
```

Unit tests must:

- be deterministic
- be fast
- not depend on the public internet
- use fixtures or mocks for external services

---

# 10. Test Fixtures

Test data belongs under the relevant test directory.

Example:

```text
tests/
└── unit/
    └── collectors/
        ├── fixtures/
        │   ├── rss_valid.xml
        │   ├── atom_valid.xml
        │   └── rss_malformed.xml
        │
        └── test_rss.py
```

Do not download live websites during normal unit tests.

---

# 11. Code Formatting

Ruff is used for formatting.

## Check Formatting

**Run from the project root.**

```bash
ruff format --check .
```

## Automatically Format Code

```bash
ruff format .
```

After formatting, run the tests again:

```bash
python -m pytest
```

---

# 12. Linting

Ruff is used for linting.

## Check for Problems

**Run from the project root.**

```bash
ruff check .
```

## Automatically Fix Safe Problems

```bash
ruff check . --fix
```

After fixing:

```bash
python -m pytest
```

---

# 13. Type Checking

mypy is used for type checking.

**Run from the project root.**

```bash
mypy src/
```

Only source code is normally passed to mypy.

Fix type errors before considering the task complete.

---

# 14. Full Verification

Before committing a completed task, run all checks from the **project root**.

Run tests:

```bash
python -m pytest
```

Run linting:

```bash
ruff check .
```

Check formatting:

```bash
ruff format --check .
```

Run type checking:

```bash
mypy src/
```

The complete verification sequence is:

```bash
python -m pytest
ruff check .
ruff format --check .
mypy src/
```

All checks should pass before committing.

If one cannot be run because the tool is not configured yet, do not invent a
workaround. Report the problem.

---

# 15. Development Phases

Development must proceed incrementally.

## Phase 1 — Domain

Implement:

```text
src/news_intelligence/domain/
```

Initial models:

```text
Source
Feed
Article
```

Tests:

```text
tests/unit/domain/
```

Complete and test this phase before moving to collectors.

---

## Phase 2 — Collector Interface

Implement:

```text
src/news_intelligence/collectors/base.py
```

Add appropriate tests.

---

## Phase 3 — RSS Collector

Implement:

```text
src/news_intelligence/collectors/rss.py
```

Tests:

```text
tests/unit/collectors/
```

The RSS collector must convert external RSS/Atom entries into canonical
`Article` objects.

---

## Phase 4 — Integration

Test the complete flow:

```text
Source
   ↓
Feed
   ↓
RSSCollector
   ↓
Article
```

Integration tests belong in:

```text
tests/integration/
```

---

# 16. Coding Style

Use Python 3.12+.

Use:

- type hints
- clear names
- small functions
- focused modules
- simple classes
- dataclasses where appropriate
- timezone-aware datetimes
- UTC internally

Prefer readable code over clever code.

Avoid:

- unnecessary abstractions
- giant functions
- duplicated logic
- global mutable state
- hidden side effects
- premature optimization
- source-specific hardcoding

---

# 17. Architecture Rules

The main boundary is:

```text
domain/
    What the data is

collectors/
    How the data is obtained
```

The domain layer must not perform:

- network requests
- RSS parsing
- database operations
- API calls

Collectors convert external data into domain objects.

Dependency direction:

```text
collectors
    ↓
domain
```

Do not reverse this dependency.

---

# 18. Source Configuration

Sources and feeds are configuration, not Python code.

Configuration belongs under:

```text
config/sources/
```

For example:

```text
config/sources/
├── news.yaml
├── science.yaml
├── publications.yaml
└── space.yaml
```

Do not create:

```text
reuters.py
nasa.py
bbc.py
nature.py
```

just because a new source is added.

Prefer:

```text
YAML configuration
       ↓
generic collector
       ↓
     Article
```

---

# 19. Current Data Scope

The initial `Article` contains:

```text
id
source_id
feed_id
title
description
url
published_at
collected_at
language
```

Do not add future intelligence fields yet:

```text
embedding
cluster_id
event_id
hotness_score
impact_score
relevance_score
AI summary
```

Do not download full article bodies during the initial collection phase.

---

# 20. Git Workflow

All Git commands are run from the **project root**.

Check status:

```bash
git status
```

Check the current branch:

```bash
git branch --show-current
```

Review changes:

```bash
git diff
```

Review changed files:

```bash
git status --short
```

---

# 21. Before Commit

From the project root:

```bash
git status
```

Review the changes:

```bash
git diff
```

Run the complete test suite:

```bash
python -m pytest
```

Run linting:

```bash
ruff check .
```

Check formatting:

```bash
ruff format --check .
```

Run type checking:

```bash
mypy src/
```

Review the Git diff again:

```bash
git diff
```

Before committing, make sure:

- no `.env` is included
- no `.venv/` is included
- no generated files are included
- no unrelated changes are included
- tests pass
- linting passes
- formatting passes
- type checking passes

---

# 22. Commit

Commits should contain **one logical change**.

Example:

```bash
git add src/news_intelligence/domain/source.py
git add tests/unit/domain/test_source.py
git commit -m "feat(domain): add Source model"
```

Another example:

```bash
git add src/news_intelligence/collectors/rss.py
git add tests/unit/collectors/
git commit -m "feat(collectors): add RSS collector"
```

Preferred commit format:

```text
type(scope): description
```

Common types:

```text
feat
fix
test
refactor
docs
chore
```

Examples:

```text
feat(domain): add Article model
test(domain): add Article validation tests
feat(collectors): add RSS collector
fix(collectors): handle missing publication date
refactor(domain): simplify Feed validation
docs: update development setup
chore: configure Ruff
```

Avoid vague commits such as:

```text
update
changes
fix
stuff
work
test
```

---

# 23. After Commit

Verify the repository:

```bash
git status
```

View the latest commit:

```bash
git log -1 --oneline
```

The working tree should normally be clean.

---

# 24. Push

Only push completed and tested work.

Before pushing:

```bash
git status
python -m pytest
```

Then:

```bash
git push
```

Do not force-push unless explicitly instructed.

Never use force-push as part of the normal workflow.

---

# 25. Files That Must Never Be Committed

The following are local or generated files:

```text
.venv/
.env
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
build/
dist/
*.egg-info/
```

Ensure `.gitignore` contains them.

---

# 26. Adding a New Source

Adding a new news source should normally require configuration only.

Process:

```text
Find source
    ↓
Find RSS/Atom feed
    ↓
Add Source configuration
    ↓
Add Feed configuration
    ↓
Validate
    ↓
Run tests
```

Do not create source-specific Python code unless the generic collector cannot
handle the source.

If custom logic is genuinely required, document why it cannot use the generic
collector before implementing it.

---

# 27. Definition of Done

A task is complete when:

- implementation is finished
- tests are added or updated
- tests pass
- code quality checks pass when configured
- no unrelated files were changed
- configuration/dependencies are updated if necessary
- Git diff has been reviewed
- commit message clearly describes the change

Do not consider code complete merely because it runs once.

---

# 28. Agent Rules

For every task:

1. Start from the project root.
2. Check `git status`.
3. Read the relevant existing code.
4. Identify the current development phase.
5. Make only the requested changes.
6. Add or update tests.
7. Run the relevant tests.
8. Run the full test suite before committing.
9. Run Ruff and mypy when configured.
10. Review `git diff`.
11. Commit one logical change.
12. Do not modify unrelated files.
13. Do not implement future phases unless explicitly requested.

When adding a dependency:

```text
Update pyproject.toml
        ↓
Install with:
python -m pip install -e ".[dev]"
        ↓
Run tests
        ↓
Run quality checks
        ↓
Commit
```

When adding an environment variable:

```text
Update .env.example
        ↓
Add actual value to .env
        ↓
Never commit .env
```

When adding a source/feed:

```text
Update config/sources/
        ↓
Validate
        ↓
Run tests
```

When adding code:

```text
Add/update source code
        ↓
Add/update tests
        ↓
Run tests
        ↓
Run quality checks
        ↓
Review git diff
        ↓
Commit
```

The repository must always remain reproducible from a fresh clone.