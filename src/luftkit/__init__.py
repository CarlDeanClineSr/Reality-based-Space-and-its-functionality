"""
LUFT (Lattice Unified Field Theory) Analysis Toolkit
"""

__version__ = "0.1.0"

from .config import Config, load_config
from .io import read_wav, read_csv_timeseries, write_csv, write_json
from .dsp import PsdParams, welch_psd, local_robust_z, bandpass_filter, hilbert_analytic
from .stats import benjamini_hochberg, harmonic_targets, match_peaks_to_targets
from .decoy import time_scramble, generate_permutation_controls

__all__ = [
    'Config', 'load_config',
    'read_wav', 'read_csv_timeseries', 'write_csv', 'write_json',
    'PsdParams', 'welch_psd', 'local_robust_z', 'bandpass_filter', 'hilbert_analytic',
    'benjamini_hochberg', 'harmonic_targets', 'match_peaks_to_targets',
    'time_scramble', 'generate_permutation_controls'
]