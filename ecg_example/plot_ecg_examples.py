import os
import numpy as np
import wfdb
import matplotlib.pyplot as plt

# Paths
BASE = r"C:\Users\Admin\OneDrive\Skrivebord\Afib-Master\data\afib_normal_subset_ecg_arrhythmia"
AFIB_DIR = os.path.join(BASE, "afib")
NORMAL_DIR = os.path.join(BASE, "normal")
SAVE_DIR = r"C:\Users\Admin\OneDrive\Skrivebord\Afib-Master\Bilder"
os.makedirs(SAVE_DIR, exist_ok=True)

FS = 500

# Pick first recording from each class
afib_name = sorted([f[:-4] for f in os.listdir(AFIB_DIR) if f.endswith('.hea')])[0]
normal_name = sorted([f[:-4] for f in os.listdir(NORMAL_DIR) if f.endswith('.hea')])[0]

print(f"Dataset: Chapman-Shaoxing")
print(f"Normal: {normal_name}")
print(f"AFib:   {afib_name}")

afib_signal = wfdb.rdrecord(os.path.join(AFIB_DIR, afib_name)).p_signal
normal_signal = wfdb.rdrecord(os.path.join(NORMAL_DIR, normal_name)).p_signal
time = np.arange(afib_signal.shape[0]) / FS

lead = 1  # Lead II

# Plot 1: Normal Sinus Rhythm
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(time, normal_signal[:, lead], color='green', linewidth=0.8)
ax.set_title(f'Normal Sinus Rhythm — Lead II (Record: {normal_name})', fontweight='bold')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude (mV)')
ax.set_xlim([0, 10])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, 'ecg_normal_sinus_rhythm.pdf'), format='pdf', bbox_inches='tight', dpi=300)
plt.show()

# Plot 2: Atrial Fibrillation
fig, ax = plt.subplots(figsize=(10, 3))
ax.plot(time, afib_signal[:, lead], color='red', linewidth=0.8)
ax.set_title(f'Atrial Fibrillation — Lead II (Record: {afib_name})', fontweight='bold')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude (mV)')
ax.set_xlim([0, 10])
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(SAVE_DIR, 'ecg_atrial_fibrillation.pdf'), format='pdf', bbox_inches='tight', dpi=300)
plt.show()

print(f"\nSaved to {SAVE_DIR}")
