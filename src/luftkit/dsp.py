"""
Digital signal processing utilities for LUFT analysis
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple

try:
    from scipy import signal
    from scipy.stats import median_abs_deviation
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


@dataclass
class PsdParams:
    """Parameters for power spectral density estimation"""
    fs: float
    segment_s: float = 4.0
    overlap: float = 0.5
    window: str = "hann"
    
    @property
    def nperseg(self) -> int:
        return int(self.segment_s * self.fs)
    
    @property
    def noverlap(self) -> int:
        return int(self.nperseg * self.overlap)


def welch_psd(data: np.ndarray, params: PsdParams) -> Tuple[np.ndarray, np.ndarray]:
    """Compute power spectral density using Welch's method"""
    if not SCIPY_AVAILABLE:
        raise ImportError("scipy is required for PSD computation")
    
    f, pxx = signal.welch(
        data, 
        fs=params.fs,
        window=params.window,
        nperseg=params.nperseg,
        noverlap=params.noverlap,
        return_onesided=True,
        scaling='density'
    )
    
    return f, pxx


def local_robust_z(f: np.ndarray, psd: np.ndarray, 
                   baseline_window_hz: float, 
                   exclude_halfwidth_hz: float) -> Tuple[np.ndarray, np.ndarray]:
    """Compute local robust z-scores for PSD"""
    
    # Convert to power in dB
    power_db = 10 * np.log10(psd + 1e-12)  # Add small constant to avoid log(0)
    
    df = f[1] - f[0]  # frequency resolution
    baseline_bins = int(baseline_window_hz / df)
    exclude_bins = int(exclude_halfwidth_hz / df)
    
    z_scores = np.zeros_like(power_db)
    
    for i in range(len(f)):
        # Define local window
        start_idx = max(0, i - baseline_bins // 2)
        end_idx = min(len(f), i + baseline_bins // 2 + 1)
        
        # Exclude region around current frequency
        exclude_start = max(start_idx, i - exclude_bins)
        exclude_end = min(end_idx, i + exclude_bins + 1)
        
        # Create mask for baseline calculation
        baseline_mask = np.ones(end_idx - start_idx, dtype=bool)
        if exclude_end > exclude_start:
            baseline_mask[exclude_start - start_idx:exclude_end - start_idx] = False
        
        # Calculate local baseline statistics
        local_power = power_db[start_idx:end_idx][baseline_mask]
        
        if len(local_power) > 5:  # Need enough points for robust statistics
            median = np.median(local_power)
            mad = median_abs_deviation(local_power, scale='normal')
            
            if mad > 0:
                z_scores[i] = (power_db[i] - median) / mad
            else:
                z_scores[i] = 0
        else:
            z_scores[i] = 0
    
    return z_scores, power_db


def bandpass_filter(data: np.ndarray, fs: float, low_hz: float, high_hz: float) -> np.ndarray:
    """Apply bandpass filter to data"""
    if not SCIPY_AVAILABLE:
        raise ImportError("scipy is required for filtering")
    
    nyquist = fs / 2
    
    # Ensure frequencies are within valid range
    low_hz = max(low_hz, 1.0)  # Minimum 1 Hz
    high_hz = min(high_hz, nyquist * 0.99)  # Max 99% of Nyquist
    
    # Skip filtering if frequency range is invalid
    if low_hz >= high_hz or high_hz >= nyquist:
        print(f"Warning: Skipping filter - invalid range {low_hz}-{high_hz} Hz for fs={fs} Hz")
        return data
    
    low = low_hz / nyquist
    high = high_hz / nyquist
    
    # Check normalized frequencies are valid
    if low <= 0 or high >= 1 or low >= high:
        print(f"Warning: Skipping filter - invalid normalized range {low}-{high}")
        return data
    
    try:
        # Design butterworth filter
        sos = signal.butter(4, [low, high], btype='band', output='sos')
        
        # Apply filter
        filtered = signal.sosfilt(sos, data)
        
        return filtered
    except Exception as e:
        print(f"Warning: Filter failed ({e}), returning unfiltered data")
        return data


def hilbert_analytic(data: np.ndarray) -> np.ndarray:
    """Compute analytic signal using Hilbert transform"""
    if not SCIPY_AVAILABLE:
        raise ImportError("scipy is required for Hilbert transform")
    
    return signal.hilbert(data)


def phase_from_analytic(analytic_signal: np.ndarray, unwrap: bool = True) -> np.ndarray:
    """Extract instantaneous phase from analytic signal"""
    phase = np.angle(analytic_signal)
    
    if unwrap:
        phase = np.unwrap(phase)
    
    return phase


def stft_analysis(data: np.ndarray, fs: float, window_s: float = 1.0, 
                  overlap: float = 0.5) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute Short-Time Fourier Transform"""
    if not SCIPY_AVAILABLE:
        raise ImportError("scipy is required for STFT")
    
    nperseg = int(window_s * fs)
    noverlap = int(nperseg * overlap)
    
    f, t, Zxx = signal.stft(data, fs, nperseg=nperseg, noverlap=noverlap)
    
    return f, t, Zxx