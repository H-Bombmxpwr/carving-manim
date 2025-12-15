# tools/precompute_memory_min_energy_bottom.py

from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import convolve

# -----------------------------------------
# Resolve PROJECT ROOT (this file is at repo root)
# -----------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

ASSETS_DIR = PROJECT_ROOT / "src" / "seamcarving_manim" / "assets" / "images"
SRC_PATH = ASSETS_DIR / "memory.jpg"

MIN_EN_DIR = ASSETS_DIR / "min_energy_bottom"
MIN_EN_DIR.mkdir(parents=True, exist_ok=True)

print("Project root:", PROJECT_ROOT)
print("Reading from:", SRC_PATH)
print("Saving to:", MIN_EN_DIR)

# -------------------------------------------------
# 1) Load original image and compute "brightness"
#    brightness(c) = 0.3 R + 0.59 G + 0.11 B
#    (same as the Julia notebook)
# -------------------------------------------------
img_rgb = Image.open(SRC_PATH).convert("RGB")
rgb = np.asarray(img_rgb, dtype=np.float32) / 255.0

R = rgb[..., 0]
G = rgb[..., 1]
B = rgb[..., 2]

brightness = 0.3 * R + 0.59 * G + 0.11 * B  # H x W, float in [0,1]
H, W = brightness.shape

# -------------------------------------------------
# 2) Sobel edge detection
#    Sy, Sx = Kernel.sobel() in Julia, then
#    edgeness = sqrt( (b * Sx)^2 + (b * Sy)^2 )
# -------------------------------------------------
Sx = np.array(
    [[1, 0, -1],
     [2, 0, -2],
     [1, 0, -1]],
    dtype=np.float32,
)
Sy = np.array(
    [[1,  2,  1],
     [0,  0,  0],
     [-1, -2, -1]],
    dtype=np.float32,
)

# Convolve with clamp-style boundaries (nearest ≈ Julia's clamping)
gx = convolve(brightness, Sx, mode="nearest")
gy = convolve(brightness, Sy, mode="nearest")

# Edginess = gradient magnitude
energy = np.sqrt(gx**2 + gy**2)  # this is E in the Julia code

# -------------------------------------------------
# 3) Dynamic programming: least_edgy(E)
#    least_E[i,j] = E[i,j] + min over {SW, S, SE} of least_E on row below
# -------------------------------------------------
least_E = np.zeros_like(energy, dtype=np.float32)

# Bottom row: minimum energy is just the energy itself
least_E[-1, :] = energy[-1, :]

# Fill from bottom-2 up to top
for i in range(H - 2, -1, -1):
    for j in range(W):
        j1 = max(0, j - 1)
        j2 = min(W - 1, j + 1)
        e_min = np.min(least_E[i + 1, j1 : j2 + 1])
        least_E[i, j] = energy[i, j] + e_min

# -------------------------------------------------
# 4) Color mapping: like show_colored_array(least_E),
#    but with an ORANGE palette instead of teal.
#
#    In Julia:
#      pos_color = RGB(0.36, 0.82, 0.8)
#      to_rgb(x) = max(x,0) * pos_color / max(abs(least_E))
#
#    Here:
#      pos_color = ORANGE (255, 165, 0) in 0–255 space
#      We normalize least_E to [0,1] and multiply by ORANGE.
# -------------------------------------------------
max_val = float(np.max(least_E)) or 1.0
norm = least_E / max_val  # 0..1, brighter = more accumulated energy

ORANGE = np.array([255.0, 165.0, 0.0], dtype=np.float32)

out_rgb = (norm[..., None] * ORANGE[None, None, :]).astype(np.uint8)

out_img = Image.fromarray(out_rgb)
out_path = MIN_EN_DIR / "memory_min_energy_bottom.png"
out_img.save(out_path)

print("Saved min-energy-to-bottom map to:", out_path)
