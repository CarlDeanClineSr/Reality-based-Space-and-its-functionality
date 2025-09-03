"""
Statistical analysis utilities for LUFT
"""
import numpy as np
from typing import List, Tuple, Any


def benjamini_hochberg(pvals: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Apply Benjamini-Hochberg FDR correction"""
    n = len(pvals)
    if n == 0:
        return np.array([], dtype=bool)
    
    # Sort p-values and get indices
    sorted_indices = np.argsort(pvals)
    sorted_pvals = pvals[sorted_indices]
    
    # Find largest k where p_k <= (k/n) * alpha
    thresholds = (np.arange(1, n + 1) / n) * alpha
    significant_mask = sorted_pvals <= thresholds
    
    if not np.any(significant_mask):
        return np.zeros(n, dtype=bool)
    
    # Find largest significant index
    max_significant_idx = np.max(np.where(significant_mask)[0])
    
    # Create result mask
    result = np.zeros(n, dtype=bool)
    significant_sorted_indices = sorted_indices[:max_significant_idx + 1]
    result[significant_sorted_indices] = True
    
    return result


def harmonic_targets(f0: float, max_n: int, include_subharmonics: bool = True, 
                     odd_only: bool = False) -> List[float]:
    """Generate harmonic target frequencies"""
    targets = []
    
    # Add fundamental
    targets.append(f0)
    
    # Add harmonics
    start_n = 2
    for n in range(start_n, max_n + 1):
        if odd_only and n % 2 == 0:
            continue
        targets.append(n * f0)
    
    # Add subharmonics
    if include_subharmonics:
        for n in range(2, max_n + 1):
            if odd_only and n % 2 == 0:
                continue
            targets.append(f0 / n)
    
    return sorted(targets)


def match_peaks_to_targets(peaks: np.ndarray, z_scores: np.ndarray, q_values: np.ndarray,
                          targets: List[float], tolerance_hz: float, 
                          z_min: float, alpha: float) -> Tuple[List[List[Any]], int]:
    """Match detected peaks to harmonic targets"""
    matches = 0
    rows = []
    
    for i, target in enumerate(targets):
        # Determine harmonic order and type
        f0 = targets[0] if targets else target  # Assume first target is fundamental
        
        if abs(target - f0) < 1e-3:
            order = 1
            harm_type = "fundamental"
        elif target > f0:
            order = int(round(target / f0))
            harm_type = "harmonic"
        else:
            order = int(round(f0 / target))
            harm_type = "subharmonic"
        
        # Find closest peak within tolerance
        diffs = np.abs(peaks - target)
        closest_idx = np.argmin(diffs)
        closest_diff = diffs[closest_idx]
        
        if closest_diff <= tolerance_hz:
            closest_z = z_scores[closest_idx]
            closest_q = q_values[closest_idx]
            
            # Check significance criteria
            if closest_z >= z_min and closest_q <= alpha:
                matched = True
                matches += 1
            else:
                matched = False
            
            peak_freq = peaks[closest_idx]
            delta_hz = peak_freq - target
        else:
            matched = False
            peak_freq = None
            delta_hz = None
            closest_z = None
            closest_q = None
        
        rows.append([target, order, harm_type, matched, peak_freq, delta_hz, closest_z, closest_q])
    
    return rows, matches


def rational_targets(f0: float, ratios: List[List[int]]) -> List[Tuple[int, int, float]]:
    """Generate rational frequency targets"""
    targets = []
    
    for ratio in ratios:
        if len(ratio) >= 2:
            p, q = ratio[0], ratio[1]
            freq = f0 * p / q
            targets.append((p, q, freq))
    
    return targets


def match_rationals(peaks: np.ndarray, z_scores: np.ndarray, q_values: np.ndarray,
                   targets: List[Tuple[int, int, float]], tolerance_hz: float,
                   z_min: float, alpha: float) -> List[List[Any]]:
    """Match peaks to rational frequency targets"""
    rows = []
    
    for p, q, target_freq in targets:
        ratio_str = f"{p}:{q}"
        
        # Find closest peak
        diffs = np.abs(peaks - target_freq)
        closest_idx = np.argmin(diffs)
        closest_diff = diffs[closest_idx]
        
        if closest_diff <= tolerance_hz:
            closest_z = z_scores[closest_idx]
            closest_q = q_values[closest_idx]
            
            if closest_z >= z_min and closest_q <= alpha:
                matched = True
            else:
                matched = False
                
            peak_freq = peaks[closest_idx]
            delta_hz = peak_freq - target_freq
        else:
            matched = False
            peak_freq = None
            delta_hz = None
            closest_z = None
            closest_q = None
        
        rows.append([ratio_str, p, q, target_freq, matched, peak_freq, delta_hz, closest_z, closest_q])
    
    return rows


def enrichment_empirical(peaks: np.ndarray, z_scores: np.ndarray, q_values: np.ndarray,
                        n_targets: int, freq_low: float, freq_high: float,
                        tolerance_hz: float, z_min: float, alpha: float,
                        permutations: int = 1000) -> List[int]:
    """Compute empirical enrichment via permutation testing"""
    null_counts = []
    
    # Filter peaks to frequency range
    freq_mask = (peaks >= freq_low) & (peaks <= freq_high)
    valid_peaks = peaks[freq_mask]
    valid_z = z_scores[freq_mask]
    valid_q = q_values[freq_mask]
    
    # Generate random target frequencies
    for _ in range(permutations):
        random_targets = np.random.uniform(freq_low, freq_high, n_targets)
        
        # Count matches to random targets
        matches = 0
        for target in random_targets:
            diffs = np.abs(valid_peaks - target)
            if len(diffs) > 0:
                closest_idx = np.argmin(diffs)
                if (diffs[closest_idx] <= tolerance_hz and 
                    valid_z[closest_idx] >= z_min and 
                    valid_q[closest_idx] <= alpha):
                    matches += 1
        
        null_counts.append(matches)
    
    return null_counts


def empirical_pvalue(observed_matches: int, null_distribution: List[int]) -> float:
    """Calculate empirical p-value"""
    if not null_distribution:
        return 1.0
    
    null_array = np.array(null_distribution)
    return (np.sum(null_array >= observed_matches) + 1) / (len(null_array) + 1)