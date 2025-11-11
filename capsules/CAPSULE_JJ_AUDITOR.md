```markdown
# Capsule: JJ Foam Auditor (CAPSULE-JJ-002)

id: CAPSULE-JJ-002
title: Josephson Junction Foam Auditor — MQT sensitivity to LUFT foam f
authors: Dr. Carl Dean Cline Sr. (CarlDeanClineSr)
date: 2025-11-11
tags: experiment;jj;metrology;priority-high
status: draft

summary:
  Use macroscopic quantum tunneling (MQT) escape rates in Josephson junctions as a laboratory metrology for small foam modulations f ≡ Δρ/ρ mapped into EJ (EJ→EJ(1+f)). The WKB exponent yields exponential sensitivity (d ln Γ/df ≈ −B0/2).

key_equations:
  - EJ = ħ Ic / 2e
  - ΔU(γ) = 2 EJ [√(1 − γ^2) − γ arccos γ]
  - ω_p = √(2e Ic / ħ C) (1 − γ^2)^(1/4)
  - B ≈ (36/5) ΔU / (ħ ω_p)
  - Γ(f) ≈ A exp[−B(f)]

evidence:
  - Simulation code and notebooks: /notebooks/collapse_demo_notebook_5.ipynb
  - Prior audit: digitized MIT thesis histograms (analysis notes in /results)
  - Starter scripts: /scripts/jj_fit_likelihood.py (if present)

falsifiable_predictions:
  - Lab constraint: |f| < 0.02 (projected) achievable with N ≳ 20k switching events at T ≪ T* and stable ramps.
  - Null detection yields upper limit on local foam modulation.

required_files:
  - /notebooks/collapse_demo_notebook_5.ipynb
  - /src/collapse.py (helper functions: plasma_frequency, phase_effective_mass, deltaU_from_gamma)
  - example dataset: /data/mit2007_digitized_histogram.csv (if available)

minimal_repro_steps:
  1. Run notebook to generate synthetic switching data and MLE inversion.
  2. Digitize a published histogram or load raw I_sw list and run /scripts/jj_fit_likelihood.py with proper r and T.
  3. Report f̂ ± σ_f and check robustness over ramp rates.

acceptance_criteria:
  - Recovery of injected f_synth to within ±0.02 in synthetic tests.
  - For real data: posterior on f with 95% CI excluding |f| ≥ 0.1 for a meaningful bound.

notes_and_caveats:
  - Control thermal vs quantum crossover; maintain T well below T* for MQT sensitivity.
  - Systematics: Ic drift, temperature instability, and electronic noise must be modeled.

references:
  - MIT thesis (2007) digitized histograms notes in /data
  - collapse_demo_notebook_5.ipynb

contact:
  - Open an issue with label `experiment:jj` to request instrument specs or to share raw I_sw files.
```
