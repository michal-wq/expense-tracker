# Expense Tracker

## Purpose

Expense Tracker is the foundation for a web application for managing and analysing
expenses. The project aims to demonstrate a complete DevOps pipeline, from
development through automated checks to deployment.

**Current status:** The Flask application exposes a status endpoint at `/` and
`POST /api/expenses` for validating and storing expenses in PostgreSQL. A
successful request returns the saved expense with a generated ID and status
201. `GET /expenses` serves a UI for submitting expenses and viewing the last
successful response. The UI does not display an expense history or provide
expense analysis yet.

## API contract

The [POST /api/expenses contract](docs/api/expenses.md) defines request validation,
persistence guarantees, and success and error responses.

## Prerequisites

- Python ≥ 3.12
- Git for cloning the repository
- uv for managing the Python environment and dependencies
- Make and awk for the Makefile shortcuts (optional when running uv directly)
- Docker with a running engine for PostgreSQL and container commands (Docker Desktop on macOS)

An internet connection is needed to install dependencies.
The application uses PostgreSQL. The Compose setup below starts a local database
with a project-specific named volume.

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
| `make lint` | Check Python lint and formatting | `uv run --locked ruff check .` and `uv run --locked ruff format --check .` |
| `make fmt` | Format Python files in place | `uv run --locked ruff format .` |
| `make cov` | Run tests with coverage and show missing lines | `uv run --locked pytest --cov=app --cov-report=term-missing` |
| `make build` | Build wheel and source distributions | `uv build` |
| `make verify-package` | Build and test the installed wheel in a temporary environment | Builds packages, installs the wheel and pytest, then runs the copied tests |
| `make docker-build` | Build the application image | `docker build -t "$(IMAGE):$(TAG)" .` |
| `make docker-run` | Run the image on localhost without database configuration | `docker run --rm -p "127.0.0.1:$(PORT):8000" "$(IMAGE):$(TAG)"` |
| `make docker-test` | Build the image and test its HTTP endpoints | Runs `docker-build`, then `checks/test_docker.py` with pytest |

Development commands use the project's uv environment; manual activation is not needed.
The build target uses an isolated build environment with the configured setuptools backend.
The `--locked` flag prevents changes to `uv.lock` and fails if it is out of date.
`make fmt` modifies files, so review its changes before committing. The coverage
configuration requires at least 80% coverage for `make cov` to pass.

### Start PostgreSQL locally

```bash
docker compose up -d --wait db
```

Compose creates the `expenses` table and stores database files in its named
`postgres_data` volume. The default local database settings are:

| Setting | Value |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `5432` |
| Database | `expense_tracker` |
| User | `expense_tracker` |
| Password | `expense_tracker_local` |

If port 5432 is already in use, start PostgreSQL on another host port, for
example `POSTGRES_PORT=5433 docker compose up -d --wait db`, and use that port
in `DATABASE_URL` below. To stop PostgreSQL while retaining its data, run
`docker compose down`. To remove the database and its data volume, run
`docker compose down --volumes`.

### Run Flask locally

Start the development server with the database URL configured:

```bash
DATABASE_URL='postgresql://expense_tracker:expense_tracker_local@127.0.0.1:5432/expense_tracker' make run
```

For a non-default PostgreSQL port, replace `5432` in the URL. The application
is available at <http://127.0.0.1:8000>. The development server runs with debug
mode enabled and is intended for local development. Press `Ctrl+C` to stop it.

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

**Current limitations:** Expenses are saved in PostgreSQL, but the UI displays
only the last successful submission from the current page. That result
disappears when the page is reloaded. The UI does not yet show an expense
history or support editing, deletion, or analysis.

### Submit an expense

With the application running, use another terminal:

```bash
curl -i http://127.0.0.1:8000/api/expenses \
  -H 'Content-Type: application/json' \
  -d '{"amount":"12.30","category":"Groceries","date":"2026-10-05"}'
```

The endpoint validates and stores the request, then returns **201 Created**
with the saved expense as JSON:

```json
{
  "id": "3d7fbcb6-cf52-4df4-9053-3ae6d294fcf5",
  "amount": "12.30",
  "category": "Groceries",
  "date": "2026-10-05"
}
```

The ID is generated for each request. The expense is stored in PostgreSQL before
the successful response is returned. Amount must be a positive decimal string
with at most two decimal places, category must contain non-whitespace text, and
date must be a valid `YYYY-MM-DD` date. Invalid requests return **400** with a
JSON `error` field. A database failure returns **500** and does not report the
expense as successfully created.

## Run with Docker

Start Docker Desktop or your Docker engine. Start PostgreSQL and build the
application image from the project root:

```bash
docker compose up -d --wait db
make docker-build
```

The default image is `expense-tracker:local`. The image uses Python 3.12 and
uv 0.10.9 to install locked application dependencies without development tools.
Gunicorn serves `wsgi:app` as a non-root user on container port 8000.

Run the image on the same Docker network as PostgreSQL and configure the
database URL to use the Compose service name `db`:

```bash
docker run --rm --network expense-tracker_default \
  -e DATABASE_URL='postgresql://expense_tracker:expense_tracker_local@db:5432/expense_tracker' \
  -p 127.0.0.1:8000:8000 expense-tracker:local
```

Open <http://127.0.0.1:8000/expenses> for the UI. The root URL
<http://127.0.0.1:8000/> returns status JSON. Container logs appear in the
terminal; keep it open while using the app and press **Ctrl+C** to stop it.
The `--rm` option removes the application container when it exits; the image and
PostgreSQL volume remain.

If port 8000 is occupied, select a different host port:

```bash
docker run --rm --network expense-tracker_default \
  -e DATABASE_URL='postgresql://expense_tracker:expense_tracker_local@db:5432/expense_tracker' \
  -p 127.0.0.1:8001:8000 expense-tracker:local
```

Then open <http://127.0.0.1:8001/expenses>. Only the host port changes: Gunicorn
still listens on port 8000 inside the container. Ports are published on
`127.0.0.1`, making the app accessible from the same computer.

Image name and tag can also be overridden. Use matching values when building
and running:

```bash
make docker-build IMAGE=my-expenses TAG=dev
docker run --rm --network expense-tracker_default \
  -e DATABASE_URL='postgresql://expense_tracker:expense_tracker_local@db:5432/expense_tracker' \
  -p 127.0.0.1:8001:8000 my-expenses:dev
```

Rebuild the image after changing application files or the Dockerfile, then
stop the old container and start a new one to use the updated image.

**Persistence:** Expenses are stored in the PostgreSQL `postgres_data` volume,
so they remain available after the application container stops or is recreated.
Removing that volume with `docker compose down --volumes` deletes the database
data. The UI still shows only the last successful submission from the current
page, and clears that display when the page is reloaded. `make docker-run` by
itself does not attach the database network or set `DATABASE_URL`; use the
command above when running the application with persistence.

After `make install`, run `make docker-test` to build the image and test the
status endpoint, HTML page, CSS, and JavaScript over HTTP. The check uses an
available localhost port, waits for startup, and stops its temporary container
afterward. These Docker checks run separately from `make test` and `make cov`.

## Build and verify packages

Build the package from the project root:

```bash
make build
```

This runs `uv build`, creating a source archive (`.tar.gz`) and an installable
wheel (`.whl`) under `dist/`. By default, uv builds the wheel from the source
archive, so both distributions must contain the required application files.
Build dependencies may need to be downloaded. Generated files under `dist/`
are ignored by Git and should not be committed.

The setuptools configuration in `pyproject.toml` includes the `app` package,
the `wsgi` module, HTML templates, CSS, and JavaScript. Inspect both archives
with the following commands (adjust filenames if the project version changes):

```bash
uv run --locked python -m zipfile -l dist/expense_tracker-0.1.0-py3-none-any.whl
tar -tzf dist/expense_tracker-0.1.0.tar.gz
```

Both archives should contain `app/templates/index.html`, `app/static/style.css`,
`app/static/app.js`, the Python application files, and `wsgi.py`. The source
archive places these files inside an `expense_tracker-0.1.0/` directory.

To test the installed wheel independently of the source checkout, run the
following after `make install`:

```bash
make verify-package
```

This target builds the packages, creates a temporary virtual environment using
the project's Python interpreter, installs the wheel and pytest, and copies the
tests into the temporary directory. It runs pytest with isolated Python and
without the project's pytest configuration, which adds the source checkout to
the import path. This ensures the tests exercise the installed wheel.

The package tests verify that the HTML page, CSS, and JavaScript are served;
they do not test browser interactions.

## Continuous integration

The [CI workflow](.github/workflows/ci.yml) runs automatically when a pull request
targeting `main` is opened, reopened, or updated with new commits. Pull requests
targeting other branches and standalone pushes do not trigger it.

Manual runs are also configured through `workflow_dispatch`. Once the workflow
exists on the default branch, open **Actions → CI → Run workflow** on GitHub
and select the branch to check.

The **CI checks** job runs on Ubuntu with Python 3.12 and uv 0.10.9. It installs
application and development dependencies using `uv sync --locked`, then runs:

| Command | Check |
| --- | --- |
| `make lint` | Ruff lint rules and Python formatting |
| `make cov` | Tests against the source checkout, with at least 80% application coverage |
| `make verify-package` | Wheel and source build, followed by all tests against the installed wheel, including HTML, CSS, and JavaScript checks |
| `make docker-test` | Docker image build and HTTP checks against a running temporary container |

A failing command marks the job as failed and stops subsequent steps. Review
the PR checks or the Actions tab for results and logs. Requiring a passing CI
check before merging is configured separately through branch protection or rulesets.

Run the same checks locally before opening a release PR:

```bash
make install
make lint
make cov
make verify-package
make docker-test
```

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
│   ├── test_api.py       API response and validation tests
│   └── test_package.py   HTML and static asset tests
├── checks/
│   └── test_docker.py    Tests against a running Docker container
├── Dockerfile           Python image and non-root Gunicorn runtime
├── .dockerignore        Files excluded from the Docker build context
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
