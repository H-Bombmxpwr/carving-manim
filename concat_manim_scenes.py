import os
from pathlib import Path
import subprocess

root = Path("media/videos")

# Find all rendered MP4s (sorted by name)
clips = sorted(root.rglob("*.mp4"))

# Make list file
with open("concat_list.txt", "w") as f:
    for c in clips:
        f.write(f"file '{c.as_posix()}'\n")

# Run ffmpeg
subprocess.run([
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", "concat_list.txt",
    "-c", "copy",
    "full_video.mp4"
])
