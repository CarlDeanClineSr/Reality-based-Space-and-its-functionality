"""
Decoy and control utilities for LUFT analysis
"""
import numpy as np
from typing import Dict, Any


def time_scramble(data: np.ndarray, block_size: int = 1000) -> np.ndarray:
    """Time-scramble data in blocks to preserve local statistics"""
    scrambled = data.copy()
    n_blocks = len(data) // block_size
    
    if n_blocks > 1:
        # Reshape into blocks
        n_samples = n_blocks * block_size
        blocks = scrambled[:n_samples].reshape(n_blocks, block_size)
        
        # Shuffle blocks
        np.random.shuffle(blocks)
        
        # Flatten back
        scrambled[:n_samples] = blocks.flatten()
    
    return scrambled


def frequency_shift_decoy(data: np.ndarray, fs: float, shift_hz: float) -> np.ndarray:
    """Create frequency-shifted decoy by mixing with offset tone"""
    t = np.arange(len(data)) / fs
    shift_tone = np.exp(1j * 2 * np.pi * shift_hz * t)
    
    # Convert to complex if needed
    if np.isrealobj(data):
        analytic_data = data + 1j * np.imag(np.fft.hilbert(data))
    else:
        analytic_data = data
    
    # Apply frequency shift
    shifted = analytic_data * shift_tone
    
    # Return real part if input was real
    if np.isrealobj(data):
        return np.real(shifted)
    else:
        return shifted


def circular_shift_decoy(data: np.ndarray, shift_samples: int) -> np.ndarray:
    """Create circular shift decoy"""
    return np.roll(data, shift_samples)


def generate_permutation_controls(data: Dict[str, np.ndarray], 
                                 n_permutations: int = 100,
                                 method: str = 'time_scramble') -> Dict[str, Dict[str, np.ndarray]]:
    """Generate permutation controls for all channels"""
    controls = {}
    
    for perm_idx in range(n_permutations):
        perm_data = {}
        
        for channel_name, channel_data in data.items():
            if method == 'time_scramble':
                perm_data[channel_name] = time_scramble(channel_data)
            elif method == 'circular_shift':
                shift = np.random.randint(1, len(channel_data))
                perm_data[channel_name] = circular_shift_decoy(channel_data, shift)
            else:
                raise ValueError(f"Unknown decoy method: {method}")
        
        controls[f"perm_{perm_idx:03d}"] = perm_data
    
    return controls