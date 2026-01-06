#!/usr/bin/env python3
"""
Automated Imperial Math Conversion Script
Converts standard notation to Imperial Math across all repos.

Usage:
    python tools/convert_to_imperial_math.py --repo /path/to/repo
    python tools/convert_to_imperial_math.py --all  # Convert all 21 repos
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Conversion patterns (standard → Imperial Math)
CONVERSIONS = {
    # Energy equations
    r"E\s*=\s*mc\^2": "energy = mass by (speed_of_light ^ 2)  [energy OK]",
    r"E\s*=\s*mc²": "energy = mass by (speed_of_light ^ 2)  [energy OK]",
    r"E\s*=\s*h\\nu": "energy_of(photon) = planck by frequency  [energy OK]",
    r"E\s*=\s*hf": "energy_of(photon) = planck by frequency  [energy OK]",
    # Force equations
    r"F\s*=\s*ma": "force = mass by acceleration  [momentum OK]",
    r"F\s*=\s*GMm/r\^2": "force = (grav_constant by mass1 by mass2) per (distance ^ 2)  [gravity OK]",
    # Chi boundary
    r"\\chi\s*=\s*max\(": "chi = max(",
    r"χ\s*=\s*max\(": "chi = max(",
    r"\\chi\s*≤\s*0\.15": "chi ≤ 0.15  [boundary OK]",
    r"χ\s*≤\s*0\.15": "chi ≤ 0.15  [boundary OK]",
    # Operators
    r"\\times": " by ",
    r"×": " by ",
    r"\\div": " per ",
    r"÷": " per ",
    r"/": " per ",
    # Greek symbols (common)
    r"\\alpha": "alpha",
    r"\\beta": "beta",
    r"\\gamma": "gamma",
    r"\\delta": "delta_",
    r"\\Delta": "DELTA_",
    r"\\epsilon": "epsilon",
    r"\\theta": "theta",
    r"\\lambda": "lambda",
    r"\\mu": "mu",
    r"\\nu": "nu",
    r"\\pi": "pi",
    r"\\rho": "rho",
    r"\\sigma": "sigma",
    r"\\tau": "tau",
    r"\\phi": "phi",
    r"\\Phi": "PHI",
    r"\\psi": "psi",
    r"\\Psi": "PSI",
    r"\\omega": "omega",
    r"\\Omega": "OMEGA",
    # Calculus operators
    r"\\nabla": "gradient_of",
    r"∇": "gradient_of",
    r"\\partial": "partial_derivative",
    r"∂": "partial_derivative",
    r"\\int": "integral_of",
    r"∫": "integral_of",
    r"\\sum": "sum_of",
    r"Σ": "sum_of",
}


def convert_file_content(content: str):
    """Convert standard notation to Imperial Math."""
    original_content = content
    for pattern, replacement in CONVERSIONS.items():
        content = re.sub(pattern, replacement, content)
    changes = sum(
        1
        for old, new in zip(original_content.split("\n"), content.split("\n"))
        if old != new
    )
    return content, changes


def process_file(filepath: Path):
    """Process a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_content, changes = convert_file_content(content)
        if changes > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ {filepath}: {changes} conversions")
            return changes
        return 0
    except Exception as exc:  # pragma: no cover - logging only
        print(f"❌ {filepath}: {exc}")
        return 0


def process_repo(repo_path: str):
    """Process all files in a repository."""
    extensions = [".md", ".py", ".html", ".tex", ".txt"]
    total_changes = 0
    files_processed = 0
    for ext in extensions:
        for filepath in Path(repo_path).rglob(f"*{ext}"):
            if any(skip in str(filepath) for skip in [".git", "node_modules", "__pycache__", "venv"]):
                continue
            changes = process_file(filepath)
            if changes > 0:
                total_changes += changes
                files_processed += 1
    print(f"\n📊 SUMMARY: {files_processed} files modified, {total_changes} total conversions\n")
    return total_changes


def main():
    parser = argparse.ArgumentParser(
        description="Convert standard notation to Imperial Math"
    )
    parser.add_argument(
        "--repo", help="Repository path (e.g., /path/to/luft-portal-)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Convert all 21 repos (requires local clones)",
    )
    args = parser.parse_args()

    if args.all:
        repos = [
            "../luft-portal-",
            "../LUFT-Auto",
            "../The-Unifying-Fields-Program-and-Physics-By-You-and-I",
            "../Unified-Field-Theory-Solutions-2025",
            "../LUFT_Recordings",
            "../LUFT-Unified-Field-Project",
            "../Lattice-Unified-Field-Theory-L.U.F. T",
            "../Unification-Utilization-Physics-",
            "../-Unthought-Of-Physics-By-You-and-I-",
            "../Reality-based-Space-and-its-functionality",
        ]
        for repo in repos:
            if os.path.exists(repo):
                print(f"\n{'='*60}\nProcessing: {repo}\n{'='*60}")
                process_repo(repo)
            else:
                print(f"⚠️  Repo not found: {repo}")
    elif args.repo:
        process_repo(args.repo)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
