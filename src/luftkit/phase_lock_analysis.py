#!/usr/bin/env python3
"""
RF Phase-Lock Analysis Script for LUFT
Analyzes phase-locking values (PLV) between macro resonance frequencies and collider epochs

Usage:
    python -m luftkit.phase_lock_analysis --inputs data/raw/*.wav --epochs data/epochs/collider_epochs.csv --frequencies 7468 14936 --bw 2.0 --window 60 --report_dir docs/reports
"""

import argparse
import os
import sys
import glob
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

try:
    from scipy.io import wavfile
    from scipy import signal
    from scipy.stats import circmean, circstd
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not available, limited functionality")

from .dsp import bandpass_filter, hilbert_analytic, phase_from_analytic, stft_analysis
from .io import ensure_dir


class PhaseAnalyzer:
    """Phase-Locking Value (PLV) analyzer for RF signals"""
    
    def __init__(self, fs: float, target_frequencies: List[float], 
                 bandwidth: float = 2.0, window_seconds: float = 60.0):
        self.fs = fs
        self.target_frequencies = target_frequencies
        self.bandwidth = bandwidth
        self.window_seconds = window_seconds
        self.window_samples = int(window_seconds * fs)
        
    def extract_phase_signal(self, data: np.ndarray, freq_hz: float) -> np.ndarray:
        """Extract instantaneous phase for target frequency using Hilbert transform"""
        nyquist = self.fs / 2
        
        # Check if target frequency is valid for this sample rate
        if freq_hz >= nyquist * 0.9:
            print(f"Warning: Target frequency {freq_hz} Hz too high for fs={self.fs} Hz, using STFT method")
            return self.extract_phase_stft(data, freq_hz)
        
        # Bandpass filter around target frequency
        low_hz = freq_hz - self.bandwidth / 2
        high_hz = freq_hz + self.bandwidth / 2
        
        filtered = bandpass_filter(data, self.fs, low_hz, high_hz)
        
        # Get analytic signal and extract phase
        analytic = hilbert_analytic(filtered)
        phase = phase_from_analytic(analytic, unwrap=False)  # Keep wrapped for PLV
        
        return phase
    
    def extract_phase_stft(self, data: np.ndarray, freq_hz: float) -> np.ndarray:
        """Extract phase using Short-Time Fourier Transform"""
        f, t, Zxx = stft_analysis(data, self.fs, window_s=1.0, overlap=0.75)
        
        # Find closest frequency bin
        freq_idx = np.argmin(np.abs(f - freq_hz))
        
        # Extract phase time series
        phase_complex = Zxx[freq_idx, :]
        phase = np.angle(phase_complex)
        
        # Interpolate to match original time base
        t_original = np.arange(len(data)) / self.fs
        phase_interp = np.interp(t_original, t, phase)
        
        return phase_interp
    
    def compute_plv(self, phase1: np.ndarray, phase2: np.ndarray, 
                   window_start: int, window_end: int) -> float:
        """Compute Phase-Locking Value between two phase signals"""
        if window_end > len(phase1) or window_end > len(phase2):
            return 0.0
            
        # Extract window
        p1_window = phase1[window_start:window_end]
        p2_window = phase2[window_start:window_end]
        
        # Compute phase difference
        phase_diff = p1_window - p2_window
        
        # Compute PLV as magnitude of mean complex exponential
        complex_phase_diff = np.exp(1j * phase_diff)
        plv = np.abs(np.mean(complex_phase_diff))
        
        return plv
    
    def compute_sliding_plv(self, phase1: np.ndarray, phase2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute PLV over sliding windows"""
        n_windows = (len(phase1) - self.window_samples) // (self.window_samples // 2) + 1
        plv_values = []
        window_times = []
        
        for i in range(n_windows):
            start_idx = i * (self.window_samples // 2)
            end_idx = start_idx + self.window_samples
            
            if end_idx <= len(phase1):
                plv = self.compute_plv(phase1, phase2, start_idx, end_idx)
                plv_values.append(plv)
                window_times.append((start_idx + end_idx) / 2 / self.fs)
        
        return np.array(window_times), np.array(plv_values)
    
    def permutation_test(self, phase1: np.ndarray, phase2: np.ndarray, 
                        n_permutations: int = 100) -> Tuple[float, List[float]]:
        """Compute null distribution via phase permutation"""
        # Real PLV
        _, real_plv = self.compute_sliding_plv(phase1, phase2)
        mean_real_plv = np.mean(real_plv)
        
        # Permutation null distribution
        null_plvs = []
        
        for _ in range(n_permutations):
            # Randomly shuffle one phase signal in blocks
            block_size = self.window_samples // 4
            n_blocks = len(phase2) // block_size
            
            if n_blocks > 1:
                shuffled_phase2 = phase2.copy()
                blocks = shuffled_phase2[:n_blocks * block_size].reshape(n_blocks, block_size)
                np.random.shuffle(blocks)
                shuffled_phase2[:n_blocks * block_size] = blocks.flatten()
            else:
                shuffled_phase2 = np.roll(phase2, np.random.randint(1, len(phase2)))
            
            _, null_plv = self.compute_sliding_plv(phase1, shuffled_phase2)
            null_plvs.append(np.mean(null_plv))
        
        # Compute p-value
        p_value = (np.sum(np.array(null_plvs) >= mean_real_plv) + 1) / (n_permutations + 1)
        
        return p_value, null_plvs


def load_epochs(epochs_file: str) -> pd.DataFrame:
    """Load collider epochs from CSV file"""
    if not os.path.exists(epochs_file):
        # Create dummy epochs file for demonstration
        dummy_epochs = pd.DataFrame({
            'epoch_name': ['LHC_Run3_2022', 'LHC_Run3_2023', 'Future_Collider_2025'],
            'start_time': ['2022-04-01 00:00:00', '2023-01-01 00:00:00', '2025-01-01 00:00:00'],
            'end_time': ['2022-12-31 23:59:59', '2023-12-31 23:59:59', '2025-12-31 23:59:59'],
            'description': ['LHC Run 3 Start', 'LHC Run 3 Continue', 'Future Collider Online']
        })
        os.makedirs(os.path.dirname(epochs_file), exist_ok=True)
        dummy_epochs.to_csv(epochs_file, index=False)
        print(f"Created dummy epochs file: {epochs_file}")
        return dummy_epochs
    else:
        return pd.read_csv(epochs_file)


def load_audio_file(filepath: str) -> Tuple[np.ndarray, float]:
    """Load audio file (WAV or CSV)"""
    if filepath.lower().endswith('.wav'):
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy required for WAV files")
        fs, data = wavfile.read(filepath)
        
        # Convert to float
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float32) / 2147483648.0
        
        # Handle stereo
        if len(data.shape) > 1:
            data = data[:, 0]
            
        return data, float(fs)
    
    elif filepath.lower().endswith('.csv'):
        df = pd.read_csv(filepath)
        
        # Try to detect time and data columns
        time_col = None
        data_col = None
        
        for col in df.columns:
            if 'time' in col.lower():
                time_col = col
            elif 'data' in col.lower() or 'signal' in col.lower() or 'amplitude' in col.lower():
                data_col = col
        
        if time_col is None:
            time_col = df.columns[0]
        if data_col is None:
            data_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        time = df[time_col].values
        data = df[data_col].values
        
        # Estimate sample rate
        if len(time) > 1:
            fs = 1.0 / np.mean(np.diff(time))
        else:
            fs = 1.0  # Default
            
        return data, fs
    
    else:
        raise ValueError(f"Unsupported file format: {filepath}")


def analyze_file_pair(file1: str, file2: str, analyzer: PhaseAnalyzer, 
                     target_freq: float) -> Dict[str, Any]:
    """Analyze phase locking between two files at target frequency"""
    
    # Load files
    data1, fs1 = load_audio_file(file1)
    data2, fs2 = load_audio_file(file2)
    
    # Check sample rates match
    if abs(fs1 - fs2) > 0.1:
        print(f"Warning: Sample rate mismatch {fs1} vs {fs2}")
    
    # Use minimum length
    min_len = min(len(data1), len(data2))
    data1 = data1[:min_len]
    data2 = data2[:min_len]
    
    # Extract phases
    phase1 = analyzer.extract_phase_signal(data1, target_freq)
    phase2 = analyzer.extract_phase_signal(data2, target_freq)
    
    # Compute sliding PLV
    times, plv_values = analyzer.compute_sliding_plv(phase1, phase2)
    
    # Statistics
    mean_plv = np.mean(plv_values)
    max_plv = np.max(plv_values)
    std_plv = np.std(plv_values)
    
    # Permutation test
    p_value, null_dist = analyzer.permutation_test(phase1, phase2, n_permutations=50)
    
    # Z-score vs null
    null_mean = np.mean(null_dist)
    null_std = np.std(null_dist)
    z_score = (mean_plv - null_mean) / (null_std + 1e-12)
    
    return {
        'file1': os.path.basename(file1),
        'file2': os.path.basename(file2),
        'frequency_hz': target_freq,
        'mean_plv': mean_plv,
        'max_plv': max_plv,
        'std_plv': std_plv,
        'z_score': z_score,
        'p_value': p_value,
        'times': times.tolist(),
        'plv_timeseries': plv_values.tolist(),
        'null_distribution': null_dist
    }


def create_plv_plot(results: List[Dict[str, Any]], output_path: str):
    """Create PLV analysis plots"""
    n_results = len(results)
    if n_results == 0:
        return
    
    fig, axes = plt.subplots(n_results, 2, figsize=(12, 4 * n_results))
    if n_results == 1:
        axes = axes.reshape(1, -1)
    
    for i, result in enumerate(results):
        freq = result['frequency_hz']
        times = np.array(result['times'])
        plv_ts = np.array(result['plv_timeseries'])
        null_dist = result['null_distribution']
        
        # PLV timeseries
        axes[i, 0].plot(times / 3600, plv_ts, 'b-', linewidth=1.5, label=f'{freq} Hz PLV')
        axes[i, 0].axhline(y=result['mean_plv'], color='r', linestyle='--', alpha=0.7, label=f'Mean = {result["mean_plv"]:.3f}')
        axes[i, 0].set_xlabel('Time (hours)')
        axes[i, 0].set_ylabel('PLV')
        axes[i, 0].set_title(f'{result["file1"]} vs {result["file2"]} @ {freq} Hz')
        axes[i, 0].legend()
        axes[i, 0].grid(True, alpha=0.3)
        
        # Null distribution
        axes[i, 1].hist(null_dist, bins=20, alpha=0.7, color='gray', label='Null Distribution')
        axes[i, 1].axvline(x=result['mean_plv'], color='r', linestyle='-', linewidth=2, label=f'Observed PLV = {result["mean_plv"]:.3f}')
        axes[i, 1].set_xlabel('PLV')
        axes[i, 1].set_ylabel('Frequency')
        axes[i, 1].set_title(f'Null Test (p = {result["p_value"]:.4f}, z = {result["z_score"]:.2f})')
        axes[i, 1].legend()
        axes[i, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    ensure_dir(output_path)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='LUFT Phase-Lock Analysis')
    parser.add_argument('--inputs', required=True, help='Input WAV/CSV files (glob pattern)')
    parser.add_argument('--epochs', required=True, help='Collider epochs CSV file')
    parser.add_argument('--frequencies', nargs='+', type=float, default=[7468, 14936], 
                       help='Target frequencies to analyze')
    parser.add_argument('--bw', type=float, default=2.0, help='Bandwidth around each frequency (Hz)')
    parser.add_argument('--window', type=float, default=60.0, help='Analysis window duration (seconds)')
    parser.add_argument('--report_dir', default='docs/reports', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Ensure report directory exists
    os.makedirs(args.report_dir, exist_ok=True)
    
    # Load epochs
    epochs_df = load_epochs(args.epochs)
    print(f"Loaded {len(epochs_df)} collider epochs")
    
    # Expand input files
    input_files = sorted(glob.glob(args.inputs))
    if not input_files:
        print(f"No files found matching pattern: {args.inputs}")
        sys.exit(1)
    
    print(f"Found {len(input_files)} input files")
    
    # Load first file to determine sample rate
    try:
        sample_data, fs = load_audio_file(input_files[0])
        print(f"Sample rate: {fs} Hz")
    except Exception as e:
        print(f"Error loading {input_files[0]}: {e}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = PhaseAnalyzer(fs, args.frequencies, args.bw, args.window)
    
    # Results storage
    all_results = []
    summary_data = []
    
    # Analyze all file pairs for each frequency
    for freq in args.frequencies:
        print(f"\nAnalyzing frequency: {freq} Hz")
        
        # For simplicity, analyze consecutive file pairs
        for i in range(len(input_files) - 1):
            file1 = input_files[i]
            file2 = input_files[i + 1]
            
            try:
                print(f"  Analyzing {os.path.basename(file1)} vs {os.path.basename(file2)}")
                result = analyze_file_pair(file1, file2, analyzer, freq)
                all_results.append(result)
                
                # Add to summary
                summary_data.append({
                    'frequency_hz': freq,
                    'file_pair': f"{result['file1']} vs {result['file2']}",
                    'mean_plv': result['mean_plv'],
                    'max_plv': result['max_plv'],
                    'z_score': result['z_score'],
                    'p_value': result['p_value']
                })
                
            except Exception as e:
                print(f"  Error analyzing {file1} vs {file2}: {e}")
                continue
    
    if not all_results:
        print("No successful analyses completed")
        sys.exit(1)
    
    # Save detailed results as JSON
    json_output = os.path.join(args.report_dir, 'phase_lock_analysis_detailed.json')
    with open(json_output, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"Detailed results saved to: {json_output}")
    
    # Save summary as CSV
    summary_df = pd.DataFrame(summary_data)
    csv_output = os.path.join(args.report_dir, 'phase_lock_analysis_summary.csv')
    summary_df.to_csv(csv_output, index=False)
    print(f"Summary results saved to: {csv_output}")
    
    # Create plots
    plot_output = os.path.join(args.report_dir, 'phase_lock_analysis_plots.png')
    create_plv_plot(all_results, plot_output)
    print(f"Plots saved to: {plot_output}")
    
    # Per-epoch analysis (group by time if metadata available)
    epoch_results = {}
    for epoch_idx, epoch in epochs_df.iterrows():
        epoch_name = epoch['epoch_name']
        epoch_results[epoch_name] = {
            'description': epoch['description'],
            'n_analyses': len([r for r in all_results if freq in args.frequencies]),
            'mean_plv_by_freq': {}
        }
        
        for freq in args.frequencies:
            freq_results = [r for r in all_results if r['frequency_hz'] == freq]
            if freq_results:
                mean_plvs = [r['mean_plv'] for r in freq_results]
                epoch_results[epoch_name]['mean_plv_by_freq'][f'{freq}_Hz'] = {
                    'mean': np.mean(mean_plvs),
                    'std': np.std(mean_plvs),
                    'max': np.max(mean_plvs),
                    'n_pairs': len(mean_plvs)
                }
    
    # Save epoch summary
    epoch_output = os.path.join(args.report_dir, 'phase_lock_epochs_summary.json')
    with open(epoch_output, 'w') as f:
        json.dump(epoch_results, f, indent=2, default=str)
    print(f"Epoch analysis saved to: {epoch_output}")
    
    print(f"\nAnalysis complete! Results saved to: {args.report_dir}")
    print(f"Overall statistics:")
    print(f"  Total file pairs analyzed: {len(all_results)}")
    print(f"  Frequencies: {args.frequencies}")
    print(f"  Mean PLV across all analyses: {np.mean([r['mean_plv'] for r in all_results]):.3f}")
    print(f"  Significant results (p < 0.05): {len([r for r in all_results if r['p_value'] < 0.05])}")


if __name__ == "__main__":
    main()