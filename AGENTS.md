# AGENTS.md

# News Intelligence — Agent Development Guide

## 1. Project

Repository:

https://github.com/NORMIES106204/News_intelligence

Project root:

    News_intelligence/

All commands below must be executed from the PROJECT ROOT unless explicitly
stated otherwise.

The project uses:

- Python 3.12+
- Python `venv`
- `pyproject.toml`
- pytest
- Ruff
- mypy

---

## 2. Project Structure

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

Do not change the project structure without a reason.

---

## 3. Fresh Environment Setup

### 3.1 Clone

Run from the directory where the project should be created:

```bash
git clone https://github.com/NORMIES106204/News_intelligence.git
cd News_intelligence

3.2 Create Virtual Environment
Run from the project root:
python3 -m venv .venv
Activate:
source .venv/bin/activate
Verify:
which python
python --version
python -m pip --version

3.3 Install the Project
Run from the project root with .venv activated:
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
The project must be installed in editable mode.
Do not use PYTHONPATH=src as a workaround.

4. Daily Development
Before starting work, run from the project root:
source .venv/bin/activate
git status
Check the current branch:
git branch --show-current

5. Coding
Application code belongs under:
src/news_intelligence/
Tests belong under:
tests/
Never put application code inside tests/.
Never put tests inside src/.
Use the src/ layout consistently.
6. Adding a New Dependency
When a new Python package is required:
Step 1 — Add it to pyproject.toml
Runtime dependency:
[project]
dependencies = [
    "package-name",
]
Development-only dependency:
[project.optional-dependencies]
dev = [
    "package-name",
]
Do NOT only run:
pip install package-name
without updating pyproject.toml.
Step 2 — Install the updated dependencies
Run from the project root with .venv activated:
python -m pip install -e ".[dev]"
Step 3 — Verify
Check that the package is installed:
python -m pip show package-name
Then run:
python -m pytest
Step 4 — Commit
The dependency change and the code that uses it should normally be committed together.
Example:
git add pyproject.toml src/ tests/
git commit -m "feat(collectors): add RSS parsing dependency"
Do not commit .venv/.

12. Type Checking
Run from the project root:
mypy src/
Only source code is normally passed to mypy.
Fix type errors before considering the task complete.
13. Full Verification
Before committing a completed task, run from the project root:
python -m pytest
ruff check .
ruff format --check .
mypy src/
All checks should pass.
If one cannot be run because the tool is not configured yet, do not invent a workaround. Report it.
