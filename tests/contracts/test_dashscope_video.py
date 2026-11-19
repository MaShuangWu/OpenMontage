"""Behavior tests for the DashScope Wan 3.0 video tool.

Shared BaseTool contract checks live in test_dashscope_tools.py; these cover
payload construction, the async submit/poll/download flow, and cost
accounting without real API calls.

Run: pytest tests/contracts/test_dashscope_video.py -v
"""

from __future__ import annotations

import json
import sys
import types

import pytest

from tools.video.dashscope_video import DashscopeVideo


class FakeResponse:
    def __init__(self, json_data=None, content=b"", status_code=200):
        self._json = json_data
        self.content = content
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.text = json.dumps(json_data) if json_data is not None else ""

    def json(self):
        return self._json

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(f"HTTP {self.status_code}")


def _install_fake_requests(monkeypatch, post_responses, get_responses):
    calls = {"post": [], "get": []}
    fake = types.ModuleType("requests")

    def fake_post(url, headers=None, json=None, timeout=None, allow_redirects=True):
        calls["post"].append({
            "url": url, "headers": headers, "json": json, "allow_redirects": allow_redirects,
        })
        response = post_responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def fake_get(url, headers=None, timeout=None):
        calls["get"].append({"url": url, "headers": headers})
        return get_responses.pop(0)

    fake.post = fake_post
    fake.get = fake_get
    monkeypatch.setitem(sys.modules, "requests", fake)
    return calls


@pytest.fixture()
def dashscope_env(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-fake-test-key")
    monkeypatch.setenv("DASHSCOPE_WORKSPACE_ID", "ws-example")
    monkeypatch.delenv("DASHSCOPE_REGION", raising=False)
    monkeypatch.delenv("DASHSCOPE_BASE_URL", raising=False)
    monkeypatch.setattr("tools.video.dashscope_video.time.sleep", lambda _s: None)


def _submitted():
    return FakeResponse({"output": {"task_id": "task-1", "task_status": "PENDING"}})


def _status(status, **output):
    return FakeResponse({"output": {"task_id": "task-1", "task_status": status, **output}})


class TestPayload:

    def test_text_to_video_defaults(self):
        payload, error = DashscopeVideo()._build_payload({"prompt": "a cat"})
        assert error is None
        assert payload["model"] == "wan3.0-video"
        assert payload["input"] == {"prompt": "a cat"}
        # 720P, not the API's 1080P default, so omitted resolution stays cheap.
        assert payload["parameters"]["resolution"] == "720P"
        assert payload["parameters"]["ratio"] == "16:9"
        assert payload["parameters"]["duration"] == 5

    def test_prime_model_passes_through(self):
        payload, error = DashscopeVideo()._build_payload({"prompt": "x", "model": "wan3.0-video-prime"})
        assert error is None
        assert payload["model"] == "wan3.0-video-prime"

    def test_unknown_model_rejected(self):
        payload, error = DashscopeVideo()._build_payload({"prompt": "x", "model": "wan3.0-t2v"})
        assert payload is None
        assert "Unsupported" in error

    def test_selector_string_duration_and_aspect_ratio(self):
        payload, error = DashscopeVideo()._build_payload(
            {"prompt": "x", "duration": "10", "aspect_ratio": "9:16"}
        )
        assert error is None
        assert payload["parameters"]["duration"] == 10
        assert payload["parameters"]["ratio"] == "9:16"

    def test_image_to_video_inlines_local_file(self, tmp_path):
        image = tmp_path / "frame.png"
        image.write_bytes(b"png-bytes")
        payload, error = DashscopeVideo()._build_payload(
            {
                "prompt": "x",
                "operation": "image_to_video",
                "reference_image_path": str(image),
            }
        )
        assert error is None
        assert payload["input"]["media"] == [
            {"type": "first_frame", "url": "data:image/png;base64,cG5nLWJ5dGVz"}
        ]
        assert payload["parameters"]["ratio"] == "adaptive"

    def test_first_last_frame(self):
        payload, error = DashscopeVideo()._build_payload(
            {
                "prompt": "x",
                "operation": "first_last_frame_to_video",
                "reference_image_url": "https://example.com/a.png",
                "last_image_url": "https://example.com/b.png",
            }
        )
        assert error is None
        assert [m["type"] for m in payload["input"]["media"]] == ["first_frame", "last_frame"]

    def test_reference_to_video_mixes_media(self):
        payload, error = DashscopeVideo()._build_payload(
            {
                "prompt": "x",
                "operation": "reference_to_video",
                "reference_image_urls": ["https://e.com/1.png", "https://e.com/2.png"],
                "reference_video_url": "https://e.com/v.mp4",
                "reference_audio_urls": ["https://e.com/a.wav"],
            }
        )
        assert error is None
        assert [m["type"] for m in payload["input"]["media"]] == [
            "reference_image",
            "reference_image",
            "reference_video",
            "reference_audio",
        ]

    @pytest.mark.parametrize(
        "inputs, message",
        [
            ({"prompt": "x", "operation": "image_to_video"}, "requires"),
            ({"prompt": "x", "operation": "reference_to_video"}, "at least one"),
            ({"prompt": "x", "duration": 1}, "duration"),
            ({"prompt": "x", "duration": 31}, "duration"),
            ({"prompt": "x", "resolution": "4K"}, "resolution"),
            ({"prompt": "x", "ratio": "2:1"}, "ratio"),
            (
                {"prompt": "x", "operation": "image_to_video", "reference_image_path": "/no/such.png"},
                "not found",
            ),
        ],
    )
    def test_rejects_invalid_inputs(self, inputs, message):
        payload, error = DashscopeVideo()._build_payload(inputs)
        assert payload is None
        assert message in error


class TestEndpoint:

    def test_defaults_to_mainland(self, dashscope_env):
        assert DashscopeVideo._base_url() == "https://ws-example.cn-beijing.maas.aliyuncs.com"

    def test_intl_region(self, dashscope_env, monkeypatch):
        monkeypatch.setenv("DASHSCOPE_REGION", "intl")
        assert DashscopeVideo._base_url() == "https://ws-example.ap-southeast-1.maas.aliyuncs.com"

    def test_base_url_override(self, dashscope_env, monkeypatch):
        monkeypatch.delenv("DASHSCOPE_WORKSPACE_ID")
        monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://proxy.example.com/")
        assert DashscopeVideo._base_url() == "https://proxy.example.com"


    @pytest.mark.parametrize("region", ["ap-northeast-1", "cn-hongkong", "eu-central-1", "us-east-1"])
    def test_regional_workspaces(self, dashscope_env, monkeypatch, region):
        monkeypatch.setenv("DASHSCOPE_REGION", region)
        assert DashscopeVideo._base_url() == f"https://ws-example.{region}.maas.aliyuncs.com"

    def test_missing_workspace(self, dashscope_env, monkeypatch):
        monkeypatch.delenv("DASHSCOPE_WORKSPACE_ID")
        assert DashscopeVideo().get_status().value == "unavailable"
        with pytest.raises(ValueError, match="DASHSCOPE_WORKSPACE_ID"):
            DashscopeVideo._base_url()


class TestCost:

    def test_scales_with_resolution_and_duration(self):
        tool = DashscopeVideo()
        assert tool.estimate_cost({"resolution": "480P", "duration": 10}) == 0.52
        assert tool.estimate_cost({"resolution": "720P", "duration": 5}) == 0.52
        assert tool.estimate_cost({"resolution": "1080P", "duration": 5}) == 1.04

    def test_prime_costs_more(self):
        tool = DashscopeVideo()
        assert tool.estimate_cost({"model": "wan3.0-video-prime", "resolution": "720P", "duration": 5}) == 0.7
        assert tool.estimate_cost({"model": "wan3.0-video-prime", "resolution": "1080P", "duration": 10}) == 2.8

    def test_model_chosen_duration_budgets_maximum(self):
        assert DashscopeVideo().estimate_cost({"duration": -1}) == 3.12


class TestExecute:

    def test_success_polls_downloads_and_bills_actual_duration(self, dashscope_env, tmp_path, monkeypatch):
        calls = _install_fake_requests(
            monkeypatch,
            post_responses=[_submitted()],
            get_responses=[
                _status("RUNNING"),
                FakeResponse(
                    {
                        "output": {
                            "task_id": "task-1",
                            "task_status": "SUCCEEDED",
                            "video_url": "https://cdn.example.com/v.mp4",
                        },
                        "usage": {"output_video_duration": 8.0},
                    }
                ),
                FakeResponse(content=b"mp4-bytes"),
            ],
        )
        out = tmp_path / "clip.mp4"
        result = DashscopeVideo().execute({"prompt": "a cat", "duration": -1, "output_path": str(out)})

        assert result.success, result.error
        assert out.read_bytes() == b"mp4-bytes"
        assert result.data["task_id"] == "task-1"
        assert result.cost_usd == 0.83  # 8s x $0.104 at 720P, not the 30s budget
        assert len(calls["post"]) == 1
        submit = calls["post"][0]
        assert submit["allow_redirects"] is False
        assert submit["url"].endswith("/api/v1/services/aigc/video-generation/video-synthesis")
        assert submit["headers"]["X-DashScope-Async"] == "enable"
        assert calls["get"][0]["url"].endswith("/api/v1/tasks/task-1")

    def test_submit_error_surfaces_api_message(self, dashscope_env, tmp_path, monkeypatch):
        _install_fake_requests(
            monkeypatch,
            post_responses=[
                FakeResponse(
                    {"code": "InvalidParameter", "message": "Model not exist."},
                    status_code=400,
                )
            ],
            get_responses=[],
        )
        result = DashscopeVideo().execute({"prompt": "x", "output_path": str(tmp_path / "o.mp4")})
        assert result.success is False
        assert "InvalidParameter: Model not exist." in result.error

    def test_failed_task_returns_reason_and_task_id(self, dashscope_env, tmp_path, monkeypatch):
        _install_fake_requests(
            monkeypatch,
            post_responses=[_submitted()],
            get_responses=[_status("FAILED", code="DataInspectionFailed", message="unsafe content")],
        )
        result = DashscopeVideo().execute({"prompt": "x", "output_path": str(tmp_path / "o.mp4")})
        assert result.success is False
        assert "unsafe content" in result.error
        assert result.data["task_id"] == "task-1"

    def test_timeout_keeps_task_id(self, dashscope_env, tmp_path, monkeypatch):
        calls = _install_fake_requests(
            monkeypatch,
            post_responses=[_submitted()],
            get_responses=[_status("RUNNING")] * 5,
        )
        clock = iter([0.0, 0.0, 0.5, 0.6, 2.0])
        monkeypatch.setattr(
            "tools.video.dashscope_video.time",
            types.SimpleNamespace(monotonic=lambda: next(clock), sleep=lambda _: None),
        )
        result = DashscopeVideo().execute(
            {"prompt": "x", "timeout_seconds": 1, "output_path": str(tmp_path / "o.mp4")}
        )
        assert result.success is False
        assert "timed out" in result.error
        assert result.data["status"] == "timed_out"
        assert result.data["task_id"] == "task-1"
        assert result.data["resume_job"]["parameters"]["resolution"] == "720P"
        assert result.cost_usd is None
        assert len(calls["post"]) == 1

    def test_lost_submit_response_is_not_retried(self, dashscope_env, monkeypatch):
        calls = _install_fake_requests(monkeypatch, [TimeoutError("response lost")], [])
        tool = DashscopeVideo()
        result = tool.execute({"prompt": "x"})
        assert not result.success
        assert result.data["status"] == "submission_unknown"
        assert "before submitting again" in result.error
        assert "task_id" not in result.data
        assert result.cost_usd is None
        assert tool.retry_policy.max_retries == 0
        assert len(calls["post"]) == 1
        assert not calls["get"]

    def test_download_failure_keeps_checkpoint_and_resume_only_queries(
        self, dashscope_env, tmp_path, monkeypatch,
    ):
        done = _status("SUCCEEDED", video_url="https://cdn.example.com/v.mp4")
        calls = _install_fake_requests(
            monkeypatch, [_submitted()],
            [done, FakeResponse(status_code=503), done, FakeResponse(content=b"mp4-bytes")],
        )
        tool = DashscopeVideo()
        job_path = tmp_path / "wan.json"
        output_path = tmp_path / "video.mp4"
        failed = tool.execute({"prompt": "x", "job_path": str(job_path)})
        assert not failed.success
        assert failed.cost_usd is None
        job = json.loads(job_path.read_text())
        assert failed.data["resume_job"] == job
        resume_inputs = {"resume_job": job, "output_path": str(output_path)}
        assert tool.estimate_cost(resume_inputs) == 0.0
        resumed = tool.execute(resume_inputs)
        assert resumed.success, resumed.error
        assert resumed.cost_usd is None
        assert resumed.data["task_id"] == "task-1"
        assert output_path.read_bytes() == b"mp4-bytes"
        assert len(calls["post"]) == 1
        assert calls["get"][0] == calls["get"][2]
        assert calls["get"][3]["headers"] is None

    def test_invalid_resume_never_submits(self, dashscope_env, monkeypatch):
        calls = _install_fake_requests(monkeypatch, [], [])
        for inputs in ({"operation": "resume"}, {"resume_job": {}, "prompt": "x"}):
            result = DashscopeVideo().execute(inputs)
            assert not result.success
            assert "valid resume_job" in result.error
        assert calls == {"post": [], "get": []}

    def test_missing_key(self, monkeypatch):
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
        result = DashscopeVideo().execute({"prompt": "x"})
        assert result.success is False
        assert "DASHSCOPE_API_KEY" in result.error


class TestRegistry:

    def test_video_selector_routes_local_image_without_fal_upload(self, dashscope_env, tmp_path, monkeypatch):
        """The selector uploads reference_image_path to fal.ai for providers that
        declare image_url; this tool must receive the path and inline it."""
        from tools.base_tool import ToolResult
        from tools.video.video_selector import VideoSelector

        tool = DashscopeVideo()
        selector = VideoSelector()
        monkeypatch.setattr(selector, "_providers", lambda: [tool])
        received = {}

        def fake_execute(inputs):
            received.update(inputs)
            return ToolResult(success=True, data={}, artifacts=[inputs["output_path"]])

        monkeypatch.setattr(tool, "execute", fake_execute)
        image = tmp_path / "frame.png"
        image.write_bytes(b"png")

        result = selector.execute(
            {
                "prompt": "x",
                "operation": "image_to_video",
                "reference_image_path": str(image),
                "preferred_provider": "dashscope",
                "output_path": str(tmp_path / "o.mp4"),
            }
        )

        assert result.success, result.error
        assert result.data["selected_tool"] == "dashscope_video"
        assert received["reference_image_path"] == str(image)
        assert "image_url" not in received
