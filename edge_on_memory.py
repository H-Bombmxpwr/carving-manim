# tools/precompute_memory_edges.py

from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import convolve, gaussian_filter, maximum_filter

# -----------------------------------------
# Resolve PROJECT ROOT (this file is at repo root)
# -----------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

ASSETS_DIR = PROJECT_ROOT / "src" / "seamcarving_manim" / "assets" / "images"
SRC_PATH   = ASSETS_DIR / "memory.jpg"

EDGES_DIR  = ASSETS_DIR / "memory_edges"
EDGES_DIR.mkdir(parents=True, exist_ok=True)

print("Project root:", PROJECT_ROOT)
print("Reading from:", SRC_PATH)
print("Saving to:", EDGES_DIR)

# Load original as grayscale
img = Image.open(SRC_PATH).convert("L")
arr = np.array(img, dtype=float)

# Sobel kernels
KX = np.array([[-1, 0, 1],
               [-2, 0, 2],
               [-1, 0, 1]], dtype=float)
KY = np.array([[-1, -2, -1],
               [ 0,  0,  0],
               [ 1,  2,  1]], dtype=float)

# Raw gradients
gx = convolve(arr, KX, mode="reflect")
gy = convolve(arr, KY, mode="reflect")
mag = np.sqrt(gx**2 + gy**2)

# ---- THICKEN EDGES (blur + max filter) ----
gx = gaussian_filter(gx, sigma=1.2)
gy = gaussian_filter(gy, sigma=1.2)
mag = gaussian_filter(mag, sigma=1.2)

# make strokes fatter
gx = maximum_filter(gx, size=5)
gy = maximum_filter(gy, size=5)
mag = maximum_filter(mag, size=5)


def norm255(a, gamma=0.45, floor=90, clip_low=10):
    """
    Map gradient magnitudes to 0–255 with:
      - hard suppression of tiny responses (clip_low)
      - gamma < 1 to boost midtones
      - 'floor' only applied to nonzero edges
    Background stays pure black.
    """
    a_abs = np.abs(a)
    m = np.max(a_abs)
    if m == 0:
        return np.zeros_like(a, dtype=np.uint8)

    # normalize
    n = a_abs / m

    # suppress tiny gradient responses
    n[n < (clip_low / 255.0)] = 0.0

    # allocate output
    out = np.zeros_like(a_abs, dtype=np.float32)

    # only apply gamma + floor where there is an edge
    mask = n > 0
    if np.any(mask):
        v = n[mask] ** gamma
        v = floor + (255 - floor) * v
        out[mask] = v

    out = np.clip(out, 0, 255)
    return out.astype(np.uint8)


gx_n  = norm255(gx)
gy_n  = norm255(gy)
mag_n = norm255(mag)

# ======================================
# Color palettes (pastel / bright)
# ======================================

LIGHT_RED  = np.array([255, 110, 110])   # soft light red
BABY_BLUE  = np.array([120, 190, 255])   # baby blue
LIME_GREEN = np.array([140, 255, 120])   # lime green

# ======================================
# Apply color on black background
# ======================================

gx_rgb  = np.zeros((*gx_n.shape, 3), dtype=np.uint8)
gy_rgb  = np.zeros((*gy_n.shape, 3), dtype=np.uint8)
mag_rgb = np.zeros((*mag_n.shape, 3), dtype=np.uint8)

scale_gx  = gx_n.astype(np.float32) / 255.0
scale_gy  = gy_n.astype(np.float32) / 255.0
scale_mag = mag_n.astype(np.float32) / 255.0

for c in range(3):
    gx_rgb[..., c]  = (scale_gx  * LIGHT_RED[c]).astype(np.uint8)
    gy_rgb[..., c]  = (scale_gy  * BABY_BLUE[c]).astype(np.uint8)
    mag_rgb[..., c] = (scale_mag * LIME_GREEN[c]).astype(np.uint8)

Image.fromarray(gx_rgb).save(EDGES_DIR / "memory_edge_x.png")
Image.fromarray(gy_rgb).save(EDGES_DIR / "memory_edge_y.png")
Image.fromarray(mag_rgb).save(EDGES_DIR / "memory_edge_mag.png")

print("Saved edge maps to:", EDGES_DIR)
