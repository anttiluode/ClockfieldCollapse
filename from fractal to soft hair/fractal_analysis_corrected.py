#!/usr/bin/env python3
"""
CORRECTED FRACTAL DIMENSION ANALYSIS
======================================

The original analysis measured the fractal dimension of thresholded VOLUMES,
which gives D_f ≈ 3 (trivially — a filled volume IS 3D).

What we actually want: the fractal dimension of the Γ-ISOSURFACE — 
the 2D boundary where Γ transitions from frozen to unfrozen.

Method: 
  1. Extract the isosurface via marching cubes at multiple Γ levels
  2. Compute fractal dimension of the resulting mesh via box-counting
     on the SURFACE POINTS (vertices), not the volume
  3. Also compute: surface area vs scale (Richardson method)
  4. Compare across τ values

A smooth 2D surface in 3D has D_f = 2.0.
A fractal surface has 2.0 < D_f < 3.0.
The Jalalzadeh prediction is D_horizon = α/2 + 1, with 1 < D_horizon ≤ 2.
But that's the INTRINSIC dimension. The EMBEDDING dimension (what box-counting
measures in 3D) would be D_f = D_horizon (for a surface embedded in 3D).

Usage:
  python fractal_analysis_corrected.py [--gamma_file FILE] [--tau 5.0]
  
  Or for the tau scan:
  python fractal_analysis_corrected.py --tau_scan

Requires: numpy, scipy, skimage (scikit-image)
Optional: matplotlib (for plots)

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import argparse
import json
import numpy as np
from pathlib import Path

try:
    from skimage import measure
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False
    print("WARNING: scikit-image not found. Install with: pip install scikit-image")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ═══════════════════════════════════════════════════════════════════
# BOX-COUNTING ON SURFACE VERTICES (not volume)
# ═══════════════════════════════════════════════════════════════════

def box_count_points(points, box_sizes=None):
    """
    Box-counting fractal dimension of a POINT CLOUD in 3D.
    
    For each box size ε, count how many boxes of that size 
    contain at least one point. The fractal dimension is the 
    slope of log(N) vs log(1/ε).
    
    This is fundamentally different from the volume-based approach:
    a set of points on a smooth surface gives D_f = 2.0,
    while the same points filling a volume give D_f = 3.0.
    """
    if len(points) < 10:
        return [], None, None
    
    # Normalize points to [0, 1] cube
    pmin = points.min(axis=0)
    pmax = points.max(axis=0)
    span = pmax - pmin
    span[span < 1e-10] = 1.0  # avoid division by zero
    normalized = (points - pmin) / span
    
    if box_sizes is None:
        # Geometric sequence of box sizes
        # From ~1/4 of the domain down to ~1/256
        box_sizes = [2**(-k) for k in range(2, 9)]
    
    results = []
    for eps in box_sizes:
        if eps <= 0:
            continue
        # Assign each point to a box
        box_indices = np.floor(normalized / eps).astype(int)
        # Count unique boxes
        # Use a set of tuples for uniqueness
        unique_boxes = set(map(tuple, box_indices))
        count = len(unique_boxes)
        if count > 0:
            results.append((np.log(1.0 / eps), np.log(count), eps, count))
    
    if len(results) < 3:
        return results, None, None
    
    x = np.array([r[0] for r in results])
    y = np.array([r[1] for r in results])
    
    # Linear fit (exclude endpoints which may be affected by boundary)
    if len(x) > 4:
        x_fit = x[1:-1]
        y_fit = y[1:-1]
    else:
        x_fit = x
        y_fit = y
    
    coeffs = np.polyfit(x_fit, y_fit, 1)
    D_f = coeffs[0]
    
    y_pred = np.polyval(coeffs, x_fit)
    ss_res = np.sum((y_fit - y_pred)**2)
    ss_tot = np.sum((y_fit - np.mean(y_fit))**2)
    r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    
    return results, D_f, r_sq


def mesh_area_at_scale(vertices, faces, scale):
    """
    Compute the 'area' of a triangulated mesh visible at resolution `scale`.
    
    Coarse-grain the mesh: merge vertices within distance `scale`,
    then count the resulting effective triangles.
    
    This gives the Richardson plot: area(ε) vs ε.
    For a smooth surface: area ~ constant.
    For a fractal surface: area ~ ε^(2 - D_f).
    """
    if len(vertices) < 3 or len(faces) < 1:
        return 0.0
    
    # Compute area of each triangle
    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]
    
    # Triangle edge lengths
    e1 = np.linalg.norm(v1 - v0, axis=1)
    e2 = np.linalg.norm(v2 - v0, axis=1)
    e3 = np.linalg.norm(v2 - v1, axis=1)
    
    # Only count triangles larger than scale
    max_edge = np.maximum(e1, np.maximum(e2, e3))
    mask = max_edge >= scale
    
    # Cross product for area
    cross = np.cross(v1 - v0, v2 - v0)
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    
    return areas[mask].sum(), mask.sum()


def richardson_fractal_dimension(vertices, faces):
    """
    Richardson method: measure how total surface area changes with 
    measurement scale.
    
    For a smooth surface: A(ε) → constant as ε → 0
    For a fractal: A(ε) ~ ε^(2-D_f), so D_f = 2 + d(log A)/d(log ε)
    """
    if len(faces) < 10:
        return None, None, []
    
    # Compute all triangle sizes
    v0 = vertices[faces[:, 0]]
    v1 = vertices[faces[:, 1]]
    v2 = vertices[faces[:, 2]]
    max_edges = np.max([
        np.linalg.norm(v1 - v0, axis=1),
        np.linalg.norm(v2 - v0, axis=1),
        np.linalg.norm(v2 - v1, axis=1)
    ], axis=0)
    
    cross = np.cross(v1 - v0, v2 - v0)
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    total_area = areas.sum()
    
    # Measure area at different scales
    scales = np.logspace(np.log10(max_edges.min() + 1e-10), 
                         np.log10(max_edges.max()), 15)
    
    results = []
    for s in scales:
        mask = max_edges >= s
        area_at_scale = areas[mask].sum()
        n_triangles = mask.sum()
        if n_triangles > 5:
            results.append((np.log(s), np.log(area_at_scale), s, area_at_scale))
    
    if len(results) < 3:
        return None, None, results
    
    x = np.array([r[0] for r in results])
    y = np.array([r[1] for r in results])
    
    # The slope of log(A) vs log(ε) is (2 - D_f)
    # So D_f = 2 - slope
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    D_f_richardson = 2.0 - slope
    
    y_pred = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    
    return D_f_richardson, r_sq, results


# ═══════════════════════════════════════════════════════════════════
# TOPOLOGY ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def analyze_mesh_topology(vertices, faces):
    """
    Basic topological analysis of the isosurface mesh.
    
    Euler characteristic χ = V - E + F
    For a sphere: χ = 2
    For a torus: χ = 0
    For genus-g surface: χ = 2 - 2g
    
    More interesting surfaces (multiple handles, punctures) 
    indicate topological complexity from the phase structure.
    """
    V = len(vertices)
    F = len(faces)
    
    # Count edges (each face has 3 edges, each shared by 2 faces... mostly)
    edge_set = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted([face[i], face[(i+1) % 3]]))
            edge_set.add(edge)
    E = len(edge_set)
    
    chi = V - E + F
    
    # For a closed orientable surface: χ = 2 - 2g
    # g = genus (number of handles)
    # This assumes a single connected component
    genus = (2 - chi) // 2 if chi <= 2 else 0
    
    return {
        'vertices': V,
        'edges': E,
        'faces': F,
        'euler_characteristic': chi,
        'genus_estimate': genus
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def analyze_single(gamma_file, beta_file, tau, json_file=None):
    """Full analysis of a single simulation's output."""
    
    print(f"\n{'='*70}")
    print(f"CORRECTED FRACTAL ANALYSIS: τ = {tau}")
    print(f"{'='*70}")
    
    gamma = np.load(gamma_file)
    beta = np.load(beta_file)
    N = gamma.shape[0]
    
    print(f"Grid: {N}³, τ = {tau}")
    print(f"Γ range: [{gamma.min():.2e}, {gamma.max():.6f}]")
    print(f"β range: [{beta.min():.4f}, {beta.max():.2e}]")
    
    # Fraction frozen
    frozen_frac = (gamma < 0.01).mean()
    print(f"Frozen fraction (Γ < 0.01): {frozen_frac*100:.1f}%")
    
    if not HAS_SKIMAGE:
        print("ERROR: scikit-image required for isosurface extraction")
        return None
    
    # ─── Extract isosurfaces at multiple Γ levels ───
    # Key insight: we want levels in the TRANSITION REGION, 
    # not in the deeply frozen bulk
    
    # Find the Γ range of the transition
    gamma_flat = gamma.flatten()
    # The transition region is where Γ changes rapidly
    # Find percentiles
    p01 = np.percentile(gamma_flat[gamma_flat > 0], 1)
    p10 = np.percentile(gamma_flat[gamma_flat > 0], 10)
    p50 = np.percentile(gamma_flat[gamma_flat > 0], 50)
    p90 = np.percentile(gamma_flat[gamma_flat > 0], 90)
    p99 = np.percentile(gamma_flat[gamma_flat > 0], 99)
    
    print(f"\nΓ percentiles: 1%={p01:.2e}, 10%={p10:.2e}, "
          f"50%={p50:.2e}, 90%={p90:.2e}, 99%={p99:.4f}")
    
    # Choose isosurface levels that capture the shell structure
    # The interesting physics is at the BOUNDARY of the frozen region
    gamma_vac = gamma.max()
    
    # Levels: from just above the frozen bulk to approaching vacuum
    levels = []
    # Logarithmic spacing in the transition region
    if p99 > p01 * 10:
        log_levels = np.logspace(np.log10(max(p10, 1e-10)), 
                                  np.log10(min(p99, gamma_vac * 0.9)), 8)
        levels = sorted(set(log_levels))
    else:
        levels = np.linspace(max(p01, 1e-10), min(p99, gamma_vac * 0.9), 8)
    
    # Also add specific physically meaningful levels
    physical_levels = [0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.5]
    for pl in physical_levels:
        if gamma.min() < pl < gamma.max():
            levels.append(pl)
    
    levels = sorted(set(levels))
    
    print(f"\nExtracting isosurfaces at {len(levels)} Γ levels...")
    print(f"{'Γ_level':>12s} {'Vertices':>10s} {'Faces':>10s} {'D_f(box)':>10s} "
          f"{'R²':>6s} {'D_f(Rich)':>10s} {'R²':>6s} {'χ':>6s} {'genus':>6s}")
    print("-" * 85)
    
    all_results = []
    
    for level in levels:
        try:
            verts, faces, normals, values = measure.marching_cubes(gamma, level=level)
        except (ValueError, RuntimeError):
            continue
        
        if len(verts) < 50 or len(faces) < 50:
            continue
        
        # Box-counting on vertices
        bc_data, D_f_box, r_sq_box = box_count_points(verts)
        
        # Richardson method on mesh
        D_f_rich, r_sq_rich, rich_data = richardson_fractal_dimension(verts, faces)
        
        # Topology
        topo = analyze_mesh_topology(verts, faces)
        
        result = {
            'gamma_level': float(level),
            'n_vertices': len(verts),
            'n_faces': len(faces),
            'D_f_box': float(D_f_box) if D_f_box is not None else None,
            'r_sq_box': float(r_sq_box) if r_sq_box is not None else None,
            'D_f_richardson': float(D_f_rich) if D_f_rich is not None else None,
            'r_sq_richardson': float(r_sq_rich) if r_sq_rich is not None else None,
            'topology': topo,
            'box_count_data': [(float(a), float(b)) for a, b, _, _ in bc_data] if bc_data else [],
        }
        all_results.append(result)
        
        Df_b_str = f"{D_f_box:.4f}" if D_f_box else "N/A"
        r2_b_str = f"{r_sq_box:.3f}" if r_sq_box else ""
        Df_r_str = f"{D_f_rich:.4f}" if D_f_rich else "N/A"
        r2_r_str = f"{r_sq_rich:.3f}" if r_sq_rich else ""
        
        print(f"  {level:10.4e}  {len(verts):10d}  {len(faces):10d}  "
              f"{Df_b_str:>10s}  {r2_b_str:>5s}  {Df_r_str:>10s}  {r2_r_str:>5s}  "
              f"{topo['euler_characteristic']:>5d}  {topo['genus_estimate']:>5d}")
    
    if not all_results:
        print("\n  No valid isosurfaces extracted.")
        return None
    
    # ─── Summary statistics ───
    # Use only good box-counting fits
    good_box = [r for r in all_results 
                if r['D_f_box'] is not None and r['r_sq_box'] > 0.95
                and r['n_vertices'] > 100]
    
    good_rich = [r for r in all_results
                 if r['D_f_richardson'] is not None and r['r_sq_richardson'] > 0.8
                 and r['n_vertices'] > 100]
    
    print(f"\n{'─'*70}")
    print(f"SUMMARY for τ = {tau}")
    print(f"{'─'*70}")
    
    if good_box:
        D_f_values = [r['D_f_box'] for r in good_box]
        D_f_mean = np.mean(D_f_values)
        D_f_std = np.std(D_f_values)
        D_f_median = np.median(D_f_values)
        print(f"\n  Box-counting D_f (R² > 0.95, n > 100 vertices):")
        print(f"    Mean:   {D_f_mean:.4f} ± {D_f_std:.4f}")
        print(f"    Median: {D_f_median:.4f}")
        print(f"    Range:  [{min(D_f_values):.4f}, {max(D_f_values):.4f}]")
        print(f"    N fits: {len(D_f_values)}")
        
        # For a surface in 3D: D_f = 2.0 means smooth, D_f > 2.0 means fractal
        if D_f_mean > 2.05:
            print(f"    → FRACTAL HORIZON: D_f = {D_f_mean:.3f} > 2.0")
            print(f"    → Fractal excess: D_f - 2 = {D_f_mean - 2:.4f}")
        elif D_f_mean < 1.95:
            print(f"    → Sub-surface structure: D_f = {D_f_mean:.3f} < 2.0")
            print(f"    → Possibly disconnected / filamentary shell")
        else:
            print(f"    → Smooth horizon within measurement precision")
    else:
        print("\n  No reliable box-counting fits (R² > 0.95 with > 100 vertices)")
        D_f_mean = None
    
    if good_rich:
        D_r_values = [r['D_f_richardson'] for r in good_rich]
        D_r_mean = np.mean(D_r_values)
        print(f"\n  Richardson D_f (R² > 0.80):")
        print(f"    Mean: {D_r_mean:.4f}")
        print(f"    (Richardson measures surface roughness at different scales)")
    
    # Topology summary
    chi_values = [r['topology']['euler_characteristic'] for r in all_results]
    genus_values = [r['topology']['genus_estimate'] for r in all_results]
    print(f"\n  Topology:")
    print(f"    Euler χ range: [{min(chi_values)}, {max(chi_values)}]")
    print(f"    Genus range:   [{min(genus_values)}, {max(genus_values)}]")
    print(f"    (Sphere: χ=2, genus=0. Complex topology: large genus)")
    
    # ─── Jalalzadeh mapping ───
    if D_f_mean is not None:
        print(f"\n  Jalalzadeh mapping:")
        print(f"    D_f(surface) = {D_f_mean:.4f}")
        # Their D_horizon = α/2 + 1
        # If our box-counting D_f corresponds to their D-2 (the horizon dim):
        alpha_implied = 2 * (D_f_mean - 1)
        D_spacetime = alpha_implied / 2 + 3
        print(f"    If D_f = α/2 + 1: α = {alpha_implied:.4f}, D_spacetime = {D_spacetime:.4f}")
        # Standard: α=2 → D_f=2 → D_spacetime=4
        print(f"    Standard case: α=2 → D_f=2 → D=4")
    
    # Compile output
    output = {
        'tau': tau,
        'grid_size': N,
        'gamma_range': [float(gamma.min()), float(gamma.max())],
        'frozen_fraction': float(frozen_frac),
        'isosurface_results': all_results,
    }
    
    if good_box:
        output['summary_box_counting'] = {
            'D_f_mean': float(D_f_mean),
            'D_f_std': float(np.std([r['D_f_box'] for r in good_box])),
            'D_f_median': float(np.median([r['D_f_box'] for r in good_box])),
            'n_good_fits': len(good_box)
        }
    
    return output


def run_tau_scan_analysis():
    """Analyze all tau-scan results."""
    
    print("=" * 70)
    print("τ-SCAN CORRECTED ANALYSIS")
    print("=" * 70)
    
    # Look for saved field files
    tau_values = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0]
    
    scan_results = []
    
    for tau in tau_values:
        gamma_file = f"fractal_horizon_tau{tau:.0f}_gamma.npy"
        beta_file = f"fractal_horizon_tau{tau:.0f}_beta.npy"
        
        if not Path(gamma_file).exists():
            # Try the default naming
            gamma_file = f"fractal_horizon_results_gamma.npy"
            beta_file = f"fractal_horizon_results_beta.npy"
            if not Path(gamma_file).exists():
                print(f"\n  τ={tau}: field files not found, skipping")
                continue
        
        result = analyze_single(gamma_file, beta_file, tau)
        if result:
            scan_results.append(result)
    
    if not scan_results:
        print("\nNo results to summarize. Run the simulation with --save_field first.")
        print("For tau scan: run each tau individually with --save_field:")
        print("  python clockfield_fractal_horizon.py --tau 1.0 --N 64 --steps 3000 "
              "--boost 1.0 --save_field --output fractal_horizon_tau1.json")
        return
    
    # Summary table
    print("\n" + "=" * 70)
    print("τ-SCAN CORRECTED SUMMARY")
    print("=" * 70)
    print(f"\n{'τ':>6s} {'τβ₀':>8s} {'Frozen%':>8s} {'D_f(box)':>10s} "
          f"{'±':>6s} {'α_impl':>8s} {'D_space':>8s}")
    print("-" * 58)
    
    for r in scan_results:
        tau = r['tau']
        beta_eq = 1.4 / 0.55
        tb0 = tau * beta_eq
        ff = r['frozen_fraction'] * 100
        
        if 'summary_box_counting' in r:
            s = r['summary_box_counting']
            D_f = s['D_f_mean']
            std = s['D_f_std']
            alpha = 2 * (D_f - 1)
            D_sp = alpha / 2 + 3
            print(f"  {tau:4.1f}  {tb0:8.3f}  {ff:7.1f}%  {D_f:10.4f}  "
                  f"{std:6.4f}  {alpha:8.4f}  {D_sp:8.4f}")
        else:
            print(f"  {tau:4.1f}  {tb0:8.3f}  {ff:7.1f}%  {'N/A':>10s}")
    
    # Save
    outfile = "fractal_analysis_corrected.json"
    with open(outfile, 'w') as f:
        json.dump(scan_results, f, indent=2, default=str)
    print(f"\nSaved: {outfile}")


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_box_counting(results, tau, outfile=None):
    """Plot box-counting data for all isosurface levels."""
    if not HAS_MPL:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: box-counting plots
    ax = axes[0]
    for r in results:
        if r['box_count_data'] and r['D_f_box'] is not None:
            x = [d[0] for d in r['box_count_data']]
            y = [d[1] for d in r['box_count_data']]
            label = f"Γ={r['gamma_level']:.3e}, D_f={r['D_f_box']:.3f}"
            ax.plot(x, y, 'o-', markersize=4, label=label)
    
    ax.set_xlabel('log(1/ε)')
    ax.set_ylabel('log(N(ε))')
    ax.set_title(f'Box-Counting (Surface Vertices), τ={tau}')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    
    # Right: D_f vs Γ level
    ax = axes[1]
    levels = [r['gamma_level'] for r in results if r['D_f_box'] is not None]
    Dfs = [r['D_f_box'] for r in results if r['D_f_box'] is not None]
    r2s = [r['r_sq_box'] for r in results if r['D_f_box'] is not None]
    
    if levels:
        colors = ['green' if r > 0.95 else 'orange' if r > 0.9 else 'red' for r in r2s]
        ax.scatter(levels, Dfs, c=colors, s=50, zorder=5)
        ax.axhline(2.0, color='blue', ls='--', alpha=0.5, label='Smooth surface (D_f=2)')
        ax.set_xlabel('Γ isosurface level')
        ax.set_ylabel('Fractal dimension D_f')
        ax.set_title(f'D_f vs Γ level, τ={tau}')
        ax.set_xscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    if outfile:
        plt.savefig(outfile, dpi=150, bbox_inches='tight')
        print(f"  Plot saved: {outfile}")
    else:
        plt.savefig(f'fractal_corrected_tau{tau:.0f}.png', dpi=150, bbox_inches='tight')


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corrected fractal dimension analysis")
    parser.add_argument('--gamma_file', type=str, default='fractal_horizon_results_gamma.npy')
    parser.add_argument('--beta_file', type=str, default='fractal_horizon_results_beta.npy')
    parser.add_argument('--tau', type=float, default=5.0)
    parser.add_argument('--tau_scan', action='store_true',
                        help='Analyze all tau-scan results')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    
    args = parser.parse_args()
    
    if args.tau_scan:
        run_tau_scan_analysis()
    else:
        result = analyze_single(args.gamma_file, args.beta_file, args.tau)
        
        if result and args.plot:
            plot_box_counting(result['isosurface_results'], args.tau)
        
        if result:
            outfile = f"fractal_corrected_tau{args.tau:.0f}.json"
            with open(outfile, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\nSaved: {outfile}")