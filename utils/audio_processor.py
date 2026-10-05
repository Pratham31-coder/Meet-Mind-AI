import yt_dlp
from pydub import AudioSegment
import os
import imageio_ffmpeg

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
AudioSegment.converter = ffmpeg_path

# Default download directory (used by CLI mode)
DEFAULT_DOWNLOAD_DIR = 'downloads'


def download_youtube_audio(url: str, output_dir: str = DEFAULT_DOWNLOAD_DIR) -> str:
    """
    Download audio from a YouTube URL using yt-dlp.

    Args:
        url:        YouTube video URL.
        output_dir: Directory to save the downloaded WAV file.

    Returns:
        Path to the downloaded WAV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "ffmpeg_location": ffmpeg_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename



def convert_to_wav(input_path: str, output_dir: str | None = None) -> str:
    """
    Convert any audio/video file to WAV format using pydub.

    Args:
        input_path: Path to the source audio/video file.
        output_dir: If provided, the WAV file is saved here instead of
                    next to the source file.

    Returns:
        Path to the converted WAV file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Source file not found: {input_path}")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base}.wav")
    else:
        output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz mono
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path: str, chunk_minutes: int = 10, output_dir: str | None = None) -> list:
    """
    Split a WAV file into chunks of `chunk_minutes` length.

    Args:
        wav_path:      Path to the WAV file.
        chunk_minutes: Duration of each chunk in minutes.
        output_dir:    If provided, chunks are written here.
                       Otherwise they are written next to the source file.

    Returns:
        List of chunk file paths.
    """
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    MIN_CHUNK_MS = 1000  # Skip chunks shorter than 1 second — Whisper crashes on empty audio

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]

        if len(chunk) < MIN_CHUNK_MS:
            print(f"Skipping chunk {i} — too short ({len(chunk)}ms), likely trailing silence.")
            continue

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            chunk_path = os.path.join(output_dir, f"chunk_{i}.wav")
        else:
            chunk_path = f"{wav_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str, output_dir: str | None = None) -> list:
    """
    Determine the media source and process it into audio chunks.

    Args:
        source:     YouTube URL or local file path.
        output_dir: Working directory for WAV and chunk files.
                    If None, uses default locations (backwards-compatible).

    Returns:
        List of WAV chunk file paths ready for transcription.
    """
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source, output_dir=output_dir or DEFAULT_DOWNLOAD_DIR)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source, output_dir=output_dir)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path, output_dir=output_dir)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
