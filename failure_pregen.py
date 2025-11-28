"""
Precompute failure mode demonstrations for seam carving comparison.

This script generates frames showing different image resizing strategies:
1. crop - Best cropping from the side
2. column - Removing columns with minimal total energy  
3. pixel - Removing the lowest energy pixel from each row (zigzag)
4. optimal - Removing pixels globally by lowest energy (destroys rectangle)
5. seam - Proper seam carving (the good approach)

Based on Figure 2 from "Seam Carving for Content-Aware Image Resizing" (Avidan & Shamir, 2007)
"""

import numpy as np
from PIL import Image
from pathlib import Path
from scipy.ndimage import convolve
import argparse


def compute_energy(img_array: np.ndarray) -> np.ndarray:
    """Compute energy using gradient magnitude (Sobel filters)."""
    if img_array.ndim == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array.astype(float)
    
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
    
    gx = convolve(gray, sobel_x, mode='reflect')
    gy = convolve(gray, sobel_y, mode='reflect')
    
    return np.abs(gx) + np.abs(gy)


def find_vertical_seam(energy: np.ndarray) -> np.ndarray:
    """Find minimum energy vertical seam using dynamic programming."""
    h, w = energy.shape
    dp = energy.copy()
    backtrack = np.zeros((h, w), dtype=np.int32)
    
    for i in range(1, h):
        for j in range(w):
            left = dp[i-1, j-1] if j > 0 else np.inf
            center = dp[i-1, j]
            right = dp[i-1, j+1] if j < w-1 else np.inf
            
            min_energy = min(left, center, right)
            dp[i, j] += min_energy
            
            if min_energy == left:
                backtrack[i, j] = j - 1
            elif min_energy == center:
                backtrack[i, j] = j
            else:
                backtrack[i, j] = j + 1
    
    # Backtrack to find seam
    seam = np.zeros(h, dtype=np.int32)
    seam[-1] = np.argmin(dp[-1])
    
    for i in range(h-2, -1, -1):
        seam[i] = backtrack[i+1, seam[i+1]]
    
    return seam


def remove_vertical_seam(img: np.ndarray, seam: np.ndarray) -> np.ndarray:
    """Remove a vertical seam from the image."""
    h, w = img.shape[:2]
    if img.ndim == 3:
        output = np.zeros((h, w-1, img.shape[2]), dtype=img.dtype)
        for i in range(h):
            j = seam[i]
            output[i, :j] = img[i, :j]
            output[i, j:] = img[i, j+1:]
    else:
        output = np.zeros((h, w-1), dtype=img.dtype)
        for i in range(h):
            j = seam[i]
            output[i, :j] = img[i, :j]
            output[i, j:] = img[i, j+1:]
    return output


def strategy_crop(img: np.ndarray, num_pixels: int, side: str = 'right') -> np.ndarray:
    """
    Strategy: Best cropping - remove pixels from one side.
    This loses content but maintains structure.
    """
    if side == 'right':
        return img[:, :-num_pixels].copy()
    elif side == 'left':
        return img[:, num_pixels:].copy()
    elif side == 'center':
        # Remove from both sides equally
        left_remove = num_pixels // 2
        right_remove = num_pixels - left_remove
        return img[:, left_remove:img.shape[1]-right_remove].copy()
    else:
        return img[:, :-num_pixels].copy()


def strategy_column(img: np.ndarray, num_columns: int) -> np.ndarray:
    """
    Strategy: Remove columns with minimal total energy.
    This creates visual artifacts because entire columns are removed.
    """
    result = img.copy()
    
    for _ in range(num_columns):
        energy = compute_energy(result)
        # Sum energy along each column
        column_energies = np.sum(energy, axis=0)
        # Find column with minimum total energy
        min_col = np.argmin(column_energies)
        # Remove that column
        if result.ndim == 3:
            result = np.delete(result, min_col, axis=1)
        else:
            result = np.delete(result, min_col, axis=1)
    
    return result


def strategy_pixel_per_row(img: np.ndarray, num_pixels: int) -> np.ndarray:
    """
    Strategy: Remove the lowest energy pixel from each row.
    This creates a zigzag effect and destroys horizontal coherence.
    Returns a non-rectangular result padded with black.
    """
    h, w = img.shape[:2]
    result = img.copy()
    
    # Track how many pixels removed from each row
    removed_per_row = np.zeros(h, dtype=np.int32)
    
    for _ in range(num_pixels):
        energy = compute_energy(result)
        
        # For each row, find and mark the minimum energy pixel
        for i in range(h):
            if removed_per_row[i] < num_pixels:
                row_energy = energy[i, :]
                # Find minimum that hasn't been "removed" yet
                min_j = np.argmin(row_energy)
                # Set that pixel to black (simulating removal with shift)
                energy[i, min_j] = np.inf  # Mark as used
        
    # Actually create the zigzag effect
    # Remove 'num_pixels' lowest energy pixels per row, shifting remaining left
    energy = compute_energy(img)
    
    if img.ndim == 3:
        output = np.zeros((h, w - num_pixels, img.shape[2]), dtype=img.dtype)
    else:
        output = np.zeros((h, w - num_pixels), dtype=img.dtype)
    
    for i in range(h):
        row_energy = energy[i, :].copy()
        row_pixels = img[i, :].copy() if img.ndim == 2 else img[i, :, :].copy()
        
        # Find indices of pixels to keep (highest energy)
        indices_to_remove = np.argsort(row_energy)[:num_pixels]
        mask = np.ones(w, dtype=bool)
        mask[indices_to_remove] = False
        
        if img.ndim == 3:
            output[i] = row_pixels[mask]
        else:
            output[i] = row_pixels[mask]
    
    return output


def strategy_optimal_global(img: np.ndarray, num_pixels: int) -> np.ndarray:
    """
    Strategy: Remove pixels globally with lowest energy (destroys rectangular shape).
    We'll visualize this by making removed pixels black, showing the destruction.
    """
    h, w = img.shape[:2]
    result = img.copy().astype(float)
    energy = compute_energy(img)
    
    # Flatten and find lowest energy pixels
    flat_energy = energy.flatten()
    indices_to_remove = np.argsort(flat_energy)[:num_pixels * h]  # Remove more to show effect
    
    # Create mask
    mask = np.zeros(h * w, dtype=bool)
    mask[indices_to_remove] = True
    mask = mask.reshape(h, w)
    
    # Set removed pixels to black
    if result.ndim == 3:
        result[mask] = [0, 0, 0]
    else:
        result[mask] = 0
    
    return result.astype(np.uint8)


def strategy_seam(img: np.ndarray, num_seams: int, return_seam_overlay: bool = False) -> np.ndarray:
    """
    Strategy: Proper seam carving - the good approach.
    Optionally returns an overlay showing the seams.
    """
    result = img.copy()
    
    if return_seam_overlay:
        overlay = img.copy()
        
    for i in range(num_seams):
        energy = compute_energy(result)
        seam = find_vertical_seam(energy)
        
        if return_seam_overlay and i < 50:  # Show first 50 seams
            # Draw seam on overlay
            for row, col in enumerate(seam):
                if col < overlay.shape[1]:
                    if overlay.ndim == 3:
                        overlay[row, col] = [255, 0, 255]  # Magenta
                    else:
                        overlay[row, col] = 255
        
        result = remove_vertical_seam(result, seam)
    
    if return_seam_overlay:
        return result, overlay
    return result


def pad_to_width(img: np.ndarray, target_width: int) -> np.ndarray:
    """Pad image with black on the right to reach target width."""
    h, w = img.shape[:2]
    if w >= target_width:
        return img
    
    if img.ndim == 3:
        padded = np.zeros((h, target_width, img.shape[2]), dtype=img.dtype)
        padded[:, :w] = img
    else:
        padded = np.zeros((h, target_width), dtype=img.dtype)
        padded[:, :w] = img
    
    return padded


def main():
    parser = argparse.ArgumentParser(description="Generate failure mode comparison images")
    parser.add_argument("--input", type=str, required=True, help="Input image path")
    parser.add_argument("--output", type=str, required=True, help="Output directory")
    parser.add_argument("--reduction-percent", type=float, default=15.0, help="Percentage to reduce width by (default: 15%%)")
    parser.add_argument("--frames", type=int, default=50, help="Number of intermediate frames")
    parser.add_argument("--force", action="store_true", help="Force recompute even if files exist")
    args = parser.parse_args()
    
    # Load image
    img_path = Path(args.input)
    if not img_path.exists():
        raise FileNotFoundError(f"Input image not found: {img_path}")
    
    img = np.array(Image.open(img_path).convert("RGB"), dtype=np.uint8)
    original_width = img.shape[1]
    original_height = img.shape[0]
    print(f"Loaded image: {img.shape}")
    
    # Calculate reduction based on percentage
    reduction = int(original_width * args.reduction_percent / 100.0)
    print(f"Reducing width by {args.reduction_percent}% = {reduction} pixels (from {original_width} to {original_width - reduction})")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each strategy (no crop)
    strategies = ['column', 'pixel', 'optimal', 'seam']
    for strategy in strategies:
        (output_dir / strategy).mkdir(exist_ok=True)
    
    # Helper to check if all frames exist
    def frames_exist(subdir, num_frames):
        for i in range(num_frames):
            if not (output_dir / subdir / f"frame_{i:04d}.png").exists():
                return False
        return True
    
    num_frames = args.frames
    
    # Also save original and energy map (if not exist)
    if not (output_dir / "original.png").exists() or args.force:
        print("Saving original...")
        Image.fromarray(img).save(output_dir / "original.png")
    else:
        print("Skipping original (already exists)")
    
    if not (output_dir / "energy_map.png").exists() or args.force:
        print("Saving energy map...")
        energy = compute_energy(img)
        energy_normalized = (energy / energy.max() * 255).astype(np.uint8)
        # Create colored energy map (blue-yellow gradient)
        energy_colored = np.zeros((*energy.shape, 3), dtype=np.uint8)
        energy_colored[:, :, 0] = energy_normalized  # Red channel
        energy_colored[:, :, 1] = energy_normalized  # Green channel  
        energy_colored[:, :, 2] = (255 - energy_normalized)  # Blue channel (inverted)
        Image.fromarray(energy_colored).save(output_dir / "energy_map.png")
    else:
        print("Skipping energy map (already exists)")
    
    print(f"Generating {num_frames} frames, reducing width by {reduction} pixels ({args.reduction_percent}%)")
    
    # Generate frames for each strategy
    steps = np.linspace(1, reduction, num_frames, dtype=int)
    
    # 1. COLUMN - remove columns iteratively
    if not frames_exist("column", num_frames) or args.force:
        print("Generating COLUMN frames...")
        result_column = img.copy()
        
        for i, step in enumerate(steps):
            frame_path = output_dir / "column" / f"frame_{i:04d}.png"
            if frame_path.exists() and not args.force:
                # Load existing result to continue from
                if i == len(steps) - 1 or not (output_dir / "column" / f"frame_{i+1:04d}.png").exists():
                    # Need to reconstruct state - just recompute from here
                    pass
                continue
                
            target_removed = step
            current_removed = original_width - result_column.shape[1]
            to_remove = target_removed - current_removed
            
            if to_remove > 0:
                result_column = strategy_column(result_column, to_remove)
            
            padded = pad_to_width(result_column, original_width)
            Image.fromarray(padded).save(frame_path)
            
            if (i + 1) % 10 == 0:
                print(f"  Column frame {i+1}/{num_frames}")
    else:
        print("Skipping COLUMN frames (already exist)")
    
    # 2. PIXEL - remove lowest energy pixel per row
    if not frames_exist("pixel", num_frames) or args.force:
        print("Generating PIXEL frames...")
        for i, step in enumerate(steps):
            frame_path = output_dir / "pixel" / f"frame_{i:04d}.png"
            if frame_path.exists() and not args.force:
                continue
                
            result_pixel = strategy_pixel_per_row(img, step)
            padded = pad_to_width(result_pixel, original_width)
            Image.fromarray(padded).save(frame_path)
            
            if (i + 1) % 10 == 0:
                print(f"  Pixel frame {i+1}/{num_frames}")
    else:
        print("Skipping PIXEL frames (already exist)")
    
    # 3. OPTIMAL - global removal (show destruction)
    if not frames_exist("optimal", num_frames) or args.force:
        print("Generating OPTIMAL (global) frames...")
        for i, step in enumerate(steps):
            frame_path = output_dir / "optimal" / f"frame_{i:04d}.png"
            if frame_path.exists() and not args.force:
                continue
            
            # Scale the number of pixels to remove to match the visual effect
            # We remove more pixels to make the effect visible since they're scattered
            pixels_to_remove = step * original_height  # Remove proportionally more
            result_optimal = strategy_optimal_global(img, pixels_to_remove)
            Image.fromarray(result_optimal).save(frame_path)
            
            if (i + 1) % 10 == 0:
                print(f"  Optimal frame {i+1}/{num_frames}")
    else:
        print("Skipping OPTIMAL frames (already exist)")
    
    # 4. SEAM - proper seam carving
    if not frames_exist("seam", num_frames) or args.force:
        print("Generating SEAM frames...")
        result_seam = img.copy()
        
        for i, step in enumerate(steps):
            frame_path = output_dir / "seam" / f"frame_{i:04d}.png"
            if frame_path.exists() and not args.force:
                # Need to maintain state - load the frame and figure out current width
                # For simplicity, just continue computing
                pass
            
            target_removed = step
            current_removed = original_width - result_seam.shape[1]
            to_remove = target_removed - current_removed
            
            if to_remove > 0:
                result_seam = strategy_seam(result_seam, to_remove)
            
            padded = pad_to_width(result_seam, original_width)
            Image.fromarray(padded).save(frame_path)
            
            if (i + 1) % 10 == 0:
                print(f"  Seam frame {i+1}/{num_frames}")
    else:
        print("Skipping SEAM frames (already exist)")
    
    # Save final comparison images
    print("Checking final comparison images...")
    
    if not (output_dir / "final_column.png").exists() or args.force:
        print("  Computing final_column...")
        final_column = strategy_column(img.copy(), reduction)
        Image.fromarray(pad_to_width(final_column, original_width)).save(output_dir / "final_column.png")
    
    if not (output_dir / "final_pixel.png").exists() or args.force:
        print("  Computing final_pixel...")
        final_pixel = strategy_pixel_per_row(img, reduction)
        Image.fromarray(pad_to_width(final_pixel, original_width)).save(output_dir / "final_pixel.png")
    
    if not (output_dir / "final_optimal.png").exists() or args.force:
        print("  Computing final_optimal...")
        final_optimal = strategy_optimal_global(img, reduction * original_height)
        Image.fromarray(final_optimal).save(output_dir / "final_optimal.png")
    
    if not (output_dir / "final_seam.png").exists() or args.force:
        print("  Computing final_seam...")
        final_seam = strategy_seam(img.copy(), reduction)
        Image.fromarray(pad_to_width(final_seam, original_width)).save(output_dir / "final_seam.png")
    
    print(f"Done! Output saved to {output_dir}")


if __name__ == "__main__":
    main()