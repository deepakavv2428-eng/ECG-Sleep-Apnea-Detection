# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 10:55:02 2025

@author: deepa
"""

import wfdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import firwin, filtfilt, find_peaks, hilbert, welch, resample, medfilt
import os

# -------------------------
# Utility functions
# -------------------------
def fir_bandpass_filter(signal, fs, lowcut, highcut, numtaps=201):
    nyq = 0.5 * fs
    taps = firwin(numtaps, [lowcut / nyq, highcut / nyq], pass_zero=False)
    return filtfilt(taps, [1.0], signal)

def normalize(x):
    return (x - np.mean(x)) / np.std(x)

def compute_EDR(ecg, fs):
    ecg_f = fir_bandpass_filter(ecg, fs, 5, 20)
    ecg_f = normalize(ecg_f)
    peaks, _ = find_peaks(ecg_f, distance=int(0.3 * fs), height=np.std(ecg_f))
    t = np.arange(len(ecg_f)) / fs
    r_amp = ecg_f[peaks]
    edr = np.interp(t, t[peaks], r_amp)
    return edr - np.mean(edr), peaks, ecg_f

def respiration_rate(seg, fs):
    f, Pxx = welch(seg, fs, nperseg=min(len(seg), fs * 20))
    return f[np.argmax(Pxx)]

# -------------------------
# Apnea detection
# -------------------------
def detect_apnea_ecg_edr(ecg, fs, window_sec=60, smooth_sec=10):
    edr, r_peaks, ecg_f = compute_EDR(ecg, fs)
    edr_f = fir_bandpass_filter(edr, fs, 0.1, 0.4)

    env = np.abs(hilbert(edr_f))
    env_smooth = medfilt(env, kernel_size=int(smooth_sec * fs // 2 * 2 + 1))
    env_smooth = normalize(env_smooth)

    win = int(fs * window_sec)
    total_len = len(ecg)
    events = []

    rr_intervals = np.diff(r_peaks) / fs
    mean_rr = np.mean(rr_intervals)
    sdnn = np.std(rr_intervals)

    for start in range(0, total_len - win, win):
        seg_edr = edr_f[start:start + win]
        env_seg = env_smooth[start:start + win]
        dom_freq = respiration_rate(seg_edr, fs)
        rr_seg = rr_intervals[(r_peaks[1:] >= start) & (r_peaks[1:] < start + win)]
        sdnn_seg = np.std(rr_seg) if len(rr_seg) > 0 else 0

        low_amp_duration = np.sum(env_seg < 0.35)
        apnea_detected = (low_amp_duration / fs >= 10) or (dom_freq < 0.08) or (sdnn_seg > 0.25)

        events.append({
            "start_time_s": start / fs,
            "end_time_s": (start + win) / fs,
            "type": "apnea" if apnea_detected else "normal",
            "mean_env": np.mean(env_seg),
            "dom_freq_Hz": dom_freq,
            "sdnn_seg": sdnn_seg
        })

    return events, mean_rr, sdnn, edr_f, r_peaks, ecg_f

# -------------------------
# Main pipeline
# -------------------------
def run_pipeline(record_name="a01", input_dir=None, output_dir=None):
    if input_dir is None:
        input_dir = os.getcwd()
    if output_dir is None:
        output_dir = os.getcwd()

    record_path = os.path.join(input_dir, record_name)
    record = wfdb.rdrecord(record_path)
    ecg = record.p_signal[:, 0]
    fs = int(record.fs)

    # Optional resample to 100 Hz
    target_fs = 100
    if fs != target_fs:
        N = int(len(ecg) * target_fs / fs)
        ecg = resample(ecg, N)
        fs = target_fs

    # Detect apnea events
    events, mean_rr, sdnn, edr, r_peaks, ecg_f = detect_apnea_ecg_edr(ecg, fs)

    # Summary
    duration_sec = len(ecg) / fs
    duration_min = duration_sec / 60
    apnea_count = sum(1 for e in events if e['type'] == 'apnea')
    ahi = apnea_count / (duration_min / 60)
    if ahi < 5: severity = "Normal"
    elif ahi < 15: severity = "Mild"
    elif ahi < 30: severity = "Moderate"
    else: severity = "Severe"

    # Save CSV
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, f"{record_name}_ecg_edr_apnea.csv")
    pd.DataFrame(events).to_csv(csv_file, index=False)
    print(f"\nCSV saved as: {csv_file}\n")

    print(f"Record: {record_name}")
    print(f"Duration: {duration_min:.1f} minutes")
    print(f"Detected apnea events: {apnea_count}")
    print(f"AHI: {ahi:.2f} → Severity: {severity}")
    print(f"HRV: Mean RR = {mean_rr:.3f}s, SDNN = {sdnn:.3f}s\n")

    # -------------------------
    # Ask user for start time
    # -------------------------
    while True:
        max_time = len(ecg) / fs - 5
        user_input = input(f"Enter start time (in seconds, 0–{max_time:.1f}) for 5-sec view (or -1 to exit): ")
        try:
            start_time = float(user_input)
            if start_time == -1:
                print("Exiting plot view.")
                break
            if start_time < 0:
                start_time = 0
            elif start_time > max_time:
                start_time = max_time

            start_idx = int(start_time * fs)
            end_idx = start_idx + int(5 * fs)
            t_segment = np.arange(start_idx, end_idx) / fs

            plt.figure(figsize=(14, 8))

            plt.subplot(3, 1, 1)
            plt.plot(t_segment, ecg[start_idx:end_idx], color='b')
            plt.title(f"Raw ECG Signal (5-second segment starting at {start_time:.1f}s)")
            plt.xlabel("Time (s)"); plt.ylabel("Amplitude (mV)"); plt.grid(True)

            plt.subplot(3, 1, 2)
            plt.plot(t_segment, ecg_f[start_idx:end_idx], color='g')
            plt.title("Filtered ECG (5–20 Hz, FIR, Normalized)")
            plt.xlabel("Time (s)"); plt.ylabel("Amplitude (a.u.)"); plt.grid(True)

            plt.subplot(3, 1, 3)
            plt.plot(t_segment, edr[start_idx:end_idx], color='r')
            plt.title("ECG-Derived Respiration (EDR)")
            plt.xlabel("Time (s)"); plt.ylabel("EDR (a.u.)"); plt.grid(True)

            plt.tight_layout()
            plt.show()

        except ValueError:
            print("Invalid input. Please enter a number.")

# -------------------------
if __name__ == "__main__":
    input_folder = r"C:\Users\deepa\OneDrive\Documents\sem 3\sp\project\apnea-ecg-database-1.0.0"
    output_folder = r"C:\Users\deepa\OneDrive\Documents\sem 3\sp\project\apnea_csv_results"
    run_pipeline("a02", input_dir=input_folder, output_dir=output_folder)
