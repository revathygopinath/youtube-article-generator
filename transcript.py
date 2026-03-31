import re
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


def extract_video_id(url: str) -> str:
    """Parse video ID from any YouTube URL format."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"embed\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_transcript(url: str) -> str:
    """
    Fetch the full transcript text from a YouTube URL.
    Compatible with both old (<0.6) and new (>=0.6) youtube-transcript-api versions.
    """
    video_id = extract_video_id(url)

    try:
        # ── Try new API style first (v0.6.x+) ──
        # In v0.6+, methods are instance-based
        try:
            ytt_instance = YouTubeTranscriptApi()
            transcript_list = ytt_instance.list(video_id)

            # Try to find English transcript
            try:
                transcript = transcript_list.find_transcript(["en"])
            except Exception:
                raise ValueError(
                    "No English transcript found for this video. "
                    "Please use a video with English captions enabled."
                )

            entries = list(transcript.fetch())

        except AttributeError:
            # ── Fall back to old API style (v0.5.x and below) ──
            # In older versions, methods are static/class-based
            try:
                entries = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            except NoTranscriptFound:
                raise ValueError(
                    "No English transcript found for this video. "
                    "Please use a video with English captions enabled."
                )

        # ── Parse entries ──
        full_text = " ".join(
            (e["text"] if isinstance(e, dict) else e.text) for e in entries
        )
        return full_text.strip()

    except ValueError:
        raise  # re-raise our own clean errors as-is

    except TranscriptsDisabled:
        raise ValueError(
            "Transcripts are disabled for this video. "
            "Try a different video that has captions enabled."
        )
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {str(e)}")


def estimate_tokens(text: str) -> int:
    """Rough token count estimate (~4 chars per token)."""
    return len(text) // 4
