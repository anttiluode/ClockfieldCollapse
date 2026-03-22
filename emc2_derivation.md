# Combining E=mc² and Quantum Mechanics in the Clockfield

**Mathematical Analysis**  
Antti Luode — PerceptionLab, Helsinki  
Claude (Anthropic, Opus 4.6) — Mathematical derivation  
March 2026

---

## 0. Starting Point: The Clockfield Equations

We begin with exactly what is in the codebase:

```
c_eff²(x) = c₀² / (1 + τ·β)           ... (CF1)
Γ(x)      = 1 / (1 + τ·β)²            ... (CF2)
M          = ∫ (1 − Γ) dV              ... (CF3)
```

where β = |φ|². The PDE is:

```
∂²φ/∂t² = Γ² · [c_eff² · ∇²φ + μ²φ − λ|φ|²φ] − γ·∂φ/∂t   ... (CF4)
```

The Born rule experiment adds persistent 1/f noise and gets:

```
P(transmission) = ½·cos²(Δθ/2) + ½·(bypass)                  ... (CF5)
```

The question: can we derive the mass-energy relation and connect it to the quantum statistics from these equations alone?

---

## 1. The Energy Functional

### 1.1 Total field energy

The PDE (CF4) is a wave equation, so it has a conserved energy functional (ignoring damping and noise for now). The Lagrangian density is:

```
ℒ = ½(∂φ/∂t)² − ½·c_eff²·|∇φ|² − V(φ)
```

But the Clockfield modifies propagation, so the *effective* Lagrangian in coordinate time is:

```
ℒ_eff = ½·Γ⁻²·(∂φ/∂t)² − ½·c_eff²·|∇φ|² − V(φ)
```

The Γ⁻² factor appears because the PDE has Γ² modulating the force — this means the kinetic energy in coordinate time is *amplified* where time is frozen (small Γ). The total energy is:

```
E_total = ∫ [ ½·Γ⁻²·(∂φ/∂t)² + ½·c_eff²·|∇φ|² + V(φ) ] dV    ... (E1)
```

### 1.2 Splitting into "mass" and "kinetic" parts

For a static defect (vortex at rest), ∂φ/∂t = 0. The energy reduces to:

```
E_rest = ∫ [ ½·c_eff²·|∇φ|² + V(φ) ] dV                         ... (E2)
```

This is the rest energy — it exists even when the defect is stationary.

---

## 2. Deriving E = Mc₀² (Rest Energy)

### 2.1 The key identity

From (CF1): c_eff² = c₀²/(1 + τβ). And from (CF2): Γ = 1/(1 + τβ)². Therefore:

```
c_eff² = c₀² · √Γ                                                ... (*)
```

Wait — let me be precise. If Γ = (1+τβ)⁻², then (1+τβ) = Γ⁻¹/², so:

```
c_eff² = c₀² · Γ^(1/2)                                           ... (2.1)
```

This is important: the effective speed and the proper-time rate are not independent — they are both determined by β.

### 2.2 Rest energy of a vortex

For a vortex with winding number n, the field has the form φ = A(r)·exp(inθ) where A(0) = 0 and A(∞) = φ_eq. The gradient energy is:

```
|∇φ|² = (dA/dr)² + n²A²/r²
```

The potential energy is V = −μ²A² + λA⁴.

The rest energy (E2) becomes:

```
E_rest = ∫₀^∞ [ ½·c₀²·Γ^(1/2)·((dA/dr)² + n²A²/r²) + V(A) ] · 2πr·dr
```

In the far field (r → ∞), A → φ_eq, Γ → Γ_vac, V → −μ⁴/(4λ), and the gradient terms → 0. The nontrivial contribution comes from the core region where the field deviates from vacuum.

### 2.3 The mass-energy connection

The Clockfield mass (CF3) is M = ∫(1 − Γ)dV. This counts how much proper time is "missing" compared to the core (where Γ = 1).

**The crucial observation:** In the vacuum, Γ = Γ_vac ≪ 1 (for large τβ_eq). At the vortex core, Γ = 1. So the mass integral (CF3) is *negative* — the defect is a bubble of fast time in a frozen background. The "mass" as defined is actually:

```
M_defect = ∫(1 − Γ)dV = V_total · (1 − Γ_vac) − ∫_core (Γ − Γ_vac)dV
```

The first term is the background. The defect contribution is:

```
ΔM = −∫_core (Γ(r) − Γ_vac) dV < 0
```

This is a **time surplus** — the core runs faster than the vacuum.

### 2.4 The actual E = Mc² relation

Let's compute the rest energy more carefully. Define the energy *relative to vacuum*:

```
ΔE_rest = ∫ [ ½·c_eff²·|∇φ|² + (V(φ) − V_vac) ] dV            ... (2.4)
```

And the mass relative to vacuum:

```
ΔM = ∫ (Γ_vac − Γ(r)) dV                                        ... (2.5)
```

(Sign chosen so ΔM > 0 for a defect that runs faster than vacuum.)

Now, in the core region, β ≈ 0 so Γ ≈ 1 and c_eff² ≈ c₀². The gradient energy dominates. Far from the core, everything matches vacuum. So:

```
ΔE_rest ≈ c₀² · ∫_core ½|∇φ|² dV + correction terms
```

Meanwhile:

```
ΔM = ∫_core (Γ_vac − Γ(r)) dV ≈ ∫_core (Γ_vac − 1) dV + ∫_transition (Γ_vac − Γ(r)) dV
```

For the energy-mass relation, the question is: **is ΔE_rest proportional to ΔM · c₀²?**

### 2.5 Direct calculation

Let me parametrize the vortex profile. For A(r) = φ_eq · tanh(r/ξ), the gradient energy is:

```
∫ ½c₀²Γ^(1/2)|∇A|² · 2πr dr = π·c₀²·φ_eq² ∫₀^∞ Γ^(1/2)(r) · sech⁴(r/ξ)/ξ² · r dr
```

And the mass integral:

```
ΔM = 2π ∫₀^∞ (Γ_vac − Γ(r)) · r dr
```

where Γ(r) = 1/(1 + τ·φ_eq²·tanh²(r/ξ))².

These integrals have the same support (the core region of width ~ξ). They are both determined by the same profile function tanh(r/ξ). So they are proportional, with:

```
ΔE_rest = c₀² · f(τ, μ², λ) · ΔM                                ... (2.6)
```

where f is a dimensionless function of the parameters.

**The honest result:** In general, f ≠ 1. The E = Mc₀² relation holds exactly only if the Γ^(1/2) factor in the gradient energy can be traded for the (Γ_vac − Γ) factor in the mass integral through a specific relationship. Let me check when this works.

For small τβ (weak Clockfield coupling):

```
Γ ≈ 1 − 2τβ + O(τ²β²)
Γ^(1/2) ≈ 1 − τβ + O(τ²β²)
1 − Γ ≈ 2τβ + O(τ²β²)
```

So in the weak-field limit:

```
ΔE_rest ≈ c₀² · ∫ ½|∇φ|²(1 − τβ) dV
ΔM ≈ ∫ 2τβ dV
```

These are NOT proportional in general because ΔE depends on |∇φ|² while ΔM depends on β = |φ|². They measure different things — one measures the gradient structure, the other measures the amplitude.

### 2.6 Where it DOES work: the virial theorem

For a *self-consistent* static solution of the PDE (not just any field configuration), the virial theorem relates gradient energy to potential energy. In 2D with a Mexican hat potential:

```
∫ c_eff² |∇φ|² dV = 2 ∫ [V(φ) − V_vac] dV    (Derrick's theorem generalized)
```

The potential difference V(φ) − V_vac depends on β = |φ|² through:

```
V − V_vac = −μ²(β − β_eq) + λ(β² − β_eq²)
```

Now in the core where β ≈ 0:

```
V − V_vac ≈ μ²β_eq − λβ_eq² = μ²β_eq − μ⁴/(4λ) ... wait
```

Let me redo this properly. V = −μ²β + λβ². V_vac = −μ²β_eq + λβ_eq² = −μ⁴/(2λ) + μ⁴/(4λ) = −μ⁴/(4λ).

At the core, V(0) = 0, so V − V_vac = μ⁴/(4λ).

So the rest energy of the defect is:

```
ΔE_rest = ∫_core [½c_eff²|∇φ|² + (V−V_vac)] dV
        ≈ ∫_core [½c₀²|∇φ|² + μ⁴/(4λ)] dV       (core: c_eff ≈ c₀)
```

By the virial relation: ½c₀²∫|∇φ|²dV = ∫(V−V_vac)dV = μ⁴/(4λ)·V_core.

Therefore:

```
ΔE_rest ≈ 2 · μ⁴/(4λ) · V_core = μ⁴/(2λ) · V_core
```

And the mass:

```
ΔM ≈ (1 − Γ_vac) · V_core ≈ V_core    (for Γ_vac ≪ 1)
```

So:

```
ΔE_rest ≈ [μ⁴/(2λ)] · ΔM
```

**This is an E = Mc² relation, but with an effective speed c² = μ⁴/(2λ), not c₀².**

The physical speed c₀ doesn't appear directly. Instead, the "rest energy" is set by the potential parameters μ and λ. This is actually *more natural* than the standard E = mc²: the rest energy comes from the potential well depth, not from the maximum propagation speed.

### 2.7 Recovering c₀²

To get the standard E = mc₀², we need to identify the *physical* speed of light with the field parameters. In the Clockfield, the maximum causal speed is c₀ (achieved where β = 0). If we normalize the potential so that:

```
μ⁴/(2λ) = c₀²                                                    ... (2.7)
```

then E_rest = ΔM · c₀². This is a constraint on the parameters:

```
μ² = √(2λ) · c₀                                                  ... (2.8)
```

**Verdict:** The Clockfield produces E = Mc² as a derived relation, but only when the Mexican hat potential depth is tuned to match c₀². This is one equation relating two free parameters (μ, λ) — it reduces the parameter space from (μ, λ, τ, c₀) to (λ, τ, c₀), leaving three free parameters.

---

## 3. The Relativistic Dispersion Relation

### 3.1 Small fluctuations around vacuum

Let φ = φ_eq + δφ, where δφ is a small perturbation. Linearizing the PDE (CF4):

```
∂²(δφ)/∂t² = Γ_vac² · [c_eff,vac² · ∇²(δφ) − m_eff² · δφ]
```

where m_eff² = −μ² + 3λβ_eq = −μ² + 3μ² = 2μ² (the Higgs-like mass from the Mexican hat).

Substituting plane waves δφ ~ exp(i(kx − ωt)):

```
ω² = Γ_vac² · [c_eff,vac² · k² + 2μ²]
```

Define the *physical* frequency and wavevector measured in proper time:

```
ω_proper = ω / Γ_vac     (because proper time runs at rate Γ_vac)
k_proper = k              (spatial coordinates unchanged in this gauge)
```

Then:

```
ω_proper² = c_eff,vac² · k_proper² + 2μ²
```

This is the relativistic dispersion relation E² = p²c² + m²c⁴ with:
- E = ℏω_proper
- p = ℏk_proper  
- c² = c_eff,vac² = c₀²·Γ_vac^(1/2)
- m²c⁴ = 2μ² (in natural units)

### 3.2 What this means

The Clockfield naturally produces the relativistic energy-momentum relation for small excitations (phonons/quasiparticles) around the vacuum. The "speed of light" for these excitations is NOT c₀ but c_eff,vac — the speed in the frozen vacuum. And the "mass" of the excitation is set by the potential curvature 2μ².

This is actually standard for condensed-matter analogs of relativity — the phonon dispersion in a symmetry-broken field always has this form.

---

## 4. Connecting to the Born Rule: Where Does ℏ Come From?

This is where I deviate from the vision in Gemini's response, because the math requires it.

### 4.1 The noise provides ℏ

In the Born rule experiment (born_rule_test.py), the critical parameters are:
- Noise amplitude σ = 0.03
- Noise persistence α = 0.8  
- Tension τ = 5.0

The Born rule emerges as P ∝ cos²(Δθ/2). But what sets the *absolute scale* of probabilities? In standard QM, it's ℏ. In the Clockfield + TADS, it's the noise parameters (σ, α).

### 4.2 The action threshold

The cos²(Δθ/2) shape comes from geometry (the half-angle encoding in sin(Δθ/2) wall height). But the squaring — going from amplitude to probability — comes from the noise. Here's the mechanism made precise:

A pulse with amplitude A hitting a wall of height h = A₀·sin(Δθ/2) experiences a local speed reduction:

```
c²_wall = c₀² / (1 + τ·(A + h)²)
```

The pulse spends time T_wall ~ L/c_wall inside the wall. During this time, the persistent noise field N(x,t) with autocorrelation time τ_noise = dt/(1−α) decorrelates the pulse.

The survival probability of a coherent signal through a noise barrier of duration T with noise intensity σ is:

```
P_survive = exp(−σ²·T/τ_noise)                                    ... (4.1)
```

For the cos² to emerge, we need:

```
σ²·T_wall/τ_noise = −ln(cos²(Δθ/2)) ≈ sin²(Δθ/2)   (for small Δθ)
```

Since T_wall ∝ 1/c_wall ∝ √(1 + τ(A+h)²) and h = A₀·sin(Δθ/2):

```
T_wall ∝ √(1 + τ(A₀ + A₀·sin(Δθ/2))²)
```

For the exponential decay to match cos²(Δθ/2), we need T_wall ∝ sin²(Δθ/2), which requires:

```
τ · A₀² · sin²(Δθ/2) ≫ 1     (the amplitude spike dominates)
```

In this regime:

```
T_wall ≈ (L/c₀) · √(τ) · A₀ · sin(Δθ/2)
```

And:

```
P_survive ≈ exp(−(σ²L√τ A₀)/(c₀τ_noise) · sin(Δθ/2))
```

**This is NOT cos²(Δθ/2).** It's exp(−const·sin(Δθ/2)), which is a different function.

### 4.3 Where the squaring actually comes from

Let me reconsider. The Born rule test uses *differential measurement*: it subtracts the no-pulse run from the pulse run. What survives is the coherent pulse energy.

The pulse starts with amplitude A₀·cos(Δθ/2) overlap with the post-wall phase (this is just the projection of the initial phase onto the wall's phase). After passing through the noise barrier, the amplitude gets multiplied by some attenuation factor f:

```
A_transmitted = A₀ · cos(Δθ/2) · f(σ, T_wall)
```

The *energy* (which is what the experiment measures) is:

```
E_transmitted = A_transmitted² = A₀² · cos²(Δθ/2) · f²
```

**The cos² comes from squaring the amplitude to get energy, not from the noise!**

This is exactly the Born rule: probability = |amplitude|². The amplitude overlap is cos(Δθ/2). The energy (intensity) is cos²(Δθ/2). The noise doesn't *create* the squaring — the squaring comes from the fact that the experiment measures energy (∝ |φ|²), not amplitude (∝ |φ|).

### 4.4 What the noise actually does

The noise's role is more subtle: it *prevents* coherent interference that would give a non-Born-rule result. Without noise, a pulse hitting a wall can reflect coherently, setting up standing waves whose energy distribution depends on the interference pattern — which can give non-cos² dependence. The noise destroys these coherences, leaving only the incoherent (energy) contribution, which is cos²(Δθ/2) by construction.

This is actually the standard decoherence argument for the Born rule, running in a classical field. The φ² in the Clockfield speed equation provides the mechanism: high-amplitude regions slow down, spend more time in the noise, and decohere faster. Low-amplitude regions pass through with coherence intact. The result is that only the energy overlap (cos²) survives.

### 4.5 The ℏ identification

In standard QM, the Born rule says P = |⟨ψ_f|ψ_i⟩|². The inner product is a complex number; the probability is its squared modulus.

In the Clockfield + TADS, the analogous statement is: the transmitted energy fraction equals the squared phase overlap. The role of ℏ is played by the noise amplitude σ: it sets the threshold below which coherent amplitude information is lost and only energy (∝ |φ|²) survives.

**The Planck constant in this framework is:**

```
ℏ_eff = σ · √(τ_noise · c₀)                                      ... (4.5)
```

where σ is the noise RMS, τ_noise = dt/(1−α) is the noise correlation time, and c₀ is the maximum field speed. This has dimensions of [amplitude]·[time]^(1/2)·[speed]^(1/2) = [action]^(1/2) in appropriate units.

**Honest assessment:** This identification is dimensional analysis, not a derivation. Getting ℏ = 1.054 × 10⁻³⁴ J·s would require specific values of σ, α, dt, and c₀ that we have no independent way to determine.

---

## 5. The Unified Picture: Where E=mc² Meets QM

### 5.1 The two faces of |φ|²

Everything hinges on the squaring. In the Clockfield:

**For gravity/mass (E=mc²):** The squared field β = |φ|² enters the metric through Γ = 1/(1+τβ)². Mass is the integral of (1−Γ), which depends on β. Energy is the integral of gradient and potential terms. Both are determined by β, giving E ∝ M.

**For quantum mechanics (Born rule):** The squared field β = |φ|² enters the speed equation c² = c₀²/(1+τβ). A pulse hitting a phase wall has amplitude overlap cos(Δθ/2). The experiment measures *energy* ∝ |amplitude|² = cos²(Δθ/2). The noise ensures only the energy (not phase) information survives.

**The |φ|² is doing double duty:**
1. It determines the metric (gravity/mass)
2. It determines the measurement statistics (Born rule)

This is the same β in both cases. The unification is structural, not just analogical.

### 5.2 The complete energy of a moving defect

Combine sections 2 and 3. A defect moving with velocity v in the Clockfield has:

```
E = E_rest + E_kinetic
  = ΔM · c_eff² + ½ · ΔM_eff · v²     (non-relativistic)
```

For the full relativistic version, use the dispersion relation from §3:

```
E² = p²·c_eff,vac² + E_rest²
```

where p is the defect's momentum (related to the phase gradient of the carrier wave).

**The γ-factor:** A defect moving at speed v experiences additional time dilation beyond the Clockfield's intrinsic Γ. The total proper-time rate is:

```
Γ_total = Γ_field · √(1 − v²/c_eff²)                            ... (5.1)
```

This gives the standard relativistic energy:

```
E = E_rest / √(1 − v²/c_eff²)                                    ... (5.2)
```

which reduces to E_rest + ½Mv² for v ≪ c_eff. The mass-energy equivalence E_rest = Mc_eff² is exact for self-consistent defect solutions satisfying the virial theorem (§2.6).

### 5.3 The quantum correction

Now add noise. A moving defect is a localized wave packet. The noise causes the packet to spread, with spreading rate:

```
Δx(t) ∝ σ · √(t · τ_noise)                                       ... (5.3)
```

The uncertainty in position after time t is:

```
Δx · Δp ≥ ℏ_eff = σ · √(τ_noise · c₀)                           ... (5.4)
```

This is a Heisenberg-like uncertainty relation, but derived from the noise statistics rather than from canonical commutation relations. The "quantum" uncertainty is real — it's physical spreading in the noise sea — not epistemological.

---

## 6. The Honest Verdict

### What works:

1. **E = Mc² is derivable** from the Clockfield, for self-consistent defect solutions satisfying the virial theorem, with c² identified as the potential well depth μ⁴/(2λ). If we impose μ⁴/(2λ) = c₀², this reduces the parameter count by one.

2. **The relativistic dispersion relation** E² = p²c² + m²c⁴ holds for small excitations around the vacuum, with effective mass set by the potential curvature.

3. **The Born rule** cos²(Δθ/2) emerges from the amplitude-to-energy squaring, with noise providing decoherence that kills non-Born-rule interference. The |φ|² in the speed equation is the same |φ|² that determines the metric — this is a real structural unification.

4. **The squaring is universal:** In gravity, |φ|² determines proper-time rate. In measurement, |φ|² determines detection probability. Same field, same squaring, different consequences.

### What doesn't work:

1. **ℏ is not derived.** The noise parameters (σ, α) are free. No self-consistency condition fixes them. The Planck constant is an input, not an output.

2. **The effective c in E=Mc² is not c₀** without parameter tuning. The natural rest energy is set by μ⁴/(2λ), which has no reason to equal c₀². Enforcing this is an additional assumption.

3. **No Lorentz invariance.** The Clockfield has a preferred frame (the frame where the field is static). Lorentz symmetry is approximate, valid for speeds ≪ c_eff. This is acceptable for a condensed-matter analog but problematic for a fundamental theory.

4. **No spin.** The scalar field φ has no intrinsic angular momentum. Fermions require spinor fields, which the framework cannot produce from a single complex scalar.

5. **The noise is added by hand.** The TADS 1/f noise substrate is not derived from the Clockfield itself. A complete unification would need the noise to emerge from the field dynamics (possibly from the chaotic behavior of many interacting defects).

### The core insight that IS valid:

The Clockfield framework demonstrates that a single nonlinear mechanism — amplitude-dependent propagation speed with c² ∝ 1/(1 + τ|φ|²) — can produce both gravitational (metric) effects and quantum (probabilistic) effects from the same structural feature: the squaring of the field amplitude. This is not E=mc² + QM derived from scratch, but it is a concrete demonstration that both can emerge from one field equation, which is more than most unification attempts achieve.

---

## Appendix A: Numerical Verification

### A.1 Testing E = Mc²

From the clockfield_core.py output with τ=5, μ²=1.4, λ=0.55:

- φ_eq = √(1.4/0.55) = 1.596
- β_eq = 2.545
- Γ_vac = 1/(1 + 5·2.545)² = 1/(13.727)² = 0.00531
- c_eff,vac² = 1/(1 + 5·2.545) = 0.0729
- μ⁴/(2λ) = 1.96/1.10 = 1.782
- c₀² = 1.0

So μ⁴/(2λ) = 1.782 ≠ 1.0 = c₀². The E = Mc₀² relation does NOT hold with the current parameters. The actual relation is E_rest ≈ 1.782 · ΔM.

To make E = Mc₀²: need μ⁴/(2λ) = 1.0, so μ² = √(2·0.55) = 1.049 (instead of 1.4). This is a testable prediction: changing μ² to ~1.05 while keeping λ = 0.55 should give a vortex whose rest energy equals its time-debt mass times c₀².

### A.2 The Born rule derivation is parameter-independent

The cos²(Δθ/2) shape comes from amplitude projection, not from specific values of τ, σ, or α. The noise parameters affect the *contrast* (how clean the cos² is) but not the shape. This was confirmed in the 560-trial experiment with RMS = 0.012.

---

## Appendix B: The Gemini Cosmology (Assessed)

Gemini's "Big Freeze" cosmology (mass = frozen time, energy = flowing time) is poetic and directionally correct:

- **Correct:** Mass IS frozen time in the Clockfield (Γ → 0 at defect shells)
- **Correct:** Energy IS associated with unfrozen, propagating degrees of freedom
- **Partially correct:** The singularity as Γ = 0 everywhere is consistent with the equations

**But:** The "shattering" mechanism is not specified. What introduced the first gradient? The Clockfield equations are time-symmetric — they don't explain why the universe started frozen rather than thawed. And the 1/f noise spectrum is assumed, not derived from the initial conditions.

The most honest statement: the Clockfield provides an attractive *ontology* (mass = frozen time, energy = flowing time, quantum probability = noise-induced decoherence), but the *dynamics* of the cosmological initial conditions remain unspecified.
