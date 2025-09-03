# Resonance Atlas

Schema (CSV columns)
- id: stable identifier (e.g., capsule filename stem)
- band: band name/category (e.g., alpha/beta/etc.)
- center_Hz: numeric center frequency in Hz
- instrument: capture/measurement instrument
- conditions: environmental/experimental conditions
- source_path: path back to the original capsule notes
- notes: freeform notes (use "TODO: manual review" when auto-extraction is uncertain)

Usage
- Place curated capsule markdown files under capsules/.
- Run: `python scripts/extract_resonance_atlas.py` to regenerate data/atlas/resonance_atlas.csv.
- Manually review and replace example rows with real entries as curation progresses.