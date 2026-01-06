#!/bin/bash
# Batch commit Imperial Math conversions to all 21 repos

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_DIR="$(cd "$BASE_DIR/.." && pwd)"

REPOS=(
    "luft-portal-"
    "LUFT-Auto"
    "The-Unifying-Fields-Program-and-Physics-By-You-and-I"
    "Unified-Field-Theory-Solutions-2025"
    "LUFT_Recordings"
    "LUFT-Unified-Field-Project"
    "Lattice-Unified-Field-Theory-L.U.F.T"
    "Unification-Utilization-Physics-"
    "-Unthought-Of-Physics-By-You-and-I-"
    "Reality-based-Space-and-its-functionality"
    # Add remaining repos as needed
)

COMMIT_MSG="Convert to Imperial Math (automated)"

for repo in "${REPOS[@]}"; do
    repo_path="$PARENT_DIR/$repo"
    if [ -d "$repo_path" ]; then
        echo "================================================"
        echo "Processing: $repo"
        echo "================================================"

        if ! cd "$repo_path"; then
            echo "⚠️  Unable to enter $repo, skipping"
            continue
        fi
        git add -A
        if git diff --cached --quiet; then
            echo "ℹ️  No changes to commit for $repo"
        else
            branch="$(git rev-parse --abbrev-ref HEAD)"
            branch=${branch:-main}
            git commit -m "$COMMIT_MSG"
            if git push origin "$branch"; then
                echo "✅ $repo committed and pushed to $branch"
            else
                echo "⚠️  Push failed for $repo on branch $branch"
            fi
        fi
        echo ""
        cd "$BASE_DIR" || exit 1
    else
        echo "⚠️  Repo not found: $repo"
    fi
done

echo ""
echo "🎉 ALL REPOS UPDATED"
