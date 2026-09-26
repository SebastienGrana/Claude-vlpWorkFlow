#!/bin/bash
# Rejoue les deux cas du filet (evals/filet F1, evals/filet-bash F2) en un appel,
# sur une copie jetable du kit à plafond bas, puis compte chaque transcription de
# sous-agent gardée. Sous WSL2 (Bash exige un sandbox) ; `claude` dans le PATH.
# Usage : bash evals/filet/rejouer.sh [plafond=6] — témoin : bash evals/filet/rejouer.sh 80
# Preuve attendue : plafond 6 → AVERTISSEMENTS=1 par cas ; plafond 80 → AVERTISSEMENTS=0.
set -u
N="${1:-6}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
K="$(mktemp -d)/kit"
python3 "$SRC/scripts/vlp.py" kit-essai "$K" --max-turns "$N" --kit "$SRC" || exit 1
mkdir -p "$SRC/evals/results"
LOG="$(mktemp)"
(cd "$K" && claude plugin eval . --tag filet --runs 1 --ablation none --no-publish --scaffold \
  --allow-tools Bash --trust-plugin --max-cost-usd 0.5 -j 1 --keep-temp \
  --json "$SRC/evals/results/filet-$N.json") 2>&1 | tee "$LOG"
for KK in $(grep -o '/tmp/claude-eval-[A-Za-z0-9]*' "$LOG" | sort -u); do
  chmod 700 "$KK" "$KK/sealed" 2>/dev/null; chmod -R u+rwX "$KK/sealed" 2>/dev/null
  for j in $(find "$KK" -path '*subagents*' -name '*.jsonl' 2>/dev/null); do
    echo "== plafond $N : $j"; python3 "$SRC/scripts/vlp.py" transcription "$j"
  done
done
