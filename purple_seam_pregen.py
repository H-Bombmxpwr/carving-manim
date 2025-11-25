# purple_seam_pregen.py
#
# Precompute vertical seams for ~15% width reduction.
# Seams are chosen ONLY from the original's energy map,
# then applied to BOTH:
#   - memory.jpg          (original painting)
#   - memory_min_energy_bottom.png (orange DP map)
#
# For each seam removal, we save:
#   assets/images/memory_dual/orig/frame_0000.png
#   assets/images/memory_dual/dp/frame_0000.png
# with the seam painted in MAGENTA on both.

from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import convolve, gaussian_filter, maximum_filter

# ==========================================================
# CONFIG
# ==========================================================
PCT_REDUCTION = 0.15  # remove 15% of columns
MAGENTA = np.array([255, 0, 255], dtype=np.uint8)

# This file is at: carving-manim/purple_seam_pregen.py
# So PROJECT_ROOT is the repo root: carving-manim/
PROJECT_ROOT = Path(__file__).resolve().parent

ASSETS_DIR = PROJECT_ROOT / "src" / "seamcarving_manim" / "assets" / "images"

ORIG_PATH = ASSETS_DIR / "memory.jpg"
DP_PATH   = ASSETS_DIR / "min_energy_bottom" / "memory_min_energy_bottom.png"

OUT_ORIG_DIR = ASSETS_DIR / "memory_dual" / "orig"
OUT_DP_DIR   = ASSETS_DIR / "memory_dual" / "dp"
OUT_ORIG_DIR.mkdir(parents=True, exist_ok=True)
OUT_DP_DIR.mkdir(parents=True, exist_ok=True)

print("Project root:", PROJECT_ROOT)
print("Original image :", ORIG_PATH)
print("DP map image   :", DP_PATH)

# ==========================================================
# Sobel + DP utilities
# ==========================================================
KX = np.array([[-1, 0, 1],
               [-2, 0, 2],
               [-1, 0, 1]], float)
KY = np.array([[-1, -2, -1],
               [ 0,  0,  0],
               [ 1,  2,  1]], float)


def sobel_edgeness(gray):
    gx = convolve(gray, KX, mode="reflect")
    gy = convolve(gray, KY, mode="reflect")
    g = np.sqrt(gx**2 + gy**2)
    g = gaussian_filter(g, 1.0)
    g = maximum_filter(g, size=5)
    return g


def compute_dp_energy(E):
    """Classic bottom-up DP: min energy from (i,j) to bottom row."""
    H, W = E.shape
    dp = np.zeros_like(E)
    dp[-1] = E[-1]
    for i in range(H - 2, -1, -1):
        for j in range(W):
            neigh = []
            for dj in (-1, 0, 1):
                jj = j + dj
                if 0 <= jj < W:
                    neigh.append(dp[i + 1, jj])
            dp[i, j] = E[i, j] + min(neigh)
    return dp


def find_min_energy_seam(dp):
    """Trace the min-energy vertical seam from top to bottom."""
    H, W = dp.shape
    seam = []
    j = int(np.argmin(dp[0]))
    seam.append((0, j))
    for i in range(1, H):
        candidates = []
        for dj in (-1, 0, 1):
            jj = j + dj
            if 0 <= jj < W:
                candidates.append((dp[i, jj], jj))
        _, j = min(candidates)
        seam.append((i, j))
    return seam


def remove_seam(arr, seam):
    """
    Remove seam from a 3D array (H x W x C).
    For 2D energies, call with arr[..., None] and strip the channel.
    """
    H, W, C = arr.shape
    out = np.zeros((H, W - 1, C), dtype=arr.dtype)
    for i, j in seam:
        out[i, :j] = arr[i, :j]
        out[i, j:] = arr[i, j + 1:]
    return out


# ==========================================================
# LOAD INPUTS
# ==========================================================
orig = np.array(Image.open(ORIG_PATH).convert("RGB"), dtype=np.uint8)
dp_img = np.array(Image.open(DP_PATH).convert("RGB"), dtype=np.uint8)

if orig.shape[:2] != dp_img.shape[:2]:
    raise ValueError(f"Original and DP map must have same HxW; got {orig.shape[:2]} vs {dp_img.shape[:2]}")

H, W, _ = orig.shape

# Energy used to pick seams comes ONLY from the original
gray_orig = np.mean(orig, axis=2) / 255.0
E_orig = sobel_edgeness(gray_orig)

# How many seams to remove
N = int(W * PCT_REDUCTION)
print(f"Width = {W}, removing {N} seams (~{PCT_REDUCTION*100:.1f}%)")

# ==========================================================
# GENERATE FRAMES WITH SHARED SEAMS
# ==========================================================
cur_orig = orig.copy()
cur_dp   = dp_img.copy()
cur_E    = E_orig.copy()

for k in range(N):
    print(f"Seam {k+1}/{N}")

    # DP on ORIGINAL energy only
    dp = compute_dp_energy(cur_E)
    seam = find_min_energy_seam(dp)

    # Visual copies with magenta seam
    o_vis = cur_orig.copy()
    d_vis = cur_dp.copy()
    for (i, j) in seam:
        if 0 <= j < o_vis.shape[1]:
            o_vis[i, j] = MAGENTA
            d_vis[i, j] = MAGENTA

    # Save frames (PNG)
    Image.fromarray(o_vis).save(OUT_ORIG_DIR / f"frame_{k:04d}.png")
    Image.fromarray(d_vis).save(OUT_DP_DIR   / f"frame_{k:04d}.png")

    # Remove the seam from both images
    cur_orig = remove_seam(cur_orig, seam)
    cur_dp   = remove_seam(cur_dp,   seam)

    # Remove the seam from energy (2D -> add dummy channel)
    cur_E = remove_seam(cur_E[..., None], seam)[..., 0]

print("Done. Frames written to:")
print("  ", OUT_ORIG_DIR)
print("  ", OUT_DP_DIR)
