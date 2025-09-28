# Seam Carving (Manim)

Short demo comparing **naive horizontal squish** vs. **seam carving** for content-aware resizing, animated with Manim.

## Quick start
```bash
# create and activate venv (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# install deps
pip install -r requirements.txt  # or: pip install manim seam-carving pillow

# ffmpeg (required by Manim): install and put ffmpeg.exe on PATH
# e.g., choco install ffmpeg  (Windows) or brew install ffmpeg (macOS)

# render (examples)
manim -pqh src\seamcarving_manim\scenes\s00_title.py TitleScene
manim -pqh src\seamcarving_manim\scenes\s10_problem_and_baselines.py BaselinesScene
````

## Layout

```
src/
  seamcarving_manim/
    scenes/        # Manim scenes (title, baselines, etc.)
    utils/         # seam-carving helpers, energy map, etc.
    assets/
      images/      # e.g., memory.jpg (keep in git)
```

> Note: `media/` is **gitignored** (large, reproducible renders). Keep source assets (e.g., `assets/images/`) in git.
