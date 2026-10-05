import re
from datetime import date
from decimal import Decimal
from uuid import uuid4

from flask import Blueprint, jsonify, request

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return jsonify(
        name="expense-tracker",
        status="running",
    )


def validate_expense(payload):
    required = {"amount", "category", "date"}
    errors = {field: "This field is required." for field in required - payload.keys()}
    errors.update({field: "Unknown field." for field in payload.keys() - required})

    if "amount" in payload:
        amount = payload["amount"]
        if not isinstance(amount, str) or not re.fullmatch(r"-?[0-9]+(?:\.[0-9]{1,2})?", amount):
            errors["amount"] = "Must be a decimal string with at most two decimal places."

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
    payload = request.get_json(silent=True) if request.mimetype == "application/json" else None
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
    if amount.is_zero():
        amount = amount.copy_abs()
    return jsonify(
        id=str(uuid4()),
        amount=format(amount, ".2f"),
        category=payload["category"].strip(),
        date=payload["date"],
    ), 201
