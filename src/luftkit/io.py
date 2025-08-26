"""
Input/output utilities for LUFT analysis
"""
import csv
import json
import os
from typing import List, Tuple, Any, Dict, Optional
import numpy as np

try:
    from scipy.io import wavfile
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def read_wav(filepath: str) -> Tuple[np.ndarray, int]:
    """Read WAV file and return data, sample rate"""
    if not SCIPY_AVAILABLE:
        raise ImportError("scipy is required for WAV file reading")
    
    fs, data = wavfile.read(filepath)
    
    # Convert to float and normalize if needed
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0
    
    # Handle stereo by taking first channel
    if len(data.shape) > 1:
        data = data[:, 0]
        
    return data, fs


def read_csv_timeseries(filepath: str, time_col: str = 'time', data_col: str = 'data') -> Tuple[np.ndarray, np.ndarray]:
    """Read CSV timeseries and return time, data arrays"""
    import pandas as pd
    df = pd.read_csv(filepath)
    time = df[time_col].values
    data = df[data_col].values
    return time, data


def write_csv(filepath: str, rows: List[List[Any]], headers: List[str]):
    """Write data to CSV file"""
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def write_json(filepath: str, data: Dict[str, Any]):
    """Write data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_sidecar(wav_path: str) -> Dict[str, Any]:
    """Load sidecar metadata for WAV file if exists"""
    base = os.path.splitext(wav_path)[0]
    sidecar_path = base + ".json"
    
    if os.path.exists(sidecar_path):
        with open(sidecar_path, 'r') as f:
            return json.load(f)
    return {}


def ensure_dir(filepath: str):
    """Ensure directory for filepath exists"""
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)