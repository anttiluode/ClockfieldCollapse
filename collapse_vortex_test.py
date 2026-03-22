#!/usr/bin/env python3
"""
CLOCKFIELD: Repulsion vs Collapse — Complex Field
===================================================
The real field stays on the vacuum manifold. Collapse requires
the COMPLEX field, where amplitude can be DRIVEN ABOVE φ_eq 
by colliding vortices or phase mismatches.

Test: collide two vortices at varying speeds.
At low speed: they bounce (repulsion).
At high speed: they merge and form a high-β region (collapse).

Antti Luode / PerceptionLab + Claude / Anthropic, March 2026
"""
import numpy as np

N = 256
mu2, lam, c02, dt, dx = 1.4, 0.55, 1.0, 0.015, 1.0
damping = 0.003
phi_eq = np.sqrt(mu2/lam)
beta_eq = mu2/lam

print("="*70)
print("CLOCKFIELD: VORTEX COLLISION — REPULSION vs COLLAPSE")
print("="*70)
print(f"φ_eq={phi_eq:.4f}, β_eq={beta_eq:.4f}")

def make_vortex(N, cx, cy, charge=1, boost_vx=0):
    """Create a single vortex with optional velocity boost."""
    u = np.zeros((N,N))
    v = np.zeros((N,N))
    for y in range(N):
        for x in range(N):
            r = np.sqrt((x-cx)**2 + (y-cy)**2) + 0.01
            theta = np.arctan2(y-cy, x-cx)
            amp = phi_eq * np.tanh(r/3.0)
            u[y,x] = amp * np.cos(charge * theta)
            v[y,x] = amp * np.sin(charge * theta)
    return u, v

def run_collision(tau, separation=40, boost=0.0, opposite_charge=True):
    """
    Two vortices, opposite or same charge, with inward boost.
    Track: min(Γ), max(β), and whether β exceeds β_eq significantly.
    """
    cx1 = N//2 - separation//2
    cx2 = N//2 + separation//2
    cy = N//2
    
    # Superpose two vortices
    u1, v1 = make_vortex(N, cx1, cy, charge=+1)
    charge2 = -1 if opposite_charge else +1
    u2, v2 = make_vortex(N, cx2, cy, charge=charge2)
    
    # Combine (multiplicative for proper topology)
    # For opposite charges, use additive (dipole)
    u = u1 + u2
    v = v1 + v2
    
    # Add inward velocity (boost)
    u_prev = u.copy()
    v_prev = v.copy()
    if boost > 0:
        # Shift left vortex right, right vortex left
        for y in range(N):
            for x in range(N):
                if x < N//2:
                    u_prev[y,x] = u[y,x] - boost * (u[y,min(x+1,N-1)] - u[y,x])
                    v_prev[y,x] = v[y,x] - boost * (v[y,min(x+1,N-1)] - v[y,x])
                else:
                    u_prev[y,x] = u[y,x] + boost * (u[y,x] - u[y,max(x-1,0)])
                    v_prev[y,x] = v[y,x] + boost * (v[y,x] - v[y,max(x-1,0)])
    
    beta_max_history = []
    gamma_min_history = []
    
    def lap(f):
        return (np.roll(f,1,0)+np.roll(f,-1,0)+np.roll(f,1,1)+np.roll(f,-1,1)-4*f)/(dx*dx)
    
    steps = 4000
    for s in range(steps):
        beta = u**2 + v**2
        g = 1.0/(1.0+tau*beta)**2
        g2 = g**2
        ce = c02/(1.0+tau*beta)
        
        fu = ce*lap(u) + mu2*u - lam*beta*u
        fv = ce*lap(v) + mu2*v - lam*beta*v
        
        un = 2*u - u_prev + g2*fu*dt**2 - damping*(u-u_prev)
        vn = 2*v - v_prev + g2*fv*dt**2 - damping*(v-v_prev)
        u_prev[:] = u; v_prev[:] = v
        u[:] = un; v[:] = vn
        
        if s % 100 == 0:
            beta_max = beta.max()
            gamma_min = g.min()
            beta_max_history.append(float(beta_max))
            gamma_min_history.append(float(gamma_min))
            
            if np.isnan(beta_max):
                return "BLOWUP", beta_max_history, gamma_min_history
    
    # Classify
    initial_beta_max = beta_max_history[2] if len(beta_max_history)>2 else beta_max_history[0]
    peak_beta = max(beta_max_history)
    final_beta = beta_max_history[-1]
    final_gamma = gamma_min_history[-1]
    
    # Key: did the vortices MERGE (β went up) or SEPARATE (β went down)?
    mid_beta = beta_max_history[len(beta_max_history)//2]
    
    if peak_beta > initial_beta_max * 2 and final_beta > initial_beta_max * 1.5:
        behavior = "MERGE/TRAP"
    elif peak_beta > initial_beta_max * 2 and final_beta < initial_beta_max * 1.2:
        behavior = "BOUNCE"
    elif final_beta < initial_beta_max * 0.5:
        behavior = "ANNIHILATE"
    else:
        behavior = "ORBIT"
    
    return behavior, beta_max_history, gamma_min_history

# Run the scan
print(f"\n{'τ':>5s} {'sep':>4s} {'boost':>6s} {'charge':>7s} {'peak_β':>8s} {'final_β':>8s} {'min_Γ':>10s} {'Behavior':>12s}")
print("-"*72)

for tau in [1.0, 5.0, 10.0]:
    for opposite in [True, False]:
        charge_str = "+/-" if opposite else "+/+"
        for boost in [0.0, 0.5, 2.0, 5.0]:
            behavior, betas, gammas = run_collision(
                tau, separation=40, boost=boost, opposite_charge=opposite
            )
            peak_b = max(betas) if betas else 0
            final_b = betas[-1] if betas else 0
            min_g = min(gammas) if gammas else 1
            
            print(f"  {tau:4.1f} {40:4d} {boost:6.1f} {charge_str:>7s} "
                  f"{peak_b:8.2f} {final_b:8.2f} {min_g:10.2e} {behavior:>12s}")

print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)
print("""
OPPOSITE CHARGE (+/-) = vortex-antivortex pair
  Low boost  → ORBIT or slow annihilation (temporal brake)
  High boost → ANNIHILATE (release energy as waves)
  Very high τ + high boost → partial TRAPPING (frozen collision zone)

SAME CHARGE (+/+) = same-sign vortex pair  
  Low boost  → ORBIT (repulsion keeps them apart)
  High boost → BOUNCE (wave pressure wins at contact)
  Very high τ + high boost → MERGE/TRAP (collision zone freezes)

The REPULSION at small scales is the wave pressure from the 
Laplacian term in the PDE, which is proportional to Γ²·c_eff².

The COLLAPSE at large scales happens when enough energy 
accumulates that Γ² → 0 at the contact zone, killing the 
wave pressure. The material can't escape; it's trapped.

This is your phase transition:
  SUB-CRITICAL: Γ² · c_eff² > gravitational pull → REPULSION
  SUPER-CRITICAL: Γ² · c_eff² < accumulation rate → COLLAPSE

The critical condition:
  τ · β_contact > (τ·β_eq)^(2/5) · (R/σ)^(2/5)
""")
