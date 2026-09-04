from flask import Flask

from backend.auth.decorators import get_development_bypass


def test_permission_bypass_is_only_enabled_by_flask_testing_mode():
    app = Flask(__name__)
    app.config["TESTING"] = False
    with app.test_request_context():
        assert get_development_bypass() is False
    app.config["TESTING"] = True
    with app.test_request_context():
        assert get_development_bypass() is True
