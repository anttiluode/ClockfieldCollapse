import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from skimage import measure
import json

# File paths
JSON_FILE = 'fractal_horizon_results.json'
GAMMA_FILE = 'fractal_horizon_results_gamma.npy'
BETA_FILE = 'fractal_horizon_results_beta.npy'

def visualize_results():
    # 1. Load Data
    try:
        with open(JSON_FILE, 'r') as f:
            results = json.load(f)
        gamma = np.load(GAMMA_FILE)
        beta = np.load(BETA_FILE)
    except FileNotFoundError as e:
        print(f"Error: Could not find files. {e}")
        return

    # 2. Setup Figure
    fig = plt.figure(figsize=(16, 6))
    
    # --- Subplot 1: 3D Isosurface of the Horizon ---
    ax1 = fig.add_subplot(131, projection='3d')
    
    # Check if gamma_thresholds exists, otherwise use a default
    # Looking at the code output, the threshold used for analysis was 0.005
    threshold = 0.005 
    if 'analysis_results' in results and len(results['analysis_results']) > 0:
        threshold = results['analysis_results'][0]['threshold']
    elif 'gamma_thresholds' in results:
        threshold = results['gamma_thresholds'][0]

    print(f"Generating 3D surface at Gamma threshold: {threshold}")
    
    # Extract isosurface using marching cubes
    verts, faces, normals, values = measure.marching_cubes(gamma, level=threshold)
    
    mesh = art3d.Poly3DCollection(verts[faces], alpha=0.3)
    mesh.set_facecolor('red')
    mesh.set_edgecolor('black')
    mesh.set_linewidth(0.1)
    ax1.add_collection3d(mesh)
    
    ax1.set_xlim(0, gamma.shape[0])
    ax1.set_ylim(0, gamma.shape[1])
    ax1.set_zlim(0, gamma.shape[2])
    ax1.set_title(f"3D Frozen Horizon\n(Gamma < {threshold:.4f})")

    # --- Subplot 2: 2D Cross-section of Gamma (Time Flow) ---
    ax2 = fig.add_subplot(132)
    mid_z = gamma.shape[2] // 2
    # Use raw strings r'' to fix SyntaxWarnings for LaTeX
    im2 = ax2.imshow(gamma[:, :, mid_z], cmap='magma', origin='lower')
    plt.colorbar(im2, ax=ax2, label=r'$\Gamma(x)$ (Time Rate)')
    ax2.set_title(f"Time Flow (Z={mid_z})")

    # --- Subplot 3: 2D Cross-section of Beta (Energy Density) ---
    ax3 = fig.add_subplot(133)
    # Using log10 because Beta reaches ~9.8e6 in your run
    log_beta = np.log10(beta[:, :, mid_z] + 1e-9)
    im3 = ax3.imshow(log_beta, cmap='viridis', origin='lower')
    plt.colorbar(im3, ax=ax3, label=r'$\log_{10}(\beta)$')
    ax3.set_title(f"Energy Density (Z={mid_z})")

    plt.tight_layout()
    plt.show()

# Summary Print
    print(f"--- Results ---")
    
    # Safely get Fractal Dimension
    if 'fractal_summary' in results and 'D_f_mean' in results['fractal_summary']:
        print(f"Fractal Dimension D_f: {results['fractal_summary']['D_f_mean']:.4f}")
    else:
        print("Fractal Dimension D_f: N/A")
        
    # Safely get Beta Max
    if 'final_state' in results and 'beta_max' in results['final_state']:
        print(f"Final Beta Max: {results['final_state']['beta_max']:.2e}")
    else:
        print("Final Beta Max: N/A")

if __name__ == "__main__":
    visualize_results()