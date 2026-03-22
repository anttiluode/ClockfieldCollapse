#!/usr/bin/env python3
"""
CLOCKFIELD FRACTAL HORIZON: 3D Multi-Vortex Collapse
======================================================

Simulate multiple vortex strings colliding in 3D Clockfield PDE.
Extract the Γ ≈ 0 isosurface after collapse.
Measure its fractal dimension via box-counting.
Compare to Jalalzadeh et al. prediction: D_horizon = α/2 + 1.

Physics:
  Field: φ = u + iv (complex scalar), Mexican hat potential
  Clockfield: Γ(x) = 1/(1 + τ·β)², c_eff² = c₀²/(1 + τ·β)
  PDE: ∂²φ/∂t² = Γ²·[c_eff²·∇²φ + μ²φ − λ|φ|²φ] − γ·∂φ/∂t
  
  We inject multiple vortex STRINGS (lines) with different orientations
  and phases, boost them inward, and let them collide.

Requirements: torch, numpy, matplotlib, scipy (for box-counting analysis)

Usage:
  python clockfield_fractal_horizon.py [--N 64] [--tau 5.0] [--steps 3000]
                                        [--boost 1.0] [--n_vortices 6]
                                        [--device cuda]

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import argparse
import time
import json
import numpy as np
import torch
import torch.nn.functional as F


# ═══════════════════════════════════════════════════════════════════
# 3D LAPLACIAN (7-point stencil via conv3d)
# ═══════════════════════════════════════════════════════════════════

def make_laplacian_kernel(device, dtype):
    """7-point 3D Laplacian stencil as a conv3d kernel."""
    k = torch.zeros(1, 1, 3, 3, 3, device=device, dtype=dtype)
    # 6 face-neighbors minus center
    k[0, 0, 1, 1, 0] = 1.0
    k[0, 0, 1, 1, 2] = 1.0
    k[0, 0, 1, 0, 1] = 1.0
    k[0, 0, 1, 2, 1] = 1.0
    k[0, 0, 0, 1, 1] = 1.0
    k[0, 0, 2, 1, 1] = 1.0
    k[0, 0, 1, 1, 1] = -6.0
    return k


def laplacian_3d(f, kernel, dx=1.0):
    """Compute 3D Laplacian with periodic boundary conditions."""
    # f shape: (N, N, N) -> pad and conv
    # Pad with wrap (periodic BC)
    fp = f.unsqueeze(0).unsqueeze(0)  # (1, 1, N, N, N)
    # Manual periodic padding (1 cell each side)
    fp = torch.cat([fp[:, :, -1:, :, :], fp, fp[:, :, :1, :, :]], dim=2)
    fp = torch.cat([fp[:, :, :, -1:, :], fp, fp[:, :, :, :1, :]], dim=3)
    fp = torch.cat([fp[:, :, :, :, -1:], fp, fp[:, :, :, :, :1]], dim=4)
    out = F.conv3d(fp, kernel, padding=0)
    return out[0, 0] / (dx * dx)


# ═══════════════════════════════════════════════════════════════════
# VORTEX STRING INJECTION
# ═══════════════════════════════════════════════════════════════════

def inject_vortex_string(u, v, phi_eq, center, direction, charge=1, core_width=3.0):
    """
    Inject a vortex string (line defect) into the 3D field.
    
    The string runs along `direction` through `center`.
    In the plane perpendicular to the string, the field winds
    with topological charge `charge`.
    
    Parameters:
        u, v: real and imaginary parts of φ (3D tensors)
        phi_eq: vacuum amplitude
        center: (cx, cy, cz) position of the string
        direction: 'x', 'y', or 'z' — axis the string runs along
        charge: winding number (+1 or -1)
        core_width: width of the vortex core in grid units
    """
    N = u.shape[0]
    device = u.device
    dtype = u.dtype
    
    coords = torch.arange(N, device=device, dtype=dtype)
    # Create 3D coordinate grids
    gz, gy, gx = torch.meshgrid(coords, coords, coords, indexing='ij')
    
    cx, cy, cz = center
    
    if direction == 'z':
        dx_local = gx - cx
        dy_local = gy - cy
    elif direction == 'x':
        dx_local = gy - cy
        dy_local = gz - cz
    elif direction == 'y':
        dx_local = gx - cx
        dy_local = gz - cz
    else:
        raise ValueError(f"Unknown direction: {direction}")
    
    r = torch.sqrt(dx_local**2 + dy_local**2 + 1e-8)
    theta = torch.atan2(dy_local, dx_local)
    amp = phi_eq * torch.tanh(r / core_width)
    
    # Superpose (additive — works for well-separated strings)
    u += amp * torch.cos(charge * theta)
    v += amp * torch.sin(charge * theta)


def inject_vortex_string_arbitrary(u, v, phi_eq, point_on_line, axis_vec,
                                    charge=1, core_width=3.0):
    """
    Inject a vortex string along an ARBITRARY axis.
    
    `axis_vec` is the direction of the string (will be normalized).
    `point_on_line` is any point the string passes through.
    
    The winding is in the plane perpendicular to axis_vec.
    We pick two orthonormal vectors e1, e2 in that plane and
    define the winding angle from them.
    """
    N = u.shape[0]
    device = u.device
    dtype = u.dtype
    
    # Normalize axis
    ax = torch.tensor(axis_vec, device=device, dtype=dtype)
    ax = ax / torch.norm(ax)
    
    # Find two orthonormal vectors perpendicular to ax
    # Pick a vector not parallel to ax
    if abs(ax[0].item()) < 0.9:
        seed = torch.tensor([1.0, 0.0, 0.0], device=device, dtype=dtype)
    else:
        seed = torch.tensor([0.0, 1.0, 0.0], device=device, dtype=dtype)
    
    e1 = seed - torch.dot(seed, ax) * ax
    e1 = e1 / torch.norm(e1)
    e2 = torch.cross(ax, e1)
    
    # Grid coordinates
    coords = torch.arange(N, device=device, dtype=dtype)
    gz, gy, gx = torch.meshgrid(coords, coords, coords, indexing='ij')
    
    p0 = torch.tensor(point_on_line, device=device, dtype=dtype)
    
    # Displacement from point on line
    dx = gx - p0[0]
    dy = gy - p0[1]
    dz = gz - p0[2]
    
    # Project onto the perpendicular plane
    # Component along e1 and e2
    comp1 = dx * e1[0] + dy * e1[1] + dz * e1[2]
    comp2 = dx * e2[0] + dy * e2[1] + dz * e2[2]
    
    r = torch.sqrt(comp1**2 + comp2**2 + 1e-8)
    theta = torch.atan2(comp2, comp1)
    amp = phi_eq * torch.tanh(r / core_width)
    
    u += amp * torch.cos(charge * theta)
    v += amp * torch.sin(charge * theta)


# ═══════════════════════════════════════════════════════════════════
# INITIAL CONDITIONS: Multiple vortex strings aimed at center
# ═══════════════════════════════════════════════════════════════════

def setup_initial_conditions(N, phi_eq, n_vortices, boost, device, dtype):
    """
    Create n_vortices vortex strings at various orientations,
    all passing through or near the center, with inward velocity boost.
    
    Returns: u, v, u_prev, v_prev (all NxNxN tensors)
    """
    u = torch.zeros(N, N, N, device=device, dtype=dtype)
    v = torch.zeros(N, N, N, device=device, dtype=dtype)
    
    cx = N / 2.0
    offset = N / 4.0  # how far from center the strings start
    
    # Generate vortex configurations
    # Strategy: place strings at different orientations and offsets
    configs = []
    
    if n_vortices >= 1:
        # String along z, offset in x
        configs.append({
            'point': (cx - offset, cx, cx),
            'axis': (0, 0, 1),
            'charge': 1
        })
    if n_vortices >= 2:
        # String along z, offset in -x (opposite charge = anti-vortex)
        configs.append({
            'point': (cx + offset, cx, cx),
            'axis': (0, 0, 1),
            'charge': -1
        })
    if n_vortices >= 3:
        # String along x, offset in y
        configs.append({
            'point': (cx, cx - offset, cx),
            'axis': (1, 0, 0),
            'charge': 1
        })
    if n_vortices >= 4:
        # String along x, offset in -y
        configs.append({
            'point': (cx, cx + offset, cx),
            'axis': (1, 0, 0),
            'charge': -1
        })
    if n_vortices >= 5:
        # String along y, offset in z
        configs.append({
            'point': (cx, cx, cx - offset),
            'axis': (0, 1, 0),
            'charge': 1
        })
    if n_vortices >= 6:
        # String along y, offset in -z
        configs.append({
            'point': (cx, cx, cx + offset),
            'axis': (0, 1, 0),
            'charge': -1
        })
    if n_vortices >= 7:
        # Diagonal strings for extra phase complexity
        configs.append({
            'point': (cx - offset*0.7, cx - offset*0.7, cx),
            'axis': (1, 1, 0),
            'charge': 1
        })
    if n_vortices >= 8:
        configs.append({
            'point': (cx + offset*0.7, cx + offset*0.7, cx),
            'axis': (1, 1, 0),
            'charge': -1
        })
    
    # Inject all strings
    for cfg in configs:
        inject_vortex_string_arbitrary(
            u, v, phi_eq,
            point_on_line=cfg['point'],
            axis_vec=cfg['axis'],
            charge=cfg['charge'],
            core_width=3.0
        )
    
    # Create boosted initial condition (u_prev shifted inward)
    # Boost: shift each vortex's contribution toward center
    # Simple approach: u_prev = u - boost * gradient_toward_center
    coords = torch.arange(N, device=device, dtype=dtype)
    gz, gy, gx = torch.meshgrid(coords, coords, coords, indexing='ij')
    
    # Radial direction toward center
    rx = gx - cx
    ry = gy - cx
    rz = gz - cx
    r = torch.sqrt(rx**2 + ry**2 + rz**2 + 1e-8)
    
    # Inward velocity: shift field toward center
    # v_field = -boost * r_hat, implemented via:
    # u_prev ≈ u(x + boost*dt*r_hat) ≈ u + boost * (∇u · r_hat)
    # Compute gradients
    du_dx = torch.roll(u, -1, 2) - torch.roll(u, 1, 2)
    du_dy = torch.roll(u, -1, 1) - torch.roll(u, 1, 1)
    du_dz = torch.roll(u, -1, 0) - torch.roll(u, 1, 0)
    dv_dx = torch.roll(v, -1, 2) - torch.roll(v, 1, 2)
    dv_dy = torch.roll(v, -1, 1) - torch.roll(v, 1, 1)
    dv_dz = torch.roll(v, -1, 0) - torch.roll(v, 1, 0)
    
    # Radial gradient (inward)
    rhat_x = -rx / r
    rhat_y = -ry / r
    rhat_z = -rz / r
    
    u_shift = boost * (du_dx * rhat_x + du_dy * rhat_y + du_dz * rhat_z) / 2.0
    v_shift = boost * (dv_dx * rhat_x + dv_dy * rhat_y + dv_dz * rhat_z) / 2.0
    
    u_prev = u - u_shift
    v_prev = v - v_shift
    
    return u, v, u_prev, v_prev


# ═══════════════════════════════════════════════════════════════════
# PDE EVOLUTION
# ═══════════════════════════════════════════════════════════════════

def evolve_step(u, v, u_prev, v_prev, lap_kernel, tau, mu2, lam, c02, dt, dx, damping):
    """One Verlet timestep of the 3D Clockfield PDE."""
    beta = u**2 + v**2
    
    gamma = 1.0 / (1.0 + tau * beta)**2
    gamma_sq = gamma * gamma
    c_eff2 = c02 / (1.0 + tau * beta)
    
    lap_u = laplacian_3d(u, lap_kernel, dx)
    lap_v = laplacian_3d(v, lap_kernel, dx)
    
    force_u = c_eff2 * lap_u + mu2 * u - lam * beta * u
    force_v = c_eff2 * lap_v + mu2 * v - lam * beta * v
    
    u_new = 2*u - u_prev + gamma_sq * force_u * dt**2 - damping * (u - u_prev)
    v_new = 2*v - v_prev + gamma_sq * force_v * dt**2 - damping * (v - v_prev)
    
    return u_new, v_new


# ═══════════════════════════════════════════════════════════════════
# FRACTAL DIMENSION: BOX-COUNTING
# ═══════════════════════════════════════════════════════════════════

def extract_gamma_shell(beta, tau, gamma_threshold_low=0.01, gamma_threshold_high=0.1):
    """
    Extract the Γ-shell: the set of points where 
    gamma_threshold_low < Γ < gamma_threshold_high.
    
    This is the "event horizon" transition region.
    Returns a boolean mask.
    """
    gamma = 1.0 / (1.0 + tau * beta)**2
    shell = (gamma > gamma_threshold_low) & (gamma < gamma_threshold_high)
    return shell, gamma


def box_count(mask_np, box_sizes=None):
    """
    Box-counting algorithm for fractal dimension.
    
    Given a 3D boolean mask, count how many boxes of size ε 
    contain at least one True point, for various ε.
    
    Returns: list of (log(1/ε), log(N(ε))) pairs
    """
    if box_sizes is None:
        # Powers of 2 up to half the grid
        N = mask_np.shape[0]
        max_power = int(np.log2(N)) - 1
        box_sizes = [2**k for k in range(0, max_power + 1)]
    
    results = []
    for eps in box_sizes:
        if eps < 1:
            continue
        # Reshape into boxes of size eps and check if any True
        N = mask_np.shape[0]
        n_boxes_per_dim = N // eps
        if n_boxes_per_dim < 1:
            continue
        
        # Trim to exact multiple
        trimmed = mask_np[:n_boxes_per_dim*eps, :n_boxes_per_dim*eps, :n_boxes_per_dim*eps]
        
        # Reshape into boxes
        reshaped = trimmed.reshape(
            n_boxes_per_dim, eps,
            n_boxes_per_dim, eps,
            n_boxes_per_dim, eps
        )
        # Check if any point in each box is True
        box_occupied = reshaped.any(axis=(1, 3, 5))
        count = box_occupied.sum()
        
        if count > 0:
            results.append((np.log(1.0 / eps), np.log(count)))
    
    return results


def compute_fractal_dimension(mask_np):
    """
    Compute fractal dimension via box-counting with linear regression.
    Returns: D_f, r_squared, box_count_data
    """
    bc_data = box_count(mask_np)
    
    if len(bc_data) < 3:
        return None, None, bc_data
    
    x = np.array([d[0] for d in bc_data])
    y = np.array([d[1] for d in bc_data])
    
    # Linear regression: y = D_f * x + b
    # Use only the scaling region (exclude largest and smallest boxes)
    if len(x) > 4:
        x_fit = x[1:-1]
        y_fit = y[1:-1]
    else:
        x_fit = x
        y_fit = y
    
    if len(x_fit) < 2:
        return None, None, bc_data
    
    coeffs = np.polyfit(x_fit, y_fit, 1)
    D_f = coeffs[0]
    
    # R-squared
    y_pred = np.polyval(coeffs, x_fit)
    ss_res = np.sum((y_fit - y_pred)**2)
    ss_tot = np.sum((y_fit - np.mean(y_fit))**2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    return D_f, r_sq, bc_data


def compute_fractal_dimension_multi_threshold(beta_np, tau, n_thresholds=5):
    """
    Compute fractal dimension at multiple Γ-shell threshold levels.
    This gives a more robust estimate and shows how D_f varies 
    across the shell.
    """
    gamma_np = 1.0 / (1.0 + tau * beta_np)**2
    
    # Define threshold pairs spanning the shell
    # From deeply frozen to almost vacuum
    gamma_min = gamma_np.min()
    gamma_max_shell = min(0.5, gamma_np.max() * 0.5)
    
    if gamma_min >= gamma_max_shell:
        print("  No significant Γ gradient found — no collapse occurred.")
        return []
    
    results = []
    
    # Isosurface approach: for each threshold γ*, count points where |Γ - γ*| < δ
    thresholds = np.linspace(gamma_min * 2, gamma_max_shell, n_thresholds)
    
    for gamma_star in thresholds:
        delta = max(0.005, gamma_star * 0.3)  # shell thickness
        shell_mask = (np.abs(gamma_np - gamma_star) < delta)
        
        n_points = shell_mask.sum()
        if n_points < 50:
            continue
        
        D_f, r_sq, bc_data = compute_fractal_dimension(shell_mask)
        
        if D_f is not None:
            results.append({
                'gamma_threshold': float(gamma_star),
                'delta': float(delta),
                'n_shell_points': int(n_points),
                'D_f': float(D_f),
                'r_squared': float(r_sq),
                'box_count_data': [(float(a), float(b)) for a, b in bc_data]
            })
    
    return results


# ═══════════════════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════

def compute_diagnostics(u, v, tau):
    """Compute key diagnostic quantities."""
    beta = u**2 + v**2
    gamma = 1.0 / (1.0 + tau * beta)**2
    
    beta_max = beta.max().item()
    beta_mean = beta.mean().item()
    gamma_min = gamma.min().item()
    gamma_mean = gamma.mean().item()
    
    # Count frozen points (Γ < 0.01)
    n_frozen = (gamma < 0.01).sum().item()
    n_total = gamma.numel()
    
    return {
        'beta_max': beta_max,
        'beta_mean': beta_mean,
        'gamma_min': gamma_min,
        'gamma_mean': gamma_mean,
        'frozen_fraction': n_frozen / n_total,
        'n_frozen': n_frozen
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN SIMULATION
# ═══════════════════════════════════════════════════════════════════

def run_simulation(args):
    print("=" * 70)
    print("CLOCKFIELD FRACTAL HORIZON — 3D Multi-Vortex Collapse")
    print("=" * 70)
    
    # Setup
    device = torch.device(args.device if torch.cuda.is_available() or args.device == 'cpu' else 'cpu')
    dtype = torch.float32  # float32 for GPU speed; use float64 for precision
    
    N = args.N
    tau = args.tau
    mu2 = args.mu2
    lam = args.lam
    c02 = args.c02
    dt = args.dt
    dx = args.dx
    damping = args.damping
    
    phi_eq = np.sqrt(mu2 / lam)
    beta_eq = mu2 / lam
    gamma_vac = 1.0 / (1.0 + tau * beta_eq)**2
    
    print(f"\nGrid: {N}³ = {N**3:,} points")
    print(f"Device: {device}")
    print(f"Parameters: τ={tau}, μ²={mu2}, λ={lam}, c₀²={c02}")
    print(f"Vacuum: φ_eq={phi_eq:.4f}, β_eq={beta_eq:.4f}, Γ_vac={gamma_vac:.6f}")
    print(f"Vortices: {args.n_vortices}, boost: {args.boost}")
    print(f"Steps: {args.steps}, dt={dt}")
    
    # Memory estimate
    mem_per_field = N**3 * 4 / 1e9  # GB for float32
    n_fields = 6  # u, v, u_prev, v_prev, + workspace
    print(f"Estimated GPU memory: {n_fields * mem_per_field:.2f} GB")
    
    # Create Laplacian kernel
    lap_kernel = make_laplacian_kernel(device, dtype)
    
    # Initial conditions
    print(f"\nInjecting {args.n_vortices} vortex strings...")
    u, v, u_prev, v_prev = setup_initial_conditions(
        N, phi_eq, args.n_vortices, args.boost, device, dtype
    )
    
    diag = compute_diagnostics(u, v, tau)
    print(f"Initial: β_max={diag['beta_max']:.2f}, Γ_min={diag['gamma_min']:.6f}")
    
    # ─── Evolution ───
    print(f"\nEvolving {args.steps} steps...")
    history = []
    t_start = time.time()
    
    for step in range(args.steps):
        u_new, v_new = evolve_step(
            u, v, u_prev, v_prev, lap_kernel,
            tau, mu2, lam, c02, dt, dx, damping
        )
        u_prev = u
        v_prev = v
        u = u_new
        v = v_new
        
        # Periodic diagnostics
        if (step + 1) % args.diag_interval == 0 or step == 0:
            diag = compute_diagnostics(u, v, tau)
            diag['step'] = step + 1
            diag['time'] = (step + 1) * dt
            history.append(diag)
            
            elapsed = time.time() - t_start
            steps_per_sec = (step + 1) / elapsed
            eta = (args.steps - step - 1) / steps_per_sec if steps_per_sec > 0 else 0
            
            print(f"  Step {step+1:5d}/{args.steps}: "
                  f"β_max={diag['beta_max']:.1f}, "
                  f"Γ_min={diag['gamma_min']:.2e}, "
                  f"frozen={diag['frozen_fraction']*100:.1f}%, "
                  f"[{steps_per_sec:.1f} steps/s, ETA {eta:.0f}s]")
            
            # Check for blowup
            if np.isnan(diag['beta_max']) or diag['beta_max'] > 1e12:
                print("  *** BLOWUP detected — reducing dt or increasing damping ***")
                break
    
    total_time = time.time() - t_start
    print(f"\nSimulation complete: {total_time:.1f}s ({args.steps/total_time:.1f} steps/s)")
    
    # ─── Final diagnostics ───
    final_diag = compute_diagnostics(u, v, tau)
    print(f"\nFinal state:")
    print(f"  β_max = {final_diag['beta_max']:.2f}")
    print(f"  Γ_min = {final_diag['gamma_min']:.2e}")
    print(f"  Frozen fraction = {final_diag['frozen_fraction']*100:.2f}%")
    
    # Determine if collapse occurred
    collapsed = final_diag['gamma_min'] < 1e-4
    if not collapsed:
        print("\n  *** No significant collapse detected. ***")
        print("  Try: increasing --boost, --tau, or --n_vortices")
    
    # ─── Fractal dimension measurement ───
    print("\n" + "=" * 70)
    print("FRACTAL DIMENSION ANALYSIS")
    print("=" * 70)
    
    beta_final = (u**2 + v**2).cpu().numpy()
    
    # Multi-threshold analysis
    fractal_results = compute_fractal_dimension_multi_threshold(
        beta_final, tau, n_thresholds=8
    )
    
    if fractal_results:
        print(f"\n{'Γ_threshold':>12s} {'δ':>8s} {'N_points':>10s} {'D_f':>8s} {'R²':>8s}")
        print("-" * 52)
        
        D_f_values = []
        for fr in fractal_results:
            print(f"  {fr['gamma_threshold']:10.4f}  {fr['delta']:8.4f}  "
                  f"{fr['n_shell_points']:10d}  {fr['D_f']:8.4f}  {fr['r_squared']:8.4f}")
            if fr['r_squared'] > 0.95:  # Only trust good fits
                D_f_values.append(fr['D_f'])
        
        if D_f_values:
            D_f_mean = np.mean(D_f_values)
            D_f_std = np.std(D_f_values)
            print(f"\n  Mean D_f (R² > 0.95): {D_f_mean:.4f} ± {D_f_std:.4f}")
            
            # Compare to Jalalzadeh prediction
            # Their D_horizon = α/2 + 1 where D_spacetime = α/2 + 3
            # For standard case α=2: D_horizon = 2 (smooth sphere)
            # For fractional: D_horizon < 2
            print(f"\n  Jalalzadeh comparison:")
            print(f"    If D_f = α/2 + 1, then α = {2*(D_f_mean - 1):.4f}")
            print(f"    Spacetime dimension D = α/2 + 3 = {D_f_mean + 2:.4f}")
            print(f"    Standard case (smooth): D_f = 2.0, α = 2, D = 4")
            
            # What does the Clockfield predict for τβ₀ ↔ α mapping?
            print(f"\n  Clockfield context:")
            print(f"    τβ_eq = {tau * beta_eq:.4f}")
            print(f"    Γ_vac = {gamma_vac:.6f}")
            print(f"    Measured horizon D_f = {D_f_mean:.4f}")
            
            if D_f_mean < 2.0:
                print(f"    → Horizon IS fractal (D_f < 2)")
                print(f"    → Fractal deficit: 2 - D_f = {2 - D_f_mean:.4f}")
            else:
                print(f"    → Horizon appears smooth within measurement precision")
        else:
            print("\n  No reliable fractal dimension estimates (all R² < 0.95)")
    else:
        print("\n  Could not extract Γ-shell for fractal analysis.")
        print("  The collapse may not have produced a clear shell structure.")
    
    # ─── Also measure the Γ-gradient at the shell (Hawking temperature proxy) ───
    print("\n" + "-" * 70)
    print("Γ-GRADIENT AT SHELL (Hawking temperature proxy)")
    print("-" * 70)
    
    gamma_final = 1.0 / (1.0 + tau * beta_final)**2
    
    # Compute |∇Γ|
    grad_gx = np.roll(gamma_final, -1, axis=2) - np.roll(gamma_final, 1, axis=2)
    grad_gy = np.roll(gamma_final, -1, axis=1) - np.roll(gamma_final, 1, axis=1)
    grad_gz = np.roll(gamma_final, -1, axis=0) - np.roll(gamma_final, 1, axis=0)
    grad_mag = np.sqrt(grad_gx**2 + grad_gy**2 + grad_gz**2) / (2 * dx)
    
    # Find max gradient (this is the "surface gravity" / temperature proxy)
    max_grad = grad_mag.max()
    # Where is it?
    max_loc = np.unravel_index(grad_mag.argmax(), grad_mag.shape)
    gamma_at_max_grad = gamma_final[max_loc]
    beta_at_max_grad = beta_final[max_loc]
    
    print(f"  Max |∇Γ| = {max_grad:.6f} at {max_loc}")
    print(f"  Γ at max gradient: {gamma_at_max_grad:.6f}")
    print(f"  β at max gradient: {beta_at_max_grad:.2f}")
    print(f"  T_Hawking ∝ |∇Γ|_shell ∝ 1/M")
    
    # ─── Save results ───
    output = {
        'params': {
            'N': N, 'tau': tau, 'mu2': mu2, 'lam': lam,
            'c02': c02, 'dt': dt, 'dx': dx, 'damping': damping,
            'n_vortices': args.n_vortices, 'boost': args.boost,
            'steps': args.steps
        },
        'vacuum': {
            'phi_eq': float(phi_eq),
            'beta_eq': float(beta_eq),
            'gamma_vac': float(gamma_vac)
        },
        'final_state': {
            'beta_max': float(final_diag['beta_max']),
            'gamma_min': float(final_diag['gamma_min']),
            'frozen_fraction': float(final_diag['frozen_fraction']),
            'collapsed': collapsed
        },
        'fractal_analysis': fractal_results,
        'hawking_proxy': {
            'max_grad_gamma': float(max_grad),
            'gamma_at_shell': float(gamma_at_max_grad),
            'beta_at_shell': float(beta_at_max_grad)
        },
        'history': history,
        'runtime_seconds': total_time
    }
    
    # Mean fractal dimension
    if fractal_results:
        good_Df = [fr['D_f'] for fr in fractal_results if fr['r_squared'] > 0.95]
        if good_Df:
            output['fractal_summary'] = {
                'D_f_mean': float(np.mean(good_Df)),
                'D_f_std': float(np.std(good_Df)),
                'n_good_fits': len(good_Df),
                'implied_alpha': float(2 * (np.mean(good_Df) - 1)),
                'implied_D_spacetime': float(np.mean(good_Df) + 2)
            }
    
    outfile = args.output
    with open(outfile, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outfile}")
    
    # ─── Save the Γ field for external visualization ───
    if args.save_field:
        field_file = outfile.replace('.json', '_gamma.npy')
        np.save(field_file, gamma_final)
        print(f"Γ field saved: {field_file}")
        
        beta_file = outfile.replace('.json', '_beta.npy')
        np.save(beta_file, beta_final)
        print(f"β field saved: {beta_file}")
    
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    
    return output


# ═══════════════════════════════════════════════════════════════════
# PARAMETER SCAN: tau vs fractal dimension
# ═══════════════════════════════════════════════════════════════════

def run_tau_scan(args):
    """
    Run the simulation at multiple τ values to map τβ₀ → D_f.
    This is the key experiment: does the Clockfield coupling 
    control the fractal dimension of the horizon?
    """
    print("=" * 70)
    print("τ-SCAN: Mapping Clockfield coupling to fractal dimension")
    print("=" * 70)
    
    tau_values = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0]
    scan_results = []
    
    for tau_val in tau_values:
        print(f"\n{'─'*70}")
        print(f"τ = {tau_val}")
        print(f"{'─'*70}")
        
        args.tau = tau_val
        args.output = f"fractal_horizon_tau{tau_val:.0f}.json"
        
        result = run_simulation(args)
        
        summary = {
            'tau': tau_val,
            'tau_beta0': tau_val * args.mu2 / args.lam,
            'gamma_vac': 1.0 / (1.0 + tau_val * args.mu2 / args.lam)**2,
            'collapsed': result['final_state']['collapsed'],
            'beta_max': result['final_state']['beta_max'],
            'gamma_min': result['final_state']['gamma_min'],
        }
        
        if 'fractal_summary' in result:
            summary['D_f'] = result['fractal_summary']['D_f_mean']
            summary['D_f_std'] = result['fractal_summary']['D_f_std']
            summary['implied_alpha'] = result['fractal_summary']['implied_alpha']
        
        scan_results.append(summary)
    
    # Summary table
    print("\n" + "=" * 70)
    print("τ-SCAN SUMMARY")
    print("=" * 70)
    print(f"\n{'τ':>6s} {'τβ₀':>8s} {'Γ_vac':>10s} {'Collapsed':>10s} "
          f"{'D_f':>8s} {'±':>6s} {'α_implied':>10s}")
    print("-" * 65)
    
    for s in scan_results:
        D_f_str = f"{s['D_f']:.4f}" if 'D_f' in s else "N/A"
        std_str = f"{s['D_f_std']:.4f}" if 'D_f_std' in s else ""
        alpha_str = f"{s['implied_alpha']:.4f}" if 'implied_alpha' in s else ""
        print(f"  {s['tau']:4.1f}  {s['tau_beta0']:8.3f}  {s['gamma_vac']:10.6f}  "
              f"{'YES' if s['collapsed'] else 'no':>10s}  "
              f"{D_f_str:>8s}  {std_str:>6s}  {alpha_str:>10s}")
    
    with open("fractal_horizon_tau_scan.json", "w") as f:
        json.dump(scan_results, f, indent=2)
    print(f"\nScan results saved: fractal_horizon_tau_scan.json")


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clockfield Fractal Horizon: 3D collapse + fractal dimension"
    )
    
    # Grid
    parser.add_argument('--N', type=int, default=64,
                        help='Grid size N³ (default: 64; use 96-128 for publication)')
    
    # Physics
    parser.add_argument('--tau', type=float, default=5.0, help='Clockfield coupling τ')
    parser.add_argument('--mu2', type=float, default=1.4, help='Mexican hat μ²')
    parser.add_argument('--lam', type=float, default=0.55, help='Mexican hat λ')
    parser.add_argument('--c02', type=float, default=1.0, help='Base speed c₀²')
    parser.add_argument('--dt', type=float, default=0.015, help='Timestep')
    parser.add_argument('--dx', type=float, default=1.0, help='Grid spacing')
    parser.add_argument('--damping', type=float, default=0.003, help='Damping coefficient')
    
    # Vortex configuration
    parser.add_argument('--n_vortices', type=int, default=6,
                        help='Number of vortex strings (2-8)')
    parser.add_argument('--boost', type=float, default=1.0,
                        help='Inward velocity boost (0=no boost, 1=moderate, 2+=aggressive)')
    
    # Simulation
    parser.add_argument('--steps', type=int, default=3000, help='Number of timesteps')
    parser.add_argument('--diag_interval', type=int, default=100,
                        help='Steps between diagnostic printouts')
    
    # Output
    parser.add_argument('--output', type=str, default='fractal_horizon_results.json',
                        help='Output JSON file')
    parser.add_argument('--save_field', action='store_true',
                        help='Save final Γ and β fields as .npy')
    
    # Device
    parser.add_argument('--device', type=str, default='cuda',
                        help='torch device (cuda or cpu)')
    
    # Mode
    parser.add_argument('--tau_scan', action='store_true',
                        help='Run τ-parameter scan instead of single simulation')
    
    args = parser.parse_args()
    
    if args.tau_scan:
        run_tau_scan(args)
    else:
        run_simulation(args)