import re
from datetime import date
from decimal import Decimal
from uuid import uuid4

import psycopg
from flask import Blueprint, current_app, jsonify, render_template, request

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return jsonify(
        name="expense-tracker",
        status="running",
    )


@bp.get("/expenses")
def expenses_page():
    return render_template("index.html")


def validate_expense(payload):
    """Collect field errors without changing the request data."""
    required = {"amount", "category", "date"}
    errors = {}
    for field in required:
        if field not in payload:
            errors[field] = "This field is required."
    for field in payload:
        if field not in required:
            errors[field] = "Unknown field."

    if "amount" in payload:
        amount = payload["amount"]
        if not isinstance(amount, str) or not re.fullmatch(r"-?[0-9]+(?:\.[0-9]{1,2})?", amount):
            errors["amount"] = "Must be a decimal string with at most two decimal places."
        elif Decimal(amount) <= 0:
            errors["amount"] = "Must be greater than zero."

    if "category" in payload:
        category = payload["category"]
        if not isinstance(category, str) or not category.strip():
            errors["category"] = "Must be a non-empty string."

    if "date" in payload:
        expense_date = payload["date"]
        if not isinstance(expense_date, str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}", expense_date
        ):
            errors["date"] = "Must be a valid YYYY-MM-DD date."
        else:
            try:
                date.fromisoformat(expense_date)
            except ValueError:
                errors["date"] = "Must be a valid YYYY-MM-DD date."
    return errors


@bp.post("/api/expenses")
def create_expense():
    payload = None
    if request.mimetype == "application/json":
        payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(
            error={
                "code": "invalid_request",
                "message": "Request must contain a JSON object with Content-Type application/json.",
            }
        ), 400

    errors = validate_expense(payload)
    if errors:
        return jsonify(
            error={
                "code": "validation_error",
                "message": "Request validation failed.",
                "fields": errors,
            }
        ), 400

    amount = Decimal(payload["amount"])
    expense_id = uuid4()
    category = payload["category"].strip()
    expense_date = date.fromisoformat(payload["date"])

    try:
        database_url = current_app.config["DATABASE_URL"]
        if not database_url:
            raise psycopg.OperationalError("DATABASE_URL is not configured.")
        with psycopg.connect(database_url) as connection:
            connection.execute(
                "INSERT INTO expenses (id, amount, category, date) VALUES (%s, %s, %s, %s)",
                (expense_id, amount, category, expense_date),
            )
    except psycopg.Error as error:
        current_app.logger.error("Could not save expense (%s).", type(error).__name__)
        return jsonify(
            error={"code": "internal_error", "message": "The expense could not be saved."},
        ), 500

    return jsonify(
        id=str(expense_id),
        amount=format(amount, ".2f"),
        category=category,
        date=expense_date.isoformat(),
    ), 201
