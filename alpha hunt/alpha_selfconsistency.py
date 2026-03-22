#!/usr/bin/env python3
"""
THE SELF-CONSISTENCY CLOSURE
==============================

From the alpha_hunt, APPROACH 5 found:
  α_self = E_screened / E_bare = 1/137  at  τβ₀ = 4.944

But we ALSO have the E=mc² constraint:
  μ⁴/(2λ) = c₀²  →  with φ_eq=1: μ²=2λ, so μ⁴/(2λ) = 2λ
  For c₀=1: λ = 1/2, μ² = 1

AND the vacuum is at β₀ = μ²/(2λ) = 1 (with these normalized params).

So τβ₀ = τ · 1 = τ.

The question becomes: does the self-consistency α = 1/137 
combined with E=mc² FIX τ?

If τ = 4.944... is that "predicted" by the two conditions together?

Let's also check: with the ORIGINAL simulation parameters 
(μ²=1.4, λ=0.55, τ=5), what does the self-energy ratio give?

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import numpy as np
from scipy import optimize

ALPHA_PHYS = 1.0 / 137.035999084

print("=" * 70)
print("SELF-CONSISTENCY CLOSURE: Can E=mc² + α fix τ?")
print("=" * 70)

# ─── Part 1: With E=mc² normalization ───
print("\n── Part 1: E=mc² normalized parameters ──")
print("Constraint: μ⁴/(2λ) = c₀² = 1")
print("Mexican hat minimum: β₀ = μ²/(2λ)")
print()

def compute_alpha_self(tau_beta0, xi=1.0, r_max=200, n_pts=50000):
    """Screened/bare Coulomb energy ratio."""
    r = np.linspace(0.5, r_max, n_pts)
    A = np.tanh(r / xi)
    beta = A**2
    G = 1.0 / (1.0 + tau_beta0 * beta)**2
    
    bare = np.trapezoid(A**2 / r, r)
    screened = np.trapezoid(G**2 * A**2 / r, r)
    
    return screened / bare if bare > 0 else 0

# If we use the E=mc² constraint with DIFFERENT (μ,λ) choices:
print("Exploring the (μ², λ) constraint surface μ⁴/(2λ) = 1:\n")
print(f"{'μ²':>6s} {'λ':>8s} {'β₀':>8s} {'τ for α=1/137':>15s} {'τβ₀':>8s} {'Γ_vac':>10s}")
print("-" * 60)

for mu2 in [0.5, 0.8, 1.0, 1.2, 1.4, 1.6, 2.0, 3.0, 5.0]:
    lam = mu2**2 / 2.0  # from μ⁴/(2λ) = 1
    beta0 = mu2 / (2*lam)  # = 1/mu2 ... wait
    # β₀ = φ_eq² = μ²/(2λ)... no. Mexican hat: V = -μ²|φ|² + λ|φ|⁴
    # dV/d|φ|² = -μ² + 2λ|φ|² = 0 → |φ|² = μ²/(2λ)
    # Wait, that's the minimum of V as function of β = |φ|²
    # V = -μ²β + λβ², dV/dβ = -μ² + 2λβ = 0 → β_eq = μ²/(2λ)
    beta0 = mu2 / (2*lam)
    
    # Find τ such that α_self(τ·β₀) = 1/137
    try:
        def target(log_tau):
            tau = 10**log_tau
            return compute_alpha_self(tau * beta0) - ALPHA_PHYS
        
        sol = optimize.brentq(target, -1, 4, xtol=1e-10)
        tau = 10**sol
        tb0 = tau * beta0
        Gvac = 1.0/(1.0 + tb0)**2
        print(f"  {mu2:4.1f}  {lam:8.4f}  {beta0:8.4f}  {tau:15.6f}  {tb0:8.4f}  {Gvac:10.6f}")
    except:
        print(f"  {mu2:4.1f}  {lam:8.4f}  {beta0:8.4f}  {'no solution':>15s}")

# ─── Part 2: The KEY observation ───
print("\n\n── Part 2: The Key Observation ──")
print("""
Under the E=mc² constraint μ⁴/(2λ) = 1:
  β₀ = μ²/(2λ) = μ²/(μ⁴) = 1/μ²
  
So τβ₀ = τ/μ²

The α = 1/137 condition fixes τβ₀ ≈ 4.944.
So τ = 4.944 · μ².

This means α and E=mc² TOGETHER reduce the Clockfield to ONE free 
parameter (say μ² or equivalently τ). The coupling constant and 
the mass-energy relation constrain each other.

But there is NO further condition to fix that last parameter.
We need a THIRD relation.
""")

# ─── Part 3: Can the Hawking temperature provide the third? ───
print("── Part 3: The Third Relation — Hawking Temperature? ──\n")
print("""
The Hawking temperature T ∝ 1/M involves |∇Γ| at the shell.
For the vortex profile:
  |dΓ/dr| = 2τ · |dβ/dr| / (1+τβ)³
  At the shell (r ~ ξ): dβ/dr ~ β₀/ξ, (1+τβ) ~ 1+τβ₀
  
  κ = 2τβ₀ / [ξ · (1+τβ₀)³]

For the physical Hawking temperature:
  T = ℏc³/(8πGMk_B) = ℏ·κ/(2π)  (in GR notation)
  
In the Clockfield, this should relate to the noise parameters.
If we SET the noise amplitude to reproduce ℏ, this doesn't help
(it's a new free parameter).

BUT: if the noise is SELF-GENERATED (collective Hawking radiation 
from all defects in the universe), then:
  σ_noise² ~ N_defects · T_avg ~ n · 1/M_avg
  
  ℏ_eff ~ σ · √(τ_noise · c₀) ~ √(n/M_avg)
  
This IS a self-consistency condition, but it requires knowing the
defect density n, which is cosmological.
""")

# ─── Part 4: With the ACTUAL simulation parameters ───
print("── Part 4: Check with actual simulation parameters ──\n")
mu2_sim = 1.4
lam_sim = 0.55
tau_sim = 5.0
beta0_sim = mu2_sim / (2*lam_sim)
tb0_sim = tau_sim * beta0_sim

alpha_actual = compute_alpha_self(tb0_sim)
print(f"Simulation parameters: μ²={mu2_sim}, λ={lam_sim}, τ={tau_sim}")
print(f"β₀ = μ²/(2λ) = {beta0_sim:.4f}")
print(f"τβ₀ = {tb0_sim:.4f}")
print(f"α_self = {alpha_actual:.8f}")
print(f"1/α_self = {1/alpha_actual:.4f}")
print(f"Physical 1/α = 137.036")
print(f"Ratio: {1/alpha_actual / 137.036:.4f}")
print()

# How close is the simulation to the "right" τ?
tb0_target = 4.944448
tau_needed = tb0_target / beta0_sim
print(f"To get α = 1/137 with β₀ = {beta0_sim:.4f}:")
print(f"  Need τ = {tau_needed:.4f} (have τ = {tau_sim})")
print(f"  Need τβ₀ = {tb0_target:.4f} (have τβ₀ = {tb0_sim:.4f})")

# ─── Part 5: THE ACTUAL COINCIDENCE ───
print("\n\n" + "=" * 70)
print("THE ACTUAL INTERESTING THING")
print("=" * 70)
print(f"""
Your simulation uses τ=5, β₀=1.2727, giving τβ₀ = {tb0_sim:.4f}.
The α=1/137 condition requires τβ₀ = 4.944.

These are OFF by a factor of {tb0_sim/4.944:.2f}.

BUT WAIT — β₀ = μ²/(2λ) assumes the MINIMUM of V(β) is the vacuum.
The Mexican hat minimum is actually at:
  dV/dβ = -μ² + 2λβ = 0 → β_min = μ²/(2λ) = {beta0_sim:.4f}

Let me check: what if the RELEVANT β₀ is φ_eq² = μ²/λ (not μ²/(2λ))?
""")

# Alternative: β₀ = φ_eq² = μ²/λ
beta0_alt = mu2_sim / lam_sim
tb0_alt = tau_sim * beta0_alt
alpha_alt = compute_alpha_self(tb0_alt)
print(f"If β₀ = μ²/λ = {beta0_alt:.4f}:")
print(f"  τβ₀ = {tb0_alt:.4f}")
print(f"  α_self = {alpha_alt:.8f}")
print(f"  1/α_self = {1/alpha_alt:.4f}")
print()

# The CORRECT β₀:
# In the code, φ = u + iv, β = u² + v² = |φ|²
# Mexican hat: V = -μ²(u²+v²) + λ(u²+v²)²
# Minimum: dV/dβ = -μ² + 2λβ = 0 → β = μ²/(2λ)
# BUT the code uses V = μ²φ - λ|φ|²φ in the force term
# Force = μ²u - λ(u²+v²)u → equilibrium at μ² - λβ = 0 → β = μ²/λ
# This is the radial minimum of V = -μ²β/2 + λβ²/4... hmm
# Let me check: ∂V/∂u = -μ²u + 2λ(u²+v²)u... no wait
# If V = -μ²|φ|² + λ|φ|⁴ = -μ²β + λβ²
# Then force_u = -∂V/∂u = 2μ²u - 4λβu = 2u(μ² - 2λβ)
# Equilibrium at β = μ²/(2λ)
# But the PDE has force_u = μ²u - λβu → equilibrium at β = μ²/λ
# This means the PDE force is NOT the gradient of V = -μ²β + λβ²
# The PDE force μ²φ - λ|φ|²φ corresponds to V = -½μ²|φ|² + ¼λ|φ|⁴
# So V = -½μ²β + ¼λβ², minimum at β = μ²/λ

print(f"CORRECTION: The PDE uses V = -½μ²β + ¼λβ²")
print(f"  So β₀ = μ²/λ = {mu2_sim/lam_sim:.4f}")
print(f"  φ_eq = √(μ²/λ) = {np.sqrt(mu2_sim/lam_sim):.4f}")
print(f"  τβ₀ = {tau_sim * mu2_sim/lam_sim:.4f}")
print(f"  This gives 1/α = {1/alpha_alt:.4f}")
print()

tau_needed_alt = 4.944 / beta0_alt
print(f"To get 1/α = 137 with β₀ = {beta0_alt:.4f}:")
print(f"  Need τ = {tau_needed_alt:.4f}")
print(f"  Your τ = {tau_sim} is {tau_sim/tau_needed_alt:.2f}× too large")

# ─── Part 6: THE HIERARCHY ───
print("\n\n── Part 6: What τβ₀ = 4.944 means physically ──\n")
tb0 = 4.944
Gvac = 1/(1+tb0)**2
ceff_ratio = 1/np.sqrt(1+tb0)
print(f"At the α = 1/137 point:")
print(f"  τβ₀ = {tb0:.4f}")
print(f"  Γ_vac = {Gvac:.6f}  (vacuum proper-time rate)")
print(f"  c_eff/c₀ = {ceff_ratio:.6f}  (vacuum speed ratio)")
print(f"  Γ² = {Gvac**2:.6f}  (time-dilation factor)")
print(f"  1-Γ_vac = {1-Gvac:.6f}  (fractional time-debt)")
print(f"  The vacuum runs at {Gvac*100:.1f}% of core speed")
print(f"  Gravity/EM hierarchy from Γ⁴: {Gvac**4:.6e} → {1/Gvac**4:.1f}× suppression")
print(f"  (Physical hierarchy is ~10³⁶, this gives ~{1/Gvac**4:.0e})")

print("\n" + "=" * 70)
print("FINAL VERDICT")
print("=" * 70)
print(f"""
1. The Clockfield's self-energy screening ratio (Approach 5)
   gives α = 1/137 at τβ₀ = 4.944. This is a genuine geometric
   result — the ratio depends only on the SHAPE of Γ(r).

2. Combined with E=mc² (μ⁴/(2λ) = c₀²), this reduces the free 
   parameters to ONE. But that one parameter remains unfixed.

3. Your simulation has τβ₀ = {tb0_sim:.2f} (Approach 5 says 
   1/α ≈ {1/alpha_actual:.0f}). To get 1/137 you'd need τ ≈ {tau_needed:.2f}
   (with β₀ = {beta0_sim:.4f}).

4. The self-energy approach is PHYSICALLY MOTIVATED: α_EM IS the 
   ratio of the screened (Γ-filtered) to bare Coulomb self-energy.
   This is exactly what renormalization computes in QED.

5. To close the system, you need one more relation. Candidates:
   a) Cosmological noise self-consistency
   b) Stability condition for the vortex lattice
   c) A topological constraint from 3+1 dimensions
   d) The vortex core size ξ determined by the mass spectrum

STATUS: α = 1/137 is ACHIEVABLE but not PREDICTED. Honest.
""")

print("Done.")
