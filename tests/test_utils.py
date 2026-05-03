import logging
import json
from unittest.mock import MagicMock, patch

from utils.response import success_response, error_response, paginated_response
from utils.validators import (
    validate_email,
    validate_password,
    validate_required_fields,
    validate_user_id,
    validate_faq_id,
    validate_timeline_id,
    sanitize_string,
)
from utils.logging_config import (
    setup_logging,
    log_request,
    log_admin_action,
    log_integration_failure,
    JSONFormatter,
    StandardFormatter,
)


class TestResponseUtils:
    def test_success_response(self):
        res = success_response(data={"key": "val"})
        assert res["success"] is True
        assert res["message"] == "Success"
        assert res["data"] == {"key": "val"}

    def test_success_response_no_data(self):
        res = success_response()
        assert "data" not in res

    def test_error_response(self):
        res = error_response(message="Bad", errors=["e1"])
        assert res["success"] is False
        assert res["message"] == "Bad"

    def test_error_response_no_errors(self):
        res = error_response(message="Error")
        assert res["success"] is False

    def test_paginated_response(self):
        res = paginated_response(
            items=[{"id": 1}, {"id": 2}], page=1, per_page=10, total=2
        )
        assert res["success"] is True
        assert res["data"] == [{"id": 1}, {"id": 2}]
        assert res["pagination"]["page"] == 1
        assert res["pagination"]["pages"] == 1

    def test_paginated_response_empty(self):
        res = paginated_response(items=[], page=1, per_page=10, total=0)
        assert res["data"] == []
        assert res["pagination"]["pages"] == 0


class TestValidators:
    def test_validate_email(self):
        assert validate_email("test@example.com") is True
        assert validate_email("invalid-email") is False

    def test_validate_password(self):
        assert validate_password("12345678") is True
        assert validate_password("short") is False

    def test_validate_required_fields(self):
        valid, missing = validate_required_fields({"a": 1, "b": 2}, ["a", "b"])
        assert valid is True
        assert missing == []

        valid, missing = validate_required_fields({"a": 1}, ["a", "b"])
        assert valid is False
        assert missing == ["b"]

    def test_validate_ids(self):
        assert validate_user_id("u1") is True
        assert not validate_user_id(", ")

        assert validate_faq_id("f1") is True
        assert not validate_faq_id(", ")

        assert validate_timeline_id("t1") is True
        assert not validate_timeline_id(", ")

    def test_sanitize_string(self):
        assert sanitize_string("  test  ") == "test"
        assert sanitize_string(None) == ", "

        long_str = "a" * 1050
        assert len(sanitize_string(long_str)) == 1000


class TestLoggingConfig:
    def test_json_formatter(self):
        formatter = JSONFormatter()
        record = logging.LogRecord("test", logging.INFO, "path", 1, "msg", None, None)
        record.user_id = "u1"
        record.request_id = "r1"

        res_str = formatter.format(record)
        res = json.loads(res_str)
        assert res["message"] == "msg"
        assert res["user_id"] == "u1"
        assert res["request_id"] == "r1"

        # With exception
        try:
            1 / 0
        except (RuntimeError, ConnectionError, ValueError):
            import sys

            record_exc = logging.LogRecord(
                "test", logging.ERROR, "path", 1, "error msg", None, sys.exc_info()
            )
            res_str_exc = formatter.format(record_exc)
            res_exc = json.loads(res_str_exc)
            assert "exception" in res_exc

    def test_standard_formatter(self):
        formatter = StandardFormatter()
        record = logging.LogRecord("test", logging.INFO, "path", 1, "msg", None, None)
        res = formatter.format(record)
        assert "msg" in res

    def test_setup_logging_prod(self):
        app = MagicMock()
        app.config = {"ENV": "production"}
        setup_logging(app)
        assert app.logger.setLevel.called

    def test_setup_logging_dev(self):
        app = MagicMock()
        app.config = {"ENV": "development"}
        setup_logging(app)
        assert app.logger.setLevel.called

    @patch("utils.logging_config.logging.getLogger")
    def test_log_request(self, mock_get_logger):
        req = MagicMock()
        req.method = "GET"
        req.path = "/test"
        req.remote_addr = "127.0.0.1"

        # Test success request log
        log_request(req, MagicMock(status_code=200))
        mock_get_logger.return_value.info.assert_called_once()

        # Test error request log
        mock_get_logger.return_value.reset_mock()
        log_request(req, error=Exception("e"))
        mock_get_logger.return_value.error.assert_called_once()

    @patch("utils.logging_config.logging.getLogger")
    def test_log_admin_action(self, mock_get_logger):
        log_admin_action("u1", "create", "user", {"k": "v"})
        mock_get_logger.return_value.info.assert_called_once()

    @patch("utils.logging_config.logging.getLogger")
    def test_log_integration_failure(self, mock_get_logger):
        log_integration_failure("maps", Exception("err"), {"c": 1})
        mock_get_logger.return_value.error.assert_called_once()
