# Numeric extractor for New Text Document files
# Usage: python scripts/numeric_extractor.py --input-dir . --output extracted_numbers.csv
# Finds files matching 'New Text Document' pattern, extracts numeric literals and nearby context, attempts to identify simple units and convert to SI when possible.

import re
import csv
import argparse
import glob
import os
from pathlib import Path

# Regex to find numbers, including scientific notation in several forms (1.23e4, 1.23 x 10^4, 1.23 × 10^4)
NUMBER_RE = re.compile(r'''(?P<number>[-+]?
\d[\d,\.]*\s*(?:[×xX*]\s*10\^?\s*[-+]?\d+|e[-+]?\d+)?)(?P<suffix>[^\n\d,;:/]*)''', re.VERBOSE)

# Common unit keywords and conversion to SI (factor, SI unit) for simple single-term units or phrases
UNIT_MAP = {
    'ft': (0.3048, 'm'),
    'feet': (0.3048, 'm'),
    'in': (0.0254, 'm'),
    'inch': (0.0254, 'm'),
    'inches': (0.0254, 'm'),
    'mi': (1609.344, 'm'),
    'mile': (1609.344, 'm'),
    'mi^3': (1609.344**3, 'm^3'),
    'cubic mile': (1609.344**3, 'm^3'),
    'mile^3': (1609.344**3, 'm^3'),
    'lb': (0.45359237, 'kg'),
    'pound': (0.45359237, 'kg'),
    'kg': (1.0, 'kg'),
    'g': (0.001, 'kg'),
    's': (1.0, 's'),
    'hz': (1.0, 'Hz'),
    'hz.': (1.0, 'Hz'),
    'khz': (1e3, 'Hz'),
    'mhz': (1e6, 'Hz'),
    'ghz': (1e9, 'Hz'),
    't': (1.0, 'T'),  # ambiguous: 't' could be tesla or tonne; user should verify
    't.': (1.0, 'T'),
    'tesla': (1.0, 'T'),
    'telsa': (1.0, 'T'),
    'hp/ft^3': (745.699872/0.028316846592, 'W/m^3'),
    'hp/ft3': (745.699872/0.028316846592, 'W/m^3'),
    'hp per ft^3': (745.699872/0.028316846592, 'W/m^3'),
    'hp': (745.699872, 'W'),
    'w': (1.0, 'W'),
    'w/m^3': (1.0, 'W/m^3'),
}

# Helper to parse numbers with 'x10^' and unicode multiplication signs
def parse_number(text):
    s = text.strip()
    # remove commas
    s = s.replace(',', '')
    # normalize unicode multiplication
    s = s.replace('×', 'x').replace('X', 'x')
    # patterns like '1.83 x 10^15' or '1.83x10^15' or '1.83 x 10 15'
    m = re.search(r'(?P<mant>[-+]?\d*\.?\d+)(?:\s*[xX*]\s*10\^?\s*(?P<exp>[-+]?\d+))', s)
    if m:
        try:
            mant = float(m.group('mant'))
            exp = int(m.group('exp'))
            return mant * (10.0 ** exp)
        except Exception:
            pass
    # patterns like 1.23e+15 or 1.23E15
    try:
        return float(re.sub(r'\s+', '', s))
    except Exception:
        # fallback: try to extract leading numeric portion
        m2 = re.match(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?', s, re.IGNORECASE)
        if m2:
            try:
                return float(m2.group(0))
            except Exception:
                return None
    return None

# Identify unit hints from the excerpt (simple keyword matching). Returns (unit_key, factor, si_unit) or (None, None, None)
def identify_unit(excerpt):
    low = excerpt.lower()
    # check for multi-word units first
    for key in ['cubic mile', 'per cubic mile', 'hp/ft^3', 'hp per ft^3', 'hp/ft3']:
        if key in low:
            ukey = key if key in UNIT_MAP else key.replace('per ', '')
            if ukey in UNIT_MAP:
                factor, si = UNIT_MAP[ukey]
                return (ukey, factor, si)
    # then single-token units
    tokens = re.findall(r"[a-zA-Z%\/\^]+", low)
    for t in tokens:
        if t in UNIT_MAP:
            return (t, UNIT_MAP[t][0], UNIT_MAP[t][1])
    # phrases like 'nodes per cubic mile' or 'nodes per mi^3'
    if 'per cubic mile' in low or 'per mi^3' in low or 'per cubic-mile' in low:
        return ('mi^3', 1609.344**3, 'm^3')
    return (None, None, None)

def extract_from_file(path, context_chars=120):
    results = []
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    # iterate over matches
    for m in NUMBER_RE.finditer(text):
        raw = m.group('number')
        suffix = m.group('suffix') or ''
        start, end = max(0, m.start() - context_chars), min(len(text), m.end() + context_chars)
        excerpt = text[start:end].replace('\n', ' ').strip()
        value = parse_number(raw)
        unit_key, factor, si_unit = identify_unit(excerpt + ' ' + suffix)
        si_value = None
        si_unit_out = ''
        if value is not None and factor is not None:
            try:
                si_value = value * factor
                si_unit_out = si_unit
            except Exception:
                si_value = None
        results.append({
            'filename': os.path.basename(path),
            'start_pos': m.start(),
            'raw': raw.strip(),
            'normalized_value': value,
            'unit_hint': unit_key or '',
            'si_value': si_value,
            'si_unit': si_unit_out,
            'excerpt': excerpt,
        })
    return results

def main():
    parser = argparse.ArgumentParser(description='Extract numeric literals and nearby context from text files matching "New Text Document" pattern')
    parser.add_argument('--input-dir', '-i', default='.', help='Directory to scan (default: current directory)')
    parser.add_argument('--pattern', '-p', default='New Text Document*.txt', help='Filename glob pattern to match (default: "New Text Document*.txt")')
    parser.add_argument('--output', '-o', default='extracted_numbers.csv', help='Output CSV filename')
    parser.add_argument('--context-chars', '-c', type=int, default=120, help='Chars of context around match to include')
    args = parser.parse_args()

    # find files
    glob_pattern = os.path.join(args.input_dir, args.pattern)
    files = sorted(glob.glob(glob_pattern))
    if not files:
        print('No files found for pattern:', glob_pattern)
        return
    print(f'Found {len(files)} files. Processing...')

    all_results = []
    for f in files:
        res = extract_from_file(f, context_chars=args.context_chars)
        print(f' {os.path.basename(f)}: {len(res)} numeric matches')
        all_results.extend(res)

    # write CSV
    fieldnames = ['filename','start_pos','raw','normalized_value','unit_hint','si_value','si_unit','excerpt']
    with open(args.output, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            writer.writerow(r)

    print(f'Wrote {len(all_results)} rows to {args.output}')

if __name__ == '__main__':
    main()
