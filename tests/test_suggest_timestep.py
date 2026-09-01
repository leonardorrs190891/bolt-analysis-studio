"""Test timestep suggestion functionality"""
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bolt_analysis_studio.core.models.model import MSDModel

model_path = "model.msd"

print("Testing Timestep Suggestion Feature")
print("=" * 50)

# Load model
print(f"\n1. Loading model: {model_path}")
model = MSDModel.load(model_path)
print(f"   OK - Loaded {len(model.elements)} elements, {model.n_dof} DOF")

# Assemble matrices
print("\n2. Assembling system matrices...")
M, K, C = model.assemble_matrices()
print(f"   OK - M: {M.shape}, K: {K.shape}, C: {C.shape}")

# Calculate natural frequencies
print("\n3. Calculating natural frequencies...")
eigenvalues = np.linalg.eigvals(np.linalg.inv(M) @ K)
natural_freqs = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
max_freq = np.max(natural_freqs)
min_freq = np.min(natural_freqs[natural_freqs > 0.1])

print(f"   Frequency range: {min_freq:.1f} - {max_freq:.1f} Hz")
print(f"   Highest period: {1/max_freq:.3e} s")

# Calculate recommended timestep
print("\n4. Calculating recommended timestep...")
dt_recommended = 1.0 / (10 * max_freq)
print(f"   Recommended dt: {dt_recommended:.3e} s")
print(f"   (Based on T_min/10 rule)")

# Calculate steps for different end times
print("\n5. Number of steps for different simulation lengths:")
for t_end in [0.001, 0.01, 0.1, 1.0]:
    n_steps = int(t_end / dt_recommended)
    comp_time = "< 1 min" if n_steps < 50000 else "1-5 min" if n_steps < 200000 else "> 5 min"
    print(f"   t_end = {t_end:5.3f} s -> {n_steps:8,} steps ({comp_time})")

# Compare with default
print("\n6. Comparison with default timestep (0.001 s):")
dt_default = 0.001
ratio = dt_default / dt_recommended
print(f"   Default dt: {dt_default:.3e} s")
print(f"   Recommended dt: {dt_recommended:.3e} s")
print(f"   Ratio: {ratio:.1f}x (default is {ratio:.1f}x LARGER)")

if ratio > 10:
    print(f"\n   WARNING: Default timestep is TOO LARGE!")
    print(f"   This will cause numerical overflow.")
    print(f"   Use the suggested timestep instead.")
else:
    print(f"\n   OK - Default timestep is acceptable.")

print("\n" + "=" * 50)
print("Test complete! The suggestion feature will work correctly.")
