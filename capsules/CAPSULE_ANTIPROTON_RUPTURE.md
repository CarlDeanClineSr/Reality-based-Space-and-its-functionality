```markdown
# Capsule: Anti‑Proton Rupture Hypothesis (CAPSULE-ANTIPROTON-004)

id: CAPSULE-ANTIPROTON-004
title: Anti‑proton rupture model for cosmic anti‑particle spews
authors: Dr. Carl Dean Cline Sr. (CarlDeanClineSr)
date: 2025-11-11
tags: astrophysics;cosmicrays;antimatter;analysis;priority-high
status: draft

summary:
  Hypothesis: localized lattice node ruptures (macro prion events) eject energetic anti-particle flux with a time-modulated amplitude Φ_ex(E) × (1 + χ cos(Ω t)). The model predicts directional excesses and energy spectra that differ from standard cosmic-ray secondary production.

key_equations:
  - Φ_total(E, t, Ω, θ) = Φ_bg(E) + Φ_ex(E) * S(θ; θ0, Δθ) * [1 + χ cos(Ω t + φ)]
  - S(θ) = directional window function (e.g., von Mises or Gaussian on the sphere)
  - χ = dimensionless modulation amplitude (expected ~0.01–0.2 for candidate ruptures)

evidence:
  - AMS‑02 anti‑proton spectra anomalies (published residuals and your repo notes)
  - HAWC and Fermi gamma cross‑checks (candidate sky regions)
  - LUFT Unification Analysis Results — directional CSVs and candidate event lists

falsifiable_predictions:
  - A sustained directional excess of anti‑protons (or anti‑helium candidates) from a fixed sky window, inconsistent with propagation models.
  - Time modulation at a characteristic Ω (seekable band 10^-6 – 10^-2 Hz); χ > 0.01 would be detectable with long‑term AMS/PAMELA fits.
  - Accompanying γ‑ray signatures from annihilation in localized clouds if rupture meets normal matter.

required_files:
  - /data/ams02_public/*.csv (downloaded AMS public flux tables)
  - /scripts/antiproton_fit.ipynb (notebook to fit Φ_ex model)
  - /LUFT Unification Analysis Results/ (directional maps)

minimal_repro_steps:
  1. Download AMS‑02 published proton and anti‑proton fluxes (public dataset).
  2. Reproduce standard propagation background model (e.g., GALPROP or published fit).
  3. Fit residuals with Φ_ex(E)×S(θ)×(1+χ cos Ωt) using MCMC or least squares over candidate sky windows.
  4. Cross‑check candidate sky windows against Fermi/HAWC gamma maps for annihilation signatures.

acceptance_criteria:
  - Model provides a statistically significant improvement (ΔAIC/BIC) over background-only at p < 0.01 for an identified sky window AND
  - A consistent χ posterior across independent time slices or instruments.

notes_and_caveats:
  - Use careful trial-factor correction for many sky windows.
  - Propagation model uncertainties (solar modulation, diffusion) can mimic spectral residuals — include nuisance propagation parameters.
  - Access to full AMS event-level data would strengthen tests; public fluxes suffice for first-pass constraints.

references:
  - AMS public releases (flux tables)
  - LUFT Unification Analysis Results (repo)

contact:
  - Create issue labeled `analysis:antiproton` to request assistance or raw data.
```
