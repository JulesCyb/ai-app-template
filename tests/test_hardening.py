"""Guard tests: SSE framing and the dev-headers environment guard."""

from __future__ import annotations

import pytest

from app.api.agents import _sse
from app.config import Settings
from app.main import check_auth_mode


def test_sse_framing_preserves_newlines():
    assert _sse("hello") == "data: hello\n\n"
    # A delta containing newlines must become multiple data: lines (the client
    # reassembles them), never a raw line without the data: prefix.
    assert _sse("line one\nline two") == "data: line one\ndata: line two\n\n"
    assert _sse("") == "data: \n\n"


def test_dev_headers_refused_outside_dev():
    with pytest.raises(RuntimeError):
        check_auth_mode(Settings(environment="prod", auth_mode="dev-headers"))
    # No raise: dev-headers in dev/test, jwt anywhere.
    check_auth_mode(Settings(environment="dev", auth_mode="dev-headers"))
    check_auth_mode(Settings(environment="test", auth_mode="dev-headers"))
    check_auth_mode(Settings(environment="prod", auth_mode="jwt"))
