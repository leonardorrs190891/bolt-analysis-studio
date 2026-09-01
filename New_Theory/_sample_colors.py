"""Amostra cores únicas dos JPEGs para identificar as curvas."""
from pathlib import Path
import numpy as np
from PIL import Image

here = Path(__file__).resolve().parent

for fname in ("Carga_x_espacamento.jpeg", "deformação_parafuso_x_carga.jpeg"):
    img = np.array(Image.open(here / fname).convert("RGB"))
    H, W, _ = img.shape
    print(f"\n=== {fname} ({W}x{H}) ===")
    # crop center plot area to skip legend/axes
    crop = img[int(H*0.15):int(H*0.85), int(W*0.15):int(W*0.95)]
    # count unique non-white, non-black pixels (saturated colors)
    pixels = crop.reshape(-1, 3)
    # filter: pixel must be saturated (not greyscale)
    saturated = pixels[
        (pixels.max(axis=1) - pixels.min(axis=1) > 50) &  # any color saturation
        (pixels.max(axis=1) > 50) &                        # not very dark
        (pixels.min(axis=1) < 250)                         # not very light
    ]
    # quantize to nearest 16 for binning
    q = (saturated // 32) * 32
    # count
    unique, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)
    for i in order[:12]:
        r, g, b = unique[i]
        print(f"  RGB({r:3d},{g:3d},{b:3d})  count={counts[i]}")
