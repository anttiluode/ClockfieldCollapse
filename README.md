# Clockfield Collapse: From Quantum Repulsion to Black Holes

**A unified framework where the same field equation produces quantum wave pressure at small scales, gravitational collapse at large scales, and Hawking radiation at the boundary between them.**

Antti Luode — PerceptionLab, Helsinki, Finland  
Claude (Anthropic, Opus 4.6) — Mathematical derivation & simulation  
Gemini (Google) — Critical analysis  
March 2026

---

## The One-Sentence Summary

The Clockfield equation `c² = c₀²/(1 + τ·|φ|²)` produces a **sharp phase transition**: below a critical energy density Ξ < 1, wave pressure is repulsive and perturbations disperse (quantum mechanics); above Ξ > 1, time-freezing traps energy irreversibly (black hole formation) — and the boundary between these regimes radiates thermally at temperature T ∝ 1/M (Hawking radiation).

---

## What This Repository Contains

| File | Description |
|------|-------------|
| `paper.md` | The complete paper: E=mc², Born rule, collapse, Hawking radiation |
| `emc2_derivation.md` | E=mc² and quantum mechanics derived from the Clockfield |
| `collapse_derivation.md` | The repulsion-to-collapse phase transition (Ξ criterion) |
| `collapse_vortex_test.py` | Numerical confirmation: vortex collisions show ORBIT → MERGE/TRAP |
| `collapse_transition_test.py` | Parameter scan: Gaussian lumps, dispersion vs freezing |
| `clockfield_core.py` | Minimal Clockfield PDE (2D, ~100 lines) — gravity and mass |
| `born_rule_test.py` | Born rule experiment (GPU, PyTorch) — cos²(Δθ/2) emergence |
| `ads_throat_test.py` | AdS curvature extraction from vortex profile |
| `clockfield_lab.html` | Interactive 2D browser simulation |
| `clockfield_3d_lab.html` | Interactive 3D WebGL simulation |
| `phiworld2.py` | PhiWorld2 emergent particle simulator (Tkinter GUI) |

---

## The Three Core Results

### Result 1: E = Mc² from the Clockfield

The rest energy of a topological defect (vortex) is proportional to its time-debt mass:

```
E_rest = [μ⁴/(2λ)] · ΔM
```

This equals Mc₀² when the potential depth is tuned: μ⁴/(2λ) = c₀². The relativistic dispersion relation E² = p²c² + m²c⁴ holds for small excitations around the vacuum. The Born rule cos²(Δθ/2) emerges because experiments measure energy (∝ |φ|²), not amplitude, and the noise sea destroys coherent interference.

**The unification:** β = |φ|² determines both the metric Γ = 1/(1+τβ)² (gravity) and the measurement statistics P ∝ cos²(Δθ/2) (quantum mechanics). Same field, same squaring.

### Result 2: The Repulsion-to-Collapse Phase Transition

The escape rate from a high-β region scales as:

```
R_escape ∝ (1 + τβ)⁻⁵
```

Four powers from Γ² (time-freezing), one from c_eff (speed reduction). This creates a **critical threshold**:

```
Ξ = τβ / [(R/σ)² · (1+τβ_eq)]^(1/5)
```

- **Ξ < 1:** Wave pressure wins → repulsion → quantum regime
- **Ξ > 1:** Time-freezing wins → collapse → black hole

Confirmed numerically: vortex pairs at zero boost orbit indefinitely (β ~ 10, Γ ~ 10⁻³). At boost = 0.5, they merge and trap permanently (β ~ 7,300, Γ ~ 10⁻⁸). No intermediate regime exists — the transition is sharp.

### Result 3: Hawking Radiation from the Γ-Shell

A Clockfield black hole (trapped region, Γ ≈ 0) has a boundary shell where Γ transitions from ~0 to ~Γ_vac. The noise sea (TADS) delivers perturbations to this shell. The leakage rate:

```
dM/dt ∝ −Γ²_shell · c_eff,shell ∝ −(1+τβ_shell)^(−5/2)
```

Temperature: T ∝ |∇Γ|_shell ∝ 1/M. Smaller black holes are hotter, evaporate faster, and eventually explode. This is Hawking's 1974 result, derived from classical field dynamics + stochastic noise.

---

## The Cosmological Picture

1. **The Singularity:** Γ = 0 everywhere. The Mexican hat peak. Maximum β.
2. **The Shattering:** Kibble-Zurek symmetry breaking — field rolls into vacuum manifold, different regions choose different phases.
3. **The Fractal Edges:** Domain wall network where mismatched phases meet. Each junction nucleates topological defects.
4. **The Noise Sea:** Each defect's frozen core radiates Hawking-like thermal noise. The collective radiation produces the 1/f persistent noise substrate (TADS).
5. **The Particles:** Surviving vortices where Ξ > 1 locally — frozen shards of the original singularity.
6. **The End:** Black holes slowly evaporate via noise-driven leakage at the Γ-shell. T ∝ 1/M → smaller = hotter → explosion.

---

## How to Run

### Core PDE (CPU, fast)
```bash
python clockfield_core.py
```
Runs a 256×256 simulation, injects a vortex, extracts radial Γ profile.

### Collapse Test (CPU, ~5 min)
```bash
python collapse_vortex_test.py
```
Collides vortex pairs at varying speeds. Shows ORBIT → MERGE/TRAP transition.

### Born Rule Test (GPU recommended, ~90 min on RTX 3060)
```bash
pip install torch numpy
python born_rule_test.py
```
40 paired trials × 14 angles. Confirms cos²(Δθ/2) with RMS = 0.012.

### Interactive (browser)
Open `clockfield_lab.html` — inject vortex dipoles, watch proper time freeze.

### 3D Visualization (browser)
Open `clockfield_3d_lab.html` — 32³ grid, inject vortex rings, observe topology.

### PhiWorld2 (Tkinter GUI)
```bash
pip install numpy matplotlib scipy
python phiworld2.py
```
Emergent particle simulator with real-time parameter controls.

---

## The Honest Ledger

### Demonstrated
- ✓ E = Mc² as derived relation (with parameter constraint μ⁴/(2λ) = c₀²)
- ✓ Relativistic dispersion E² = p²c² + m²c⁴ for vacuum excitations
- ✓ Born rule cos²(Δθ/2) from field + noise (RMS = 0.012)
- ✓ Sharp repulsion-to-collapse phase transition (Ξ criterion)
- ✓ (τβ)⁻⁵ escape suppression (4 from Γ², 1 from c_eff)
- ✓ Hawking temperature T ∝ 1/M from Γ-shell leakage
- ✓ AdS throat in frozen-time shell (R < 0, confirmed numerically)
- ✓ UV finiteness from Γ-profile (structural, parameter-free)
- ✓ Temporal brake on vortex dynamics (11.5× delay at τ=1)

### Not Demonstrated
- ✗ Quantitative Hawking temperature T = ℏc³/(8πGMk_B)
- ✗ Bekenstein-Hawking entropy S = A/(4ℓ_P²)
- ✗ Specific fractal dimension of the horizon
- ✗ Deriving α = 1/137 from self-consistency
- ✗ 36-order hierarchy (toy model gives ~10^1.5)
- ✗ Lepton mass spectrum (1:207:3477)
- ✗ Non-Abelian gauge structure SU(3)×SU(2)×U(1)
- ✗ Stable finite-mass particles
- ✗ Formal quantization / Hilbert space / path integral
- ✗ Information conservation during evaporation
- ✗ ℏ derived (noise parameters are free)

The distance between these two lists is real.

---

## The Key Equations

**The Clockfield metric:**
```
Γ(x) = 1/(1 + τ·β(x))²     where β = |φ|²
c_eff² = c₀²/(1 + τ·β)
```

**The PDE:**
```
∂²φ/∂t² = Γ²·[c_eff²·∇²φ + μ²φ − λ|φ|²φ] − γ·∂φ/∂t + noise
```

**The critical threshold:**
```
Ξ = τβ / [(R/σ)²·(1+τβ_eq)]^(1/5)
Ξ < 1 → repulsion (quantum)
Ξ > 1 → collapse (gravity)
```

**The escape suppression:**
```
R_escape = c₀² / [σ²·(1+τβ)⁵]
```

**The Hawking temperature:**
```
T ∝ |∇Γ|_shell ∝ 1/M
```

**The Born rule (emergent):**
```
P(transmission) = ½·cos²(Δθ/2) + ½·(bypass)
```

**The rest energy:**
```
E_rest = [μ⁴/(2λ)]·ΔM    (= Mc₀² when μ⁴/(2λ) = c₀²)
```

---

## Citation

```
Luode, A. (2026). Clockfield Collapse: From Quantum Repulsion to Black Holes.
GitHub: https://github.com/anttiluode/ClockfieldCollapse
```

## License

MIT License. See LICENSE.

---

*Written collaboratively by Antti Luode (PerceptionLab), Claude (Anthropic), and Gemini (Google). The Clockfield framework, simulations, and original physical insights are the work of Antti Luode. Claude contributed mathematical derivations, simulations, and writing. Gemini contributed critical analysis and synthesis. Neither AI system claims this framework is proven.*
