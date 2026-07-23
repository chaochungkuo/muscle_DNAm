#!/usr/bin/env python3
"""Visualize annotated top positive/negative PCA-loading CpGs.

The input table contains the strongest positive and negative CpG loadings for
scaled PCA PC1-PC5. This script summarizes those CpGs by annotation category.
It is intended as a reviewer-response support figure, not as proof that a PC is
caused by one biological or technical variable.
"""

from __future__ import annotations

from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "results" / "tables" / "pca_scaled_top_loadings_annotated.tsv"
OUT_DIR = ROOT / "figures" / "response"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def pc_direction_label(row: pd.Series) -> str:
    sign = "+" if row["direction"] == "positive" else "-"
    return f"{row['PC']} {sign}"


def collapse_gene_region(value: object) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "Intergenic / unannotated"
    parts = set(re.split(r";", str(value)))
    promoter_terms = {"TSS1500", "TSS200", "5'UTR", "1stExon"}
    if parts & promoter_terms:
        return "Promoter / 5' region"
    if "Body" in parts:
        return "Gene body"
    if "3'UTR" in parts:
        return "3' UTR"
    return "Other genic"


def collapse_regulatory(value: object) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "No regulatory annotation"
    text = str(value)
    if "Promoter_Associated" in text:
        return "Promoter-associated"
    if "Gene_Associated" in text:
        return "Gene-associated"
    if "Cell_type_specific" in text:
        return "Cell-type-specific"
    if "Unclassified" in text:
        return "Unclassified regulatory"
    return "Other regulatory"


def stacked_percent(ax, df: pd.DataFrame, category_col: str, title: str, colors: dict[str, str]) -> None:
    order = [f"PC{i} {sign}" for i in range(1, 6) for sign in ["+", "-"]]
    counts = (
        df.groupby(["pc_direction", category_col], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(order)
    )
    pct = counts.div(counts.sum(axis=1), axis=0) * 100
    bottom = pd.Series(0, index=pct.index, dtype=float)
    for category in [c for c in colors if c in pct.columns]:
        ax.bar(
            pct.index,
            pct[category],
            bottom=bottom,
            color=colors[category],
            edgecolor="white",
            linewidth=0.4,
            label=category,
        )
        bottom += pct[category]
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of top-loading CpGs")
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.tick_params(axis="x", rotation=45)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1.0), loc="upper left", fontsize=9)


def first_genes(values: pd.Series, n: int = 10) -> str:
    seen: list[str] = []
    for value in values.dropna().astype(str):
        if not value.strip():
            continue
        for gene in value.split(";"):
            gene = gene.strip()
            if gene and gene not in seen:
                seen.append(gene)
            if len(seen) >= n:
                return "; ".join(seen)
    return ""


def main() -> None:
    df = pd.read_csv(TABLE, sep="\t")
    df["pc_direction"] = df.apply(pc_direction_label, axis=1)
    df["gene_region_collapsed"] = df["UCSC_RefGene_Group"].apply(collapse_gene_region)
    df["regulatory_collapsed"] = df["Regulatory_Feature_Group"].apply(collapse_regulatory)
    df["island_relation"] = df["Relation_to_Island"].fillna("Unknown").replace("", "Unknown")

    gene_region_colors = {
        "Promoter / 5' region": "#4575B4",
        "Gene body": "#74ADD1",
        "3' UTR": "#ABD9E9",
        "Other genic": "#FDAE61",
        "Intergenic / unannotated": "#BDBDBD",
    }
    island_colors = {
        "Island": "#1B9E77",
        "N_Shore": "#66A61E",
        "S_Shore": "#A6D854",
        "N_Shelf": "#E6AB02",
        "S_Shelf": "#FFD92F",
        "OpenSea": "#7570B3",
        "Unknown": "#BDBDBD",
    }
    regulatory_colors = {
        "Promoter-associated": "#D73027",
        "Gene-associated": "#FC8D59",
        "Cell-type-specific": "#7B3294",
        "Unclassified regulatory": "#F1B6DA",
        "Other regulatory": "#A6D854",
        "No regulatory annotation": "#BDBDBD",
    }

    fig, axes = plt.subplots(3, 1, figsize=(12.5, 11), constrained_layout=True)
    stacked_percent(axes[0], df, "gene_region_collapsed", "A. Gene-region annotation of top-loading CpGs", gene_region_colors)
    stacked_percent(axes[1], df, "island_relation", "B. CpG-island relation of top-loading CpGs", island_colors)
    stacked_percent(axes[2], df, "regulatory_collapsed", "C. Regulatory-feature annotation of top-loading CpGs", regulatory_colors)
    axes[2].set_xlabel("Principal component and loading direction")

    stem = OUT_DIR / "Response_Figure_PC_loading_annotation_summary"
    fig.savefig(stem.with_suffix(".png"), dpi=300, facecolor="white")
    fig.savefig(stem.with_suffix(".pdf"), facecolor="white")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, facecolor="white", pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)

    summary = (
        df.sort_values(["PC", "direction", "loading"], ascending=[True, True, False])
        .groupby(["PC", "direction"], observed=True)
        .agg(
            n_cpgs=("CpG", "size"),
            top_genes=("UCSC_RefGene_Name", first_genes),
        )
        .reset_index()
    )
    summary.to_csv(OUT_DIR / "Response_Table_PC_top_loading_genes.tsv", sep="\t", index=False)
    print(stem.with_suffix(".png"))
    print(OUT_DIR / "Response_Table_PC_top_loading_genes.tsv")


if __name__ == "__main__":
    main()
