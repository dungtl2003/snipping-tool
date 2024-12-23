import os
import ffmpeg


def process_video_and_audio_ffmpeg(
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
    video_duration = get_duration(video_file)

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
        os.remove(audio_file)


def get_duration(file: str) -> float:
    """Get the duration of a video file."""
    try:
        probe = ffmpeg.probe(file)
        duration = float(probe["format"]["duration"])
        return duration
    except KeyError:
        raise ValueError("Could not retrieve duration from the file.")
    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode('utf-8')}")
