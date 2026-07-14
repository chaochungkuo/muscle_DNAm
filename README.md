# muscle_DNAm

Reproducible analysis code for a pilot study of disease-group-associated DNA methylation patterns in non-neoplastic skeletal muscle pathology.

This repository contains code, dependency locks, small metadata schemas, and reproducibility manifests. Raw IDAT files, full methylation matrices, fitted models, private metadata, and generated reports are not stored in Git.

## Current development

The `reviewer-round-2-rebuild` branch rebuilds the analysis as one confounder-aware workflow. It preserves the submitted scripts while the new workflow is validated.

The revised analytical order is:

1. sample and metadata validation
2. methylation-array QC and preprocessing
3. unsupervised PCA/t-SNE reproduction and bias checks
4. differential methylation with sensitivity analyses
5. functional and gene-focused analyses
6. supervised learning with leakage-safe, confounder-aware validation
7. manuscript figures and tables

## Environment

[Pixi](https://pixi.sh/) manages both R and Python dependencies from the repository root.

```bash
pixi install
pixi run setup-bioc-data
pixi run check
```

The exact resolved environment is recorded in `pixi.lock`. The explicit
`setup-bioc-data` step is needed because Pixi does not execute the post-link
downloaders used by Bioconda annotation packages. Do not maintain separate
Conda, pip, renv, or nested Pixi specifications for the rebuilt workflow.

## Data configuration

Copy the example configuration without committing the local copy:

```bash
cp config/paths.example.yml config/paths.local.yml
```

Edit `config/paths.local.yml` to point to data outside the repository. Analysis code must not contain machine-specific absolute paths.

Expected external inputs include IDAT files, a private sample sheet, Juliane's reviewer-round bias metadata, external MMC data, and post-QC matrices when starting downstream of preprocessing. See `data/README.md` and `metadata/README.md`.

## Repository layout

- `analysis/`: narrative Quarto/R/Python analyses
- `R/`: reusable R functions
- `python/`: reusable Python modules
- `scripts/`: command-line entry points and validation tools
- `config/`: portable analysis and path configuration
- `metadata/`: public schemas/examples only; `metadata/private/` is ignored
- `data/`: placeholders only; raw and derived data are ignored
- `results/`, `figures/`, `reports/`: generated, untracked outputs
- `tests/`: lightweight reproducibility tests

## Reproducibility policy

- All sample joins use explicit identifiers, never row order alone.
- Every figure has a machine-readable source table or coordinate file.
- Seeds and analysis parameters live in `config/analysis.yml`.
- PCA/t-SNE baseline reproduction is separate from sensitivity analyses.
- Label-informed heatmaps are described as supervised descriptive analyses.
- Undefined clinical/pathology categories are displayed only as supplied and are not interpreted or modeled without provenance.
- Unavailable variables are never inferred or imputed to satisfy a reviewer request.
- Manuscript terminology uses `disease group`; legacy `PM` is mapped to `non-IBM IIM, NOS` only for presentation.

## Legacy scripts

The existing numbered subdirectories under `analysis/` are the previous workflow. They remain until the rebuilt pipeline reproduces the relevant results. Archival or removal will occur later in a separate, reviewable commit.
