```markdown
# Capsule: Hierarchy Simulator (CAPSULE-HIERARCHY-005)

id: CAPSULE-HIERARCHY-005
title: Hierarchy simulator chaining micro prions to macro coils
authors: Dr. Carl Dean Cline Sr. (CarlDeanClineSr)
date: 2025-11-11
tags: simulation;hierarchy;scaling;priority-high
status: draft

summary:
  A compact, parameterized simulator that implements the LUFT scale-amplifier: micro fractional modulation f0 at scale X0 is amplified by power-law/exponential rules to produce macro δρ, effective mass m_eq, and observable signals (e.g., Γ or thrust). This capsule defines the model, example parameters, and a reproducible simulation notebook.

key_equations:
  - f(X) = κ [ (X/X0)^α − 1 ] f0
  - m_eq(X) = m0 / (1 + β δρ(X))
  - O(X) = O0 * g( f(X) )  where g is the observable response (e.g., exp(S f) for tunneling)
  - Continuous accumulation form:
    f_macro = ∫_{ln X0}^{ln X} w(u) f0 e^{α(u) u} du

evidence:
  - Preliminary sim runs (relay sim logs) showing ridge windows
  - Coil test logs (File 135 analogs) with measured fractional response vs B-field

falsifiable_predictions:
  - For chosen α, β, κ, simulator predicts a precise m_eq drop at B = 1.5 T (e.g., -0.09 ± 0.02); measure directly on coil rig.
  - Predicts domain of B where Γ enhancement appears; test in JJ or coil proxies.

required_files:
  - /sim/hierarchy_simulator.ipynb (notebook implementing equations)
  - /data/coil_logs/*.csv (sample coil response to B sweeps)
  - /scripts/plot_hierarchy.py

minimal_repro_steps:
  1. Open sim/hierarchy_simulator.ipynb, set seed parameters (f0, X0, α, κ, β).
  2. Run scale sweep from X0 to Xmacro (log scale).
  3. Produce plots: f(X), m_eq(X), predicted observable O(X).
  4. Compare to one coil log (CSV) and compute residuals to tune α, β.

acceptance_criteria:
  - Simulator reproduces coil log features within factor 2 at baseline; then tune to hit ±20% predictive region.
  - Stability: small changes in f0 (<10%) do not produce unphysical runaway predictions.

notes_and_caveats:
  - This is a phenomenological simulator. The parameters α, κ are empirical and should be treated as fit parameters per device class.
  - Energy accounting must be explicit: predicted thrust/power must obey conservation; include power source in modeling.

references:
  - Relay sim logs in /sim/
  - Coil experiment records in /hardware/

contact:
  - Create issue label `sim:hierarchy` to request runs, parameter scans, or cluster resources.
```
