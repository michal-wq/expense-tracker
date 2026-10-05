# Expense Tracker

## Purpose

Expense Tracker is the foundation for a web application for managing and analysing
expenses. The project aims to demonstrate a complete DevOps pipeline, from
development through automated checks to deployment.

**Current status:** The Flask application exposes an endpoint at `/` that returns
the application name and status as JSON. Expense tracking and analysis have not
been implemented yet.

## API contract

The proposed [POST /api/expenses contract](docs/api/expenses.md) defines request
validation, persistence guarantees, and success and error responses. The endpoint
is documented for future implementation and is not available yet.

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

## Project structure

```text
expense-tracker/
├── app/
│   ├── __init__.py       Creates and configures the Flask application
│   └── routes.py         Defines the status endpoint
├── tests/
│   └── test_app.py       Placeholder for automated tests
├── wsgi.py              Entry point and local development server
├── pyproject.toml       Dependencies and development tool configuration
├── uv.lock              Locked dependency versions
├── README.md            Project documentation
└── LICENSE              MIT licence
```

## Licence

This project is released under the [MIT licence](LICENSE).
