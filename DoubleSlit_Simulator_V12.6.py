# -*- coding: utf-8 -*-
"""
Berramdane Model V12.6 – Temporal Thread Visualization (Micrometer Interface)
Author : Al Moalim Berramdane
License: CC BY 4.0

- Micrometer sliders for slit width and separation (user‑friendly).
- 2×3 layout: interference, screen, complementarity, comparison table, φ₁/φ₂/Δφ plot, thread integrity curve.
- Random seed for reproducibility.
- CSV export.
- All features from V12.5 and V12.4 combined.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from ipywidgets import interact, FloatSlider, Checkbox, IntSlider, Dropdown, Button, Output, IntText
from scipy.signal import find_peaks
import pandas as pd
from IPython.display import display
import warnings
warnings.filterwarnings('ignore')

# ========================= CONSTANTS =========================
h = 6.626e-34
m = 9.109e-31
c = 3e8
REF_SPACING_MM = 0.18          # Jönsson 1961 reference
REF_V = 70000.0                 # m/s
REF_A_UM = 0.3                  # slit width in micrometers
REF_D_UM = 1.0                  # slit separation in micrometers

# ========================= CORE PHYSICS =========================
def de_broglie_wavelength(v):
    return h / (m * v)

def double_slit_intensity(x, lam, L, a_width, d_slit):
    beta = (np.pi * d_slit * x) / (lam * L)
    interference = np.cos(beta)**2
    alpha = (np.pi * a_width * x) / (lam * L)
    envelope = np.sinc(alpha / np.pi)**2
    return interference * envelope

def particle_like_pattern(x, lam, L, a_width, d_slit):
    sigma = a_width * L / lam
    I_left = np.exp(-(x + d_slit/2)**2 / (2 * sigma**2))
    I_right = np.exp(-(x - d_slit/2)**2 / (2 * sigma**2))
    return 0.5 * (I_left + I_right)

def compute_visibility(x, I):
    peaks, _ = find_peaks(I, distance=len(x)//30)
    if len(peaks) < 2:
        return 0.0
    I_max = np.max(I[peaks])
    center = np.where(np.abs(x) < 5e-3)[0]
    I_min = np.min(I[center]) if len(center) > 0 else np.min(I)
    return (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0.0

def white_light_rgb(x, L, a_width, d_slit):
    lams = {'R': 650e-9, 'G': 532e-9, 'B': 450e-9}
    channels = {k: double_slit_intensity(x, v, L, a_width, d_slit) for k, v in lams.items()}
    mx = max(np.max(v) for v in channels.values())
    if mx > 0:
        channels = {k: v/mx for k, v in channels.items()}
    return channels['R'], channels['G'], channels['B']

# ========== TEMPORAL THREAD MECHANICS ==========
def thread_integrity(meas_strength, decay_rate=3.0):
    """Thread integrity: 1 = intact, 0 = cut"""
    return np.exp(-decay_rate * meas_strength)

def apply_temporal_split(x, lam, L, a_width, d_slit, meas_strength, decay_rate, seed):
    """
    φ₁ = +π d x/(λ L)   (slit 1)
    φ₂ = -π d x/(λ L)   (slit 2)
    Thread controls correlation between φ₁ and φ₂.
    """
    rng = np.random.default_rng(seed)
    phi_1 = +(np.pi * d_slit * x) / (lam * L)
    phi_2 = -(np.pi * d_slit * x) / (lam * L)
    thread = thread_integrity(meas_strength, decay_rate)

    coherent_delta = phi_1 - phi_2      # = 2π d x/(λ L)

    if thread < 1.0:
        noise = rng.uniform(0, 2*np.pi, size=len(x))
        delta_phi = thread * coherent_delta + (1 - thread) * noise
    else:
        delta_phi = coherent_delta

    envelope = np.sinc((np.pi * a_width * x) / (lam * L) / np.pi)**2
    intensity = np.cos(delta_phi / 2)**2 * envelope
    return intensity, phi_1, phi_2, delta_phi, thread

def thread_state_label(thread):
    if thread > 0.9:
        return "🧵 Thread intact – φ₁ and φ₂ correlated → full interference"
    elif thread > 0.3:
        return "⚠️ Thread strained – partial decorrelation → reduced interference"
    else:
        return "✂️ Thread cut – φ₁ and φ₂ independent → particle-like behavior"

# ========================= CSV EXPORT =========================
current_x, current_I = None, None
export_button = Button(description="📥 Download CSV Data", button_style='success')
export_output = Output()

def on_export_clicked(b):
    global current_x, current_I
    with export_output:
        export_output.clear_output()
        if current_x is not None and current_I is not None:
            pd.DataFrame({'Position_mm': current_x*1000, 'Intensity': current_I}).to_csv('berramdane_data.csv', index=False)
            print("✅ Data exported to berramdane_data.csv")
        else:
            print("❌ No data yet. Run simulation first.")

export_button.on_click(on_export_clicked)

# ========================= MAIN SIMULATION =========================
@interact(
    mode=Dropdown(options=['Electron (de Broglie)', 'Photon (monochromatic)', 'White light (RGB)'],
                  value='Electron (de Broglie)', description='Mode'),
    L_mm=FloatSlider(value=350, min=10, max=1000, step=5, description='Distance L (mm)', continuous_update=False),
    v_mean=FloatSlider(value=REF_V, min=20000, max=150000, step=1000, description='Electron velocity (m/s)', continuous_update=False),
    wavelength_nm=FloatSlider(value=532, min=380, max=750, step=1, description='Wavelength (nm)', continuous_update=False),
    a_width_um=FloatSlider(value=REF_A_UM, min=0.1, max=2.0, step=0.01, description='Slit width (µm)', continuous_update=False),
    d_slit_um=FloatSlider(value=REF_D_UM, min=0.5, max=5.0, step=0.05, description='Slit separation (µm)', continuous_update=False),
    observer_active=Checkbox(value=False, description='Which‑path detector ON'),
    meas_strength=FloatSlider(value=0.0, min=0.0, max=1.0, step=0.05, description='Measurement strength'),
    decay_rate=FloatSlider(value=3.0, min=0.5, max=10.0, step=0.5, description='Thread cut sharpness', continuous_update=False),
    temperature=FloatSlider(value=0.0, min=0, max=1000, step=10, description='Detector noise (K)', continuous_update=False),
    rng_seed=IntText(value=42, description='Random seed')
)
def run_lab(mode, L_mm, v_mean, wavelength_nm, a_width_um, d_slit_um,
            observer_active, meas_strength, decay_rate, temperature, rng_seed):

    global current_x, current_I

    # Convert to SI units
    L = L_mm / 1000.0
    a_width = a_width_um * 1e-6
    d_slit = d_slit_um * 1e-6

    # Ensure a_width < d_slit
    if a_width >= d_slit:
        print("⚠️ Slit width must be smaller than separation. Adjusting automatically.")
        a_width = d_slit * 0.99
        a_width_um = a_width * 1e6

    # Determine mode and wavelength
    if 'Electron' in mode:
        phys_mode = 'Electron'
        lam = de_broglie_wavelength(v_mean)
        lam_display = lam * 1e9
    elif 'Photon' in mode:
        phys_mode = 'Photon'
        lam = wavelength_nm * 1e-9
        lam_display = wavelength_nm
    else:
        phys_mode = 'White'
        lam = 532e-9
        lam_display = 532

    # Dynamic range
    spacing = lam * L / d_slit
    x_limit = max(0.002, 3 * spacing)
    x = np.linspace(-x_limit, x_limit, 1500)
    current_x = x

    # Compute interference / thread effects
    phi_1 = phi_2 = delta_phi = None
    thread_val = 1.0

    if phys_mode == 'Electron' and observer_active:
        I, phi_1, phi_2, delta_phi, thread_val = apply_temporal_split(
            x, lam, L, a_width, d_slit, meas_strength, decay_rate, rng_seed)
        print(thread_state_label(thread_val))
    elif phys_mode == 'Electron':
        I = double_slit_intensity(x, lam, L, a_width, d_slit)
        phi_1 = +(np.pi * d_slit * x) / (lam * L)
        phi_2 = -(np.pi * d_slit * x) / (lam * L)
        delta_phi = phi_1 - phi_2
        print("🧵 Thread intact (no measurement) – full interference")
    elif phys_mode == 'White':
        I_R, I_G, I_B = white_light_rgb(x, L, a_width, d_slit)
        I = (I_R + I_G + I_B) / 3.0
    else:  # Photon (without observer, just classic)
        I = double_slit_intensity(x, lam, L, a_width, d_slit)

    # Reference patterns for complementarity panel
    I_ref = double_slit_intensity(x, lam, L, a_width, d_slit) if phys_mode != 'White' else I
    I_particle = particle_like_pattern(x, lam, L, a_width, d_slit) if phys_mode != 'White' else (I_R + I_G + I_B)/3.0

    # Detector noise
    if temperature > 0:
        noise_scale = (temperature/1000) * 0.15 * np.max(I)
        I += np.random.default_rng(rng_seed+1).normal(0, noise_scale, len(I))
        I = np.maximum(I, 0)

    if np.max(I) > 0:
        I /= np.max(I)
    current_I = I

    # Metrics
    visibility = compute_visibility(x, I)
    sim_spacing_mm = spacing * 1000
    sim_first_min_mm = (lam * L / a_width) * 1000

    # ========================= PLOTTING (2×3) =========================
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0])   # Interference pattern
    ax2 = fig.add_subplot(gs[0, 1])   # Detector screen
    ax3 = fig.add_subplot(gs[1, 0])   # Complementarity
    ax4 = fig.add_subplot(gs[1, 1])   # Comparison table
    ax5 = fig.add_subplot(gs[0, 2])   # φ₁, φ₂, Δφ
    ax6 = fig.add_subplot(gs[1, 2])   # Thread integrity curve

    # --- ax1: Main pattern ---
    ax1.plot(x*1000, I, 'b-', lw=1.5)
    ax1.fill_between(x*1000, I, alpha=0.25, color='blue')
    title = f'{mode} | V={visibility:.1%} | L={L_mm}mm'
    if observer_active and phys_mode == 'Electron':
        title += f' | m={meas_strength:.2f} | integrity={thread_val:.2f}'
    ax1.set_title(title, fontsize=10)
    ax1.set_xlabel('Position (mm)')
    ax1.set_ylabel('Intensity')
    ax1.set_xlim(-x_limit*1000, x_limit*1000)
    ax1.grid(alpha=0.3)

    # --- ax2: Detector screen ---
    if phys_mode == 'White':
        I_R, I_G, I_B = white_light_rgb(x, L, a_width, d_slit)
        scr = np.zeros((100, len(x), 3))
        scr[:,:,0] = np.tile(I_R, (100,1))
        scr[:,:,1] = np.tile(I_G, (100,1))
        scr[:,:,2] = np.tile(I_B, (100,1))
        ax2.imshow(scr, aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
    else:
        scr = np.tile(I, (100,1))
        im = ax2.imshow(scr, cmap='hot', aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
        plt.colorbar(im, ax=ax2, shrink=0.8)
    ax2.set_title('Detector screen')
    ax2.set_xlabel('Position (mm)')
    ax2.set_yticks([])

    # --- ax3: Complementarity ---
    def norm(arr):
        return arr / np.max(arr) if np.max(arr) > 0 else arr
    ax3.plot(x*1000, norm(I_ref),      'b--', lw=1, alpha=0.7, label='Pure wave (φ₁↔φ₂)')
    ax3.plot(x*1000, norm(I_particle), 'r--', lw=1, alpha=0.7, label='Pure particle (indep.)')
    ax3.plot(x*1000, I,                'k-',  lw=2,             label='Current state')
    ax3.set_xlim(-x_limit*1000, x_limit*1000)
    ax3.set_ylim(0, 1.05)
    ax3.set_title('Complementarity Principle')
    ax3.set_xlabel('Position (mm)')
    ax3.set_ylabel('Norm. intensity')
    ax3.legend(fontsize=7)
    ax3.grid(alpha=0.3)

    # --- ax4: Comparison table (Jönsson 1961) ---
    ax4.axis('off')
    if phys_mode == 'Electron':
        err_spacing = min(999, abs(sim_spacing_mm - REF_SPACING_MM)/REF_SPACING_MM*100)
        err_min = min(999, abs(sim_first_min_mm - REF_SPACING_MM)/REF_SPACING_MM*100)
        ax4.text(0.5, 0.95, "📊 Jönsson 1961 Comparison", transform=ax4.transAxes,
                 ha='center', va='top', fontsize=11, weight='bold')
        data = [
            ["Quantity",       "Sim (mm)",       "Ref (mm)",   "Err (%)"],
            ["Fringe spacing", f"{sim_spacing_mm:.3f}", f"{REF_SPACING_MM:.2f}", f"{err_spacing:.1f}"],
            ["First minimum",  f"{sim_first_min_mm:.3f}", f"{REF_SPACING_MM:.2f}", f"{err_min:.1f}"],
        ]
        table = ax4.table(cellText=data, loc='center', cellLoc='center', bbox=[0.05, 0.3, 0.9, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor('#cccccc')
                cell.set_text_props(weight='bold')
        ax4.text(0.5, 0.05, "Jönsson (1961): v=70 km/s, a=0.3 µm, d=1.0 µm",
                 transform=ax4.transAxes, ha='center', fontsize=7, style='italic')
    else:
        ax4.text(0.5, 0.6, f"Theoretical fringe spacing: {sim_spacing_mm:.3f} mm\nFirst min: {sim_first_min_mm:.3f} mm",
                 transform=ax4.transAxes, ha='center', va='center', fontsize=10, family='monospace')

    # --- ax5: Temporal Thread – Phase Map ---
    if phi_1 is not None:
        x_mm = x * 1000
        # Restrict to central region for clarity
        window = np.abs(x_mm) < x_limit*1000*0.8
        ax5.plot(x_mm[window], (phi_1[window] % (2*np.pi)), 'b-',  lw=1.2, label='φ₁ (slit 1)', alpha=0.8)
        ax5.plot(x_mm[window], (phi_2[window] % (2*np.pi)), 'r-',  lw=1.2, label='φ₂ (slit 2)', alpha=0.8)
        ax5.plot(x_mm[window], (delta_phi[window] % (2*np.pi)), 'g--', lw=1.5, label='Δφ = φ₁-φ₂')
        ax5.set_title(f'Temporal Thread – Phase Map\nThread = {thread_val:.3f}', fontsize=9)
        ax5.set_xlabel('Position (mm)')
        ax5.set_ylabel('Phase (rad)')
        ax5.set_ylim(0, 2*np.pi)
        ax5.set_yticks([0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi],
                       ['0', 'π/2', 'π', '3π/2', '2π'])
        ax5.legend(fontsize=7)
        ax5.grid(alpha=0.3)
        # Shaded region indicating constructive interference zone
        ax5.axhspan(0, np.pi, alpha=0.05, color='green', label='_interference region')
    else:
        ax5.text(0.5, 0.5, "Enable detector (Electron mode)\nto visualize φ₁ and φ₂",
                 transform=ax5.transAxes, ha='center', va='center', fontsize=10, style='italic', color='gray')
        ax5.set_title('Temporal Thread – Phase Map', fontsize=9)
        ax5.axis('off')

    # --- ax6: Thread Integrity Curve ---
    m_range = np.linspace(0, 1, 200)
    t_range = thread_integrity(m_range, decay_rate)
    ax6.plot(m_range, t_range, 'purple', lw=2.5, label=f'decay={decay_rate:.1f}')
    current_m = meas_strength if observer_active and phys_mode == 'Electron' else 0
    ax6.axvline(current_m, color='red', ls='--', lw=1.5, label=f'Current m={current_m:.2f}')
    ax6.axhline(thread_val, color='orange', ls=':', lw=1.5, label=f'integrity={thread_val:.2f}')
    # Color zones
    ax6.axhspan(0.9, 1.0, alpha=0.1, color='blue',  label='Intact')
    ax6.axhspan(0.3, 0.9, alpha=0.1, color='yellow', label='Strained')
    ax6.axhspan(0.0, 0.3, alpha=0.1, color='red',   label='Cut')
    ax6.set_xlabel('Measurement strength (m)')
    ax6.set_ylabel('Thread integrity')
    ax6.set_title('Temporal Thread Integrity', fontsize=10)
    ax6.set_xlim(0, 1)
    ax6.set_ylim(0, 1)
    ax6.legend(fontsize=7, loc='upper right')
    ax6.grid(alpha=0.3)

    plt.suptitle('Berramdane Model V12.6 – Temporal Thread Visualization', fontsize=13, weight='bold', y=1.01)
    plt.tight_layout()
    plt.show()

    # Console output
    print(f"✅ Visibility = {visibility:.1%} | Fringe spacing = {sim_spacing_mm:.3f} mm")
    if phys_mode == 'Electron':
        print(f"⏱️ Electron flight time: {L/v_mean*1e9:.2f} ns | λ = {lam*1e9:.4f} nm")
    elif phys_mode == 'Photon':
        print(f"⏱️ Photon flight time: {L/c*1e9:.2f} ns")
    else:
        print("⏱️ Flight time varies per wavelength (~7.3 ns for green light)")
    print(f"🔢 Random seed used: {rng_seed}")

# Display the interface and export button
display(export_button, export_output)
