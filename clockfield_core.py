#!/usr/bin/env python3
"""
CLOCKFIELD CORE: Minimal 2D Simulation
========================================
The complete Clockfield PDE in ~100 lines.

Physics:
  Field: φ = u + iv, Mexican hat potential V = -μ²|φ|² + λ|φ|⁴
  Clockfield metric: Γ(x) = 1/(1 + τ·β)²  where β = |φ|²
  Effective speed: c_eff² = c₀²/(1 + τ·β)
  Verlet integration with Γ²-modulated timestep

What it demonstrates:
  - Inject a vortex (topological defect)
  - Watch Γ freeze at the core
  - Extract the radial β(r) and Γ(r) profiles
  - Compute the effective Ricci scalar R(r)

Usage: python clockfield_core.py

Antti Luode / PerceptionLab, March 2026
"""

import numpy as np
import json

# Parameters
N       = 256
mu2     = 1.4
lam     = 0.55
c02     = 1.0
dt      = 0.02
dx      = 1.0
tau     = 5.0
damping = 0.005

phi_eq  = np.sqrt(mu2 / lam)
beta_eq = mu2 / lam

print(f"Clockfield Core: {N}x{N} grid, tau={tau}")
print(f"Vacuum: phi_eq={phi_eq:.4f}, beta_eq={beta_eq:.4f}, Gamma_vac={1/(1+tau*beta_eq)**2:.6f}")

# Field arrays
u = np.zeros((N, N), dtype=np.float64)
v = np.zeros((N, N), dtype=np.float64)
u_prev = np.zeros((N, N), dtype=np.float64)
v_prev = np.zeros((N, N), dtype=np.float64)

# Inject single n=1 vortex at center
cx, cy = N // 2, N // 2
for y in range(N):
    for x in range(N):
        r = np.sqrt((x - cx)**2 + (y - cy)**2)
        theta = np.arctan2(y - cy, x - cx)
        amp = phi_eq * np.tanh(r / 3.0)
        u[y, x] = amp * np.cos(theta)
        v[y, x] = amp * np.sin(theta)

u_prev[:] = u
v_prev[:] = v

def laplacian(f):
    return (np.roll(f, 1, 0) + np.roll(f, -1, 0) +
            np.roll(f, 1, 1) + np.roll(f, -1, 1) - 4*f) / (dx*dx)

# Evolve
N_STEPS = 3000
print(f"Evolving {N_STEPS} steps...")
for i in range(N_STEPS):
    lap_u = laplacian(u)
    lap_v = laplacian(v)
    beta = u**2 + v**2
    gamma_factor = 1.0 / (1.0 + tau * beta)**2
    gamma_sq = gamma_factor ** 2
    ceff2 = c02 / (1.0 + tau * beta)
    force_u = ceff2 * lap_u + mu2 * u - lam * beta * u
    force_v = ceff2 * lap_v + mu2 * v - lam * beta * v
    u_next = 2*u - u_prev + gamma_sq * force_u * dt**2 - damping*(u - u_prev)
    v_next = 2*v - v_prev + gamma_sq * force_v * dt**2 - damping*(v - v_prev)
    u_prev[:] = u; v_prev[:] = v
    u[:] = u_next; v[:] = v_next
    if (i+1) % 500 == 0:
        min_g = (1.0 / (1.0 + tau * (u**2+v**2))**2).min()
        print(f"  Step {i+1}: min(Gamma) = {min_g:.8f}")

# Extract radial profile
print("\nExtracting radial profile...")
beta_field = u**2 + v**2
yy, xx = np.mgrid[0:N, 0:N]
r_field = np.sqrt((xx - cx)**2 + (yy - cy)**2)

max_r = N // 2 - 1
beta_r = np.zeros(max_r)
count_r = np.zeros(max_r)
for y in range(N):
    for x in range(N):
        r = int(round(r_field[y, x]))
        if 0 <= r < max_r:
            beta_r[r] += beta_field[y, x]
            count_r[r] += 1

mask = count_r > 0
beta_r[mask] /= count_r[mask]

# Compute Gamma(r), f(r) = Gamma^2, Ricci scalar
gamma_r = 1.0 / (1.0 + tau * beta_r)**2
f_r = gamma_r ** 2

f_prime = np.zeros_like(f_r)
f_dprime = np.zeros_like(f_r)
for i in range(1, len(f_r) - 1):
    f_prime[i] = (f_r[i+1] - f_r[i-1]) / (2*dx)
    f_dprime[i] = (f_r[i+1] - 2*f_r[i] + f_r[i-1]) / (dx**2)

R_r = np.zeros_like(f_r)
for i in range(2, len(f_r) - 1):
    R_r[i] = -f_dprime[i] - (2.0 / i) * f_prime[i]

# Results
ring_r = np.argmax(beta_r[2:]) + 2
R_region = R_r[2:ring_r+10]
R_negative = np.sum(R_region < 0)

print(f"\nRESULTS:")
print(f"  Frozen ring at r = {ring_r}")
print(f"  Gamma at ring: {gamma_r[ring_r]:.8f}")
print(f"  Ricci R < 0 in {R_negative}/{len(R_region)} annular points")
print(f"  Peak R = {R_region.min():.2e} at r = {np.argmin(R_region)+2}")
print(f"  -> {'AdS THROAT CONFIRMED' if R_negative > len(R_region)*0.3 else 'AdS throat not confirmed'}")

G_ring = gamma_r[ring_r]
print(f"\n  Hierarchy: Gamma^2 = {G_ring**2:.2e} ({abs(np.log10(G_ring**2)):.1f} orders)")

output = {
    "r": list(range(max_r)),
    "beta": beta_r[:max_r].tolist(),
    "gamma": gamma_r[:max_r].tolist(),
    "R": R_r[:max_r].tolist(),
    "params": {"N": N, "tau": tau, "mu2": mu2, "lambda": lam}
}
with open("clockfield_core_profile.json", "w") as f:
    json.dump(output, f, indent=2)

print("\nSaved: clockfield_core_profile.json")
print("Done.")
