from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import convolve

# ============================================================
# Resolve root
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "carving-manim" / "src" / "seamcarving_manim" / "assets" / "images"

SRC = ASSETS_DIR / "memory.jpg"
OUT = ASSETS_DIR / "memory_edges_fast"
OUT.mkdir(parents=True, exist_ok=True)

print("Reading:", SRC)
print("Saving to:", OUT)

# ============================================================
# Load and downsample image (color + grayscale)
# ============================================================
orig_color = Image.open(SRC).convert("RGB")
gray = np.array(orig_color.convert("L"), dtype=float)

# Downsample factor (tune for quality/speed)
DOWNSAMPLE = 2
color_ds = np.array(orig_color)[::DOWNSAMPLE, ::DOWNSAMPLE]
gray_ds = gray[::DOWNSAMPLE, ::DOWNSAMPLE]

H, W = gray_ds.shape
print("Working resolution:", H, "x", W)

# ============================================================
# Sobel kernels
# ============================================================
KX = np.array([[-1, 0, 1],
               [-2, 0, 2],
               [-1, 0, 1]], dtype=float)

KY = np.array([[-1, -2, -1],
               [ 0,  0,  0],
               [ 1,  2,  1]], dtype=float)

gx  = convolve(gray_ds, KX, mode="reflect")
gy  = convolve(gray_ds, KY, mode="reflect")
mag = np.sqrt(gx**2 + gy**2)

def norm255(a):
    aa = np.abs(a)
    m = aa.max() if aa.max() != 0 else 1.0
    return (aa / m * 255).clip(0, 255).astype(np.uint8)

gx_norm  = norm255(gx)
gy_norm  = norm255(gy)
mag_norm = norm255(mag)

# ============================================================
# Save PNGs for Manim
# ============================================================
Image.fromarray(color_ds).save(OUT / "orig_color.png")
Image.fromarray(gx_norm).save(OUT / "sobel_x.png")
Image.fromarray(gy_norm).save(OUT / "sobel_y.png")
Image.fromarray(mag_norm).save(OUT / "sobel_mag.png")

# ============================================================
# Dense vector field for arrows (normalized coordinates)
# ============================================================
STEP = max(2, H // 60)  # dense but not insane

xs, ys, dxs, dys = [], [], [], []
maxmag = mag.max() if mag.max() != 0 else 1.0

for i in range(0, H, STEP):
    for j in range(0, W, STEP):
        dvx = gx[i, j] / maxmag
        dvy = gy[i, j] / maxmag
        if np.hypot(dvx, dvy) < 0.03:
            continue

        # normalize coordinates to [0,1] in image space
        xs.append(j / W)
        ys.append(i / H)
        dxs.append(dvx)
        dys.append(dvy)

np.save(OUT / "vec_x.npy",  np.array(xs))
np.save(OUT / "vec_y.npy",  np.array(ys))
np.save(OUT / "vec_dx.npy", np.array(dxs))
np.save(OUT / "vec_dy.npy", np.array(dys))

print("Done.")
