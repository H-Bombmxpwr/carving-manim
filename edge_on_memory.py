# tools/precompute_memory_edges.py
from importlib.resources import files
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import convolve, gaussian_filter, maximum_filter

# Locate the *installed* assets/images folder
assets_root = files("seamcarving_manim.assets.images")
src_path    = assets_root.joinpath("memory.jpg")

# Output dir inside the installed package
edges_dir = assets_root.joinpath("memory_edges")
Path(edges_dir).mkdir(parents=True, exist_ok=True)

# Load original
img = Image.open(src_path).convert("L")  # grayscale
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

# ---- THICKEN EDGES (important change) ----

# First thickening pass
gx = gaussian_filter(gx, sigma=1.6)
gy = gaussian_filter(gy, sigma=1.6)
mag = gaussian_filter(mag, sigma=1.6)

# Second pass (“soft dilation” using local max)
gx = maximum_filter(gx, size=3)
gy = maximum_filter(gy, size=3)
mag = maximum_filter(mag, size=3)

def norm255(a, gamma=0.45, floor=90, clip_low=10):
    """
    Extra bold edges:
    - gamma < 0.5 = boosts even mid-low responses
    - floor = guarantees minimum visibility
    - clip_low removes tiny specks
    """
    m = np.max(np.abs(a))
    if m == 0:
        return np.zeros_like(a, dtype=np.uint8)

    n = np.abs(a) / m
    n[n < (clip_low / 255.0)] = 0.0
    n = np.power(n, gamma)
    n = floor + (255 - floor) * n
    n = np.clip(n, 0, 255)

    return n.astype(np.uint8)

gx_n  = norm255(gx)
gy_n  = norm255(gy)
mag_n = norm255(mag)

# ======================================
# Color palettes
# ======================================

LIGHT_RED  = np.array([255, 110, 110])   # soft light red
BABY_BLUE  = np.array([120, 190, 255])   # baby blue
LIME_GREEN = np.array([140, 255, 120])   # lime green

# ======================================
# Apply color
# ======================================

gx_rgb  = np.zeros((*gx_n.shape, 3), dtype=np.uint8)
gy_rgb  = np.zeros((*gy_n.shape, 3), dtype=np.uint8)
mag_rgb = np.zeros((*mag_n.shape, 3), dtype=np.uint8)

for c in range(3):
    gx_rgb[..., c]  = (gx_n / 255.0) * LIGHT_RED[c]
    gy_rgb[..., c]  = (gy_n / 255.0) * BABY_BLUE[c]
    mag_rgb[..., c] = (mag_n / 255.0) * LIME_GREEN[c]

Image.fromarray(gx_rgb.astype(np.uint8)).save(edges_dir / "memory_edge_x.png")
Image.fromarray(gy_rgb.astype(np.uint8)).save(edges_dir / "memory_edge_y.png")
Image.fromarray(mag_rgb.astype(np.uint8)).save(edges_dir / "memory_edge_mag.png")

print("Saved EXTRA thick, high-contrast pastel edge maps to:", edges_dir)
