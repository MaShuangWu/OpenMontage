from pathlib import Path
from unittest.mock import patch

from tools.video.video_trimmer import VideoTrimmer


def test_portrait_cut_transcodes_and_center_crops(tmp_path):
    source = tmp_path / "source.mp4"
    source.touch()
    tool = VideoTrimmer()
    commands = []

    with patch.object(tool, "run_command", side_effect=lambda command: commands.append(command)):
        result = tool.execute({
            "operation": "cut",
            "input_path": str(source),
            "output_path": str(tmp_path / "portrait.mp4"),
            "start_seconds": 0,
            "end_seconds": 3,
            "aspect_ratio": "9:16",
        })

    assert result.success, result.error
    command = commands[0]
    assert command[command.index("-vf") + 1].startswith("crop=")
    assert command[command.index("-c:v") + 1] == "libx264"


def test_portrait_cut_rejects_stream_copy(tmp_path):
    source = tmp_path / "source.mp4"
    source.touch()
    result = VideoTrimmer().execute({
        "operation": "cut",
        "input_path": str(source),
        "output_path": str(tmp_path / "portrait.mp4"),
        "aspect_ratio": "9:16",
        "codec": "copy",
    })

    assert not result.success
    assert "requires video encoding" in result.error


def test_cache_key_distinguishes_portrait_crop_from_source_frame(tmp_path):
    source = tmp_path / "source.mp4"
    source.touch()
    tool = VideoTrimmer()
    common = {
        "operation": "cut",
        "input_path": str(source),
        "output_path": str(tmp_path / "clip.mp4"),
        "start_seconds": 1,
        "end_seconds": 3,
        "codec": "libx264",
    }

    source_frame_key = tool.cache_key({**common, "aspect_ratio": "source"})
    portrait_key = tool.cache_key({**common, "aspect_ratio": "9:16"})

    assert source_frame_key != portrait_key
