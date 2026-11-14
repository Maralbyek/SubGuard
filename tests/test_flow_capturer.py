import json

import pytest

from subguard.flow_capture.capturer import InvalidPublicUrlError, validate_public_url
from subguard.flow_capture.models import CapturedFlow, CapturedScreen


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://user:password@example.com",
    ],
)
def test_validate_public_url_rejects_non_public_urls(url):
    with pytest.raises(InvalidPublicUrlError):
        validate_public_url(url)


def test_validate_public_url_accepts_https():
    assert validate_public_url("https://example.com/signup") == "https://example.com/signup"


def test_flow_manifest_preserves_screen_order(tmp_path):
    screens = (
        CapturedScreen(1, "https://example.com", "1/dom.html", "1/text.txt", "1/shot.png"),
        CapturedScreen(2, "https://example.com/next", "2/dom.html", "2/text.txt", "2/shot.png"),
    )
    flow = CapturedFlow("https://example.com", "sign-up", str(tmp_path), screens)

    manifest = json.loads(json.dumps(flow.to_dict()))

    assert [screen["order"] for screen in manifest["screens"]] == [1, 2]
    assert manifest["screen_count"] == 2

