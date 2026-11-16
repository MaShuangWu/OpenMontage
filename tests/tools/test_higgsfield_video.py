"""higgsfield_video against the current api.higgsfield.ai contract (issue #957).

No network: requests.post/get are replaced with fakes.
"""

import pytest
import requests

import tools.video.higgsfield_video as hf
from tools.video.higgsfield_video import HiggsFieldVideo


class _Resp:
    def __init__(self, data=None, content=b""):
        self._data = data or {}
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.delenv("HIGGSFIELD_API_KEY", raising=False)
    monkeypatch.delenv("HIGGSFIELD_API_SECRET", raising=False)
    monkeypatch.setenv("HIGGSFIELD_KEY", "kid:ksecret")
    monkeypatch.setattr(hf.time, "sleep", lambda s: None)


@pytest.fixture
def fake_api(monkeypatch, creds):
    calls = {"post": [], "get": []}
    statuses = iter(["queued", "in_progress", "COMPLETED"])

    def post(url, headers=None, json=None, timeout=None):
        calls["post"].append({"url": url, "headers": headers, "json": json})
        return _Resp({"status": "queued", "request_id": "req-1",
                      "status_url": "https://api.higgsfield.ai/requests/req-1/status"})

    def get(url, headers=None, timeout=None):
        calls["get"].append(url)
        if url.endswith("/status"):
            return _Resp({"status": next(statuses), "video": {"url": "https://cdn.example/v.mp4"}})
        return _Resp(content=b"mp4")

    monkeypatch.setattr(requests, "post", post)
    monkeypatch.setattr(requests, "get", get)
    monkeypatch.setattr("tools.video._shared.probe_output", lambda p: {})
    return calls


def test_kling_text_to_video_request_and_polling(fake_api, tmp_path):
    out = tmp_path / "clip.mp4"
    result = HiggsFieldVideo().execute({
        "prompt": "a duck", "model": "kling_3.0", "duration": "3",
        "aspect_ratio": "9:16", "generate_audio": False, "output_path": str(out),
    })

    assert result.success, result.error
    post = fake_api["post"][0]
    assert post["url"] == "https://api.higgsfield.ai/kling-video/v3.0/pro/text-to-video"
    assert post["headers"]["Authorization"] == "Key kid:ksecret"
    assert post["json"] == {"prompt": "a duck", "duration": 3, "sound": "off", "aspect_ratio": "9:16"}
    assert fake_api["get"][-1] == "https://cdn.example/v.mp4"
    assert out.read_bytes() == b"mp4"
    assert result.data["request_id"] == "req-1"
    assert result.cost_usd == pytest.approx(0.0962 * 3)


def test_seedance_image_to_video_payload(fake_api, tmp_path):
    result = HiggsFieldVideo().execute({
        "prompt": "a duck", "operation": "image_to_video", "duration": "5",
        "image_url": "https://example.com/a.jpg", "output_path": str(tmp_path / "c.mp4"),
    })

    assert result.success, result.error
    post = fake_api["post"][0]
    assert post["url"] == "https://api.higgsfield.ai/bytedance/seedance-2.0/image-to-video"
    assert post["json"] == {"prompt": "a duck", "duration": 5, "generate_audio": True,
                            "resolution": "720p", "image_url": "https://example.com/a.jpg"}


@pytest.mark.parametrize("inputs, msg", [
    ({"model": "veo_3.1"}, "no verified Higgsfield endpoint"),
    ({"model": "kling_3.0", "duration": "2"}, "3-15"),
    ({"model": "kling_3.0", "duration": "16"}, "3-15"),
    ({"model": "seedance_2.0", "duration": "3"}, "4-15"),
    ({"model": "seedance_2.0", "duration": "16"}, "4-15"),
    ({"model": "kling_3.0", "aspect_ratio": "21:9"}, "aspect_ratio"),
    ({"model": "seedance_2.0", "resolution": "8k"}, "resolution"),
    ({"operation": "image_to_video"}, "image_url"),
])
def test_invalid_requests_fail_before_any_network_call(fake_api, inputs, msg):
    result = HiggsFieldVideo().execute({"prompt": "x", **inputs})

    assert not result.success
    assert msg in result.error
    assert fake_api["post"] == [] and fake_api["get"] == []


@pytest.mark.parametrize("model, duration", [("kling_3.0", "3"), ("kling_3.0", "15"),
                                             ("seedance_2.0", "4"), ("seedance_2.0", "15")])
def test_duration_bounds_accepted(model, duration):
    url, payload = HiggsFieldVideo()._build_request({"prompt": "x", "model": model, "duration": duration})
    assert payload["duration"] == int(duration)


def test_terminal_failure_status_is_reported(monkeypatch, creds):
    monkeypatch.setattr(requests, "post", lambda *a, **k: _Resp({"request_id": "req-2"}))
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp({"status": "nsfw"}))

    result = HiggsFieldVideo().execute({"prompt": "x", "model": "kling_3.0"})

    assert not result.success
    assert "nsfw" in result.error and "req-2" in result.error


def test_cost_estimates_use_published_rates():
    tool = HiggsFieldVideo()
    assert tool.estimate_cost({"model": "kling_3.0", "duration": "6"}) == pytest.approx(0.5772)
    assert tool.estimate_cost({"model": "kling_3.0", "duration": "6", "resolution": "4k"}) == pytest.approx(0.5772)
    assert tool.estimate_cost({"duration": "5"}) == pytest.approx(0.1735 * 5)
    assert tool.estimate_cost({"duration": "5", "resolution": "1080p"}) == pytest.approx(0.4293 * 5)
    assert tool.estimate_cost({"model": "sora_2"}) == 0.0
