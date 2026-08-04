#!/bin/bash
#SBATCH --job-name=extract_shade
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=extract_shade_%j.out
#SBATCH --error=extract_shade_%j.err

src="/global/cfs/cdirs/neon_aop/10-15485-3013527/flightline"
out="/pscratch/sd/e/erincarr/col/data/2018/shade"

find "$src" -type f -name "*.tar.gz" -print0 |
while IFS= read -r -d '' archive; do
    tar -tzf "$archive" |
    grep '_shade\.tif$' |
    while IFS= read -r member; do
        outfile="$out/$(basename "$member")"

        if [[ -e "$outfile" ]]; then
            echo "Skipping existing: $outfile"
        else
            echo "Extracting $member from $(basename "$archive")"
            tar -xOzf "$archive" "$member" > "${outfile}.tmp" &&
                mv "${outfile}.tmp" "$outfile"
        fi
    done
done