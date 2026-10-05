from uuid import UUID

import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def payload():
    return {
        "amount": "12.30",
        "category": "Groceries",
        "date": "2026-10-05",
    }


def test_create_expense_returns_created_expense(app, payload):
    with app.test_client() as client:
        response = client.post("/api/expenses", json=payload)

    assert response.status_code == 201
    assert response.mimetype == "application/json"
    expense = response.get_json()
    expense_id = UUID(expense["id"])
    assert expense_id.version == 4
    assert str(expense_id) == expense["id"]
    assert expense == {"id": expense["id"], **payload}


def test_create_expense_rejects_missing_amount(app, payload):
    del payload["amount"]
    with app.test_client() as client:
        response = client.post("/api/expenses", json=payload)

    assert response.status_code == 400
    assert response.get_json()["error"]["fields"] == {"amount": "This field is required."}


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("-12.30", "-12.30"),
        ("0", "0.00"),
        ("-0.00", "0.00"),
        ("0012.3", "12.30"),
        ("12", "12.00"),
        ("123456789012345678901234567890.12", "123456789012345678901234567890.12"),
    ],
)
def test_create_expense_normalizes_exact_amount(app, payload, amount, expected):
    payload.update(amount=amount, category="  Groceries  ", date="2024-02-29")
    response = app.test_client().post("/api/expenses", json=payload)
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
        ("amount", value)
        for value in [
            None,
            12.30,
            True,
            [],
            {},
            "",
            " 12.30 ",
            "+12.30",
            ".50",
            "12.",
            "12.345",
            "1e2",
            "12,30",
            "NaN",
            "Infinity",
            "１２.３０",
            "12\n",
        ]
    ]
    + [("category", value) for value in [None, 42, [], {}, "", " \t\n"]]
    + [
        ("date", value)
        for value in [
            None,
            20261005,
            "2025-02-29",
            "2026-04-31",
            "2026-1-05",
            "0000-01-01",
            "2026-10-05T00:00:00",
            " 2026-10-05",
            "２０２６-10-05",
            "2026-10-05\n",
        ]
    ]
    + [("id", "client-id")],
)
def test_create_expense_rejects_invalid_field(app, payload, field, value):
    client = app.test_client()
    response = client.post("/api/expenses", json={**payload, field: value})
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
def test_create_expense_rejects_invalid_request(app, body, content_type):
    client = app.test_client()
    response = client.post("/api/expenses", data=body, content_type=content_type)
    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "code": "invalid_request",
            "message": "Request must contain a JSON object with Content-Type application/json.",
        }
    }


def test_reports_all_field_errors(app):
    response = app.test_client().post("/api/expenses", json={"amount": "bad", "extra": True})
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert set(fields) == {"amount", "category", "date", "extra"}
    assert fields["category"] == fields["date"] == "This field is required."
    assert fields["extra"] == "Unknown field."


def test_repeated_requests_generate_different_ids(app, payload):
    first = app.test_client().post("/api/expenses", json=payload).get_json()
    response = app.test_client().post(
        "/api/expenses",
        json=payload,
        content_type="application/json; charset=utf-8",
    )
    assert response.status_code == 201
    second = response.get_json()
    assert first["id"] != second["id"]


def test_status_endpoint(app):
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert response.get_json() == {"name": "expense-tracker", "status": "running"}
