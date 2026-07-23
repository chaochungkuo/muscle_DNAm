from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
OUT = FIG / "response"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


TITLE_FONT = font(52, True)
SUBTITLE_FONT = font(30, False)
PANEL_FONT = font(40, True)
CAPTION_FONT = font(25, False)
SMALL_FONT = font(22, False)


def source_path(stem: str) -> Path:
    for folder in ["web", "main", "supplementary"]:
        for suffix in [".png", ".tiff", ".tif"]:
            p = FIG / folder / f"{stem}{suffix}"
            if p.exists():
                return p
    raise FileNotFoundError(stem)


def load_image(stem: str) -> Image.Image:
    img = Image.open(source_path(stem)).convert("RGB")
    return img


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fnt, fill=(40, 45, 55), width=70, line_spacing=8) -> int:
    x, y = xy
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, width=width))
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        bbox = draw.textbbox((x, y), line or " ", font=fnt)
        y += bbox[3] - bbox[1] + line_spacing
    return y


def make_panel_card(panel: dict, width: int, height: int) -> Image.Image:
    card = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(card)
    pad = 26
    label_w = 58
    draw.text((pad, pad - 4), panel["label"], font=PANEL_FONT, fill=(20, 30, 45))
    title_x = pad + label_w
    draw.text((title_x, pad + 2), panel["title"], font=SUBTITLE_FONT, fill=(30, 41, 59))
    image_box = (pad, 92, width - pad, height - 26)
    img = load_image(panel["stem"])
    contained = ImageOps.contain(img, (image_box[2] - image_box[0], image_box[3] - image_box[1]), Image.Resampling.LANCZOS)
    x = image_box[0] + ((image_box[2] - image_box[0]) - contained.width) // 2
    y = image_box[1] + ((image_box[3] - image_box[1]) - contained.height) // 2
    card.paste(contained, (x, y))
    return card


def build_figure(name: str, title: str, subtitle: str, panels: list[dict], ncols: int, panel_size=(1500, 1120)) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    nrows = (len(panels) + ncols - 1) // ncols
    panel_w, panel_h = panel_size
    margin = 70
    gap = 34
    title_h = 20
    footer_h = 0
    width = margin * 2 + ncols * panel_w + (ncols - 1) * gap
    height = margin + title_h + nrows * panel_h + (nrows - 1) * gap + footer_h
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    top = margin + title_h
    for idx, panel in enumerate(panels):
        row = idx // ncols
        col = idx % ncols
        x = margin + col * (panel_w + gap)
        y = top + row * (panel_h + gap)
        canvas.paste(make_panel_card(panel, panel_w, panel_h), (x, y))
    png = OUT / f"{name}.png"
    pdf = OUT / f"{name}.pdf"
    tiff = OUT / f"{name}.tiff"
    canvas.save(png, optimize=True)
    canvas.save(pdf, "PDF", resolution=300.0)
    canvas.save(tiff, compression="tiff_lzw", dpi=(300, 300))
    print(png)
    print(pdf)
    print(tiff)


def panel(label: str, stem: str, title: str, caption: str) -> dict:
    return {"label": label, "stem": stem, "title": title, "caption": caption}


def main() -> None:
    build_figure(
        "Response_Figure_1_unsupervised_structure",
        "Response Figure 1. Unsupervised methylation structure and cohort variables",
        "Summary panels for Reviewer 1: the full post-QC methylation matrix shows disease-group-associated structure in PCA, t-SNE and label-free sample correlation, while PC-metadata associations document overlap with technical and cohort variables that must be considered in the interpretation.",
        [
            panel("A", "Figure_unsupervised_PCA", "Baseline PCA", "Scaled PCA shows broad group-associated methylation structure."),
            panel("B", "Figure_unsupervised_tSNE", "Baseline t-SNE", "t-SNE visualizes local neighborhood structure among the studied groups."),
            panel("C", "Figure_PC_metadata_associations", "PC–metadata associations", "Leading PCs associate with disease group and with available cohort variables."),
            panel("D", "Figure_sample_correlation_heatmap", "Full-matrix correlation heatmap", "Label-free sample clustering from all post-QC M-values."),
            panel("E", "Figure_sample_correlation_annotation_legend", "Annotation legend", "Color key for disease group, source, Sentrix and other annotation tracks."),
        ],
        ncols=2,
    )

    build_figure(
        "Response_Figure_2_tsne_pca_sensitivity",
        "Response Figure 2. t-SNE and PCA sensitivity analyses",
        "Summary panels addressing the reviewer’s t-SNE and PCA concerns: baseline structure was evaluated across random seeds, perplexities, initial PCA dimensions, direct pca=FALSE t-SNE and centered-scaled versus centered-unscaled PCA.",
        [
            panel("A", "Figure_tSNE_stability", "t-SNE parameter and seed sensitivity", "Main structure is not explained by one random seed or one parameter choice."),
            panel("B", "Figure_tSNE_direct_pca_false", "Direct t-SNE with pca=FALSE", "Direct full-matrix t-SNE provides an additional sensitivity check."),
            panel("C", "Figure_PCA_scree", "PCA variance explained", "Scree/cumulative-variance plots show how much variance is captured by leading PCs."),
            panel("D", "PCA_scaled_PC1_PC2", "Scaled PCA PC1–PC2", "Primary PCA view using centered and unit-variance-scaled CpGs."),
            panel("E", "PCA_unscaled_PC1_PC2", "Unscaled PCA PC1–PC2", "Sensitivity PCA using centered but unscaled M-values."),
        ],
        ncols=2,
    )

    build_figure(
        "Response_Figure_3_downstream_robustness",
        "Response Figure 3. Downstream robustness checks",
        "Summary panels for downstream robustness: covariate-adjusted differential methylation where estimable, metadata-only classification as a confounding diagnostic and patient-aware leakage-controlled supervised learning define the appropriate scope of the results.",
        [
            panel("A", "Figure_differential_sensitivity", "Differential methylation sensitivity", "Covariate sensitivity shows which contrasts remain supported under estimable adjustments."),
            panel("B", "Figure_metadata_only_classifier", "Metadata-only classifier", "Metadata alone contains disease-group information, supporting cautious interpretation."),
            panel("C", "Figure_patient_aware_ML", "Patient-aware supervised learning", "Leakage-fixed classification is internal to this selected pilot cohort."),
        ],
        ncols=3,
        panel_size=(1200, 1050),
    )

    pca_metadata_panels = [
        ("display_group", "Disease group", "Disease groups are shown on the same scaled PCA projection to define the reference pattern for comparison with cohort variables."),
        ("sentrix_id", "Sentrix ID", "Sentrix IDs are overlaid on the same PCA coordinates to assess whether chip-level structure overlaps with the leading components."),
        ("age_group", "Age group", "Age categories are displayed on the unchanged PCA projection to evaluate whether age distribution contributes to the visible structure."),
        ("gender", "Sex", "Sex is shown despite removal of sex-chromosome probes, because autosomal methylation can still show sex-associated differences."),
        ("muscle_location_group", "Biopsy site", "Biopsy-site groups are displayed to assess whether anatomical sampling location overlaps with the PCA structure."),
        ("city_of_origin", "City", "City or contributing center is shown as an available cohort variable that may overlap with disease group and technical processing."),
    ]
    metadata_panels = [
        ("display_group", "Disease group"),
        ("dataset_source", "Source"),
        ("sentrix_id", "Sentrix ID"),
        ("age_group", "Age group"),
        ("gender", "Sex"),
        ("muscle_location_group", "Biopsy site"),
        ("city_of_origin", "City"),
        ("lymphomonocytes", "Lymphomonocytes"),
    ]
    tsne_metadata_panels = [
        ("display_group", "Disease group"),
        ("sentrix_id", "Sentrix ID"),
        ("age_group", "Age group"),
        ("gender", "Sex"),
        ("muscle_location_group", "Biopsy site"),
        ("city_of_origin", "City"),
    ]
    build_figure(
        "Supplementary_Response_Figure_S1_PCA_metadata_coloring",
        "Supplementary Response Figure S1. PCA colored by available metadata",
        "The same scaled PCA coordinates are recolored by selected available metadata variables so that disease-group structure can be visually compared with Sentrix ID, age, sex, biopsy site and city without changing the underlying PCA projection.",
        [
            panel(chr(65 + i), f"pca_scaled_by_{stem}", title, caption)
            for i, (stem, title, caption) in enumerate(pca_metadata_panels)
        ],
        ncols=2,
    )
    build_figure(
        "Supplementary_Response_Figure_S2_tSNE_metadata_coloring",
        "Supplementary Response Figure S2. t-SNE colored by available metadata",
        "The same baseline t-SNE coordinates are recolored by each available metadata variable requested by the reviewer, allowing direct visual comparison of disease group with source, Sentrix ID, demographic variables, biopsy site, city and supplied lymphomonocyte category.",
        [
            panel(chr(65 + i), f"tsne_baseline_by_{stem}", title, "Same t-SNE coordinates; only the color annotation changes.")
            for i, (stem, title) in enumerate(tsne_metadata_panels)
        ],
        ncols=2,
    )
    build_figure(
        "Supplementary_Response_Figure_S3_PCA_sensitivity",
        "Supplementary Response Figure S3. Expanded PCA sensitivity",
        "Expanded PCA scrutiny requested by the reviewer: cumulative variance, multiple pairwise PC projections and centered-scaled versus centered-unscaled PCA were used to test whether the observed structure depends on one projection or one scaling choice.",
        [
            panel("A", "Figure_PCA_scree", "PCA scree plot", "Variance explained by each leading PC."),
            panel("B", "PCA_cumulative_variance", "Cumulative variance", "Cumulative variance explained by leading PCs."),
            panel("C", "PCA_scaled_PC1_PC2", "Scaled PC1–PC2", "Primary scaled PCA projection."),
            panel("D", "PCA_unscaled_PC1_PC2", "Unscaled PC1–PC2", "Sensitivity without unit-variance scaling."),
            panel("E", "PCA_scaled_PC1_PC3", "Scaled PC1–PC3", "Scaled PCA projection including PC3."),
            panel("F", "PCA_unscaled_PC1_PC3", "Unscaled PC1–PC3", "Unscaled PCA projection including PC3."),
            panel("G", "PCA_scaled_PC2_PC3", "Scaled PC2–PC3", "Scaled secondary PCA structure."),
            panel("H", "PCA_unscaled_PC2_PC3", "Unscaled PC2–PC3", "Unscaled secondary PCA structure."),
        ],
        ncols=2,
    )
    build_figure(
        "Supplementary_Response_Figure_S4_subset_analyses",
        "Supplementary Response Figure S4. Recomputed subset analyses",
        "PCA and t-SNE were recomputed independently within each reviewer-requested subset rather than by removing points from the full-cohort embedding, allowing clinically focused comparisons and source-sensitive analyses to be evaluated on their own structure.",
        [
            panel("A", "subset_excluding_MMC_PCA", "Excluding MMC — PCA", "Recomputed PCA after excluding MMC."),
            panel("B", "subset_excluding_MMC_tSNE", "Excluding MMC — t-SNE", "Recomputed t-SNE after excluding MMC."),
            panel("C", "subset_excluding_controls_PCA", "Excluding controls — PCA", "Recomputed PCA after excluding controls."),
            panel("D", "subset_excluding_controls_tSNE", "Excluding controls — t-SNE", "Recomputed t-SNE after excluding controls."),
            panel("E", "subset_in_house_data_PCA", "In-house data — PCA", "Recomputed PCA using in-house data."),
            panel("F", "subset_in_house_data_tSNE", "In-house data — t-SNE", "Recomputed t-SNE using in-house data."),
            panel("G", "subset_IBM_vs_nonIBM_IIM_PCA", "IBM vs non-IBM IIM — PCA", "Clinically focused inflammatory-myopathy subset."),
            panel("H", "subset_IBM_vs_nonIBM_IIM_tSNE", "IBM vs non-IBM IIM — t-SNE", "Clinically focused inflammatory-myopathy subset."),
            panel("I", "subset_ALS_vs_nonALS_NMA_PCA", "ALS vs non-ALS NMA — PCA", "Clinically focused neurogenic-atrophy subset."),
            panel("J", "subset_ALS_vs_nonALS_NMA_tSNE", "ALS vs non-ALS NMA — t-SNE", "Clinically focused neurogenic-atrophy subset."),
        ],
        ncols=2,
    )
    build_figure(
        "Supplementary_Response_Figure_S5_ALS_NMA_robustness",
        "Supplementary Response Figure S5. Exploratory ALS versus non-ALS NMA robustness",
        "The ALS versus non-ALS NMA comparison was evaluated separately because it is the smallest clinically focused comparison; subset PCA/t-SNE and leave-one-sample checks support keeping this result exploratory and hypothesis-generating.",
        [
            panel("A", "subset_ALS_vs_nonALS_NMA_PCA", "ALS vs non-ALS NMA — PCA", "Subset PCA shows overlap in the smallest clinically focused comparison."),
            panel("B", "subset_ALS_vs_nonALS_NMA_tSNE", "ALS vs non-ALS NMA — t-SNE", "Subset t-SNE supports exploratory rather than definitive ALS/NMA interpretation."),
            panel("C", "influential_sample_analysis", "Influential samples", "Leave-one-sample checks show sensitivity in small disease-pair contrasts."),
        ],
        ncols=3,
        panel_size=(1200, 1050),
    )


if __name__ == "__main__":
    main()
