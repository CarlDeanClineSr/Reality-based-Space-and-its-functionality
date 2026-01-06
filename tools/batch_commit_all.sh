#!/bin/bash
# Batch commit Imperial Math conversions to all 21 repos

REPOS=(
    "luft-portal-"
    "LUFT-Auto"
    "The-Unifying-Fields-Program-and-Physics-By-You-and-I"
    "Unified-Field-Theory-Solutions-2025"
    "LUFT_Recordings"
    "LUFT-Unified-Field-Project"
    "Lattice-Unified-Field-Theory-L.U.F. T"
    "Unification-Utilization-Physics-"
    "-Unthought-Of-Physics-By-You-and-I-"
    "Reality-based-Space-and-its-functionality"
    # Add remaining 11 repos
)

COMMIT_MSG="Convert to Imperial Math (automated)"

for repo in "${REPOS[@]}"; do
    if [ -d "../$repo" ]; then
        echo "================================================"
        echo "Processing: $repo"
        echo "================================================"

        cd "../$repo" || exit 1
        git add -A
        git commit -m "$COMMIT_MSG"
        git push origin main
        echo "✅ $repo committed and pushed"
        echo ""
        cd - > /dev/null || exit 1
    else
        echo "⚠️  Repo not found: $repo"
    fi
done

echo ""
echo "🎉 ALL REPOS UPDATED"
