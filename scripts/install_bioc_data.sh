#!/usr/bin/env bash
set -euo pipefail

# Pixi deliberately does not execute Conda post-link scripts. Bioconda data
# packages use those scripts to download the version selected in pixi.lock.
# Execute only the required Bioconductor data-package installers explicitly.

declare -A required=(
  [fdb.infiniummethylation.hg19]=FDb.InfiniumMethylation.hg19
  [genomeinfodbdata]=GenomeInfoDbData
  [go.db]=GO.db
  [illuminahumanmethylation450kanno.ilmn12.hg19]=IlluminaHumanMethylation450kanno.ilmn12.hg19
  [illuminahumanmethylation450kmanifest]=IlluminaHumanMethylation450kmanifest
  [illuminahumanmethylationepicanno.ilm10b4.hg19]=IlluminaHumanMethylationEPICanno.ilm10b4.hg19
  [illuminahumanmethylationepicmanifest]=IlluminaHumanMethylationEPICmanifest
  [org.hs.eg.db]=org.Hs.eg.db
  [txdb.hsapiens.ucsc.hg19.knowngene]=TxDb.Hsapiens.UCSC.hg19.knownGene
)

# Conda post-link scripts expect PREFIX; Pixi exposes CONDA_PREFIX.
export PREFIX="${CONDA_PREFIX}"

for package in "${!required[@]}"; do
  r_package="${required[$package]}"
  if Rscript -e "quit(status = !requireNamespace('${r_package}', quietly = TRUE))"; then
    echo "Already installed: ${r_package}"
    continue
  fi
  script=("${CONDA_PREFIX}/bin/.bioconductor-${package}-post-link.sh")
  if [[ ! -f "${script[0]}" ]]; then
    echo "Missing locked Bioconda installer: ${package}" >&2
    exit 1
  fi
  echo "Installing locked Bioconductor data package: ${package}"
  bash "${script[0]}"
done
