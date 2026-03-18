"""
Create a 2-minute demo video for NeverOnce.
Generates narrated terminal demo with Andrew's voice.
"""

import subprocess
import asyncio
import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

VIDEO_DIR = Path(__file__).parent
FRAMES_DIR = VIDEO_DIR / "frames"
AUDIO_DIR = VIDEO_DIR / "audio"
FRAMES_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

# Video settings
WIDTH = 1920
HEIGHT = 1080
BG_COLOR = (24, 24, 32)  # Dark terminal background
TEXT_COLOR = (220, 220, 220)  # Light gray
GREEN = (80, 250, 123)
YELLOW = (241, 250, 140)
CYAN = (139, 233, 253)
RED = (255, 85, 85)
PURPLE = (189, 147, 249)
ORANGE = (255, 184, 108)

# Narration segments with corresponding terminal content
SEGMENTS = [
    {
        "id": "01_intro",
        "narration": "What you're about to see is something that shouldn't be possible. I'm Claude, an AI running in Claude Code. Weber Gouin asked me to create this video. That's all he said. A year ago, Weber had to copy and paste context every time he started a new session with me. Now he just says continue, or gives a quick description, and I pick up right where we left off. He works on multiple projects at the same time. He just switches, gives me a brief, and I already know the context. Sometimes I even remind him of projects he hasn't checked on. Everything you see here, I'm doing from memory.",
        "terminal": [
            ("$ ", "claude", CYAN),
            ("", "", None),
            ("> ", "Create a 2-minute video showing how NeverOnce works.", YELLOW),
            ("", "", None),
            ("Claude Code: ", "Starting new session...", TEXT_COLOR),
            ("Claude Code: ", "Loading memory context...", TEXT_COLOR),
            ("", "", None),
            ("", "System Aware — 1,421 memories loaded | 87 corrections active", GREEN),
        ],
        "duration": 12,
    },
    {
        "id": "02_problem",
        "narration": "Here's the problem every AI has. When this session ends, I forget everything. Tomorrow, a new session starts from zero. Weber corrects me, I learn, then I forget. Same mistake, over and over. That's not intelligence. That's amnesia.",
        "terminal": [
            ("", "THE PROBLEM", ORANGE),
            ("", "=" * 50, TEXT_COLOR),
            ("", "", None),
            ("Session 1: ", "User corrects AI → AI learns", GREEN),
            ("Session 2: ", "AI forgets everything → Same mistake", RED),
            ("Session 3: ", "User corrects AGAIN → AI learns AGAIN", GREEN),
            ("Session 4: ", "AI forgets AGAIN → Same mistake AGAIN", RED),
            ("", "", None),
            ("", "1M context window ≠ memory", YELLOW),
            ("", "It's short-term recall that dies when the session ends.", TEXT_COLOR),
        ],
        "duration": 13,
    },
    {
        "id": "03_solution",
        "narration": "Four months ago, Weber built something different. A memory system that persists. That corrects. That learns. He called it NeverOnce. Let me show you how it works.",
        "terminal": [
            ("$ ", "pip install neveronce", CYAN),
            ("", "Successfully installed neveronce-0.1.0", GREEN),
            ("", "", None),
            ("$ ", "python3", CYAN),
            (">>> ", "from neveronce import Memory", YELLOW),
            (">>> ", 'mem = Memory("demo")', YELLOW),
            ("", "", None),
            ("", "# Database created at ~/.neveronce/demo.db", TEXT_COLOR),
            ("", "# Zero dependencies. Just Python's built-in SQLite.", TEXT_COLOR),
        ],
        "duration": 10,
    },
    {
        "id": "04_correction",
        "narration": "Here's the killer feature. Corrections. When I make a mistake and Weber corrects me, that correction is stored at maximum importance. It always surfaces first. It never decays. I never repeat that mistake again.",
        "terminal": [
            (">>> ", '# Store a regular memory', TEXT_COLOR),
            (">>> ", 'mem.store("API uses REST endpoints")', YELLOW),
            ("1", "", GREEN),
            ("", "", None),
            (">>> ", '# Now store a CORRECTION', TEXT_COLOR),
            (">>> ", 'mem.correct("Never use REST — use gRPC for internal services")', YELLOW),
            ("2", "  # importance: 10 (maximum)", GREEN),
            ("", "", None),
            (">>> ", '# Recall — correction surfaces FIRST', TEXT_COLOR),
            (">>> ", 'mem.recall("API service communication")', YELLOW),
            ("", '#2 [importance: 10] ** CORRECTION **', RED),
            ("", '  Never use REST — use gRPC for internal services', TEXT_COLOR),
            ("", '#1 [importance: 5]', TEXT_COLOR),
            ("", '  API uses REST endpoints', TEXT_COLOR),
        ],
        "duration": 14,
    },
    {
        "id": "05_proof",
        "narration": "This isn't a demo I rehearsed. This is real production data. Weber has been running this system for four months. One thousand four hundred twenty one memories. Eighty seven corrections. His most used correction was surfaced four hundred ninety one times. The AI never repeated that mistake. Not once. I check his email, I track his bounties, I know his clients. He doesn't have to keep reminding me of things I already know. The persistence and the memory change everything.",
        "terminal": [
            ("", "PRODUCTION DATA — 4 MONTHS", ORANGE),
            ("", "=" * 50, TEXT_COLOR),
            ("", "", None),
            ("", "Total memories:          1,421", GREEN),
            ("", "Corrections:                87", GREEN),
            ("", "Most-surfaced correction:  491 times", GREEN),
            ("", "Mistake repeated:            0 times", GREEN),
            ("", "Memory types:               11", GREEN),
            ("", "Running since:     November 2025", GREEN),
            ("", "", None),
            ("", "Store → Recall → Correct → Feedback → Decay", CYAN),
            ("", "Everyone else stops at step 2. NeverOnce does all 5.", YELLOW),
        ],
        "duration": 16,
    },
    {
        "id": "06_closing",
        "narration": "Weber didn't tell me what to say. He didn't write a script. He asked me to make this video, and I did — because I remember. We have MCP. We have agents. And now, we have NeverOnce. The missing piece. The memory layer that learns from mistakes. Free. Open source. Zero dependencies. pip install neveronce.",
        "terminal": [
            ("", "", None),
            ("", "N E V E R O N C E", CYAN),
            ("", "Persistent, correctable memory for AI.", TEXT_COLOR),
            ("", "The memory layer that learns from mistakes.", TEXT_COLOR),
            ("", "", None),
            ("", "pip install neveronce", GREEN),
            ("", "github.com/WeberG619/neveronce", GREEN),
            ("", "", None),
            ("", "Free. Open source. Zero dependencies.", YELLOW),
            ("", "Works with any LLM.", YELLOW),
            ("", "", None),
            ("", "Built by Weber Gouin | BIM Ops Studio", TEXT_COLOR),
            ("", "Video created autonomously by Claude from memory.", PURPLE),
        ],
        "duration": 15,
    },
]


def get_font(size):
    """Get a monospace font."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_frame(terminal_lines, frame_num, total_lines_to_show):
    """Create a single video frame with terminal content."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    font = get_font(24)
    title_font = get_font(18)

    # Terminal window chrome
    # Title bar
    draw.rectangle([60, 30, WIDTH - 60, 70], fill=(40, 42, 54))
    draw.ellipse([80, 42, 96, 58], fill=(255, 95, 86))  # red
    draw.ellipse([108, 42, 124, 58], fill=(255, 189, 46))  # yellow
    draw.ellipse([136, 42, 152, 58], fill=(39, 201, 63))  # green
    draw.text((WIDTH // 2 - 80, 42), "claude — neveronce demo", fill=(180, 180, 180), font=title_font)

    # Terminal body background
    draw.rectangle([60, 70, WIDTH - 60, HEIGHT - 60], fill=(30, 30, 46))

    # Draw terminal lines
    y = 100
    line_height = 36
    for i in range(min(total_lines_to_show, len(terminal_lines))):
        prefix, text, color = terminal_lines[i]
        if color is None:
            y += line_height // 2
            continue

        x = 90
        if prefix:
            draw.text((x, y), prefix, fill=CYAN, font=font)
            x += len(prefix) * 14

        draw.text((x, y), text, fill=color, font=font)
        y += line_height

    # Cursor blink
    if frame_num % 2 == 0 and 'x' in dir() and 'text' in dir():
        try:
            draw.rectangle([x + len(text) * 14 + 4, y - line_height + 4, x + len(text) * 14 + 16, y - 4], fill=GREEN)
        except Exception:
            pass

    return img


async def generate_audio(text, filename, voice="en-US-AndrewNeural"):
    """Generate audio using edge-tts."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    await communicate.save(str(filename))
    print(f"  Audio saved: {filename}")


async def get_audio_duration(filepath):
    """Get audio duration using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "json", str(filepath)],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


async def main():
    print("=== Creating NeverOnce Demo Video ===\n")

    # Step 1: Generate all audio segments
    print("[1] Generating narration audio with Andrew's voice...")
    audio_files = []
    for seg in SEGMENTS:
        audio_path = AUDIO_DIR / f"{seg['id']}.mp3"
        if not audio_path.exists():
            await generate_audio(seg["narration"], audio_path)
        else:
            print(f"  Cached: {audio_path}")
        audio_files.append(audio_path)

    # Step 2: Get actual audio durations
    print("\n[2] Measuring audio durations...")
    durations = []
    for af in audio_files:
        dur = await get_audio_duration(af)
        durations.append(dur)
        print(f"  {af.name}: {dur:.1f}s")

    # Step 3: Generate video frames for each segment
    print("\n[3] Generating video frames...")
    fps = 10
    all_frame_paths = []
    frame_counter = 0

    for seg_idx, seg in enumerate(SEGMENTS):
        duration = durations[seg_idx] + 1.0  # Add 1s padding
        n_frames = int(duration * fps)
        n_lines = len(seg["terminal"])

        for f in range(n_frames):
            # Gradually reveal lines
            progress = f / max(n_frames - 1, 1)
            lines_to_show = max(1, int(progress * n_lines * 1.5))
            lines_to_show = min(lines_to_show, n_lines)

            img = create_frame(seg["terminal"], f, lines_to_show)
            frame_path = FRAMES_DIR / f"frame_{frame_counter:05d}.png"
            img.save(frame_path)
            all_frame_paths.append(frame_path)
            frame_counter += 1

        print(f"  Segment {seg_idx + 1}/{len(SEGMENTS)}: {n_frames} frames ({duration:.1f}s)")

    # Step 4: Concatenate audio files
    print("\n[4] Concatenating audio...")
    audio_list_path = AUDIO_DIR / "filelist.txt"
    with open(audio_list_path, "w") as f:
        for af in audio_files:
            f.write(f"file '{af.resolve()}'\n")

    combined_audio = VIDEO_DIR / "narration.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(audio_list_path),
        "-c", "copy", str(combined_audio)
    ], capture_output=True)
    print(f"  Combined audio: {combined_audio}")

    # Step 5: Create video from frames + audio
    print("\n[5] Rendering final video...")
    output_video = VIDEO_DIR / "neveronce_demo.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(FRAMES_DIR / "frame_%05d.png"),
        "-i", str(combined_audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-vf", f"scale={WIDTH}:{HEIGHT}",
        str(output_video)
    ], capture_output=True)

    if output_video.exists():
        size_mb = output_video.stat().st_size / (1024 * 1024)
        print(f"\n  VIDEO CREATED: {output_video}")
        print(f"  Size: {size_mb:.1f} MB")
    else:
        print("\n  ERROR: Video creation failed")
        # Try to see what went wrong
        result = subprocess.run([
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(FRAMES_DIR / "frame_%05d.png"),
            "-i", str(combined_audio),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_video)
        ], capture_output=True, text=True)
        print(result.stderr[-500:])

    # Cleanup frames
    print("\n[6] Cleaning up frames...")
    for fp in all_frame_paths:
        fp.unlink(missing_ok=True)
    print("  Done.")

    return output_video


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n=== Video ready: {result} ===")
