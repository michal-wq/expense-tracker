from uuid import UUID

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def payload():
    return {
        "amount": "12.30",
        "category": "Groceries",
        "date": "2026-10-05",
    }


def test_create_expense_returns_created_expense(client, payload):
    response = client.post("/api/expenses", json=payload)

    assert response.status_code == 201
    assert response.mimetype == "application/json"
    expense = response.get_json()
    expense_id = UUID(expense["id"])
    assert expense_id.version == 4
    assert str(expense_id) == expense["id"]
    assert expense == {"id": expense["id"], **payload}


@pytest.mark.parametrize("field", ["amount", "category", "date"])
def test_create_expense_rejects_missing_required_field(client, payload, field):
    del payload[field]
    response = client.post("/api/expenses", json=payload)

    assert response.status_code == 400
    assert response.mimetype == "application/json"
    assert response.get_json()["error"]["fields"] == {field: "This field is required."}


@pytest.mark.parametrize("amount", ["-12.30", "0", "0.00", "-0.00", "000.0"])
def test_create_expense_rejects_non_positive_amount(client, payload, amount):
    payload["amount"] = amount
    response = client.post("/api/expenses", json=payload)

    assert response.status_code == 400
    assert response.mimetype == "application/json"
    assert "amount" in response.get_json()["error"]["fields"]


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("0.01", "0.01"),
        ("0012.3", "12.30"),
        ("12", "12.00"),
        ("123456789012345678901234567890.12", "123456789012345678901234567890.12"),
    ],
)
def test_create_expense_normalizes_exact_amount(client, payload, amount, expected):
    payload.update(amount=amount, category="  Groceries  ", date="2024-02-29")
    response = client.post("/api/expenses", json=payload)
    assert response.status_code == 201
    expense = response.get_json()
    assert expense == {
        "id": expense["id"],
        "amount": expected,
        "category": "Groceries",
        "date": "2024-02-29",
    }


@pytest.mark.parametrize(
    "field, value",
    [
        ("amount", None),
        ("amount", 12.30),
        ("amount", True),
        ("amount", []),
        ("amount", {}),
        ("amount", ""),
        ("amount", " 12.30 "),
        ("amount", "+12.30"),
        ("amount", ".50"),
        ("amount", "12."),
        ("amount", "12.345"),
        ("amount", "1e2"),
        ("amount", "12,30"),
        ("amount", "NaN"),
        ("amount", "Infinity"),
        ("amount", "１２.３０"),
        ("amount", "12\n"),
        ("category", None),
        ("category", 42),
        ("category", []),
        ("category", {}),
        ("category", ""),
        ("category", " \t\n"),
        ("date", None),
        ("date", 20261005),
        ("date", "2025-02-29"),
        ("date", "2026-04-31"),
        ("date", "2026-1-05"),
        ("date", "0000-01-01"),
        ("date", "2026-10-05T00:00:00"),
        ("date", " 2026-10-05"),
        ("date", "２０２６-10-05"),
        ("date", "2026-10-05\n"),
        ("id", "client-id"),
    ],
)
def test_create_expense_rejects_invalid_field(client, payload, field, value):
    payload[field] = value
    response = client.post("/api/expenses", json=payload)
    assert response.status_code == 400
    assert response.mimetype == "application/json"
    error = response.get_json()["error"]
    assert error["code"] == "validation_error"
    assert set(error["fields"]) == {field}


@pytest.mark.parametrize(
    "body, content_type",
    [
        ("", "application/json"),
        ("{", "application/json"),
        ("[]", "application/json"),
        ("null", "application/json"),
        ('"text"', "application/json"),
        ("42", "application/json"),
        ("true", "application/json"),
        ("{}", None),
        ("{}", "text/plain"),
        ("{}", "application/vnd.api+json"),
    ],
)
def test_create_expense_rejects_invalid_request(client, body, content_type):
    response = client.post("/api/expenses", data=body, content_type=content_type)
    assert response.status_code == 400
    assert response.mimetype == "application/json"
    assert response.get_json() == {
        "error": {
            "code": "invalid_request",
            "message": "Request must contain a JSON object with Content-Type application/json.",
        }
    }


def test_reports_all_field_errors(client):
    response = client.post("/api/expenses", json={"amount": "bad", "extra": True})
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert set(fields) == {"amount", "category", "date", "extra"}
    assert fields["category"] == fields["date"] == "This field is required."
    assert fields["extra"] == "Unknown field."


def test_repeated_requests_generate_different_ids(client, payload):
    first_response = client.post("/api/expenses", json=payload)
    assert first_response.status_code == 201
    first = first_response.get_json()
    response = client.post(
        "/api/expenses",
        json=payload,
        content_type="application/json; charset=utf-8",
    )
    assert response.status_code == 201
    second = response.get_json()
    assert first["id"] != second["id"]


def test_status_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json() == {"name": "expense-tracker", "status": "running"}
