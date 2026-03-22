#!/usr/bin/env python3
"""
ALPHA HUNT: Fine Structure Constant from the Clockfield
=========================================================

Strategy: The previous searches tried self-consistency (α = C·Γ²(f(α)))
and found nothing near 137. This attempt takes a DIFFERENT route.

APPROACH 1 — Topological Phase Filtering
  A vortex with winding n=1 has total phase flux 2π.
  The Γ-filter suppresses communication through the frozen core.
  The "effective charge" is the fraction of the 2π flux that
  propagates through the Γ-weighted medium.
  
  q_eff² = [∫ Γ(r) · (n/r) · A(r) · 2πr dr]² / [∫ (n/r) · A(r) · 2πr dr]²
  
  This is a purely geometric ratio — it depends only on the SHAPE
  of the Γ profile, not on any dimensional parameters.

APPROACH 2 — The Running Coupling at the Self-Consistent Scale
  α(D) runs with distance. Is there a natural scale D* where
  the vortex "measures itself"? D* = the scale where the 
  Γ-weighted interaction energy equals the rest energy.
  
APPROACH 3 — Spectral (Fourier) Approach
  The coupling in k-space involves the form factor F(k) = FT[Γ²·A²].
  The dimensionless coupling is α = F(k*)/F(0) at the natural k*.

APPROACH 4 — The Euler-Mascheroni / ln(τβ₀) Connection
  Many fundamental constants involve logarithms and π.
  If α = f(π, e, ln) from some geometric identity...

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""

import numpy as np
from scipy import integrate, optimize, special
import json

ALPHA_PHYS = 1.0 / 137.035999084  # CODATA 2018

print("=" * 70)
print("ALPHA HUNT: Fine Structure Constant from the Clockfield")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════
# APPROACH 1: Topological Phase Filtering
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("APPROACH 1: Topological Phase Filtering")
print("─" * 70)

def vortex_profile(r, xi=1.0):
    """Amplitude profile A(r) = tanh(r/xi)"""
    return np.tanh(r / xi)

def gamma_profile(r, tau_beta0, xi=1.0):
    """Γ(r) = 1/(1 + τβ₀·tanh²(r/ξ))²"""
    beta = vortex_profile(r, xi)**2
    return 1.0 / (1.0 + tau_beta0 * beta)**2

def phase_coupling_ratio(tau_beta0, xi=1.0, r_max=200, n_pts=50000):
    """
    The fraction of phase flux that survives the Γ-filter.
    
    Numerator: ∫ Γ(r) · A(r) dr  (the surviving flux, note 1/r · 2πr = 2π cancels)
    Denominator: ∫ A(r) dr  (the total flux)
    
    α_eff = (numerator/denominator)²  (squared because coupling ~ charge²)
    """
    r = np.linspace(0.01, r_max, n_pts)
    A = vortex_profile(r, xi)
    G = gamma_profile(r, tau_beta0, xi)
    
    num = np.trapezoid(G * A, r)
    den = np.trapezoid(A, r)
    
    ratio = num / den
    return ratio**2  # coupling ~ charge²

print("\nScanning τ·β₀ for α = 1/137...")
print(f"{'τβ₀':>10s} {'α_eff':>12s} {'1/α_eff':>10s} {'Δ from 137':>12s}")
print("-" * 50)

tb_values = np.logspace(-1, 4, 500)
alpha_values_1 = np.array([phase_coupling_ratio(tb) for tb in tb_values])

for tb in [0.5, 1, 2, 5, 10, 12.73, 20, 50, 100, 500, 1000]:
    a = phase_coupling_ratio(tb)
    inv_a = 1.0/a if a > 0 else np.inf
    delta = inv_a - 137.036
    marker = " ← CLOSE!" if abs(delta) < 5 else ""
    print(f"  {tb:8.2f}  {a:12.8f}  {inv_a:10.4f}  {delta:+12.4f}{marker}")

# Find the τβ₀ that gives exactly 1/137
try:
    def target_1(log_tb):
        tb = 10**log_tb
        return phase_coupling_ratio(tb) - ALPHA_PHYS
    
    sol = optimize.brentq(target_1, -1, 4, xtol=1e-12)
    tb_star = 10**sol
    a_check = phase_coupling_ratio(tb_star)
    print(f"\n  ★ τβ₀ = {tb_star:.6f} gives α = {a_check:.10f} (1/α = {1/a_check:.6f})")
    print(f"    Is this a 'natural' value? τβ₀ ≈ {tb_star:.4f}")
except:
    print("\n  No crossing found in this range.")

# ═══════════════════════════════════════════════════════════════════
# APPROACH 2: Γ²-weighted coupling integral (the EM interaction)
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("APPROACH 2: Γ²-weighted Phase Coupling")
print("─" * 70)

def coupling_Gamma_sq(tau_beta0, xi=1.0, r_max=200, n_pts=50000):
    """
    α = ∫ Γ²(r) · [A(r)/r]² · 2πr dr  /  normalization
    
    This is the overlap integral of two vortex phase gradients
    weighted by the Γ² propagator.
    
    Normalization: ∫ [A(r)/r]² · 2πr dr
    """
    r = np.linspace(0.5, r_max, n_pts)
    A = vortex_profile(r, xi)
    G = gamma_profile(r, tau_beta0, xi)
    
    # Phase gradient squared weighted by Γ²
    num = np.trapezoid(G**2 * A**2 / r * 2 * np.pi, r)
    # Unweighted
    den = np.trapezoid(A**2 / r * 2 * np.pi, r)
    
    return num / den

print(f"\n{'τβ₀':>10s} {'α_Γ²':>12s} {'1/α_Γ²':>10s} {'Δ from 137':>12s}")
print("-" * 50)

for tb in [0.5, 1, 2, 5, 10, 12.73, 20, 50, 100, 500, 1000]:
    a = coupling_Gamma_sq(tb)
    inv_a = 1.0/a if a > 0 else np.inf
    delta = inv_a - 137.036
    marker = " ← CLOSE!" if abs(delta) < 5 else ""
    print(f"  {tb:8.2f}  {a:12.8f}  {inv_a:10.4f}  {delta:+12.4f}{marker}")

try:
    def target_2(log_tb):
        tb = 10**log_tb
        return coupling_Gamma_sq(tb) - ALPHA_PHYS
    
    sol2 = optimize.brentq(target_2, -1, 4, xtol=1e-12)
    tb_star2 = 10**sol2
    a_check2 = coupling_Gamma_sq(tb_star2)
    print(f"\n  ★ τβ₀ = {tb_star2:.6f} gives α = {a_check2:.10f} (1/α = {1/a_check2:.6f})")
except:
    print("\n  No crossing found.")

# ═══════════════════════════════════════════════════════════════════
# APPROACH 3: The Running Coupling — Universal Shape
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("APPROACH 3: Running Coupling α(D/ξ) — Parameter-Independent Shape")
print("─" * 70)

def running_coupling(D_over_xi, tau_beta0, xi=1.0, n_pts=20000):
    """
    α(D) = coupling measured at distance D from the vortex core.
    
    This is the Γ²-weighted flux at radius D:
    α(D) = Γ²(D) · [A(D)]² · [1/D]
    
    Normalized by the vacuum value.
    """
    r = D_over_xi * xi
    A = np.tanh(r / xi)
    G = 1.0 / (1.0 + tau_beta0 * A**2)**2
    
    # The coupling at distance D is the Gamma-propagated charge
    # compared to the bare charge
    return G**2 * A**2

def running_coupling_integrated(D_over_xi, tau_beta0, xi=1.0, n_pts=20000):
    """
    α(D) = ∫₀^D Γ²(r)·A²(r)/r · 2πr dr  /  ∫₀^D A²(r)/r · 2πr dr
    
    Cumulative coupling up to scale D.
    """
    r = np.linspace(0.5, D_over_xi * xi, n_pts)
    if len(r) < 2:
        return 1.0
    A = np.tanh(r / xi)
    G = 1.0 / (1.0 + tau_beta0 * A**2)**2
    
    num = np.trapezoid(G**2 * A**2, r)
    den = np.trapezoid(A**2, r)
    
    return num / den if den > 0 else 1.0

print("\nThe shape of α(D/ξ) for different τβ₀:")
D_range = np.logspace(-0.5, 3, 200)

print(f"\n{'D/ξ':>8s}", end="")
for tb in [5, 12.73, 50, 200]:
    print(f"  {'1/α(τβ₀='+str(tb)+')':>18s}", end="")
print()
print("-" * 82)

for D in [0.5, 1, 2, 5, 10, 20, 50, 100, 500]:
    print(f"  {D:6.1f}", end="")
    for tb in [5, 12.73, 50, 200]:
        a = running_coupling_integrated(D, tb)
        inv_a = 1.0/a if a > 1e-15 else np.inf
        print(f"  {inv_a:18.4f}", end="")
    print()

# ═══════════════════════════════════════════════════════════════════
# APPROACH 4: Pure Mathematical / Geometric Constants
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("APPROACH 4: Mathematical Structure")
print("─" * 70)
print("\nCan 1/137 emerge from π, e, and the topology of the problem?")

# Known near-misses from mathematical constants
candidates = {
    "π³ + π²":               np.pi**3 + np.pi**2,
    "4π³ + π²":              4*np.pi**3 + np.pi**2,
    "π⁻¹ · e⁵·²":           np.pi**(-1) * np.exp(5.2),
    "π · e^(π+1)":           np.pi * np.exp(np.pi + 1),
    "2⁸/√(2π·e)":           256 / np.sqrt(2*np.pi*np.e),
    "e^(2π) / (2π)":        np.exp(2*np.pi) / (2*np.pi),
    "29·π·e/(4+π)":         29*np.pi*np.e/(4+np.pi),
    "137 (trivial)":         137,
    "tan(1)·e⁴·π/5":        np.tan(1)*np.e**4*np.pi/5,
    "4π/3 · 10 + 7π/2":     4*np.pi/3 * 10 + 7*np.pi/2,
}

print(f"\n{'Expression':>25s} {'Value':>12s} {'1/Value':>12s} {'Δ from 137.036':>15s}")
print("-" * 70)
for name, val in sorted(candidates.items(), key=lambda x: abs(x[1] - 137.036)):
    delta = val - 137.036
    print(f"  {name:>23s}  {val:12.6f}  {1/val:12.8f}  {delta:+15.6f}")

# ═══════════════════════════════════════════════════════════════════
# APPROACH 5: Self-Consistency at the Vortex's Own Scale
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("APPROACH 5: Self-Consistent Vortex — α from the profile equation")
print("─" * 70)
print("""
The vortex profile A(r) satisfies a nonlinear ODE:
  A'' + A'/r - A/r² + μ²A - λA³ = 0  (static, no Clockfield)
  
WITH the Clockfield (Γ² modulation):
  Γ²(A) · [c_eff²(A) · (A'' + A'/r - A/r²) + μ²A - λA³] = 0

The Γ² drops out for static solutions! But the ENERGY depends on Γ.

The self-consistent condition: the vortex's own Γ-profile determines
its rest energy E_rest and its coupling α. If we require:
  
  E_rest = α · E_Coulomb    (the vortex's self-energy = α times the 
                              bare Coulomb energy of its phase charge)

This gives a SELF-CONSISTENCY EQUATION for τβ₀ in terms of α.
""")

def vortex_energies(tau_beta0, xi=1.0, n_pts=50000, r_max=200):
    """
    Compute rest energy and Coulomb energy of a vortex.
    
    E_rest = ∫ [½c_eff²|∇φ|² + V - V_vac] dV
    E_Coulomb = ∫ ½|∇θ|² dV = ∫ π/r dr  (logarithmically divergent, cut at r_max)
    E_Gamma = ∫ Γ² · ½|∇θ|² dV  (the screened Coulomb energy)
    """
    r = np.linspace(0.01, r_max, n_pts)
    dr = r[1] - r[0]
    A = np.tanh(r / xi)
    dAdr = (1.0 / xi) * (1.0 - np.tanh(r/xi)**2)  # sech²(r/ξ)/ξ
    beta = A**2
    G = 1.0 / (1.0 + tau_beta0 * beta)**2
    c_eff2 = 1.0 / (1.0 + tau_beta0 * beta)
    
    # Gradient energy (radial + angular)
    grad_radial = dAdr**2
    grad_angular = A**2 / r**2  # n=1 winding
    
    # Potential (Mexican hat with φ_eq = 1 for simplicity)
    # V = -μ²β + λβ², V_vac = -μ²β_eq + λβ_eq² = -μ⁴/(4λ)
    # With φ_eq = 1: μ² = λ = 1 (say), V = -β + β², V_vac = -1/4
    V_diff = -(A**2 - 1) + (A**4 - 1)  # V(A) - V_vac, simplified
    # More carefully: V - V_vac = -(A² - 1) + (A⁴ - 1) = -(A²-1)(1 - A² - 1) 
    # Hmm let me just compute directly
    # V(A) = -A² + A⁴
    # V_vac = V(1) = -1 + 1 = 0... 
    # Actually for Mexican hat V = -μ²|φ|² + λ|φ|⁴, minimum at β = μ²/(2λ)
    # Let's use μ² = 2, λ = 1, so β_eq = 1, φ_eq = 1, V_vac = -1+1 = 0... 
    # No: V(φ_eq) = -2·1 + 1·1 = -1. V(0) = 0. So V-V_vac = V(A)-(-1) = -2A²+A⁴+1 = (1-A²)²
    V_diff = (1 - A**2)**2
    
    E_rest = np.trapezoid(2*np.pi*r * (0.5 * c_eff2 * (grad_radial + grad_angular) + V_diff), r)
    E_coulomb_bare = np.trapezoid(2*np.pi*r * 0.5 * grad_angular, r)  # = π·ln(r_max/r_min)
    E_coulomb_screened = np.trapezoid(2*np.pi*r * G**2 * 0.5 * grad_angular, r)
    
    alpha_self = E_coulomb_screened / E_coulomb_bare if E_coulomb_bare > 0 else 0
    
    return E_rest, E_coulomb_bare, E_coulomb_screened, alpha_self

print(f"\n{'τβ₀':>10s} {'E_rest':>10s} {'E_bare':>10s} {'E_screen':>10s} {'α_self':>12s} {'1/α_self':>10s}")
print("-" * 70)

for tb in [1, 2, 5, 10, 12.73, 15, 20, 30, 50, 100, 200, 500, 1000]:
    Er, Eb, Es, a_self = vortex_energies(tb)
    inv_a = 1/a_self if a_self > 1e-15 else np.inf
    delta = inv_a - 137.036
    marker = " ★" if abs(delta) < 5 else ""
    print(f"  {tb:8.2f}  {Er:10.4f}  {Eb:10.4f}  {Es:10.4f}  {a_self:12.8f}  {inv_a:10.4f}{marker}")

# Find exact τβ₀ for α_self = 1/137
try:
    def target_self(log_tb):
        _, _, _, a = vortex_energies(10**log_tb)
        return a - ALPHA_PHYS
    
    sol_self = optimize.brentq(target_self, 0, 3.5, xtol=1e-10)
    tb_self = 10**sol_self
    Er, Eb, Es, a_check = vortex_energies(tb_self)
    print(f"\n  ★ α_self = 1/137.036 at τβ₀ = {tb_self:.6f}")
    print(f"    Check: α = {a_check:.10f}, 1/α = {1/a_check:.6f}")
    print(f"    This means: Γ_vac = {1/(1+tb_self)**2:.8f}")
    print(f"    And: c_eff/c₀ = {1/np.sqrt(1+tb_self):.6f}")
except Exception as e:
    print(f"\n  Could not find crossing: {e}")

# ═══════════════════════════════════════════════════════════════════
# APPROACH 6: 3D vs 2D — Does dimensionality matter?
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("APPROACH 6: Dimensionality — 3D Vortex (String) Coupling")
print("─" * 70)
print("In 3D, a vortex becomes a string. The coupling changes:")
print("  2D: ∫ Γ² · A²/r · 2πr dr  → integrand ~ Γ² · A²")
print("  3D: ∫ Γ² · A²/r · 4πr² dr → integrand ~ Γ² · A² · r")
print("The extra factor of r changes the weighting!")

def coupling_3D(tau_beta0, xi=1.0, r_max=200, n_pts=50000):
    """3D version: the extra r changes the radial weight."""
    r = np.linspace(0.5, r_max, n_pts)
    A = np.tanh(r / xi)
    G = 1.0 / (1.0 + tau_beta0 * A**2)**2
    
    # 3D: angular gradient ∝ A/r, volume element ∝ r² dr
    # So integrand ∝ Γ² · A²/r² · r² = Γ² · A²
    # Wait — same as 2D! The 1/r² from the gradient and r² from volume cancel.
    # But the normalization differs because the total integral ∝ ∫r² dr
    
    # Actually for a vortex STRING in 3D:
    # Energy per unit length = ∫ Γ²(ρ) · A²(ρ)/ρ² · 2πρ dρ  (cylindrical)
    # Same as 2D. But for a MONOPOLE in 3D:
    # Energy = ∫ Γ²(r) · A²(r) · [ℓ(ℓ+1)/r²] · 4πr² dr
    #        = 4πℓ(ℓ+1) ∫ Γ²(r) · A²(r) dr
    
    # Monopole coupling (ℓ=1):
    num_mono = np.trapezoid(G**2 * A**2 * 4*np.pi, r)
    den_mono = np.trapezoid(A**2 * 4*np.pi, r)
    
    # Monopole with 1/r² gradient and r² volume:
    num_3d = np.trapezoid(G**2 * A**2 * r**2, r)
    den_3d = np.trapezoid(A**2 * r**2, r)
    
    return num_mono/den_mono, num_3d/den_3d

print(f"\n{'τβ₀':>10s} {'α_3D_flat':>12s} {'1/α':>10s} {'α_3D_r²':>12s} {'1/α':>10s}")
print("-" * 60)

for tb in [1, 5, 10, 20, 50, 100, 200, 500, 1000]:
    a1, a2 = coupling_3D(tb)
    print(f"  {tb:8.2f}  {a1:12.8f}  {1/a1:10.4f}  {a2:12.8f}  {1/a2:10.4f}")

# Find τβ₀ for 3D coupling = 1/137
try:
    def target_3d(log_tb):
        _, a = coupling_3D(10**log_tb)
        return a - ALPHA_PHYS
    sol_3d = optimize.brentq(target_3d, 0, 3.5, xtol=1e-10)
    tb_3d = 10**sol_3d
    _, a_3d_check = coupling_3D(tb_3d)
    print(f"\n  ★ 3D (r²-weighted): α = 1/137 at τβ₀ = {tb_3d:.6f}")
    print(f"    Check: 1/α = {1/a_3d_check:.6f}")
except Exception as e:
    print(f"\n  3D crossing: {e}")

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("SUMMARY: What Determines τβ₀?")
print("=" * 70)
print("""
Every approach finds that α = 1/137 requires a SPECIFIC value of τβ₀.
The question is: does the Clockfield PREDICT that value, or is it a 
free parameter?

Possible self-consistency conditions that could fix τβ₀:

1. ENERGY BALANCE: The vortex's Γ-screened self-energy equals its rest 
   mass × c². This relates τβ₀ to (μ,λ) which is already constrained 
   by E=mc².

2. TOPOLOGICAL STABILITY: The vortex is stable only if its screened 
   charge exceeds some threshold. This might select τβ₀.

3. COSMOLOGICAL: The noise sea (TADS) amplitude, set by collective 
   Hawking radiation from all defects, determines τβ₀ self-consistently.

4. RENORMALIZATION: The running coupling at the Compton wavelength 
   of the vortex fixes α at low energy.

None of these have been proven to give 1/137. The honest conclusion:
the Clockfield CAN produce 1/137 for a specific τβ₀, but does not 
yet PREDICT that τβ₀ from first principles.
""")

# Save results
results = {
    "approach_1_phase_filter": {
        "description": "Γ-filtered phase flux ratio",
    },
    "approach_5_self_energy": {
        "description": "Screened/bare Coulomb ratio",
    }
}

try:
    results["approach_1_phase_filter"]["tb_star"] = float(tb_star)
    results["approach_5_self_energy"]["tb_star"] = float(tb_self)
except:
    pass

with open("alpha_hunt_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Saved: alpha_hunt_results.json")
print("Done.")
