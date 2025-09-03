# LUFT Phase-Lock Analysis Guide

## Overview

The LUFT Phase-Lock Analysis module provides tools for analyzing phase-locking values (PLV) between RF signals at LUFT resonance frequencies and collider epochs. This system implements the theoretical framework described in the EM-Lattice Coupling Module.

## Installation

The system requires the following Python packages:
- numpy
- scipy
- pandas  
- matplotlib
- pyyaml

Install with:
```bash
pip install numpy scipy pandas matplotlib pyyaml
```

## Usage

### Command Line Interface

```bash
python -m luftkit.phase_lock_analysis \
  --inputs "data/raw/*.wav" \
  --epochs "data/epochs/collider_epochs.csv" \
  --frequencies 7468 14936 \
  --bw 2.0 \
  --window 60 \
  --report_dir docs/reports
```

### Parameters

- `--inputs`: Glob pattern for input WAV or CSV files
- `--epochs`: CSV file containing collider epoch information
- `--frequencies`: Target frequencies to analyze (Hz)
- `--bw`: Bandwidth around each frequency (Hz)
- `--window`: Analysis window duration (seconds)
- `--report_dir`: Output directory for reports

### Input File Formats

#### WAV Files
- Standard WAV format audio files
- Supports various sample rates (12 kHz to 176.4 kHz tested)
- Automatically handles stereo to mono conversion

#### CSV Files
- Time-series data with columns for time and signal amplitude
- Auto-detects column names containing 'time', 'data', 'signal', or 'amplitude'
- Sample rate estimated from time intervals

#### Epochs File
CSV format with columns:
- `epoch_name`: Identifier for the epoch
- `start_time`: Start timestamp
- `end_time`: End timestamp  
- `description`: Human-readable description

Example:
```csv
epoch_name,start_time,end_time,description
LHC_Run3_2022,2022-04-01 00:00:00,2022-12-31 23:59:59,LHC Run 3 Start
```

## Output Files

### Summary CSV
`phase_lock_analysis_summary.csv` contains:
- `frequency_hz`: Target frequency
- `file_pair`: Files analyzed
- `mean_plv`: Average PLV over analysis windows
- `max_plv`: Maximum PLV observed
- `z_score`: Z-score vs permutation null distribution
- `p_value`: Statistical significance

### Detailed JSON
`phase_lock_analysis_detailed.json` contains:
- Complete time series of PLV values
- Null distribution from permutation testing
- Analysis parameters and metadata

### Plots
`phase_lock_analysis_plots.png` shows:
- PLV time series for each frequency/file pair
- Null distribution histograms with statistical tests

### Epoch Summary
`phase_lock_epochs_summary.json` contains:
- Aggregated results grouped by collider epochs
- Statistics per frequency and epoch

## Analysis Methods

### Phase-Locking Value (PLV)
PLV measures phase consistency between two signals:

```
PLV = |⟨e^{i(φ₁(t) - φ₂(t))}⟩|
```

Where φ₁(t) and φ₂(t) are instantaneous phases extracted via:
1. Bandpass filtering around target frequency
2. Hilbert transform for analytic signal
3. Phase extraction via angle computation

### Statistical Testing
- **Permutation tests**: Null distribution via block-shuffled phase signals
- **Z-score calculation**: (observed - null_mean) / null_std
- **P-value**: Empirical probability from permutation distribution

### Window Analysis
- Sliding window approach for temporal resolution
- Window size configurable (default 60 seconds)
- 50% overlap between consecutive windows

## Interpretation

### PLV Values
- **PLV ≈ 0**: Random phase relationship
- **PLV ≈ 1**: Strong phase locking
- **PLV > 0.6**: Potentially significant (depends on null distribution)

### Statistical Significance
- **p < 0.05**: Significant phase locking
- **z > 3**: Strong evidence above noise level
- **z > 5**: Very strong evidence

### Physical Meaning
High PLV values suggest:
- Coherent oscillations between measurement locations
- Possible lattice-mediated correlations
- Synchronization with macro-scale resonance patterns

## Troubleshooting

### Common Issues

#### "Digital filter critical frequencies" Error
- **Cause**: Target frequency too high for sample rate
- **Solution**: Use files with higher sample rates or lower target frequencies

#### "Zero-size array" Error  
- **Cause**: Very short audio files
- **Solution**: Use longer recordings or reduce window size

#### Sample Rate Mismatch
- **Cause**: Files have different sample rates
- **Solution**: Resample files to common rate or analyze separately

### Optimization Tips

1. **File Selection**: Use consistent sample rates across files
2. **Frequency Choice**: Ensure f_target < 0.4 × f_sample for best results
3. **Window Size**: Balance temporal resolution vs statistical power
4. **Bandwidth**: Wider bands capture more signal but less specificity

## Example Analysis Workflow

```bash
# 1. Prepare data directory structure
mkdir -p data/raw data/epochs docs/reports

# 2. Create epochs file
cat > data/epochs/collider_epochs.csv << EOF
epoch_name,start_time,end_time,description
LHC_Run3_2022,2022-04-01 00:00:00,2022-12-31 23:59:59,LHC Run 3 Start
LHC_Run3_2023,2023-01-01 00:00:00,2023-12-31 23:59:59,LHC Run 3 Continue
EOF

# 3. Run analysis
export PYTHONPATH="./src:$PYTHONPATH"
python -m luftkit.phase_lock_analysis \
  --inputs "*.wav" \
  --epochs "data/epochs/collider_epochs.csv" \
  --frequencies 7468 \
  --bw 10.0 \
  --window 30 \
  --report_dir docs/reports

# 4. Review results
ls docs/reports/
cat docs/reports/phase_lock_analysis_summary.csv
```

## Integration with LUFT Framework

This analysis tool integrates with the broader LUFT theoretical framework:

- **EM-Lattice Coupling**: Tests predictions from lattice-dressed electromagnetic theory
- **Cross-Scale Correlations**: Links macro resonance (~7.468 kHz) to microscale phenomena
- **Collider Epoch Analysis**: Searches for correlations with high-energy physics events
- **Statistical Validation**: Provides rigorous null hypothesis testing for LUFT predictions

## Future Extensions

Planned enhancements include:
- Real-time analysis capability
- Integration with existing LUFT resonance detection
- Advanced coherence metrics beyond PLV
- Machine learning classification of phase patterns
- Direct interface with collider data streams