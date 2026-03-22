#!/usr/bin/env python3
"""
CLOCKFIELD FRACTAL HORIZON — Complete Experiment
==================================================

All-in-one: simulate → extract isosurface → measure fractal D_f + topology
→ track evolution over time → τ-scan → answer: is the fractal permanent?

THREE EXPERIMENTS in one script:

  1. SINGLE RUN with time-tracking:
     python clockfield_horizon_complete.py --N 64 --tau 5 --steps 5000 --boost 1.0
     
     Snapshots the Γ-field at intervals, extracts isosurfaces,
     measures D_f and genus over time. Answers: does genus→0 or freeze in?

  2. TAU SCAN:
     python clockfield_horizon_complete.py --mode tau_scan --N 64 --steps 3000
     
     Sweeps τ = [0.5, 1, 2, 3, 5, 7, 10, 15], measures D_f(τ).

  3. LONG-EVOLUTION TEST:
     python clockfield_horizon_complete.py --mode long_run --N 64 --tau 5 --steps 15000
     
     Runs 15k steps, tracks topology every 500 steps. 
     The definitive test: permanent fractal or transient?

Requires: torch, numpy, scikit-image
Optional: matplotlib (for plots)

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import argparse
import time
import json
import sys
import numpy as np
import torch
import torch.nn.functional as F

try:
    from skimage import measure
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False
    print("WARNING: pip install scikit-image  (required for isosurface extraction)")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ═══════════════════════════════════════════════════════════════════
# CLOCKFIELD PDE ENGINE (PyTorch, GPU)
# ═══════════════════════════════════════════════════════════════════

def make_lap_kernel(device, dtype):
    k = torch.zeros(1, 1, 3, 3, 3, device=device, dtype=dtype)
    k[0, 0, 1, 1, 0] = 1; k[0, 0, 1, 1, 2] = 1
    k[0, 0, 1, 0, 1] = 1; k[0, 0, 1, 2, 1] = 1
    k[0, 0, 0, 1, 1] = 1; k[0, 0, 2, 1, 1] = 1
    k[0, 0, 1, 1, 1] = -6
    return k


def lap3d(f, kernel, dx=1.0):
    fp = f.unsqueeze(0).unsqueeze(0)
    fp = torch.cat([fp[:,:,-1:,:,:], fp, fp[:,:,:1,:,:]], dim=2)
    fp = torch.cat([fp[:,:,:,-1:,:], fp, fp[:,:,:,:1,:]], dim=3)
    fp = torch.cat([fp[:,:,:,:,-1:], fp, fp[:,:,:,:,:1]], dim=4)
    return F.conv3d(fp, kernel, padding=0)[0, 0] / (dx * dx)


def inject_vortex(u, v, phi_eq, point, axis_vec, charge=1, core_w=3.0):
    N = u.shape[0]; dev = u.device; dt = u.dtype
    ax = torch.tensor(axis_vec, device=dev, dtype=dt)
    ax = ax / torch.norm(ax)
    seed = torch.tensor([1.,0.,0.], device=dev, dtype=dt) if abs(ax[0].item()) < 0.9 \
           else torch.tensor([0.,1.,0.], device=dev, dtype=dt)
    e1 = seed - torch.dot(seed, ax) * ax
    e1 = e1 / torch.norm(e1)
    e2 = torch.linalg.cross(ax, e1)
    coords = torch.arange(N, device=dev, dtype=dt)
    gz, gy, gx = torch.meshgrid(coords, coords, coords, indexing='ij')
    p0 = torch.tensor(point, device=dev, dtype=dt)
    dx = gx - p0[0]; dy = gy - p0[1]; dz = gz - p0[2]
    c1 = dx*e1[0] + dy*e1[1] + dz*e1[2]
    c2 = dx*e2[0] + dy*e2[1] + dz*e2[2]
    r = torch.sqrt(c1**2 + c2**2 + 1e-8)
    theta = torch.atan2(c2, c1)
    amp = phi_eq * torch.tanh(r / core_w)
    u += amp * torch.cos(charge * theta)
    v += amp * torch.sin(charge * theta)


def setup_fields(N, phi_eq, n_vortices, boost, device, dtype):
    u = torch.zeros(N, N, N, device=device, dtype=dtype)
    v = torch.zeros(N, N, N, device=device, dtype=dtype)
    cx = N / 2.0; off = N / 4.0
    configs = [
        ((cx-off, cx, cx), (0,0,1), 1),
        ((cx+off, cx, cx), (0,0,1), -1),
        ((cx, cx-off, cx), (1,0,0), 1),
        ((cx, cx+off, cx), (1,0,0), -1),
        ((cx, cx, cx-off), (0,1,0), 1),
        ((cx, cx, cx+off), (0,1,0), -1),
        ((cx-off*.7, cx-off*.7, cx), (1,1,0), 1),
        ((cx+off*.7, cx+off*.7, cx), (1,1,0), -1),
    ]
    for i, (pt, ax, ch) in enumerate(configs[:n_vortices]):
        inject_vortex(u, v, phi_eq, pt, ax, ch)
    
    # Boost: inward velocity
    coords = torch.arange(N, device=device, dtype=dtype)
    gz, gy, gx = torch.meshgrid(coords, coords, coords, indexing='ij')
    rx = gx - cx; ry = gy - cx; rz = gz - cx
    r = torch.sqrt(rx**2 + ry**2 + rz**2 + 1e-8)
    rhat_x = -rx/r; rhat_y = -ry/r; rhat_z = -rz/r
    
    du_dx = (torch.roll(u,-1,2) - torch.roll(u,1,2)) / 2
    du_dy = (torch.roll(u,-1,1) - torch.roll(u,1,1)) / 2
    du_dz = (torch.roll(u,-1,0) - torch.roll(u,1,0)) / 2
    dv_dx = (torch.roll(v,-1,2) - torch.roll(v,1,2)) / 2
    dv_dy = (torch.roll(v,-1,1) - torch.roll(v,1,1)) / 2
    dv_dz = (torch.roll(v,-1,0) - torch.roll(v,1,0)) / 2
    
    u_prev = u - boost * (du_dx*rhat_x + du_dy*rhat_y + du_dz*rhat_z)
    v_prev = v - boost * (dv_dx*rhat_x + dv_dy*rhat_y + dv_dz*rhat_z)
    return u, v, u_prev, v_prev


def step_pde(u, v, up, vp, kern, tau, mu2, lam, c02, dt, dx, damp):
    beta = u**2 + v**2
    g = 1.0 / (1.0 + tau * beta)**2
    g2 = g * g
    ce = c02 / (1.0 + tau * beta)
    lu = lap3d(u, kern, dx); lv = lap3d(v, kern, dx)
    fu = ce*lu + mu2*u - lam*beta*u
    fv = ce*lv + mu2*v - lam*beta*v
    un = 2*u - up + g2*fu*dt**2 - damp*(u - up)
    vn = 2*v - vp + g2*fv*dt**2 - damp*(v - vp)
    return un, vn


# ═══════════════════════════════════════════════════════════════════
# ISOSURFACE FRACTAL + TOPOLOGY ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def box_count_vertices(verts, n_sizes=8):
    """Box-counting D_f of a point cloud (isosurface vertices)."""
    if len(verts) < 30:
        return None, None, []
    pmin = verts.min(axis=0); pmax = verts.max(axis=0)
    span = pmax - pmin; span[span < 1e-10] = 1.0
    norm = (verts - pmin) / span
    sizes = [2**(-k) for k in range(2, 2 + n_sizes)]
    data = []
    for eps in sizes:
        boxes = set(map(tuple, np.floor(norm / eps).astype(int)))
        if len(boxes) > 0:
            data.append((np.log(1.0/eps), np.log(len(boxes))))
    if len(data) < 3:
        return None, None, data
    x = np.array([d[0] for d in data])
    y = np.array([d[1] for d in data])
    xf, yf = (x[1:-1], y[1:-1]) if len(x) > 4 else (x, y)
    if len(xf) < 2:
        return None, None, data
    c = np.polyfit(xf, yf, 1)
    Df = c[0]
    yp = np.polyval(c, xf)
    ss_r = np.sum((yf - yp)**2); ss_t = np.sum((yf - yf.mean())**2)
    r2 = 1 - ss_r/ss_t if ss_t > 0 else 0
    return Df, r2, data


def mesh_topology(verts, faces):
    """Euler characteristic and genus."""
    V = len(verts); F = len(faces)
    edges = set()
    for f in faces:
        for i in range(3):
            edges.add(tuple(sorted([f[i], f[(i+1)%3]])))
    E = len(edges)
    chi = V - E + F
    genus = max(0, (2 - chi) // 2)
    return {'V': V, 'E': E, 'F': F, 'chi': chi, 'genus': genus}


def analyze_isosurface(gamma_np, levels=None):
    """
    Extract isosurfaces at multiple Γ levels, measure D_f and topology.
    
    Returns list of dicts with all measurements.
    """
    if not HAS_SKIMAGE:
        return []
    
    if levels is None:
        gmin = gamma_np[gamma_np > 0].min() if (gamma_np > 0).any() else 1e-16
        gmax = gamma_np.max()
        # Logarithmic levels spanning the transition
        levels = np.logspace(np.log10(max(gmin*10, 1e-10)), 
                             np.log10(max(gmax*0.8, 1e-6)), 10)
        # Also add physically meaningful levels
        for pl in [1e-8, 1e-6, 1e-4, 1e-3, 0.005, 0.01, 0.05, 0.1]:
            if gmin < pl < gmax:
                levels = np.append(levels, pl)
        levels = np.sort(np.unique(levels))
    
    results = []
    for lv in levels:
        try:
            verts, faces, _, _ = measure.marching_cubes(gamma_np, level=float(lv))
        except (ValueError, RuntimeError):
            continue
        if len(verts) < 30 or len(faces) < 20:
            continue
        
        Df, r2, bc = box_count_vertices(verts)
        topo = mesh_topology(verts, faces)
        
        results.append({
            'gamma_level': float(lv),
            'n_verts': len(verts),
            'n_faces': len(faces),
            'D_f': float(Df) if Df is not None else None,
            'r_sq': float(r2) if r2 is not None else None,
            'chi': topo['chi'],
            'genus': topo['genus'],
        })
    
    return results


def summarize_surface(results):
    """Pick the best isosurface measurements."""
    good = [r for r in results if r['D_f'] is not None and r['r_sq'] 
            and r['r_sq'] > 0.95 and r['n_verts'] > 100]
    if not good:
        good = [r for r in results if r['D_f'] is not None and r['r_sq']
                and r['r_sq'] > 0.90 and r['n_verts'] > 50]
    if not good:
        return None
    
    Dfs = [r['D_f'] for r in good]
    chis = [r['chi'] for r in good]
    genera = [r['genus'] for r in good]
    
    return {
        'D_f_mean': float(np.mean(Dfs)),
        'D_f_median': float(np.median(Dfs)),
        'D_f_std': float(np.std(Dfs)),
        'D_f_min': float(min(Dfs)),
        'D_f_max': float(max(Dfs)),
        'chi_range': [int(min(chis)), int(max(chis))],
        'genus_range': [int(min(genera)), int(max(genera))],
        'genus_max': int(max(genera)),
        'n_good_fits': len(good),
    }


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 1: Single run with time-evolution tracking
# ═══════════════════════════════════════════════════════════════════

def run_single(args):
    print("=" * 70)
    print("CLOCKFIELD FRACTAL HORIZON — Single Run with Time Tracking")
    print("=" * 70)
    
    dev = torch.device(args.device if torch.cuda.is_available() or args.device == 'cpu' else 'cpu')
    dtype = torch.float32
    N = args.N; tau = args.tau
    mu2 = args.mu2; lam = args.lam; c02 = 1.0
    dt_sim = args.dt; dx = 1.0; damp = args.damping
    phi_eq = np.sqrt(mu2 / lam)
    beta_eq = mu2 / lam
    gvac = 1/(1 + tau*beta_eq)**2
    
    print(f"Grid: {N}³, τ={tau}, boost={args.boost}, steps={args.steps}")
    print(f"φ_eq={phi_eq:.4f}, β_eq={beta_eq:.4f}, Γ_vac={gvac:.6f}")
    print(f"Device: {dev}")
    
    kern = make_lap_kernel(dev, dtype)
    u, v, up, vp = setup_fields(N, phi_eq, args.n_vortices, args.boost, dev, dtype)
    
    # Snapshot interval for time-evolution tracking
    snap_interval = max(args.steps // 20, 100)  # ~20 snapshots
    
    snapshots = []
    t0 = time.time()
    
    for step in range(args.steps):
        un, vn = step_pde(u, v, up, vp, kern, tau, mu2, lam, c02, dt_sim, dx, damp)
        up = u; vp = v; u = un; v = vn
        
        # Snapshot
        if (step + 1) % snap_interval == 0 or step == 0 or step == args.steps - 1:
            beta = (u**2 + v**2).cpu().numpy()
            gamma = 1.0 / (1.0 + tau * beta)**2
            
            bmax = beta.max()
            gmin = gamma.min()
            frozen = (gamma < 0.01).mean()
            
            elapsed = time.time() - t0
            sps = (step + 1) / elapsed if elapsed > 0 else 0
            
            # Isosurface analysis (lightweight — only a few levels)
            quick_levels = []
            for pl in [1e-6, 1e-4, 1e-3, 0.005, 0.01, 0.05]:
                if gamma.min() < pl < gamma.max():
                    quick_levels.append(pl)
            
            iso_results = analyze_isosurface(gamma, quick_levels) if HAS_SKIMAGE else []
            summary = summarize_surface(iso_results)
            
            snap = {
                'step': step + 1,
                'time': (step + 1) * dt_sim,
                'beta_max': float(bmax),
                'gamma_min': float(gmin),
                'frozen_frac': float(frozen),
            }
            
            if summary:
                snap['D_f'] = summary['D_f_mean']
                snap['D_f_std'] = summary['D_f_std']
                snap['genus_max'] = summary['genus_max']
                snap['chi_min'] = summary['chi_range'][0]
                
                print(f"  Step {step+1:6d}: β_max={bmax:.0f}, Γ_min={gmin:.2e}, "
                      f"frozen={frozen*100:.1f}%, D_f={summary['D_f_mean']:.3f}±{summary['D_f_std']:.3f}, "
                      f"genus={summary['genus_max']}, χ={summary['chi_range'][0]} "
                      f"[{sps:.0f} st/s]")
            else:
                print(f"  Step {step+1:6d}: β_max={bmax:.0f}, Γ_min={gmin:.2e}, "
                      f"frozen={frozen*100:.1f}%, [no isosurface] [{sps:.0f} st/s]")
            
            snapshots.append(snap)
            
            # NaN check
            if np.isnan(bmax) or bmax > 1e14:
                print("  *** BLOWUP ***")
                break
    
    total = time.time() - t0
    print(f"\nDone: {total:.1f}s")
    
    # ─── Final detailed analysis ───
    print(f"\n{'='*70}")
    print("FINAL DETAILED ISOSURFACE ANALYSIS")
    print(f"{'='*70}")
    
    beta_final = (u**2 + v**2).cpu().numpy()
    gamma_final = 1.0 / (1.0 + tau * beta_final)**2
    
    final_iso = analyze_isosurface(gamma_final)
    final_summary = summarize_surface(final_iso)
    
    if final_iso:
        print(f"\n{'Γ_level':>12s} {'Verts':>8s} {'Faces':>8s} {'D_f':>8s} {'R²':>6s} {'χ':>6s} {'genus':>6s}")
        print("-" * 58)
        for r in final_iso:
            df_str = f"{r['D_f']:.4f}" if r['D_f'] else "N/A"
            r2_str = f"{r['r_sq']:.3f}" if r['r_sq'] else ""
            print(f"  {r['gamma_level']:10.2e}  {r['n_verts']:8d}  {r['n_faces']:8d}  "
                  f"{df_str:>8s}  {r2_str:>5s}  {r['chi']:>5d}  {r['genus']:>5d}")
    
    if final_summary:
        print(f"\n  SUMMARY:")
        print(f"    D_f = {final_summary['D_f_mean']:.4f} ± {final_summary['D_f_std']:.4f}")
        print(f"    D_f range: [{final_summary['D_f_min']:.4f}, {final_summary['D_f_max']:.4f}]")
        print(f"    Genus range: {final_summary['genus_range']}")
        print(f"    Max genus: {final_summary['genus_max']}")
        
        Df = final_summary['D_f_mean']
        if Df > 2.05:
            print(f"\n    → FRACTAL HORIZON: D_f={Df:.3f} > 2 (rough surface)")
        elif Df < 1.95:
            print(f"\n    → FILAMENTARY HORIZON: D_f={Df:.3f} < 2 (string-like network)")
            print(f"      The horizon is a sponge/web, not a smooth bubble")
        else:
            print(f"\n    → SMOOTH HORIZON: D_f≈2.0 within precision")
        
        if final_summary['genus_max'] > 0:
            print(f"    → TOPOLOGICALLY COMPLEX: genus={final_summary['genus_max']}")
            print(f"      {final_summary['genus_max']} tunnels/handles in the horizon surface")
            print(f"      Phase structure of infalling vortices imprinted on shell")
        
        alpha_implied = 2 * (Df - 1)
        print(f"\n    Jalalzadeh mapping: α={alpha_implied:.4f}, D_space={alpha_implied/2+3:.4f}")
    
    # ─── Time evolution: is the topology permanent? ───
    print(f"\n{'='*70}")
    print("TIME EVOLUTION: Is the fractal topology permanent?")
    print(f"{'='*70}")
    
    genus_history = [(s['step'], s.get('genus_max', None)) for s in snapshots]
    df_history = [(s['step'], s.get('D_f', None)) for s in snapshots]
    
    genus_vals = [g for _, g in genus_history if g is not None]
    df_vals = [d for _, d in df_history if d is not None]
    
    if len(genus_vals) >= 3:
        # Check if genus is stable, increasing, or decreasing
        early = genus_vals[:len(genus_vals)//3]
        late = genus_vals[-len(genus_vals)//3:]
        
        early_mean = np.mean(early)
        late_mean = np.mean(late)
        
        print(f"\n  Genus: early avg = {early_mean:.1f}, late avg = {late_mean:.1f}")
        
        if abs(late_mean - early_mean) < 1:
            print(f"  → STABLE: Topology is FROZEN IN. The fractal structure is permanent.")
            print(f"    The Γ→0 time-freeze locks the phase-mismatch scars into place.")
        elif late_mean < early_mean * 0.5:
            print(f"  → SMOOTHING: Topology simplifying over time. Genus decreasing.")
            print(f"    The horizon is relaxing toward a simpler surface.")
        else:
            print(f"  → GROWING: Topology becoming more complex. Genus increasing.")
    
    if len(df_vals) >= 3:
        early_df = df_vals[:len(df_vals)//3]
        late_df = df_vals[-len(df_vals)//3:]
        print(f"  D_f: early avg = {np.mean(early_df):.4f}, late avg = {np.mean(late_df):.4f}")
    
    # ─── Save everything ───
    output = {
        'params': {'N': N, 'tau': tau, 'mu2': mu2, 'lam': lam,
                   'boost': args.boost, 'n_vortices': args.n_vortices,
                   'steps': args.steps, 'dt': dt_sim, 'damping': damp},
        'vacuum': {'phi_eq': float(phi_eq), 'beta_eq': float(beta_eq), 'gamma_vac': float(gvac)},
        'snapshots': snapshots,
        'final_isosurface': final_iso,
        'final_summary': final_summary,
        'runtime_s': total,
    }
    
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved: {args.output}")
    
    # Save fields
    np.save(args.output.replace('.json', '_gamma.npy'), gamma_final)
    np.save(args.output.replace('.json', '_beta.npy'), beta_final)
    print(f"Saved: {args.output.replace('.json', '_gamma.npy')}")
    
    # Plot time evolution
    if HAS_MPL and len(snapshots) > 3:
        plot_time_evolution(snapshots, tau, args.output.replace('.json', '_evolution.png'))
    
    return output


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 2: τ-scan
# ═══════════════════════════════════════════════════════════════════

def run_tau_scan(args):
    print("=" * 70)
    print("τ-SCAN: Fractal dimension vs Clockfield coupling")
    print("=" * 70)
    
    tau_values = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0]
    scan = []
    
    for tau_val in tau_values:
        print(f"\n{'─'*70}")
        print(f"τ = {tau_val}")
        print(f"{'─'*70}")
        
        args.tau = tau_val
        args.output = f"horizon_tau{tau_val:.1f}.json"
        result = run_single(args)
        
        entry = {
            'tau': tau_val,
            'tau_beta0': tau_val * args.mu2 / args.lam,
            'gamma_vac': 1/(1 + tau_val * args.mu2/args.lam)**2,
        }
        if result and result.get('final_summary'):
            s = result['final_summary']
            entry['D_f'] = s['D_f_mean']
            entry['D_f_std'] = s['D_f_std']
            entry['genus_max'] = s['genus_max']
            entry['alpha_implied'] = 2 * (s['D_f_mean'] - 1)
        scan.append(entry)
    
    # Summary
    print(f"\n{'='*70}")
    print("τ-SCAN SUMMARY (Corrected: Isosurface D_f)")
    print(f"{'='*70}")
    print(f"\n{'τ':>6s} {'τβ₀':>8s} {'Γ_vac':>10s} {'D_f':>8s} {'±':>6s} {'genus':>6s} {'α':>8s}")
    print("-" * 56)
    
    for e in scan:
        if 'D_f' in e:
            print(f"  {e['tau']:4.1f}  {e['tau_beta0']:8.3f}  {e['gamma_vac']:10.6f}  "
                  f"{e['D_f']:8.4f}  {e.get('D_f_std',0):6.4f}  "
                  f"{e.get('genus_max','?'):>5}  {e.get('alpha_implied',0):8.4f}")
        else:
            print(f"  {e['tau']:4.1f}  {e['tau_beta0']:8.3f}  {e['gamma_vac']:10.6f}  {'N/A':>8s}")
    
    with open("horizon_tau_scan_corrected.json", "w") as f:
        json.dump(scan, f, indent=2)
    print(f"\nSaved: horizon_tau_scan_corrected.json")
    
    # Plot
    if HAS_MPL and len([e for e in scan if 'D_f' in e]) >= 3:
        plot_tau_scan(scan)


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_time_evolution(snapshots, tau, outfile):
    if not HAS_MPL:
        return
    
    steps = [s['step'] for s in snapshots]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # D_f over time
    ax = axes[0, 0]
    df_steps = [(s['step'], s['D_f']) for s in snapshots if 'D_f' in s]
    if df_steps:
        ax.plot([d[0] for d in df_steps], [d[1] for d in df_steps], 'b.-', lw=2)
        ax.axhline(2.0, color='red', ls='--', alpha=0.5, label='Smooth surface')
        ax.set_ylabel('D_f (box-counting)')
        ax.set_title(f'Fractal Dimension Evolution (τ={tau})')
        ax.legend()
        ax.grid(True, alpha=0.3)
    ax.set_xlabel('Step')
    
    # Genus over time
    ax = axes[0, 1]
    g_steps = [(s['step'], s['genus_max']) for s in snapshots if 'genus_max' in s]
    if g_steps:
        ax.plot([g[0] for g in g_steps], [g[1] for g in g_steps], 'r.-', lw=2)
        ax.set_ylabel('Max Genus')
        ax.set_title('Topological Complexity Evolution')
        ax.grid(True, alpha=0.3)
    ax.set_xlabel('Step')
    
    # Beta max
    ax = axes[1, 0]
    ax.semilogy(steps, [s['beta_max'] for s in snapshots], 'g.-', lw=2)
    ax.set_xlabel('Step'); ax.set_ylabel('β_max')
    ax.set_title('Peak Energy Density')
    ax.grid(True, alpha=0.3)
    
    # Frozen fraction
    ax = axes[1, 1]
    ax.plot(steps, [s['frozen_frac']*100 for s in snapshots], 'm.-', lw=2)
    ax.set_xlabel('Step'); ax.set_ylabel('Frozen %')
    ax.set_title('Fraction of Grid with Γ < 0.01')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle(f'Clockfield Horizon Evolution — τ={tau}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(outfile, dpi=150, bbox_inches='tight')
    print(f"  Plot saved: {outfile}")


def plot_tau_scan(scan):
    if not HAS_MPL:
        return
    
    good = [e for e in scan if 'D_f' in e]
    if len(good) < 2:
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    taus = [e['tau'] for e in good]
    tb0s = [e['tau_beta0'] for e in good]
    
    # D_f vs τ
    ax = axes[0]
    ax.errorbar(taus, [e['D_f'] for e in good],
                yerr=[e.get('D_f_std', 0) for e in good],
                fmt='bo-', capsize=4, lw=2)
    ax.axhline(2.0, color='red', ls='--', alpha=0.5, label='Smooth (D_f=2)')
    ax.set_xlabel('τ'); ax.set_ylabel('D_f (surface)')
    ax.set_title('Fractal Dimension vs τ')
    ax.legend(); ax.grid(True, alpha=0.3)
    
    # Genus vs τ
    ax = axes[1]
    ax.plot(taus, [e.get('genus_max', 0) for e in good], 'rs-', lw=2)
    ax.set_xlabel('τ'); ax.set_ylabel('Max Genus')
    ax.set_title('Topological Complexity vs τ')
    ax.grid(True, alpha=0.3)
    
    # Implied α vs τβ₀
    ax = axes[2]
    alphas = [e.get('alpha_implied', None) for e in good]
    ax.plot(tb0s, alphas, 'g^-', lw=2)
    ax.axhline(2.0, color='gold', ls='--', label='Standard (α=2)')
    ax.set_xlabel('τβ₀'); ax.set_ylabel('Implied α (Jalalzadeh)')
    ax.set_title('Lévy Parameter vs Clockfield Coupling')
    ax.legend(); ax.grid(True, alpha=0.3)
    
    plt.suptitle('Clockfield Horizon: τ-Scan (Corrected)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('horizon_tau_scan_corrected.png', dpi=150, bbox_inches='tight')
    print(f"Plot saved: horizon_tau_scan_corrected.png")


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Clockfield Fractal Horizon — Complete")
    p.add_argument('--mode', choices=['single', 'tau_scan', 'long_run'], default='single')
    p.add_argument('--N', type=int, default=64)
    p.add_argument('--tau', type=float, default=5.0)
    p.add_argument('--mu2', type=float, default=1.4)
    p.add_argument('--lam', type=float, default=0.55)
    p.add_argument('--dt', type=float, default=0.015)
    p.add_argument('--damping', type=float, default=0.003)
    p.add_argument('--n_vortices', type=int, default=6)
    p.add_argument('--boost', type=float, default=1.0)
    p.add_argument('--steps', type=int, default=5000)
    p.add_argument('--device', type=str, default='cuda')
    p.add_argument('--output', type=str, default='horizon_complete.json')
    
    args = p.parse_args()
    
    if args.mode == 'tau_scan':
        run_tau_scan(args)
    elif args.mode == 'long_run':
        args.steps = max(args.steps, 15000)
        args.output = f'horizon_long_tau{args.tau:.0f}.json'
        run_single(args)
    else:
        run_single(args)