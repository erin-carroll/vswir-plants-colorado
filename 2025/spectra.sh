#!/bin/bash
set -euo pipefail

FID_FILES=(
  /store/carroll/col/data/2025/mosaic/file_lists/ALMO_2025_fids.txt
  /store/carroll/col/data/2025/mosaic/file_lists/CRBU_2025_fids.txt
  /store/carroll/col/data/2025/mosaic/file_lists/UPTA_2025_fids.txt
)

for f in "${FID_FILES[@]}"; do
  while IFS= read -r fid; do
    [[ -z "$fid" ]] && continue
    sbatch \
        --job-name=extract_${fid} \
        --nodes=1 \
        --cpus-per-task=2 \
        --partition=standard \
        --mem=150G \
        --output=/home/carroll/logs/%j_%x.out \
        --error=/home/carroll/logs/%j_%x.err \
        --wrap="python /store/carroll/repos/vswir-plants-colorado/2025/spectra.py --fid ${fid}"
  done < "$f"
done