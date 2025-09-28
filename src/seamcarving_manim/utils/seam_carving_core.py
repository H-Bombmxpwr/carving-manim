import numpy as np
from scipy.ndimage import sobel

def to_luma(img_float):  # img in [0,1], shape (H,W,3)
    r,g,b = img_float[...,0], img_float[...,1], img_float[...,2]
    return 0.2126*r + 0.7152*g + 0.0722*b

def energy_map(img):
    Y = to_luma(img)
    gx = sobel(Y, axis=1, mode="reflect")
    gy = sobel(Y, axis=0, mode="reflect")
    return np.hypot(gx, gy)

def cumulative_min_energy_vertical(E):
    H, W = E.shape
    M = E.copy()
    back = np.zeros((H,W), dtype=np.int8)  # -1,0,+1 predecessor column offsets
    for i in range(1,H):
        left  = np.r_[np.inf, M[i-1,:-1]]
        up    = M[i-1,:]
        right = np.r_[M[i-1,1:], np.inf]
        stack = np.vstack([left,up,right])  # 3 x W
        idx = np.argmin(stack, axis=0) - 1  # -> -1,0,+1
        M[i,:] += stack[idx+1, range(W)]
        back[i,:] = idx
    return M, back

def find_vertical_seam(M, back):
    H, W = M.shape
    seam = np.zeros(H, dtype=int)
    j = np.argmin(M[-1])
    seam[-1] = j
    for i in range(H-2, -1, -1):
        j = j + back[i+1, j]
        seam[i] = j
    return seam

def remove_vertical_seam(img, seam):
    H, W, C = img.shape
    out = np.zeros((H, W-1, C), dtype=img.dtype)
    for i in range(H):
        j = seam[i]
        out[i,:j,:]   = img[i,:j,:]
        out[i,j:,:]   = img[i,j+1:,:]
    return out
