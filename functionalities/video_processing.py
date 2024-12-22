import subprocess
from moviepy.editor import AudioFileClip, VideoFileClip, os


def merge_with_audio_moviepy(
    video_file: str, audio_file: str, output_file: str, fps: float
):
    """Merge video and audio using moviepy."""
    print("Merging video and audio using moviepy")
    try:
        audio = AudioFileClip(audio_file)
        video = VideoFileClip(video_file)

        video_duration = video.duration
        audio_duration = audio.duration

        if video_duration > audio_duration:
            video = video.subclip(0, audio_duration)

        if audio_duration > video_duration:
            audio = audio.subclip(0, video_duration)

        # Set audio to video
        video = video.set_audio(audio)

        # Write the final output
        video.write_videofile(
            output_file,
            codec="libx264",  # High quality video codec
            audio_codec="aac",  # High quality audio codec
            preset="slow",  # Slow encoding for better quality
            threads=8,  # Use 8 threads for encoding
            bitrate="5000k",  # 5 Mbps bitrate
            fps=fps,
        )
    except Exception as e:
        print("An error occurred:", e)


def merge_with_audio_ffmpeg(
    video_file: str,
    audio_file: str,
    output_file: str,
    expected_fps: float,
    expected_duration: float,
    keep: bool = False,
):
    """Merge video and audio using ffmpeg."""
    video_duration = get_duration(video_file)

    actual_fps = expected_fps * (video_duration / expected_duration)
    duration_ratio = expected_duration / video_duration

    # if audio_duration > video_duration:
    #     trim_ffmpeg(audio_file, video_duration)

    print("Merging video and audio using ffmpeg")
    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_file,
        "-i",
        audio_file,
        "-vf",
        f"setpts={duration_ratio}*PTS",
        "-r",
        str(actual_fps),
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-threads",
        "8",
        "-shortest",
        output_file,
    ]
    subprocess.run(command, check=True)

    if not keep:
        os.remove(video_file)
        os.remove(audio_file)


def trim_ffmpeg(file: str, new_duration: float) -> None:
    """Trim a video using ffmpeg."""
    temp_file = f"temp_{file}"
    command = [
        "ffmpeg",
        "-y",
        "-i",
        file,
        "-t",
        str(new_duration),
        "-c",
        "copy",
        temp_file,
    ]
    subprocess.run(command, check=True)

    os.replace(temp_file, file)


def get_duration(file: str) -> float:
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
