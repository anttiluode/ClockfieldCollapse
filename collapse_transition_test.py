#!/usr/bin/env python3
"""
CLOCKFIELD: Repulsion-to-Collapse — Fast targeted scan
"""
import numpy as np

N = 256
mu2, lam, c02, dt, dx, damping = 1.4, 0.55, 1.0, 0.02, 1.0, 0.005
phi_eq = np.sqrt(mu2/lam)
beta_eq = mu2/lam

print("="*70)
print("CLOCKFIELD REPULSION vs COLLAPSE")
print("="*70)
print(f"φ_eq={phi_eq:.4f}, β_eq={beta_eq:.4f}\n")

def test_lump(tau, amp, sigma=6, steps=1500):
    phi = np.ones((N,N)) * phi_eq
    cx,cy = N//2, N//2
    yy,xx = np.mgrid[0:N,0:N]
    rr2 = (xx-cx)**2 + (yy-cy)**2
    phi += phi_eq * amp * np.exp(-rr2/(2*sigma**2))
    phi_prev = phi.copy()
    
    peaks = []
    for s in range(steps):
        beta = phi**2
        g = 1.0/(1.0+tau*beta)**2
        g2 = g**2
        ce = c02/(1.0+tau*beta)
        lap = (np.roll(phi,1,0)+np.roll(phi,-1,0)+np.roll(phi,1,1)+np.roll(phi,-1,1)-4*phi)/(dx*dx)
        f = ce*lap + mu2*phi - lam*phi**3
        pn = 2*phi - phi_prev + g2*f*dt**2 - damping*(phi-phi_prev)
        phi_prev = phi.copy()
        phi = pn
        
        if s % 200 == 0:
            pk = np.max(np.abs(phi - phi_eq))
            peaks.append(pk)
            if np.isnan(pk) or pk > 50:
                return "BLOWUP", peaks
    
    if len(peaks) < 3:
        return "SHORT", peaks
    # Compare early vs late
    early = peaks[1]
    late = peaks[-1]
    if late > early * 2.0:
        return "COLLAPSE", peaks
    elif late < early * 0.3:
        return "DISPERSE", peaks
    else:
        return "STABLE", peaks

print(f"{'τ':>5s} {'amp':>6s} {'τ·β_peak':>8s} {'Γ_peak':>10s} {'Γ²_peak':>10s} {'Result':>10s} {'peak_trend':>20s}")
print("-"*75)

for tau in [1.0, 3.0, 5.0, 10.0]:
    for amp in [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0]:
        beta_peak = (phi_eq*(1+amp))**2
        tb = tau * beta_peak
        gp = 1.0/(1+tb)**2
        
        result, peaks = test_lump(tau, amp)
        trend = " → ".join([f"{p:.3f}" for p in peaks[:4]])
        
        print(f"  {tau:4.1f} {amp:6.2f} {tb:8.2f} {gp:10.6f} {gp**2:10.2e} {result:>10s} {trend:>20s}")

# ─── Theoretical critical line ───
print("\n" + "="*70)
print("CRITICAL LINE ANALYSIS")
print("="*70)

print("\nThe critical condition for collapse is when Γ² suppression")
print("kills the dispersive wave operator faster than it can spread.\n")

print("Effective dispersal rate:  R_disp = Γ² · c_eff² / σ²")
print("Effective growth rate:    R_grow = Γ² · 3λ · δφ²")
print("Kinetic freezing:         when Γ² < (σ · ω₀ / c₀)²\n")

print(f"{'τ':>5s} {'β_crit (force)':>15s} {'β_crit (freeze)':>16s}")
print("-"*40)
for tau in [0.5, 1.0, 2.0, 5.0, 10.0]:
    # Force balance: c₀²/(τβσ²) = 3λβ → β = sqrt(c₀²/(3λτσ²))
    sigma = 6.0
    beta_force = np.sqrt(c02 / (3*lam*tau*sigma**2))
    # Freeze: (1+τβ)⁴ > big → τβ ~ few
    beta_freeze = 2.0/tau  # rough: Γ² ~ 0.01 when τβ ~ 2
    print(f"  {tau:4.1f} {beta_force:15.4f} {beta_freeze:16.4f}")

print("\nThe LOWER of the two thresholds determines the critical β*.")
print("For large τ, the freeze mechanism dominates (collapse is easy).")
print("For small τ, the force balance determines it (need more amplitude).")
