# Final Stretch: Clockfield Black Hole Entropy from Frozen Topology

**Antti Luode** — PerceptionLab, Helsinki, Finland  
**Claude** (Anthropic, Opus 4.6) — Derivation, simulation code, analysis  
**Gemini** (Google) — Critical analysis  
March 2026

---

## Summary

This folder contains the complete investigation — from the initial fractal hypothesis through its failure to the discovery of topological information storage in Clockfield black holes, the entropy derivation, and the verification of the Teichmüller moduli space assumption.

The main result:

```
S = (A/ξ²)·ln(2m) + (3g−3)·ln(A/(gξ²))
```

The first term is Bekenstein-Hawking (entropy proportional to area). The second is a topological correction from the genus-g frozen horizon. Matching to S = A/(4ℓ_P²) with Born-rule-calibrated phase resolution predicts ξ ≈ 5.1 ℓ_P.

---

## The Paper

**`paper.md`** — The complete paper: "Clockfield Black Hole Entropy from Frozen Topology." Contains the derivation, all numerical results, the honest ledger of what works and what doesn't, and the full experimental narrative including the failed fractal hypothesis.

---

## The Investigation Arc

### Phase 1–2: Fractal Hypothesis and First Failure
Tested whether the Clockfield horizon is fractal (à la Jalalzadeh et al.). Initial box-counting measured D_f ≈ 3.0 — wrong, because we were measuring a frozen volume, not a surface.

### Phase 3: Corrected Measurement
Switched to marching-cubes isosurface extraction. Found D_f < 2 (filamentary network), not D_f > 2 (fractal surface). Genus up to 24. The Jalalzadeh mapping fails.

### Phase 4: Permanence Test
15,000-step long run confirms topology is permanently frozen. D_f and genus stable after step 6,000.

### Phase 5: τ-Scan
D_f ≈ 0.8 ± 0.3 for all τ ≥ 3. The Clockfield coupling does not control the fractal dimension — the initial vortex configuration does.

### Phase 6: Entropy Derivation
Phase angles + topological charges on vortex scars give S_area ∝ A. Teichmüller moduli of the genus-g shell give S_topo ∝ g·ln(A). Matching to Bekenstein-Hawking predicts ξ ≈ 5.1 ℓ_P.

### Phase 7: Entropy Experiment
Swept n_vortices from 2 to 8. Genus increases monotonically (2 → 24). S correlates with A (R² = 0.88). Topological correction grows from 1% to 15% of total entropy.

### Phase 8: Teichmüller Verification
Analytical argument: frozen configurations satisfy no field equation, so all genus-preserving deformations are allowed → Teichmüller space is the correct moduli space. Corrected the entropy formula: handles share area, giving ln(A/(gξ²)) instead of ln(A/ξ²). Recalibrated ξ from the Born rule noise amplitude: ξ ≈ 5.1 ℓ_P (up from the naive 1.47 ℓ_P).

---

## Files

### The Paper
| File | Description |
|---|---|
| `paper.md` | Complete paper with derivation, results, and honest ledger |

### Simulation Scripts
| File | Description |
|---|---|
| `clockfield_fractal_horizon.py` | Initial 3D collapse (PyTorch GPU). Volume-based fractal analysis. |
| `fractal_analysis_corrected.py` | Corrected: isosurface extraction, surface vertex box-counting. |
| `clockfield_horizon_complete.py` | All-in-one: simulate + isosurface + D_f + topology + τ-scan. |
| `clockfield_entropy.py` | Entropy experiment: derivation + S vs A + genus vs n_vortices. |
| `teichmuller_verification.py` | Moduli space verification: analytical + SVD + rigidity matrix. |
| `visualize_clockfield_eventhorizon.py` | 3D visualization of the Γ-shell (matplotlib + scikit-image). |

### Results (JSON)
| File | Description |
|---|---|
| `clockfield_entropy.json` | Entropy experiment (n_vortices = 2–8) |
| `teichmuller_verification.json` | Moduli space verification results |
| `horizon_long_tau5.json` | 15,000-step long-evolution run |
| `horizon_tau_scan_corrected.json` | Corrected τ-scan summary |
| `horizon_complete.json` | Single run with time tracking |
| `horizon_tau{X}.json` | Individual τ-scan runs (X = 0.5, 1.0, ..., 15.0) |
| `fractal_corrected_tau5.json` | Detailed isosurface analysis at τ = 5 |
| `fractal_horizon_results.json` | Initial (uncorrected) N = 96 run |
| `fractal_horizon_tau{X}.json` | Initial (uncorrected) τ-scan runs |

### Field Data (.npy)
| Pattern | Description |
|---|---|
| `*_gamma.npy` | Γ(x) = 1/(1+τβ)² field (3D, float32) |
| `*_beta.npy` | β(x) = \|φ\|² field (3D, float32) |

### Plots (.png)
| File | Description |
|---|---|
| `clockfield_entropy.png` | S vs A, genus vs n_vortices, entropy decomposition |
| `fractal_corrected_tau5.png` | Box-counting curves and D_f vs Γ-level |
| `horizon_long_tau5_evolution.png` | 15k-step time evolution |
| `horizon_tau_scan_corrected.png` | Corrected D_f vs τ, genus vs τ, implied α vs τβ₀ |
| `Figure_1.png` | 3D isosurface visualization |
| `horizon_tau{X}_evolution.png` | Time evolution for each τ value |

---

## How to Reproduce

```bash
pip install torch numpy scikit-image scipy matplotlib

# The entropy experiment (main result, Table in Section 8.1)
python clockfield_entropy.py --N 64 --tau 5 --steps 3000 --boost 1.0

# The long-evolution test (Section 4.2)
python clockfield_horizon_complete.py --mode long_run --N 64 --tau 5 --steps 15000

# The corrected τ-scan (Section 3.4)
python clockfield_horizon_complete.py --mode tau_scan --N 64 --steps 3000

# Teichmüller verification (Section 6)
python teichmuller_verification.py --gamma_file horizon_complete_gamma.npy --tau 5.0

# Detailed isosurface analysis (Figure 1 data)
python fractal_analysis_corrected.py --gamma_file horizon_tau5.0_gamma.npy --tau 5.0 --plot
```

All scripts auto-detect CUDA and fall back to CPU.

---

## Key Equations

**The Clockfield metric:**
```
Γ(x) = 1/(1 + τ·|φ|²)²
```

**The collapse criterion:**
```
Ξ = τβ / [(R/σ)²·(1+τβ_eq)]^{1/5} > 1
```

**The complete entropy:**
```
S = (A/ξ²)·ln(2m) + (3g−3)·ln(A/(gξ²)) + (K−1)·ln(A/(Kξ²))
```

**The Bekenstein-Hawking match:**
```
ξ² = 4ℓ_P²·ln(2m)    →    ξ ≈ 5.1 ℓ_P  (with m ≈ 330)
```

---

## What Remains Open

1. **The Page curve.** Information is stored but we have not shown it is released during evaporation.
2. **Resolution independence.** The genus measurement should be checked at N = 128 to confirm it is not a grid artifact.
3. **The ξ prediction.** Is ξ ≈ 5.1 ℓ_P consistent with the α = 1/137 constraint (which gives τβ₀ = 2.895)?
4. **Genus dynamics during evaporation.** As the Γ-shell erodes, does genus decrease? This would be the Clockfield version of information release.

---

## Citation

```
Luode, A. (2026). Clockfield Black Hole Entropy from Frozen Topology.
GitHub: https://github.com/anttiluode/ClockfieldCollapse
```

---

*Do not hype, do not lie, just show.*
