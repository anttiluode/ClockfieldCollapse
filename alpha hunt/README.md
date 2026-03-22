# Hunt for α = 1/137 from the Clockfield

**Antti Luode** — PerceptionLab, Helsinki  
**Claude** (Anthropic, Opus 4.6) — Computation & analysis  
March 2026

---

## The Question

Can the Clockfield's single coupling parameter τ produce the fine-structure constant α = 1/137.036 from self-consistency, rather than as a free input?

## The Answer (Honest)

**Partially.** The Clockfield produces a natural geometric definition of α as the screened-to-bare Coulomb self-energy ratio of a vortex. Combined with E=mc², this reduces the framework from 4 free parameters to 1. But that last parameter (τβ₀) is not fixed from first principles in the 2D toy model.

## The Key Result

The fine-structure constant emerges as a Γ²-screening ratio:

```
α = ∫ Γ²(r) · A²(r)/r dr  /  ∫ A²(r)/r dr
```

This equals 1/137.036 at τβ₀ = 2.863. The physics: the bare topological charge (2π winding) is screened by the frozen-time propagator Γ², and α measures the fraction that survives. This is exactly what renormalization computes in QED.

## The Constraint Count

| Constraint | What it fixes | Remaining free params |
|---|---|---|
| None | — | 4 (μ, λ, τ, c₀) |
| E=mc²: μ⁴/(2λ) = c₀² | Relates μ and λ | 3 |
| α = 1/137: τβ₀ = 2.863 | Relates τ to β₀ | 1 |
| ??? | Would fix everything | 0 |

## The Third Constraint Search

We tested 12 candidates for the missing third relation. None independently produce τβ₀ = 2.863.

**Closest candidate:** Marginal collapse stability (Ξ = 1 at the vortex edge) gives τβ₀ = 2.172. At the α = 1/137 point, the vortex sits at Ξ = 1.28 — barely supercritical, 28% above the collapse threshold. The gap narrows in 3D (from ratio 1.32 to 1.11) but does not close.

**What didn't work:** Derrick's virial condition (τβ₀ = 24.7, way off). Integrated escape-accumulation balance (never reaches 1). Bekenstein entropy bound (requires ℏ as input). Classical electron radius condition (no match). UV fixed point (none exists — coupling runs monotonically). G/α hierarchy (requires τβ₀ ~ 10⁹, incompatible).

## Files

| File | Description |
|---|---|
| `alpha_hunt.py` | Six approaches to deriving α from the Clockfield geometry |
| `alpha_selfconsistency.py` | E=mc² + α constraint surface analysis |
| `alpha_hunt_final.py` | Clean summary with plots |
| `third_constraint.py` | Systematic search through 12 candidates for the missing relation |
| `alpha_closure.py` | Deep dive on the gap between Ξ=1 and α=1/137 |
| `alpha_hunt_plot.png` | 1/α vs τβ₀ for all approaches + vortex Γ profile at α point |
| `alpha_constraint_surface.png` | E=mc² and α constraint lines in (μ², τ) space |
| `third_constraint_plot.png` | All constraint curves — hunting the triple point |
| `alpha_hunt_complete.json` | Machine-readable results |

## What This Means

The Clockfield framework is more constrained than most approaches at this stage — one free parameter, with a clear geometric mechanism for α. The missing closure likely requires 3D vortex topology, many-body cosmological input, or non-Abelian gauge structure. It cannot be faked within the 2D scalar model.

---

*Do not hype, do not lie, just show.*
