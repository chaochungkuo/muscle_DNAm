#!/usr/bin/env python3
"""Build one PCA/t-SNE row figure per reviewer-requested subset.

Each output file contains two panels (PCA and t-SNE) with a single shared
legend on the right. This is intended for A4 rebuttal-letter use where the
10-panel combined figure is too dense.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "results" / "coordinates" / "subset_coordinates.tsv"
SUMMARY = ROOT / "results" / "tables" / "subset_analysis_summary.tsv"
OUT = ROOT / "figures" / "response"
OUT.mkdir(parents=True, exist_ok=True)

MANUSCRIPT_DIRS = [
    ROOT.parents[1] / "manuscripts" / "reviewer_round_2" / "to_Juliane_2026-07-23" / "figures_response",
    ROOT.parents[1] / "manuscripts" / "reviewer_round_2" / "official_submission_2026-07-23" / "figures_response",
]

PALETTE = {
    "Control": "#666666",
    "ALS": "#D73027",
    "NMA": "#FC8D59",
    "IBM": "#4575B4",
    "non-IBM IIM, NOS": "#74ADD1",
    "Multiminicores": "#1A9850",
}

SUBSETS = [
    ("excluding_MMC", "excluding MMC", "Response_Figure_subset_1_excluding_MMC"),
    ("excluding_controls", "excluding controls", "Response_Figure_subset_2_excluding_controls"),
    ("in_house_data", "in-house data", "Response_Figure_subset_3_in_house_data"),
    ("IBM_vs_nonIBM_IIM", "IBM vs non-IBM IIM", "Response_Figure_subset_4_IBM_vs_nonIBM_IIM"),
    ("ALS_vs_nonALS_NMA", "ALS vs non-ALS NMA", "Response_Figure_subset_5_ALS_vs_nonALS_NMA"),
]


def add_scatter(ax, df: pd.DataFrame, x: str, y: str, title: str, xlabel: str, ylabel: str) -> None:
    for group in [g for g in PALETTE if g in set(df["display_group"])]:
        gdf = df[df["display_group"] == group]
        ax.scatter(
            gdf[x],
            gdf[y],
            s=58,
            c=PALETTE[group],
            label=group,
            alpha=0.92,
            edgecolors="none",
        )
    ax.set_title(title, fontsize=16, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, fontsize=15, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", labelsize=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def save_all(fig, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".png"), dpi=300, facecolor="white", bbox_inches="tight")
    fig.savefig(stem.with_suffix(".pdf"), facecolor="white", bbox_inches="tight")
    fig.savefig(stem.with_suffix(".tiff"), dpi=600, facecolor="white", bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})


def main() -> None:
    coords = pd.read_csv(COORDS, sep="\t")
    summary = pd.read_csv(SUMMARY, sep="\t")
    written: list[Path] = []

    for subset, label, stem_name in SUBSETS:
        df = coords[coords["subset"] == subset].copy()
        ss = summary[summary["subset"] == subset].iloc[0]
        groups = [g for g in PALETTE if g in set(df["display_group"])]

        fig = plt.figure(figsize=(11.7, 4.4), constrained_layout=True)
        gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.34], wspace=0.08)
        ax_pca = fig.add_subplot(gs[0, 0])
        ax_tsne = fig.add_subplot(gs[0, 1])
        ax_leg = fig.add_subplot(gs[0, 2])
        ax_leg.axis("off")

        add_scatter(
            ax_pca,
            df,
            "PC1",
            "PC2",
            f"PCA: {label}",
            f"PC1 ({100 * ss['PC1_variance']:.2f}%)",
            f"PC2 ({100 * ss['PC2_variance']:.2f}%)",
        )
        add_scatter(
            ax_tsne,
            df,
            "TSNE1",
            "TSNE2",
            f"t-SNE: {label}",
            "t-SNE 1",
            "t-SNE 2",
        )

        handles = [
            plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=PALETTE[g], markeredgecolor="none", markersize=9, label=g)
            for g in groups
        ]
        ax_leg.legend(
            handles=handles,
            title="Disease group",
            loc="center left",
            frameon=False,
            fontsize=13,
            title_fontsize=14,
            borderaxespad=0,
        )

        stem = OUT / stem_name
        save_all(fig, stem)
        plt.close(fig)
        written.extend([stem.with_suffix(ext) for ext in [".png", ".pdf", ".tiff"]])

    for target_dir in MANUSCRIPT_DIRS:
        target_dir.mkdir(parents=True, exist_ok=True)
        for path in written:
            (target_dir / path.name).write_bytes(path.read_bytes())

    for path in written:
        print(path)


if __name__ == "__main__":
    main()
