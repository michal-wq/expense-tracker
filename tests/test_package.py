import pytest

from wsgi import app


def test_package_serves_expense_page():
    response = app.test_client().get("/expenses")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert b"Expense Tracker" in response.data
    assert b"/static/style.css" in response.data
    assert b"/static/app.js" in response.data


@pytest.mark.parametrize(
    "path, mimetype",
    [("/static/style.css", "text/css"), ("/static/app.js", "text/javascript")],
)
def test_package_serves_static_assets(path, mimetype):
    response = app.test_client().get(path)

    assert response.status_code == 200
    assert response.mimetype == mimetype
    assert response.data
