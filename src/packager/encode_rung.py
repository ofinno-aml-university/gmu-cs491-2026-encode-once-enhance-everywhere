"""Encode a source clip into one x265 base rung with two-pass average bitrate.

Run from the repo root, with src on the path:
    PYTHONPATH=src python -m packager.encode_rung --clip temp/clip.y4m \
        --rung 480p --out temp/base_480p.mp4
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from common.config import get_rung_config, load_config
from packager import frame_math


@dataclass
class RungResult:
    """What one finished encode produced, ready to go into the manifest."""

    rung_id: str
    file: str
    width: int
    height: int
    frame_rate: str
    gop_frames: int
    target_bitrate_kbps: int
    bitrate_kbps: float
    within_tolerance: bool


def build_x265_params(pass_number, gop, stats_file, encoder_config):
    """Build the -x265-params string for one pass."""
    if ":" in stats_file:
        raise ValueError(
            f"Stats file path {stats_file!r} has a colon, which breaks "
            "-x265-params. Use a relative path with no drive letter."
        )
    parts = [
        f"pass={pass_number}",
        f"stats={stats_file}",
        f"keyint={gop}",
        f"min-keyint={gop}",
        f"scenecut={encoder_config['scenecut']}",
        f"open-gop={int(encoder_config['open_gop'])}",
    ]
    return ":".join(parts)


def build_ffmpeg_command(
    clip_path,
    output_path,
    rung_height,
    target_bitrate_kbps,
    x265_params,
    encoder_config,
):
    """Build the FFmpeg command for one pass. Pass 1 writes nothing (null output)."""
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(clip_path),
        "-vf",
        f"scale=-2:{rung_height}",
        "-c:v",
        encoder_config["name"],
        "-preset",
        encoder_config["preset"],
        "-pix_fmt",
        encoder_config["pix_fmt"],
        "-b:v",
        f"{target_bitrate_kbps}k",
        "-x265-params",
        x265_params,
        "-an",
    ]
    if output_path is None:
        return command + ["-f", "null", "-"]
    return command + [str(output_path)]


def run_command(command):
    """Run a command and stop with a clear error if it fails."""
    try:
        completed = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            f"Could not run {command[0]!r}. Is it installed and on your PATH?"
        ) from error
    if completed.returncode != 0:
        raise RuntimeError(
            f"{command[0]} failed with exit code {completed.returncode}:\n"
            f"{completed.stderr.strip()}"
        )


def probe_video(path):
    """Return width, height, frame_rate (a Fraction), and duration_s for a video."""
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate:format=duration",
        "-of",
        "json",
        str(path),
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError as error:
        raise RuntimeError(
            "Could not run 'ffprobe'. Is FFmpeg on your PATH?"
        ) from error
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}:\n{completed.stderr.strip()}")
    info = json.loads(completed.stdout)
    stream = info["streams"][0]
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "frame_rate": frame_math.parse_frame_rate(stream["r_frame_rate"]),
        "duration_s": float(info["format"]["duration"]),
    }


def check_source_big_enough(source_height, rung_height):
    """Stop if the source is smaller than the rung, since that would upscale."""
    if source_height < rung_height:
        raise ValueError(
            f"Source is {source_height}p, smaller than the {rung_height}p rung. "
            "Use a larger source clip."
        )


def encode_rung(clip_path, output_path, config, rung_id):
    """Run both passes for one rung and return what was produced."""
    encoder_config = config["encoder"]
    rung_config = get_rung_config(config, rung_id)
    work_dir = Path(config["paths"]["work_dir"])
    clip_path = Path(clip_path)
    output_path = Path(output_path)

    source = probe_video(clip_path)
    check_source_big_enough(source["height"], rung_config["height"])
    gop = frame_math.gop_frames(source["frame_rate"], encoder_config["gop_seconds"])

    work_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats_file = (work_dir / f"x265_{rung_id}.log").as_posix()

    for pass_number in (1, 2):
        x265_params = build_x265_params(pass_number, gop, stats_file, encoder_config)
        command = build_ffmpeg_command(
            clip_path,
            output_path if pass_number == 2 else None,
            rung_config["height"],
            rung_config["target_bitrate_kbps"],
            x265_params,
            encoder_config,
        )
        run_command(command)

    result_video = probe_video(output_path)
    achieved = frame_math.bitrate_kbps(
        output_path.stat().st_size, result_video["duration_s"]
    )
    tolerance = config["matching"]["bitrate_tolerance"]
    return RungResult(
        rung_id=rung_id,
        file=output_path.as_posix(),
        width=result_video["width"],
        height=result_video["height"],
        frame_rate=str(source["frame_rate"]),
        gop_frames=gop,
        target_bitrate_kbps=rung_config["target_bitrate_kbps"],
        bitrate_kbps=round(achieved, 1),
        within_tolerance=frame_math.within_tolerance(
            achieved, rung_config["target_bitrate_kbps"], tolerance
        ),
    )


def main(argv=None):
    """Command line entry point. Returns 0 on success and 1 on a clear error."""
    parser = argparse.ArgumentParser(description="Encode one x265 base rung.")
    parser.add_argument("--clip", required=True, help="source clip, such as a .y4m")
    parser.add_argument("--rung", required=True, help="rung_id from the config")
    parser.add_argument("--out", required=True, help="output .mp4 path")
    parser.add_argument("--config", default="config.file", help="settings file")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
        result = encode_rung(args.clip, args.out, config, args.rung)
    except (RuntimeError, ValueError, KeyError, FileNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
