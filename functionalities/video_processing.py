import os
import ffmpeg
import subprocess


def process_video_and_audio_ffmpeg_raw_command(
    video_file: str,
    audio_file: str,
    output_file: str,
    expected_fps: float,
    expected_duration: float,
    keep: bool = False,
):
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    """Merge video and audio using ffmpeg."""
    video_duration = get_duration_ffmpeg_raw_command(video_file)

    actual_fps = expected_fps * (video_duration / expected_duration)
    duration_ratio = expected_duration / video_duration

    # Prepare the common part of the command
    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_file,
        "-vf",
        f"setpts={duration_ratio}*PTS",
        "-r",
        str(actual_fps),
        "-c:v",
        "libx264",
        "-threads",
        "16",
        "-shortest",
        output_file,
    ]

    # Add audio file if it exists
    if os.path.isfile(audio_file):
        command.insert(3, "-i")
        command.insert(4, audio_file)
        command.insert(-2, "-c:a")
        command.insert(-1, "aac")

    subprocess.run(command, check=True)

    if not keep:
        os.remove(video_file)
        if os.path.isfile(audio_file):
            os.remove(audio_file)


def process_video_and_audio_ffmpeg_python(
    video_file: str,
    audio_file: str,
    output_file: str,
    expected_fps: float,
    expected_duration: float,
    keep: bool = False,
):
    if not os.path.isfile(video_file):
        raise FileNotFoundError(f"Video file not found: {video_file}")

    """Merge video and audio using ffmpeg."""
    video_duration = get_duration_ffmpeg_python(video_file)

    actual_fps = expected_fps * (video_duration / expected_duration)
    duration_ratio = expected_duration / video_duration

    input = ffmpeg.input(video_file)
    if os.path.isfile(audio_file):
        input_audio = ffmpeg.input(audio_file)
        input = ffmpeg.concat(input, input_audio, v=1, a=1)

    (
        input.filter("setpts", f"{duration_ratio}*PTS")  # Apply the setpts filter
        .filter("fps", fps=actual_fps)  # Set the output frame rate
        .output(
            vcodec="libx264",
            acodec="aac",
            shortest=None,
            threads=16,
            filename=output_file,
        )
        .overwrite_output()  # Equivalent to -y
        .run()
    )

    if not keep:
        os.remove(video_file)
        if os.path.isfile(audio_file):
            os.remove(audio_file)


def get_duration_ffmpeg_raw_command(file: str) -> float:
    """Get the duration of a video file."""
    command = [
        "ffprobe",
        "-i",
        file,
        "-show_entries",
        "format=duration",
        "-v",
        "quiet",
        "-of",
        "csv=p=0",
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return float(result.stdout)


def get_duration_ffmpeg_python(file: str) -> float:
    """Get the duration of a video file."""
    try:
        probe = ffmpeg.probe(file)
        duration = float(probe["format"]["duration"])
        return duration
    except KeyError:
        raise ValueError("Could not retrieve duration from the file.")
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode('utf-8')}")
