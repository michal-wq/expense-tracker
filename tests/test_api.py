from uuid import UUID
from app import create_app

def test_create_expense_returns_created_expense():
    app = create_app()
    app.config["TESTING"] = True

    payload = {
        "amount": "12.30",
        "category": "Groceries",
        "date": "2026-10-05",
    }

    with app.test_client() as client:
        response = client.post("/api/expenses", json=payload)

    assert response.status_code == 201

    expense = response.get_json()
    assert expense["id"] is not None
    assert expense["amount"] == payload["amount"]
    assert expense["category"] == payload["category"]
    assert expense["date"] == payload["date"]


def test_create_expense_rejects_missing_amount():
    app = create_app()
    app.config["TESTING"] = True

    payload = {
        "category": "Groceries",
        "date": "2026-10-05",
    }

    with app.test_client() as client:
        response = client.post("/api/expenses", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_expense_rejects_negative_amount():
    app = create_app()
    app.config["TESTING"] = True

    payload = {
        "amount": "-12.30",
        "category": "Groceries",
        "date": "2026-10-05",
    }

    with app.test_client() as client:
        response = client.post("/api/expenses", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()
