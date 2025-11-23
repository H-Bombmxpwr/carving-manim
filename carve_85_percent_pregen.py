"""
Pregenerate seam carving frames for animation.
Run this script once to generate all intermediate frames.
Save to: src/seamcarving_manim/assets/images/memory_carved/
"""

import numpy as np
from PIL import Image
from pathlib import Path
import seam_carving

def generate_frames():
    # Setup paths
    base_path = Path("src/seamcarving_manim/assets/images")
    img_path = base_path / "memory.jpg"
    output_dir = base_path / "memory_carved"
    output_dir.mkdir(exist_ok=True)
    
    # Load original image
    print(f"Loading image from {img_path}...")
    img_original = np.array(Image.open(img_path).convert("RGB"), dtype=np.uint8)
    original_h, original_w = img_original.shape[:2]
    
    # Save original as frame 0
    Image.fromarray(img_original).save(output_dir / "frame_000.jpg", quality=95)
    print(f"Saved frame_000.jpg (original: {original_w}x{original_h})")
    
    # Parameters
    fx = 0.85  # 15% reduction
    target_w = int(original_w * fx)
    seams_to_remove = original_w - target_w
    
    # Generate 60 intermediate frames
    num_frames = 60
    
    print(f"\nGenerating {num_frames} frames...")
    print(f"Original width: {original_w}")
    print(f"Target width: {target_w}")
    print(f"Seams to remove: {seams_to_remove}\n")
    
    for i in range(1, num_frames + 1):
        # Calculate target width for this frame
        progress = i / num_frames
        current_target_w = int(original_w - (seams_to_remove * progress))
        
        print(f"Frame {i:02d}/{num_frames}: Carving to width {current_target_w}...", end=" ")
        
        # Seam carve to target width
        carved_img = seam_carving.resize(
            img_original, 
            (current_target_w, original_h),
            energy_mode='backward',
            order='width-first'
        )
        
        # Save frame
        frame_filename = f"frame_{i:03d}.jpg"
        Image.fromarray(carved_img).save(output_dir / frame_filename, quality=95)
        print(f"✓ Saved {frame_filename}")
    
    print(f"\n✅ Successfully generated {num_frames + 1} frames in {output_dir}")
    print(f"Total size reduction: {original_w} → {target_w} pixels ({(1-fx)*100:.0f}% reduction)")

if __name__ == "__main__":
    generate_frames()