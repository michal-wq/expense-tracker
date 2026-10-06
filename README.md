# Expense Tracker

## Purpose

Expense Tracker is the foundation for a web application for managing and analysing
expenses. The project aims to demonstrate a complete DevOps pipeline, from
development through automated checks to deployment.

**Current status:** The Flask application exposes a status endpoint at `/` and
`POST /api/expenses` for validating requests and returning expense fields with a
generated ID and status 201. `GET /expenses` is a placeholder for the future UI
and currently returns an empty 204 response. Expenses are not stored. Persistence,
the UI, and expense analysis have not been implemented yet.

## API contract

The [POST /api/expenses contract](docs/api/expenses.md) defines request validation,
success and error responses, and planned persistence guarantees. The current
implementation intentionally omits storage.

## Prerequisites

- Python ≥ 3.12
- Git for cloning the repository
- uv for managing the Python environment and dependencies

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

### Check the expenses page placeholder

```bash
curl -i http://127.0.0.1:8000/expenses
```

`GET /expenses` currently returns **204 No Content** with an empty response body.
This is temporary behavior: the endpoint is reserved for the future expenses UI
and does not serve HTML or return expense data yet. The status endpoint at `/`
remains unchanged.

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
│   └── routes.py         Defines status, expense creation, and page placeholder endpoints
├── tests/
│   └── test_api.py       API response and validation tests
├── wsgi.py              Entry point and local development server
├── pyproject.toml       Dependencies and development tool configuration
├── uv.lock              Locked dependency versions
├── README.md            Project documentation
└── LICENSE              MIT licence
```

Run the tests with `uv run --locked pytest`.
Run the configured lint checks with `uv run --locked ruff check .`.

## Licence

This project is released under the [MIT licence](LICENSE).
