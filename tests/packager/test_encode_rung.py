"""Tests for the pure parts of encode_rung: command building and checks."""

import pytest

from packager import encode_rung

ENCODER = {
    "name": "libx265",
    "preset": "medium",
    "pix_fmt": "yuv420p",
    "scenecut": 0,
    "open_gop": False,
}


def test_build_x265_params_has_fixed_closed_gop():
    params = encode_rung.build_x265_params(1, 60, "temp/x265_480p.log", ENCODER)
    assert params == (
        "pass=1:stats=temp/x265_480p.log:keyint=60:min-keyint=60:scenecut=0:open-gop=0"
    )


def test_build_x265_params_rejects_drive_letter():
    with pytest.raises(ValueError):
        encode_rung.build_x265_params(1, 60, "C:/temp/x.log", ENCODER)


def test_pass_1_writes_to_null_and_pass_2_writes_the_file():
    args = ("clip.y4m",)
    first = encode_rung.build_ffmpeg_command(*args, None, 480, 600, "pass=1", ENCODER)
    second = encode_rung.build_ffmpeg_command(
        *args, "out.mp4", 480, 600, "pass=2", ENCODER
    )
    assert first[-3:] == ["-f", "null", "-"]
    assert second[-1] == "out.mp4"


def test_command_uses_settings_from_config():
    command = encode_rung.build_ffmpeg_command(
        "clip.y4m", "out.mp4", 480, 600, "pass=2", ENCODER
    )
    assert command[command.index("-preset") + 1] == "medium"
    assert command[command.index("-b:v") + 1] == "600k"
    assert command[command.index("-vf") + 1] == "scale=-2:480"
    assert "-an" in command


def test_source_smaller_than_rung_is_refused():
    with pytest.raises(ValueError):
        encode_rung.check_source_big_enough(288, 480)
    encode_rung.check_source_big_enough(1080, 480)
