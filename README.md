# Expense Tracker

## Purpose

Expense Tracker is the foundation for a web application for managing and analysing
expenses. The project aims to demonstrate a complete DevOps pipeline, from
development through automated checks to deployment.

**Current status:** The Flask application exposes a status endpoint at `/` and
`POST /api/expenses` for validating requests and returning expense fields with a
generated ID and status 201. `GET /expenses` serves a UI for submitting expenses
and viewing the last successful response. Expenses are not stored. Persistence
and expense analysis have not been implemented yet.

## API contract

The [POST /api/expenses contract](docs/api/expenses.md) defines request validation,
success and error responses, and planned persistence guarantees. The current
implementation intentionally omits storage.

## Prerequisites

- Python ≥ 3.12
- Git for cloning the repository
- uv for managing the Python environment and dependencies
- Make and awk for the Makefile shortcuts (optional when running uv directly)

An internet connection is needed to install dependencies.
No database configuration is required at this stage.

## Setup

Clone the repository and open the project directory:

```bash
git clone https://github.com/michal-wq/expense-tracker.git
cd expense-tracker
```

Install dependencies:

```bash
uv sync --locked
```

This command creates the `.venv` virtual environment and installs application and
development dependencies using the versions recorded in `uv.lock`. The `--locked`
option checks that the lockfile matches `pyproject.toml` without modifying it.
There is no need to activate the environment manually because the commands below
use `uv run`.

## Usage

Run all commands from the project directory.

### Make commands

The Makefile provides shortcuts for the project's uv commands. Run `make` or
`make help` to list the available targets.

| Command | Purpose | Underlying command |
| --- | --- | --- |
| `make help` | List available commands (the default target) | Prints target descriptions |
| `make install` | Install application and development dependencies | `uv sync --locked` |
| `make run` | Start the development server on port 8000 | `uv run --locked python wsgi.py` |
| `make test` | Run the test suite | `uv run --locked pytest` |
| `make lint` | Check Python code with Ruff | `uv run --locked ruff check .` |
| `make fmt` | Format Python files in place | `uv run --locked ruff format .` |
| `make cov` | Run tests with coverage and show missing lines | `uv run --locked pytest --cov=app --cov-report=term-missing` |

These targets use the project's uv environment; manual activation is not needed.
The `--locked` flag prevents changes to `uv.lock` and fails if it is out of date.
`make fmt` modifies files, so review its changes before committing. The coverage
configuration requires at least 80% coverage for `make cov` to pass.

### Run locally

```bash
uv run python wsgi.py
```

The application is available at <http://127.0.0.1:8000>.
The development server runs with debug mode enabled and is intended for local
development. Press `Ctrl+C` to stop it.

### Check the application status

Open the application URL in a browser or request it with `curl`:

```bash
curl http://127.0.0.1:8000/
```

The response contains:

```json
{
  "name": "expense-tracker",
  "status": "running"
}
```

### Use the expense UI

With the application running, open <http://127.0.0.1:8000/expenses> in a browser
with JavaScript enabled. `GET /expenses` returns the HTML page with **200 OK**.
The status endpoint at `/` remains unchanged.

Enter an amount, category, and date, then select **Create expense**. All fields
are required. The amount must be positive with at most two decimal places;
the UI accepts a comma or period and converts a decimal comma to a period before
sending the amount as a string, without floating-point conversion or rounding.
Categories cannot contain only whitespace, and dates must be valid with a year
from 0001 through 9999. The API also validates every submission.

The button is disabled while a request is pending. Errors are displayed without
clearing your inputs. A successful response appears under **Last submitted
expense**. The layout adapts to narrow screens, follows your system's light/dark
theme, and includes visible keyboard focus outlines.

**Current limitations:** Expenses are not saved on the server or in browser
storage. Only the last successful submission is displayed, and that result
disappears when the page is reloaded. There is no expense history, editing,
deletion, or analysis yet.

### Submit an expense

With the application running, use another terminal:

```bash
curl -i http://127.0.0.1:8000/api/expenses \
  -H 'Content-Type: application/json' \
  -d '{"amount":"12.30","category":"Groceries","date":"2026-10-05"}'
```

The endpoint validates the request and returns **201 Created** with JSON like:

```json
{
  "id": "3d7fbcb6-cf52-4df4-9053-3ae6d294fcf5",
  "amount": "12.30",
  "category": "Groceries",
  "date": "2026-10-05"
}
```

The ID is generated for each request. **Expenses are returned but are not saved
yet**, including in memory. Amount must be a positive decimal string with at most
two decimal places, category must contain non-whitespace text, and date must be
a valid `YYYY-MM-DD` date. Invalid requests return **400** with a JSON `error` field.

## Project structure

```text
expense-tracker/
├── app/
│   ├── __init__.py       Creates and configures the Flask application
│   ├── routes.py         Defines status, expense creation, and UI endpoints
│   ├── templates/
│   │   └── index.html   Expense form and result display
│   └── static/
│       ├── style.css    Responsive layout, themes, and focus styles
│       └── app.js       Validation, API submission, and feedback
├── tests/
│   └── test_api.py       API response and validation tests
├── wsgi.py              Entry point and local development server
├── pyproject.toml       Dependencies and development tool configuration
├── uv.lock              Locked dependency versions
├── Makefile             Shortcuts for setup, running, and quality checks
├── README.md            Project documentation
└── LICENSE              MIT licence
```

Run the tests with `uv run --locked pytest`.
Run the configured lint checks with `uv run --locked ruff check .`.

## Contributing

See the [Contribution guidelines](CONTRIBUTING.md) for the branching workflow,
commit conventions, and checks before merging.

## Licence

This project is released under the [MIT licence](LICENSE).
