#!/usr/bin/env python3
"""
CLOCKFIELD AdS THROAT TEST
============================
Inject a vortex, let it stabilize, extract radial beta(r),
compute Gamma(r) and the effective Ricci scalar R(r).

The prediction: R < 0 in the annular region around the core
(the frozen-time shell generates AdS-like geometry).

Usage: python ads_throat_test.py

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import numpy as np
import json

N = 256
mu2, lam, c02, dt, dx, tau, damping = 1.4, 0.55, 1.0, 0.02, 1.0, 5.0, 0.005
phi_eq = np.sqrt(mu2 / lam)
beta_eq = mu2 / lam

print("=" * 70)
print("CLOCKFIELD AdS THROAT TEST")
print("=" * 70)
print(f"Grid: {N}x{N}, tau={tau}, Gamma_vac={1/(1+tau*beta_eq)**2:.6f}")

# Init vortex
u = np.zeros((N, N)); v = np.zeros((N, N))
cx, cy = N//2, N//2
for y in range(N):
    for x in range(N):
        r = np.sqrt((x-cx)**2 + (y-cy)**2)
        theta = np.arctan2(y-cy, x-cx)
        amp = phi_eq * np.tanh(r / 3.0)
        u[y,x] = amp * np.cos(theta)
        v[y,x] = amp * np.sin(theta)
u_prev = u.copy(); v_prev = v.copy()

def lap(f):
    return (np.roll(f,1,0)+np.roll(f,-1,0)+np.roll(f,1,1)+np.roll(f,-1,1)-4*f)/(dx*dx)

# Evolve
print("Evolving 3000 steps...")
for i in range(3000):
    beta = u**2 + v**2
    g = 1.0/(1.0+tau*beta)**2
    g2 = g**2
    ce = c02/(1.0+tau*beta)
    fu = ce*lap(u) + mu2*u - lam*beta*u
    fv = ce*lap(v) + mu2*v - lam*beta*v
    un = 2*u - u_prev + g2*fu*dt**2 - damping*(u-u_prev)
    vn = 2*v - v_prev + g2*fv*dt**2 - damping*(v-v_prev)
    u_prev[:]=u; v_prev[:]=v; u[:]=un; v[:]=vn
    if (i+1)%1000==0:
        print(f"  Step {i+1}: min(Gamma)={(1/(1+tau*(u**2+v**2))**2).min():.8f}")

# Radial profile
beta_field = u**2 + v**2
yy, xx = np.mgrid[0:N, 0:N]
r_field = np.sqrt((xx-cx)**2 + (yy-cy)**2)
max_r = N//2 - 1
beta_r = np.zeros(max_r); count_r = np.zeros(max_r)
for y in range(N):
    for x in range(N):
        r = int(round(r_field[y,x]))
        if 0 <= r < max_r:
            beta_r[r] += beta_field[y,x]; count_r[r] += 1
m = count_r > 0
beta_r[m] /= count_r[m]

# Curvature
gamma_r = 1.0/(1.0+tau*beta_r)**2
f_r = gamma_r**2
fp = np.zeros_like(f_r); fpp = np.zeros_like(f_r)
for i in range(1, len(f_r)-1):
    fp[i] = (f_r[i+1]-f_r[i-1])/(2*dx)
    fpp[i] = (f_r[i+1]-2*f_r[i]+f_r[i-1])/(dx**2)
R_r = np.zeros_like(f_r)
for i in range(2, len(f_r)-1):
    R_r[i] = -fpp[i] - (2.0/i)*fp[i]

# Report
ring_r = np.argmax(beta_r[2:]) + 2
r_end = min(ring_r+10, len(R_r)-2)
region = R_r[2:r_end]
neg = np.sum(region < 0)

print(f"\n{'='*70}")
print(f"RESULT: R < 0 in {neg}/{len(region)} annular points")
print(f"Peak R = {region.min():.2e} at r = {np.argmin(region)+2}")
print(f"Gamma at ring: {gamma_r[ring_r]:.8f}")
print(f"Hierarchy Gamma^2 = {gamma_r[ring_r]**2:.2e}")
print(f"{'AdS THROAT CONFIRMED' if neg > len(region)*0.3 else 'Not confirmed'}")
print(f"{'='*70}")

with open("ads_throat_profile.json", "w") as f:
    json.dump({"r": list(range(max_r)), "beta": beta_r[:max_r].tolist(),
               "gamma": gamma_r[:max_r].tolist(), "R": R_r[:max_r].tolist()}, f, indent=2)
print("\nSaved: ads_throat_profile.json")
