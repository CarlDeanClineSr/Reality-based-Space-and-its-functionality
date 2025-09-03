"""
Configuration utilities for LUFT analysis pipeline
"""
import yaml
import os
import glob
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class WelchConfig:
    segment_s: float = 4.0
    overlap: float = 0.5
    window: str = "hann"


@dataclass 
class BandConfig:
    psd_low_hz: float = 100.0
    psd_high_hz: float = 20000.0
    target_hz: float = 7468.0


@dataclass
class SignificanceConfig:
    alpha: float = 0.05
    z_min: float = 3.0
    local_baseline_window_hz: float = 50.0
    exclude_bin_halfwidth_hz: float = 5.0


@dataclass
class HarmonicsConfig:
    enable: bool = True
    max_n: int = 10
    include_subharmonics: bool = True
    odd_only: bool = False
    tolerance_hz: float = 2.0
    enrichment: Dict[str, Any] = None


@dataclass
class RationalsConfig:
    enable: bool = False
    ratios: List[List[int]] = None
    tolerance_hz: float = 2.0


@dataclass
class Config:
    input: str
    welch: WelchConfig
    band: BandConfig
    significance: SignificanceConfig
    harmonics: HarmonicsConfig
    rationals: RationalsConfig
    report_dir: str = "reports"


def load_config(config_path: str) -> Config:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Create nested configs
    welch_cfg = WelchConfig(**data.get('welch', {}))
    band_cfg = BandConfig(**data.get('band', {}))
    sig_cfg = SignificanceConfig(**data.get('significance', {}))
    
    harmonics_data = data.get('harmonics', {})
    if 'enrichment' not in harmonics_data:
        harmonics_data['enrichment'] = {'enable': False, 'permutations': 1000, 'freq_low': 1000, 'freq_high': 15000}
    harmonics_cfg = HarmonicsConfig(**harmonics_data)
    
    rationals_data = data.get('rationals', {})
    if 'ratios' not in rationals_data:
        rationals_data['ratios'] = [[2, 1], [3, 2], [4, 3]]
    rationals_cfg = RationalsConfig(**rationals_data)
    
    config = Config(
        input=data['input'],
        welch=welch_cfg,
        band=band_cfg,
        significance=sig_cfg,
        harmonics=harmonics_cfg,
        rationals=rationals_cfg,
        report_dir=data.get('report_dir', 'reports')
    )
    
    return config


def expand_inputs(input_pattern: str) -> List[str]:
    """Expand glob patterns to file list"""
    if '*' in input_pattern or '?' in input_pattern:
        return sorted(glob.glob(input_pattern))
    else:
        return [input_pattern]


def ensure_report_dir(config: Config) -> str:
    """Ensure report directory exists and return path"""
    os.makedirs(config.report_dir, exist_ok=True)
    return config.report_dir