from __future__ import annotations

import base64
import html
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
PACKAGE = PROJECT / "manuscripts" / "reviewer_round_2" / "to_Juliane_2026-07-16"
OUT = PACKAGE / "reviewer_response_workbook.html"
WEB_FIG = ROOT / "figures" / "web"
SUPP_FIG = ROOT / "figures" / "supplementary"
SUPP_PREVIEW = PACKAGE / "figures_review_png" / "supplementary"


def png_data(name: str) -> str:
    path = WEB_FIG / name
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{payload}"


def p(text: str) -> str:
    return f"<p>{html.escape(text)}</p>"


def li(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def quote(text: str) -> str:
    return f"<blockquote>{html.escape(text)}</blockquote>"


def paragraph_list(items: list[str]) -> str:
    return "".join(f"<p>{html.escape(item)}</p>" for item in items)


def main_fig(name: str, caption: str) -> str:
    return (
        '<figure class="figure">'
        f'<img src="{png_data(name)}" alt="{html.escape(caption)}">'
        f"<figcaption>{html.escape(caption)}</figcaption>"
        "</figure>"
    )


def build_supplementary_previews() -> None:
    if SUPP_PREVIEW.exists():
        shutil.rmtree(SUPP_PREVIEW)
    SUPP_PREVIEW.mkdir(parents=True)
    for source in sorted(SUPP_FIG.glob("*.tiff")):
        destination = SUPP_PREVIEW / f"{source.stem}.png"
        with Image.open(source) as img:
            img = img.convert("RGB")
            img.thumbnail((1500, 1050), Image.Resampling.LANCZOS)
            img.save(destination, optimize=True)


def figure_remark(name: str) -> str:
    stem = Path(name).stem
    exact = {
        "PCA_cumulative_variance": "Shows cumulative variance beyond the first two PCs.",
        "PCA_scaled_PC1_PC2": "Submitted-style scaled PCA reference view.",
        "PCA_scaled_PC1_PC3": "Checks whether structure persists when PC3 is considered.",
        "PCA_scaled_PC2_PC3": "Checks secondary PCA structure beyond PC1.",
        "PCA_unscaled_PC1_PC2": "Tests whether PCA structure depends on unit-variance scaling.",
        "PCA_unscaled_PC1_PC3": "Unscaled PCA sensitivity view including PC3.",
        "PCA_unscaled_PC2_PC3": "Unscaled PCA sensitivity view of secondary components.",
        "influential_sample_analysis": "Leave-one-sample influence check for small-group contrasts.",
    }
    if stem in exact:
        return exact[stem]
    if stem.startswith("subset_ALS_vs_nonALS_NMA"):
        return "ALS versus non-ALS NMA subset; weakest and most exploratory contrast."
    if stem.startswith("subset_IBM_vs_nonIBM_IIM"):
        return "IBM versus non-IBM IIM, NOS subset recomputed independently."
    if stem.startswith("subset_excluding_MMC"):
        return "Checks whether structure is driven by the MMC group."
    if stem.startswith("subset_excluding_controls"):
        return "Checks whether structure is driven by control samples."
    if stem.startswith("subset_in_house_data"):
        return "Restricts the analysis to in-house data."
    if stem.startswith("pca_scaled_by_"):
        variable = stem.replace("pca_scaled_by_", "").replace("_", " ")
        return f"Scaled PCA colored by {variable}; checks alignment with PCA structure."
    if stem.startswith("pca_unscaled_by_"):
        variable = stem.replace("pca_unscaled_by_", "").replace("_", " ")
        return f"Unscaled PCA colored by {variable}; checks robustness without CpG scaling."
    if stem.startswith("tsne_baseline_by_"):
        variable = stem.replace("tsne_baseline_by_", "").replace("_", " ")
        return f"Baseline t-SNE colored by {variable}; checks alignment with the submitted embedding."
    return "Supporting sensitivity figure for this reviewer-response point."


def supplementary_figures(names: list[str]) -> str:
    if not names:
        return ""
    cards = []
    for name in names:
        stem = Path(name).stem
        title = stem.replace("_", " ")
        cards.append(
            '<figure class="figure thumb">'
            f'<img src="figures_review_png/supplementary/{html.escape(stem)}.png" alt="{html.escape(title)}">'
            f"<figcaption><strong>{html.escape(title)}</strong><br>{html.escape(figure_remark(name))}</figcaption>"
            "</figure>"
        )
    return '<div class="figure-grid">' + "".join(cards) + "</div>"


def table_block(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


INSTRUCTIONS = {
    "overall_confounding": {
        "where": "Abstract, Results opening, Discussion, conclusion, and rebuttal overview.",
        "change": [
            "Replace disease-intrinsic, disease-specific, or diagnostic-certainty wording with disease-group-associated / pilot / hypothesis-generating wording.",
            "State that source, Sentrix, demographic variables and biopsy site align with leading structure and cannot be fully separated from disease group in this cohort.",
        ],
        "wording": "The revised analyses show methylation structure associated with the studied disease groups, but this structure also overlaps with dataset source, Sentrix array, demographic variables and biopsy site. We therefore interpret the findings as pilot, disease-group-associated observations rather than disease-intrinsic signatures or clinical diagnostic validation.",
        "owner": "Joseph can implement the wording; Juliane should approve the final scientific tone.",
        "status": "Implemented in draft at high level; final approval needed.",
    },
    "metadata_annotations": {
        "where": "Methods metadata paragraph, Results confounder analysis paragraph, Supplementary figure legends, Discussion limitations.",
        "change": [
            "List the supplied annotation variables used for recoloring PCA/t-SNE coordinates.",
            "State explicitly that lymphomonocytes were displayed as supplied but not interpreted biologically because the scoring definition was unavailable to the analyst.",
            "State that macrophage, fiber-type, denervation, fibrosis, necrosis and pathology-severity scores were not available unless Juliane supplies validated measures.",
        ],
        "wording": "PCA and t-SNE coordinates were annotated by disease group, dataset source, Sentrix ID, age, sex, biopsy-site group, city of origin and the supplied lymphomonocyte category. The lymphomonocyte category was used only as a descriptive annotation because its scoring definition was unavailable to the analyst.",
        "owner": "Joseph for analysis wording; Juliane for the lymphomonocyte definition and unavailable pathology variables.",
        "status": "Analysis implemented; clinical/pathology definitions remain owner-dependent.",
    },
    "tsne_pca_sensitivity": {
        "where": "Methods, Results t-SNE sensitivity paragraph, Supplementary figure legend, rebuttal response.",
        "change": [
            "Correct the t-SNE method to state that Rtsne used pca=TRUE and initial_dims=50 by default.",
            "Add direct pca=FALSE analysis and the initial_dims/perplexity/seed sensitivity grid.",
            "Avoid interpreting exact t-SNE distances or cluster geometry as stable global distances.",
        ],
        "wording": "The baseline t-SNE was computed with Rtsne using pca=TRUE and initial_dims=50; therefore, the full post-QC M-value matrix was first internally reduced to 50 centered, unscaled principal components before generating the two-dimensional embedding. We additionally performed direct pca=FALSE and parameter/seed sensitivity analyses.",
        "owner": "Joseph.",
        "status": "Implemented in draft; wording can be tightened for journal style.",
    },
    "correlation_heatmap_figure1f": {
        "where": "Figure 1 panel plan, Results first methylation-structure paragraph, Figure 1 legend, supplement.",
        "change": [
            "Replace Figure 1F with the label-free full-matrix sample-correlation heatmap, or add it as the main unsupervised heatmap.",
            "Move the previous top-CpG heatmap to the supplement or label it clearly as supervised descriptive visualization.",
            "State that clustering order was determined without disease labels.",
        ],
        "wording": "Figure 1F now shows a label-free sample-to-sample Pearson correlation heatmap calculated from the complete post-QC M-value matrix. Samples were hierarchically clustered using 1 minus Pearson correlation and complete linkage; disease group and metadata variables were added only as annotations after clustering.",
        "owner": "Juliane to approve final figure placement; Joseph can update figure legend and rebuttal.",
        "status": "Analysis complete; final figure allocation needs approval.",
    },
    "pca_scrutiny": {
        "where": "Methods PCA paragraph, Results PCA sensitivity paragraph, Supplementary figures/tables, rebuttal.",
        "change": [
            "Add scree/cumulative variance and PC1-PC2, PC1-PC3, PC2-PC3 projections.",
            "Describe scaled PCA as the submitted baseline and centered-unscaled PCA as sensitivity.",
            "Report quantitative PC-metadata associations and top-loading annotation without claiming disease-only axes.",
        ],
        "wording": "We expanded the PCA analysis by adding PC1-PC20 variance summaries, multiple pairwise projections, centered-scaled and centered-unscaled analyses, quantitative PC-metadata associations and annotation of leading loadings. These analyses show robust structure but also overlap with technical and cohort variables.",
        "owner": "Joseph.",
        "status": "Implemented analytically; final figure numbering and supplement references need proofreading.",
    },
    "subset_influence": {
        "where": "Results sensitivity paragraph, Supplementary figures, Discussion limitations, rebuttal.",
        "change": [
            "State that PCA and t-SNE were recomputed within each requested subset, not merely subsetted from the full embedding.",
            "Report that in-house-data and disease-pair analyses are weaker than the full mixed-source cohort.",
            "Use the influence analysis to justify cautious wording for small disease-pair contrasts.",
        ],
        "wording": "PCA and t-SNE were recomputed independently after excluding MMC, excluding controls, restricting to in-house data, comparing IBM with non-IBM IIM, NOS, and comparing ALS with non-ALS NMA. The subset analyses, especially ALS versus non-ALS NMA, support exploratory rather than definitive interpretation.",
        "owner": "Joseph.",
        "status": "Implemented analytically; wording needs final integration.",
    },
    "downstream_validation": {
        "where": "Methods differential analysis/classifier paragraphs, Results downstream sensitivity paragraph, Discussion limitations, rebuttal.",
        "change": [
            "State which covariate models were estimable and which were rank deficient.",
            "Add metadata-only classifier as a confounding diagnostic, not as a biological classifier.",
            "Keep supervised learning language internal to the studied groups.",
        ],
        "wording": "Age/sex and biopsy-site adjusted models were fitted where estimable, whereas source and Sentrix could not be separated from disease group in full-rank models because of structural alignment. Metadata-only classification further indicated that classifier performance cannot be interpreted as disease-intrinsic or clinically validated.",
        "owner": "Joseph; Juliane to approve limitation strength.",
        "status": "Implemented analytically; final limitation wording needs approval.",
    },
    "supervised_wording": {
        "where": "Abstract, supervised learning Methods/Results, Figure 6 legend, Discussion, rebuttal.",
        "change": [
            "Replace correct diagnosis / predicted diagnosis with classified disease group or classified the studied groups.",
            "Clarify that non-ALS NMA and non-IBM IIM, NOS are study groups, not complete clinical diagnoses.",
            "State that the model is not an externally validated clinical diagnostic classifier.",
        ],
        "wording": "The supervised analysis is presented as exploratory classification among the studied disease groups. It does not establish a clinically validated diagnostic classifier and does not cover the complete clinical differential diagnosis.",
        "owner": "Joseph for wording; Juliane for final clinical terminology.",
        "status": "Mostly implemented; final full-manuscript proofreading required.",
    },
    "inclusion_exclusion": {
        "where": "Methods, Human samples section; rebuttal to Reviewer 2 comment 1.",
        "change": [
            "Add archive candidate totals by group, exclusion counts and exclusion reasons.",
            "State whether all candidate cases in the eight-year interval were reviewed.",
            "Describe slide review, clinical-information review, diagnosing pathologists and adjudication process.",
        ],
        "wording": "[Juliane to insert exact factual wording: total archive candidates, cases reviewed, slide/clinical re-review process, adjudication, exclusion counts and exclusion reasons.]",
        "owner": "Juliane / clinical pathology team.",
        "status": "Blocked until clinical/pathology facts are supplied.",
    },
    "cell_composition": {
        "where": "Methods if covariates exist; otherwise Discussion limitations and rebuttal to Reviewer 2 comment 2.",
        "change": [
            "If validated deconvolution or pathology scores exist, provide them and rerun relevant models.",
            "If not, explicitly state that cell-composition-adjusted analyses were unavailable and this is a major limitation.",
            "Do not use undefined lymphomonocyte categories as a substitute for validated deconvolution.",
        ],
        "wording": "Validated sample-level deconvolution estimates or histopathology scores suitable for covariate adjustment were not available for the present analysis. The absence of cell-composition-adjusted differential methylation models is therefore a major limitation.",
        "owner": "Juliane to confirm availability; Joseph to rerun if valid covariates are supplied.",
        "status": "Limitation route drafted; can change only if new validated covariates are supplied.",
    },
    "als_nma": {
        "where": "ALS/NMA Results, gene-set interpretation, Discussion, rebuttal to Reviewer 2 comment 3.",
        "change": [
            "Keep the comparison but label it exploratory and hypothesis-generating.",
            "Mention small ALS sample size, overlap, individual-sample influence and biopsy-site sensitivity.",
            "Avoid language implying a validated ALS methylation signature.",
        ],
        "wording": "The ALS versus non-ALS NMA comparison is retained as exploratory and hypothesis-generating. The small ALS sample size, overlap in unsupervised analyses, individual-sample influence and loss of FDR-significant CpGs after biopsy-site adjustment preclude strong interpretation.",
        "owner": "Joseph for draft; Juliane to approve clinical tone.",
        "status": "Implemented conceptually; final wording needs approval.",
    },
    "proofreading": {
        "where": "Entire manuscript, supplement references, author list, title page, final rebuttal.",
        "change": [
            "Run a final terminology pass after Juliane inserts clinical text.",
            "Check supplement numbering and remove remaining placeholders.",
            "Confirm author order, Tayfun Palaz placeholder and co-last/equal-contribution wording.",
        ],
        "wording": "The manuscript has been revised for diagnostic overstatement and placeholder supplement references; final author-level proofreading and remaining placeholder resolution will be completed before resubmission.",
        "owner": "Juliane / all authors.",
        "status": "Not submission-ready until clinical text and author decisions are finalized.",
    },
}


def manuscript_edits_box(chunk: dict) -> str:
    edits = chunk.get("exact_edits")
    if not edits:
        edits = [
            {
                "location": "Whole relevant manuscript section",
                "find": "No exact paragraph locator has been assigned yet.",
                "action": "Use the general manuscript guidance below.",
                "replacement": " ".join(chunk.get("manuscript", [])),
            }
        ]
    note = (
        "<p>DOCX files do not preserve stable line numbers in a machine-readable way. "
        "The locations below use the current clean revision draft page/paragraph locator plus exact searchable text; "
        "final page/line numbers should be confirmed in Word after Juliane accepts the final tracked manuscript layout.</p>"
    )
    rows = [
        [
            edit["location"],
            edit["find"],
            edit["action"],
            edit["replacement"],
        ]
        for edit in edits
    ]
    return (
        '<div class="box edit-box"><div class="label">Suggested modification in the manuscript</div>'
        + note
        + table_block(["Location", "Find this text", "Action", "Proposed exact text"], rows)
        + "</div>"
    )


def draft_rebuttal_box(chunk: dict) -> str:
    figures = chunk.get("rebuttal_figures")
    figure_table = ""
    if figures:
        rows = [[f["where"], f["figure"], f["reason"], f["caption"]] for f in figures]
        figure_table = (
            '<div class="subsection-label">Figures to include with this rebuttal response</div>'
            + table_block(["Where to insert", "Figure file", "Why it belongs here", "Suggested caption text"], rows)
        )
    else:
        figure_table = (
            '<div class="subsection-label">Figures to include with this rebuttal response</div>'
            "<p>No separate rebuttal figure is required for this point unless the editor requests all supporting material inline. "
            "If space allows, refer to the relevant supplementary figure/table rather than duplicating it in the rebuttal letter.</p>"
        )
    return (
        '<div class="box draft"><div class="label">Draft for rebuttal letter</div>'
        + p(chunk["draft"])
        + figure_table
        + "</div>"
    )


CHUNKS = [
    {
        "id": "overall_confounding",
        "reviewer": "Reviewer 1",
        "title": "1. Overall concern: strong clustering may reflect confounding",
        "status": "Analysis complete; interpretation must be cautious",
        "owner": "Joseph drafted; Juliane to approve wording",
        "quote": "The cluster separation observed in the t-SNE and PCA plots is unexpectedly strong... It is essential to establish that this structure is robustly associated with the disease groups rather than technical, demographic, or tissue composition variables.",
        "asking": [
            "The reviewer is not rejecting the observation; they are asking whether the apparent disease-group separation is stable and whether it may be explained by source, batch, demographics, biopsy site, or tissue composition.",
            "The safest answer is to treat the structure as disease-group-associated, not disease-intrinsic or diagnostic.",
        ],
        "decision": [
            "Use Juliane's revised Excel table as the authoritative metadata source.",
            "Retain all 73 samples from 72 patients.",
            "Do not change disease groups.",
            "Do not invent definitions for unknown clinical/pathology variables.",
        ],
        "did": [
            "Reproduced baseline PCA and t-SNE.",
            "Colored the same coordinates by disease group, dataset source, Sentrix, age, sex, biopsy site, city, and supplied lymphomonocyte category.",
            "Quantified PC-metadata associations and added source/Sentrix estimability checks.",
            "Added downstream sensitivity checks for differential methylation and supervised learning.",
        ],
        "figures": main_fig("Figure_unsupervised_PCA.png", "Baseline scaled PCA.")
        + main_fig("Figure_unsupervised_tSNE.png", "Baseline t-SNE.")
        + main_fig("Figure_PC_metadata_associations.png", "Leading PC associations with disease group and supplied metadata."),
        "supplementary": "",
        "interpretation": [
            "The methylation matrix contains strong structure, but the leading structure is not cleanly separable from source, Sentrix, demographic variables, and biopsy site in this cohort.",
            "This supports a pilot, hypothesis-generating interpretation and argues against disease-entity-specific or clinical diagnostic wording.",
        ],
        "draft": "We agree that the strong separation in the unsupervised plots required additional scrutiny. We therefore reanalyzed the cohort using the revised metadata table, annotated PCA and t-SNE coordinates by disease group and available confounders, and quantified associations between leading PCs and metadata variables. These analyses show disease-group-associated structure, but also substantial alignment with dataset source, Sentrix array, demographic variables and biopsy site. We therefore revised the manuscript to avoid disease-intrinsic or clinical-diagnostic claims and now present the findings as pilot, group-associated observations requiring validation in larger balanced cohorts.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 1, paragraph 2; submitted manuscript: page 1, title paragraph",
                "find": "Disease group-specific DNA methylation patterns",
                "action": "Replace title to avoid disease-specific/intrinsic claim.",
                "replacement": "Disease group-associated DNA methylation patterns in non-neoplastic skeletal muscle pathology",
            },
            {
                "location": "Current clean draft: page 4, paragraph 42; abstract/concluding abstract paragraph",
                "find": "T-SNE analysis and hierarchical clustering revealed alignment with distinct muscle disease groups. Based on the CpG site methylation data, supervised learning...",
                "action": "Replace the abstract result/conclusion with the cautious version below.",
                "replacement": "Unsupervised PCA, t-SNE and sample-correlation analyses demonstrated strong structure associated with the studied disease groups. However, sensitivity analyses also identified substantial associations with dataset source, Sentrix array, age, sex and biopsy site. Patient-aware supervised learning classified the studied groups with high held-out accuracy, but metadata alone also predicted group membership, indicating that the present pilot cohort cannot establish a clinically validated or disease-intrinsic classifier.",
            },
            {
                "location": "Current clean draft: page 12, paragraph 75; first Results subsection on unsupervised structure",
                "find": "Disease groups cluster together in PCA and t-SNE analysis / When performing hierarchical clustering considering only top 10 differentially methylated sites...",
                "action": "Replace the section heading and opening interpretation.",
                "replacement": "Disease-group-associated methylation structure is accompanied by technical and cohort structure. Unsupervised PCA and t-SNE showed strong structure associated with the studied groups, although ALS and non-ALS NMA overlapped. The exact t-SNE geometry varied across initial dimensions, perplexities and random seeds; a direct full-matrix t-SNE with pca=FALSE was feasible and provided an additional sensitivity analysis. Leading PCs were associated not only with disease group but also with dataset source, Sentrix ID and other supplied metadata.",
            },
            {
                "location": "Current clean draft: page 12, paragraph 112; Discussion opening limitation paragraph",
                "find": "In this cohort consisting of inclusion body myositis...",
                "action": "Replace with pilot/cohort limitation wording.",
                "replacement": "In this pilot cohort, bulk-muscle CpG methylation showed strong structure associated with inflammatory myopathy, neurogenic atrophy, multi-minicore myopathy and control groups. However, disease group, dataset source, Sentrix array, age, sex and biopsy site were imbalanced and partly aligned. Consequently, the observed patterns cannot be attributed exclusively to disease-intrinsic methylation, and their clinical diagnostic value remains undetermined.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 overall confounding response, immediately after the first paragraph saying we reanalyzed metadata/confounders.",
                "figure": "Figure_PC_metadata_associations.pdf",
                "reason": "This is the strongest compact evidence that disease group is not the only variable aligned with leading PCs.",
                "caption": "Association of leading scaled and unscaled PCs with disease group and supplied metadata, quantified by eta-squared.",
            }
        ],
        "manuscript": [
            "Title/abstract/results/discussion should use disease-group-associated wording.",
            "Avoid intrinsic, disease-specific entity, or diagnostic classifier claims.",
        ],
    },
    {
        "id": "metadata_annotations",
        "reviewer": "Reviewer 1 / Juliane action mapping",
        "title": "2. Metadata and confounder coloring requested by Juliane",
        "status": "Available metadata covered; unavailable variables require Juliane",
        "owner": "Juliane for unavailable pathology variables",
        "quote": "Please display the same coordinates with samples colored separately by potential confounder variables: dataset source, batch information, age, sex, biopsy site, estimated inflammatory cell fraction, fiber type estimates, denervation estimates and pathology severity...",
        "asking": [
            "The reviewer wants to know whether the visual clusters also follow technical or tissue-composition variables.",
            "They also ask for variables that were not available in the analysis table.",
        ],
        "decision": [
            "Use the low/medium/high lymphomonocyte field only as a supplied descriptive annotation.",
            "Do not interpret lymphomonocytes biologically without Juliane's definition.",
            "Do not estimate macrophages, fiber type, denervation, fibrosis, necrosis, or pathology severity without validated inputs.",
        ],
        "did": [
            "Generated confounder-colored PCA/t-SNE panels for all supplied variables.",
            "Documented unavailable requested pathology variables as a limitation rather than guessing.",
        ],
        "figures": main_fig("Figure_unsupervised_PCA.png", "PCA overview; detailed confounder views are shown below.")
        + main_fig("Figure_unsupervised_tSNE.png", "t-SNE overview; detailed confounder views are shown below."),
        "supplementary": supplementary_figures([
            "pca_scaled_by_display_group.pdf",
            "pca_scaled_by_dataset_source.pdf",
            "pca_scaled_by_sentrix_id.pdf",
            "pca_scaled_by_age_group.pdf",
            "pca_scaled_by_gender.pdf",
            "pca_scaled_by_muscle_location_group.pdf",
            "pca_scaled_by_city_of_origin.pdf",
            "pca_scaled_by_lymphomonocytes.pdf",
            "tsne_baseline_by_display_group.pdf",
            "tsne_baseline_by_dataset_source.pdf",
            "tsne_baseline_by_sentrix_id.pdf",
            "tsne_baseline_by_age_group.pdf",
            "tsne_baseline_by_gender.pdf",
            "tsne_baseline_by_muscle_location_group.pdf",
            "tsne_baseline_by_city_of_origin.pdf",
            "tsne_baseline_by_lymphomonocytes.pdf",
        ]),
        "interpretation": [
            "Available metadata were fully displayed.",
            "The missing tissue-composition variables remain a real limitation and should be acknowledged explicitly.",
        ],
        "draft": "We displayed the PCA and t-SNE coordinates with samples colored by all available metadata fields, including dataset source, Sentrix ID, age, sex, biopsy-site group, city of origin and the supplied lymphomonocyte category. The lymphomonocyte category was treated as a descriptive annotation only because its scoring provenance was unavailable to the analyst. Validated macrophage fraction, fiber-type, denervation, fibrosis, necrosis and pathology-severity estimates were not available for covariate modeling; this is now stated as a limitation.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 9, paragraph 63; Methods, array data analysis",
                "find": "The same coordinates were annotated separately by disease group, dataset source, Sentrix ID, age, sex, biopsy site, city of origin and the supplied lymphomonocyte category.",
                "action": "Keep this sentence, but expand the following limitation sentence.",
                "replacement": "The supplied lymphomonocyte category was displayed as a descriptive annotation only, because its scoring definition and reproducibility were unavailable to the analyst. Validated macrophage fraction, fiber-type, denervation, fibrosis, necrosis and pathology-severity estimates were not available and therefore were not inferred or used as adjustment covariates.",
            },
            {
                "location": "Current clean draft: Supplementary figure legend section; add after PCA/t-SNE confounder panels",
                "find": "No dedicated legend currently lists all confounder-colored PCA/t-SNE panels.",
                "action": "Add a supplementary figure legend grouping the confounder-colored panels.",
                "replacement": "Supplementary Figure X. PCA and t-SNE coordinates colored by available metadata variables. The same scaled PCA and baseline t-SNE coordinates are displayed repeatedly with colors representing disease group, dataset source, Sentrix ID, age group, sex, biopsy-site group, city of origin and the supplied lymphomonocyte category. These plots evaluate whether apparent disease-group structure overlaps with technical, demographic or biopsy variables.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 confounder-coloring response.",
                "figure": "Supplementary PCA/t-SNE confounder panels: pca_scaled_by_*.pdf and tsne_baseline_by_*.pdf",
                "reason": "Juliane noted that more figures should be added in the rebuttal or supplement; these directly answer the request to color identical coordinates by each confounder.",
                "caption": "Same PCA/t-SNE coordinates colored separately by disease group, dataset source, Sentrix ID, age group, sex, biopsy-site group, city of origin and lymphomonocytes.",
            },
            {
                "where": "Reviewer 1 overall confounding response or supplement.",
                "figure": "Figure_PC_metadata_associations.pdf",
                "reason": "Provides quantitative support beyond visual inspection.",
                "caption": "Eta-squared association between leading PCs and supplied metadata variables.",
            },
        ],
        "manuscript": [
            "Add explicit statement that unavailable tissue-composition variables were not inferred.",
            "Add major limitation wording if Juliane confirms no validated estimates are available.",
        ],
    },
    {
        "id": "tsne_pca_sensitivity",
        "reviewer": "Reviewer 1",
        "title": "3. t-SNE default PCA, direct pca=FALSE, and parameter sensitivity",
        "status": "Complete",
        "owner": "Joseph drafted; Juliane to approve wording",
        "quote": "Rtsne default parameters include pca = TRUE and initial_dims = 50... Please include a direct analysis with pca = FALSE if computationally feasible. Please provide a systematic sensitivity analysis...",
        "asking": [
            "The reviewer wants us to correct the method description: baseline t-SNE did not directly use the full probe space; it used Rtsne's internal PCA first.",
            "They also want to know whether the t-SNE map depends on parameter choice or random seed.",
        ],
        "decision": [
            "Report Rtsne default internal PCA explicitly.",
            "Show direct pca=FALSE and systematic sensitivity.",
        ],
        "did": [
            "Ran initial_dims 10, 20, 30, 50, 72; perplexity 5, 10, 15, 20; ten seeds, for 200 runs.",
            "Quantified stability with Procrustes similarity and silhouette.",
            "Ran direct full 771,381-probe t-SNE with pca=FALSE.",
        ],
        "figures": main_fig("Figure_tSNE_stability.png", "t-SNE stability across initial dimensions, perplexities and seeds.")
        + main_fig("Figure_tSNE_direct_pca_false.png", "Direct full-matrix t-SNE with pca=FALSE."),
        "supplementary": "",
        "interpretation": [
            "Disease-group structure is not a single-seed artifact, but exact two-dimensional geometry changes with parameters.",
            "The baseline figure should not be overinterpreted as a precise global geometry.",
        ],
        "draft": "We thank the reviewer for pointing out the Rtsne default. We now state explicitly that the baseline t-SNE used pca=TRUE and initial_dims=50, meaning that t-SNE was performed after Rtsne's internal centered, unscaled PCA. We performed the requested sensitivity analysis across five initial-dimensional settings, four perplexities and ten random seeds, and quantified stability using Procrustes similarity and silhouette values. We also performed a direct full-matrix analysis with pca=FALSE. These analyses support the presence of broad group-associated structure but show that the exact cluster geometry is parameter-dependent.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 9, paragraph 63; Methods, array data analysis",
                "find": "Baseline t-SNE used Rtsne with perplexity 15, theta 0.5, seed 42 and its default internal centered, unscaled PCA (pca=TRUE, initial_dims=50).",
                "action": "Keep and verify this sentence is in Methods.",
                "replacement": "Baseline t-SNE used Rtsne with perplexity 15, theta 0.5, seed 42 and its default internal centered, unscaled PCA (pca=TRUE, initial_dims=50). Sensitivity analyses varied initial_dims (10, 20, 30, 50 and 72), perplexity (5, 10, 15 and 20), and ten random seeds; a direct full-matrix analysis with pca=FALSE was also performed.",
            },
            {
                "location": "Current clean draft: page 12, paragraph 75; Results, unsupervised methylation structure",
                "find": "The exact t-SNE geometry varied across initial dimensions, perplexities and random seeds...",
                "action": "Keep this interpretation and avoid claiming exact t-SNE distances are stable.",
                "replacement": "The exact t-SNE geometry varied across initial dimensions, perplexities and random seeds; a direct full-matrix t-SNE with pca=FALSE was feasible and provided an additional sensitivity analysis. Therefore, the t-SNE is interpreted as a visualization of broad neighborhood structure rather than a quantitative global distance map.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 Rtsne default/sensitivity response, immediately after the first sentence explaining pca=TRUE and initial_dims=50.",
                "figure": "Figure_tSNE_stability.pdf",
                "reason": "Reviewer specifically requested systematic sensitivity and quantitative stability rather than visual inspection only.",
                "caption": "t-SNE stability across initial dimensions, perplexities and random seeds, summarized by Procrustes similarity and disease-group silhouette.",
            },
            {
                "where": "Same rebuttal subsection, after Figure_tSNE_stability.",
                "figure": "Figure_tSNE_direct_pca_false.pdf",
                "reason": "Reviewer specifically requested direct pca=FALSE analysis if feasible.",
                "caption": "Direct full post-QC M-value matrix t-SNE with pca=FALSE.",
            },
        ],
        "manuscript": [
            "Methods: explicitly state Rtsne pca=TRUE, initial_dims=50.",
            "Results/supplement: add pca=FALSE and sensitivity summaries.",
        ],
    },
    {
        "id": "correlation_heatmap_figure1f",
        "reviewer": "Reviewer 1",
        "title": "4. Figure 1F and the label-free full-matrix correlation heatmap",
        "status": "Complete; final figure placement needs approval",
        "owner": "Juliane to approve Figure 1F plan",
        "quote": "The heatmap in Figure 1F is misleading... probes were selected using the diagnostic labels... If the heatmap was meant to further support the unsupervised clustering... it should be replaced or supplemented by the unsupervised sample-to-sample correlation heatmap.",
        "asking": [
            "The reviewer says the original top-CpG heatmap is supervised because CpGs were chosen using disease labels.",
            "They want a label-free heatmap from the full post-QC M-value matrix if the figure is used as unsupervised evidence.",
        ],
        "decision": [
            "Use a label-free full-matrix sample correlation heatmap as the unsupervised heatmap.",
            "Move the old top-CpG heatmap to supplementary material or describe it only as supervised descriptive visualization.",
        ],
        "did": [
            "Calculated Pearson sample-to-sample correlations using all post-QC M-values.",
            "Clustered samples with 1 minus correlation and complete linkage.",
            "Added disease and confounder annotations only after clustering.",
        ],
        "figures": main_fig("Figure_sample_correlation_heatmap.png", "Label-free full-matrix Pearson sample-correlation heatmap.")
        + main_fig("Figure_sample_correlation_annotation_legend.png", "Annotation color legend for Figure 1F heatmap."),
        "supplementary": "",
        "interpretation": [
            "This directly answers the reviewer because ordering is not label-informed.",
            "The former heatmap should not be presented as independent evidence of natural clustering.",
            "The heatmap needs an explicit annotation-color legend; a separate legend panel has now been generated for insertion into the figure, rebuttal or supplement.",
        ],
        "draft": "We agree that the previous top-CpG heatmap was label-informed and therefore should not be presented as independent unsupervised evidence. We replaced/supplemented this panel with a sample-to-sample Pearson correlation heatmap calculated from the complete post-QC M-value matrix. Samples were ordered by hierarchical clustering using 1 minus Pearson correlation and complete linkage; diagnostic and metadata annotations were added only after clustering. The previous top-CpG heatmap is now described only as supervised descriptive visualization.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 12, paragraph 76; Figure 1 legend",
                "find": "(F) Label-free sample-to-sample Pearson-correlation heatmap calculated from the complete post-QC M-value matrix...",
                "action": "Keep the label-free heatmap text but add explicit color-legend explanation.",
                "replacement": "(F) Label-free sample-to-sample Pearson-correlation heatmap calculated from the complete post-QC M-value matrix and hierarchically clustered using 1 minus Pearson correlation and complete linkage. Disease group and potential confounders were added only as annotations and did not determine sample ordering. Annotation colors are defined in the adjacent legend panel / Supplementary Figure X.",
            },
            {
                "location": "Figure preparation action, before resubmission",
                "find": "Current Figure_sample_correlation_heatmap has correlation scale but no readable annotation-color legend.",
                "action": "Use the newly generated legend panel with the heatmap.",
                "replacement": "Combine Figure_sample_correlation_heatmap with Figure_sample_correlation_annotation_legend, or place the legend panel as a supplementary figure referenced from the Figure 1 legend.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 Figure 1F / heatmap response, immediately after explaining the previous heatmap was label-informed.",
                "figure": "Figure_sample_correlation_heatmap.pdf",
                "reason": "This is the direct replacement/supplement requested by the reviewer.",
                "caption": "Label-free sample-to-sample Pearson correlation heatmap from the full post-QC M-value matrix; clustering used 1 minus Pearson correlation and complete linkage.",
            },
            {
                "where": "Immediately below the heatmap in rebuttal, or as a supplementary legend panel.",
                "figure": "Figure_sample_correlation_annotation_legend.pdf",
                "reason": "Juliane noted that the heatmap lacked legends for the annotation colors.",
                "caption": "Annotation color legend for disease group, source, Sentrix ID, age group, sex, biopsy-site group, city of origin and lymphomonocyte category.",
            },
        ],
        "manuscript": [
            "Figure 1F: use label-free correlation heatmap.",
            "Move label-informed heatmap to supplement or relabel as supervised descriptive.",
            "Add annotation color legend for Disease, Source, Sentrix, Age, Sex, Site, City and Lymphomonocytes.",
        ],
    },
    {
        "id": "pca_scrutiny",
        "reviewer": "Reviewer 1",
        "title": "5. PCA scrutiny: scree, PC pairs, scaled vs unscaled PCA, and loadings",
        "status": "Complete",
        "owner": "Joseph drafted; Juliane to approve wording",
        "quote": "Please provide a scree plot... show multiple pairwise projections... quantify the association of each of the leading PCs... provide an analysis using centered but unscaled M-values... examine the CpGs with the largest positive and negative loadings...",
        "asking": [
            "The reviewer wants PCA treated as an analysis, not only a two-dimensional picture.",
            "They specifically challenge scale.=TRUE because scaling gives low-variance probes equal weight.",
        ],
        "decision": [
            "Keep scaled PCA as the submitted baseline, but add unscaled PCA as sensitivity.",
            "Explain that scaled and unscaled answer related but not identical questions.",
        ],
        "did": [
            "Added PC1-PC20 variance and cumulative variance.",
            "Generated PC1-PC2, PC1-PC3 and PC2-PC3 projections.",
            "Generated scaled and unscaled PCA.",
            "Quantified PC-metadata eta-squared associations.",
            "Annotated top positive and negative loadings for leading PCs.",
        ],
        "figures": main_fig("Figure_PCA_scree.png", "PCA scree and cumulative variance.")
        + main_fig("Figure_PC_metadata_associations.png", "PC-metadata association heatmap."),
        "supplementary": supplementary_figures([
            "PCA_cumulative_variance.pdf",
            "PCA_scaled_PC1_PC2.pdf",
            "PCA_scaled_PC1_PC3.pdf",
            "PCA_scaled_PC2_PC3.pdf",
            "PCA_unscaled_PC1_PC2.pdf",
            "PCA_unscaled_PC1_PC3.pdf",
            "PCA_unscaled_PC2_PC3.pdf",
            "pca_unscaled_by_display_group.pdf",
            "pca_unscaled_by_dataset_source.pdf",
            "pca_unscaled_by_sentrix_id.pdf",
            "pca_unscaled_by_age_group.pdf",
            "pca_unscaled_by_gender.pdf",
            "pca_unscaled_by_muscle_location_group.pdf",
            "pca_unscaled_by_city_of_origin.pdf",
            "pca_unscaled_by_lymphomonocytes.pdf",
        ]),
        "interpretation": [
            "Scaled and unscaled PCA both show structure, so the observation is not solely a scaling artifact.",
            "However, leading PCs also align with source/Sentrix and other cohort variables, so disease-only interpretation is not justified.",
        ],
        "draft": "We expanded the PCA evaluation substantially. We now provide scree and cumulative-variance plots for the leading PCs, multiple pairwise projections, centered-scaled and centered-unscaled analyses, quantitative associations between leading PCs and available metadata variables, and annotation of the strongest positive and negative loadings. The unscaled analysis supports the presence of structure beyond the original scaling choice, but the leading components remain associated with technical and cohort variables as well as disease group.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 9, paragraph 63; Methods, array data analysis",
                "find": "Scaled PCA used prcomp with centering and unit-variance scaling; a centered, unscaled PCA was added as a sensitivity analysis.",
                "action": "Keep this Methods sentence and add explicit rationale so the scaling choice is transparent.",
                "replacement": "Scaled PCA used prcomp with centering and unit-variance scaling as the primary visualization so that CpGs with different absolute variance ranges contributed comparably. Because this choice can give low-variance probes increased relative weight, we also performed centered, unscaled PCA as a sensitivity analysis.",
            },
            {
                "location": "Current clean draft: page 12, paragraph 75; Results, unsupervised methylation structure",
                "find": "Leading PCs were associated not only with disease group but also with dataset source, Sentrix ID and other supplied metadata.",
                "action": "Add the PCA scrutiny results after this sentence.",
                "replacement": "We therefore added scree and cumulative-variance plots for the first 20 PCs, PC1-PC2, PC1-PC3 and PC2-PC3 projections, scaled and unscaled PCA, quantitative PC-metadata association testing, and annotation of the strongest positive and negative CpG loadings. These analyses support robust methylation structure but do not support interpretation of the leading PCs as disease-only axes.",
            },
            {
                "location": "Supplementary figure/table legends",
                "find": "No consolidated legend currently describes the expanded PCA scrutiny outputs.",
                "action": "Add supplementary references for PCA scree, pairwise projections, unscaled PCA, PC-metadata associations and top-loadings table.",
                "replacement": "Supplementary Figure X/Table X. Expanded PCA scrutiny. Scree and cumulative-variance plots, PC1-PC2/PC1-PC3/PC2-PC3 projections, centered-scaled and centered-unscaled PCA, PC-metadata eta-squared associations and top CpG loadings were used to evaluate whether leading components reflected disease group, technical variables or cohort structure.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 PCA scrutiny response, after describing the added scree/pairwise PC analyses.",
                "figure": "Figure_PCA_scree.pdf",
                "reason": "Directly answers the request for variance explained and cumulative variance.",
                "caption": "Variance explained and cumulative variance for the first 20 PCs in scaled and centered-unscaled PCA.",
            },
            {
                "where": "Same PCA rebuttal subsection, after the scree figure or in the supplement.",
                "figure": "Figure_PC_metadata_associations.pdf",
                "reason": "Directly answers the request to quantify PC associations with diagnosis and confounders.",
                "caption": "Eta-squared association of leading PCs with disease group and available metadata variables.",
            },
        ],
        "manuscript": [
            "Methods: explain scaled PCA and unscaled sensitivity.",
            "Results: avoid reading PC1/PC2 as disease-only axes.",
        ],
    },
    {
        "id": "subset_influence",
        "reviewer": "Reviewer 1",
        "title": "6. Subset and influential-sample analyses",
        "status": "Complete",
        "owner": "Joseph drafted; Juliane to approve wording",
        "quote": "Re-run the t-SNE and PCA in subsets... excluding MMC; excluding controls; in-house data only; IBM versus non-IBM IIM; ALS versus non-ALS NMA... assess whether the observed structure is sensitive to individual influential samples.",
        "asking": [
            "The reviewer wants embeddings recomputed within each subset, not just points removed from the full-cohort map.",
            "They especially want clinically relevant contrasts tested for robustness.",
        ],
        "decision": [
            "Run all requested subsets.",
            "Treat ALS versus non-ALS NMA as exploratory because it is unstable and small.",
        ],
        "did": [
            "Recomputed PCA and t-SNE independently for all five requested subsets.",
            "Performed leave-one-sample influence analysis for clinically focused contrasts.",
        ],
        "figures": "",
        "supplementary": supplementary_figures([
            "subset_excluding_MMC_PCA.pdf",
            "subset_excluding_MMC_tSNE.pdf",
            "subset_excluding_controls_PCA.pdf",
            "subset_excluding_controls_tSNE.pdf",
            "subset_in_house_data_PCA.pdf",
            "subset_in_house_data_tSNE.pdf",
            "subset_IBM_vs_nonIBM_IIM_PCA.pdf",
            "subset_IBM_vs_nonIBM_IIM_tSNE.pdf",
            "subset_ALS_vs_nonALS_NMA_PCA.pdf",
            "subset_ALS_vs_nonALS_NMA_tSNE.pdf",
            "influential_sample_analysis.pdf",
        ]),
        "interpretation": [
            "The full-cohort pattern is stronger than some clinically focused subsets.",
            "ALS versus non-ALS NMA is the weakest comparison and should be framed as hypothesis-generating only.",
        ],
        "draft": "We recomputed PCA and t-SNE independently for all requested subsets rather than removing samples from the full-cohort embedding. The in-house-data and disease-pair analyses show weaker structure than the full mixed-source cohort. ALS versus non-ALS neurogenic atrophy was the least stable comparison and was sensitive to individual samples; we therefore revised the manuscript to describe this contrast as exploratory.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 9, paragraph 63; Methods, array data analysis",
                "find": "PCA and t-SNE were recomputed independently after excluding MMC, excluding controls, restricting to the in-house data, comparing IBM with non-IBM IIM, NOS, and comparing ALS with non-ALS NMA.",
                "action": "Keep this Methods sentence; it is essential because the reviewer asked that subsets be recomputed, not only subsetted from the full embedding.",
                "replacement": "PCA and t-SNE were recomputed independently after excluding MMC, excluding controls, restricting to the in-house data, comparing IBM with non-IBM IIM, NOS, and comparing ALS with non-ALS NMA; these were new embeddings calculated within each subset, not visual subsets of the full-cohort embedding.",
            },
            {
                "location": "Current clean draft: Results, after the main unsupervised PCA/t-SNE paragraph",
                "find": "No explicit subset-analysis result paragraph may be present yet.",
                "action": "Add a short Results paragraph summarizing the subset and influential-sample analyses.",
                "replacement": "Subset analyses showed that the full-cohort structure was stronger than several clinically focused subset analyses. The in-house-data, IBM versus non-IBM IIM, NOS, and ALS versus non-ALS NMA embeddings were less separated than the full mixed-source cohort, and the ALS versus non-ALS NMA comparison showed the greatest sensitivity to individual samples. These results support cautious, exploratory interpretation of disease-pair contrasts.",
            },
            {
                "location": "Discussion section discussing ALS/NMA and cohort limitations",
                "find": "Any sentence implying robust ALS versus non-ALS NMA separation.",
                "action": "Delete or soften strong ALS/NMA separation claims.",
                "replacement": "The ALS versus non-ALS NMA comparison should be described as exploratory because of small ALS sample size, overlap in unsupervised analyses and sensitivity to individual samples.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 subset/influence response.",
                "figure": "Supplementary subset figures: subset_excluding_MMC_*.pdf, subset_excluding_controls_*.pdf, subset_in_house_data_*.pdf, subset_IBM_vs_nonIBM_IIM_*.pdf, subset_ALS_vs_nonALS_NMA_*.pdf",
                "reason": "Directly answers the request for recomputed PCA/t-SNE in each subset.",
                "caption": "PCA and t-SNE recomputed independently within each requested subset.",
            },
            {
                "where": "Same subset/influence response, after the subset panels.",
                "figure": "influential_sample_analysis.pdf",
                "reason": "Directly answers the request to assess sensitivity to individual influential samples.",
                "caption": "Influence of individual samples on disease-group silhouette in clinically focused contrasts.",
            },
        ],
        "manuscript": [
            "Add supplementary subset figure references.",
            "Soften ALS-NMA claims in Results and Discussion.",
        ],
    },
    {
        "id": "downstream_validation",
        "reviewer": "Reviewer 1",
        "title": "7. Downstream differential methylation and classifier confounder validation",
        "status": "Complete within estimability limits",
        "owner": "Juliane to approve limitation wording",
        "quote": "If the apparent unsupervised separation is instead substantially driven by confounders, these same variables would also be expected to influence the subsequent supervised and differential analyses... differential methylation and supervised-learning analyses will still require their own confounder validation.",
        "asking": [
            "The reviewer wants us to stop using unsupervised structure as a foundation for all later disease-specific claims.",
            "They want downstream analyses checked for confounding too.",
        ],
        "decision": [
            "Run covariate sensitivity where statistically estimable.",
            "Explicitly state source/Sentrix cannot be separated from disease group when rank deficient.",
            "Treat supervised learning as internal exploratory classification, not clinical validation.",
        ],
        "did": [
            "Ran age/sex and biopsy-site limma sensitivity models where estimable.",
            "Audited source/Sentrix rank deficiency.",
            "Ran metadata-only classification checks.",
            "Rebuilt supervised learning using patient-aware splitting and training-only feature selection.",
        ],
        "figures": main_fig("Figure_differential_sensitivity.png", "Differential methylation covariate sensitivity.")
        + main_fig("Figure_metadata_only_classifier.png", "Metadata-only classifier as a confounding diagnostic.")
        + main_fig("Figure_patient_aware_ML.png", "Patient-aware exploratory supervised classification."),
        "supplementary": "",
        "interpretation": [
            "Some covariate models are estimable; source/Sentrix are too aligned with disease group for full separation.",
            "Metadata-only predictive performance confirms that classifier results cannot be read as disease-intrinsic or clinically diagnostic.",
        ],
        "draft": "We performed additional downstream sensitivity analyses. Age/sex and biopsy-site adjusted differential methylation models were estimable for selected contrasts, whereas source and Sentrix models were rank deficient because these variables were structurally aligned with disease group. We also evaluated metadata-only classification and rebuilt supervised learning with patient-aware splitting and training-only feature selection. These results support a cautious interpretation: the supervised and differential analyses are exploratory and cannot establish disease-intrinsic methylation signatures or clinical diagnostic performance in this cohort.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 9, paragraph 63; Methods, array data analysis",
                "find": "Differential methylation used limma with Benjamini-Hochberg FDR correction. Age/sex and biopsy-site sensitivity models were fitted when estimable; source and Sentrix models were retained as design audits when rank deficiency prevented separation from disease group.",
                "action": "Keep this Methods text and verify that it is not hidden only in the rebuttal.",
                "replacement": "Differential methylation used limma with Benjamini-Hochberg FDR correction. Age/sex and biopsy-site sensitivity models were fitted when estimable. Source and Sentrix were evaluated as design audits because full adjustment models containing disease group plus source or Sentrix were rank deficient, reflecting structural alignment in this cohort.",
            },
            {
                "location": "Current clean draft: supervised learning Methods/Results and Discussion",
                "find": "Any statement implying classifier performance alone validates disease-intrinsic methylation signatures.",
                "action": "Delete or replace with explicit confounding caveat.",
                "replacement": "Metadata-only classification was used as a confounding diagnostic, not as a biological classifier. Because source, Sentrix and demographic variables predicted disease group above chance, methylation-classifier performance cannot be interpreted as clinical validation or disease-intrinsic signal in this cohort.",
            },
            {
                "location": "Discussion limitations",
                "find": "No explicit downstream confounder-validation limitation may be present yet.",
                "action": "Add limitation wording.",
                "replacement": "Although downstream differential methylation and supervised classification analyses were rebuilt with leakage control and sensitivity checks, residual confounding remains possible because several technical and cohort variables were structurally aligned with disease group and could not be fully adjusted in this sample size.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 1 downstream validation response.",
                "figure": "Figure_differential_sensitivity.pdf",
                "reason": "Shows how differential methylation results change under estimable covariate adjustments.",
                "caption": "Differential methylation sensitivity to age/sex and biopsy-site adjustment where models were estimable.",
            },
            {
                "where": "Same downstream validation response.",
                "figure": "Figure_metadata_only_classifier.pdf",
                "reason": "Shows why classifier performance cannot be interpreted as disease-intrinsic without caution.",
                "caption": "Metadata-only classification demonstrates disease-group information contained in source, Sentrix and cohort variables.",
            },
            {
                "where": "Same downstream validation response or supervised-learning response.",
                "figure": "Figure_patient_aware_ML.pdf",
                "reason": "Documents the leakage-fixed, patient-aware supervised learning result.",
                "caption": "Patient-aware exploratory classification after training-only feature selection.",
            },
        ],
        "manuscript": [
            "Methods/Results: state which covariates were estimable.",
            "Discussion: state source/Sentrix confounding cannot be fully removed in this cohort.",
        ],
    },
    {
        "id": "supervised_wording",
        "reviewer": "Reviewer 2",
        "title": "8. Supervised learning wording: disease group, not diagnosis",
        "status": "Mostly covered; final proofreading still needed",
        "owner": "Juliane and Joseph",
        "quote": "Instead of diagnosis, the correct term should be disease group... That's an overstatement again, since non-ALS is not a diagnosis, and neither is non-IBM, NOS...",
        "asking": [
            "Reviewer 2 is objecting to diagnostic overstatement and imprecise disease terminology.",
            "This is not only a wording issue; it changes the claim from clinical diagnosis to internal group classification.",
        ],
        "decision": [
            "Use disease group / studied groups / exploratory classification.",
            "Avoid correct diagnosis, diagnostic classifier, disease-specific entity, and beyond disease group wording.",
        ],
        "did": [
            "Changed supervised learning section heading and figure legend in the draft.",
            "Added metadata-only classifier warning.",
            "Used patient-aware split for the paired samples.",
        ],
        "figures": main_fig("Figure_patient_aware_ML.png", "Patient-aware exploratory classification of studied disease groups.")
        + main_fig("Figure_metadata_only_classifier.png", "Metadata-only prediction shows confounding risk."),
        "supplementary": "",
        "interpretation": [
            "The analysis can describe internal classification among selected study groups.",
            "It must not claim clinical diagnostic performance or broad differential diagnosis coverage.",
        ],
        "draft": "We agree and have revised the terminology throughout. The supervised learning analysis is now described as exploratory classification among the studied disease groups, not prediction of a correct clinical diagnosis. We also emphasize that non-ALS neurogenic atrophy and non-IBM IIM, NOS are study groups rather than complete diagnostic entities and that the present cohort does not include the full clinical differential diagnosis.",
        "exact_edits": [
            {
                "location": "Submitted manuscript: reviewer-stated page 25; current clean draft: page 12, paragraph 109; supervised learning Results heading",
                "find": "Supervised learning can predict diagnosis in most cases based on methylation data",
                "action": "Replace heading; delete diagnosis language.",
                "replacement": "Exploratory supervised classification of the studied disease groups",
            },
            {
                "location": "Submitted manuscript: reviewer-stated page 25; current clean draft: page 12, paragraph 109",
                "find": "Next, we wanted to find out whether supervised learning can predict a correct diagnosis.",
                "action": "Replace sentence; avoid diagnosis/clinical performance wording.",
                "replacement": "We evaluated whether methylation data could classify samples among the six studied groups while keeping samples from the same patient in one partition.",
            },
            {
                "location": "Abstract and Discussion",
                "find": "predicted diagnosis / correct diagnosis / beyond disease group / disease-specific classifier",
                "action": "Delete these phrases or replace with disease-group classification wording.",
                "replacement": "Use: classified the studied disease groups within this selected cohort. Add: This does not establish a clinically validated diagnostic classifier and does not cover the full clinical differential diagnosis.",
            },
            {
                "location": "Current clean draft: page 12, paragraph 110; Figure 6 legend",
                "find": "Supervised learning algorithms",
                "action": "Replace or expand the figure legend to state the exploratory scope.",
                "replacement": "Figure 6. Patient-aware exploratory classification of the studied disease groups. Results describe internal classification of this selected pilot cohort and are not an externally validated clinical diagnostic test.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 2 supervised-learning wording response, only if figures are included inline in the rebuttal.",
                "figure": "Figure_patient_aware_ML.pdf",
                "reason": "Shows the corrected patient-aware exploratory classification, but should be framed as disease-group classification only.",
                "caption": "Patient-aware exploratory classification among the studied disease groups.",
            },
            {
                "where": "Same response or Reviewer 1 downstream response.",
                "figure": "Figure_metadata_only_classifier.pdf",
                "reason": "Supports the caution that classification is not clinical diagnostic validation.",
                "caption": "Metadata-only classification indicates confounding risk in interpreting classifier performance.",
            },
        ],
        "manuscript": [
            "Search entire manuscript for diagnosis, diagnostic, disease-specific, entity-specific.",
            "Final proofreading after Juliane fills clinical placeholders.",
        ],
    },
    {
        "id": "inclusion_exclusion",
        "reviewer": "Reviewer 2",
        "title": "9. Inclusion/exclusion criteria and archive selection",
        "status": "Needs Juliane clinical/pathology input",
        "owner": "Juliane / clinical pathology team",
        "quote": "The inclusion and exclusion criteria are still not sufficiently detailed... how were these specific cases selected among all others? Were all candidate cases within the 8-year period reviewed? Were slides reviewed before inclusion... Was clinical information also evaluated...",
        "asking": [
            "Reviewer 2 wants a factual audit trail for case selection.",
            "This cannot be answered from methylation data or code.",
        ],
        "decision": [
            "Do not invent archive totals or workflow.",
            "Ask Juliane for exact candidate counts, exclusion counts/reasons, slide review, clinical review, and adjudication wording.",
        ],
        "did": [
            "Flagged the Human samples section with a yellow decision-needed note.",
            "Kept all 73 samples and did not rename/remove disease groups.",
        ],
        "figures": "",
        "supplementary": "",
        "interpretation": [
            "This is currently the largest non-bioinformatic blocker before journal resubmission.",
            "Juliane's response should become both manuscript Methods text and rebuttal text.",
        ],
        "draft": "We have expanded the Methods section to describe the case-selection procedure in more detail. [JULIANE TO INSERT: total archive candidates by group, whether all candidates in the eight-year interval were reviewed, whether slides and clinical information were re-reviewed, who adjudicated inclusion, and the exclusion counts/reasons.] We agree that these details are necessary for transparency and have added them to the revised manuscript.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 12, paragraph 74; Human samples / cohort selection paragraph",
                "find": "We selected 41 fresh-frozen muscle biopsies from our diagnostic archives with well-defined neuropathological diagnosis...",
                "action": "Add a factual archive-selection paragraph immediately after this sentence. Do not invent missing clinical/pathology details.",
                "replacement": "[JULIANE TO INSERT EXACT FACTS] During the eight-year archive interval, [N] candidate cases of non-IBM IIM, NOS and [N] candidate cases of non-ALS neurogenic atrophy were identified. Candidate cases were selected for methylation analysis based on [selection criteria]. [All / selected] candidate cases were reviewed. Inclusion was based on [histology only / histology plus clinical information / original report plus re-review]. Slides were reviewed by [names/roles], and disagreements or borderline cases were adjudicated by [process]. Exclusion criteria were [list], resulting in exclusion of [N] cases for [reasons].",
            },
            {
                "location": "Methods, Human samples section",
                "find": "Any vague statement implying cases were simply selected from the archive without explaining how.",
                "action": "Delete vague selection wording or replace it with the factual audit trail above.",
                "replacement": "Replace vague case-selection language with explicit candidate totals, selection process, slide-review process, clinical-information review, pathologist/adjudication process and exclusion reasons.",
            },
            {
                "location": "Point-by-point rebuttal response to Reviewer 2 inclusion/exclusion comment",
                "find": "[JULIANE TO INSERT...] placeholder",
                "action": "Replace placeholder before sending to journal.",
                "replacement": "We expanded the Methods to specify the archive-search interval, number of candidate cases, selection workflow, slide and clinical-information review, adjudication process and exclusion criteria. [Insert exact numbers and process from Juliane.]",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 2 inclusion/exclusion response, optional if Juliane wants a compact visual audit trail.",
                "figure": "No current figure; recommended addition is a simple case-flow diagram/table after Juliane supplies candidate/exclusion counts.",
                "reason": "Reviewer asks for case-selection transparency; a flow diagram would answer more clearly than prose if counts are available.",
                "caption": "Case-selection flow from archive candidates to included methylation cohort, with exclusion reasons.",
            },
        ],
        "manuscript": [
            "Add factual archive selection paragraph from Juliane.",
            "Replace remaining xxx placeholders.",
        ],
        "needs_structured": True,
    },
    {
        "id": "cell_composition",
        "reviewer": "Reviewer 2",
        "title": "10. Deconvolution and cell-composition limitation",
        "status": "Covered by limitation route unless Juliane supplies validated covariates",
        "owner": "Juliane to confirm availability",
        "quote": "The authors either need to perform deconvolution analyses... or explicitly discuss that the absence of such analyses is a major limitation of the current study.",
        "asking": [
            "Reviewer 2 accepts that longitudinal analysis is out of scope, but still wants cell composition addressed.",
            "The acceptable alternatives are: perform valid deconvolution/covariate modeling, or explicitly state absence as a major limitation.",
        ],
        "decision": [
            "Do not model undefined lymphomonocyte low/medium/high as deconvolution.",
            "Use major-limitation wording unless Juliane can provide validated cell-composition or pathology covariates.",
        ],
        "did": [
            "Described lymphomonocytes only as supplied metadata.",
            "Added manuscript wording that sample-level deconvolution estimates suitable for adjustment were unavailable.",
        ],
        "figures": "",
        "supplementary": "",
        "interpretation": [
            "This point should be answered transparently; overstating the lymphomonocyte variable would be risky.",
            "If Juliane has validated scores, we would need to rerun relevant models.",
        ],
        "draft": "We agree that cell composition is a major concern for bulk skeletal-muscle methylation. Validated sample-level deconvolution estimates or histopathology scores suitable for covariate adjustment were not available for the current analysis. We therefore did not add unsupported deconvolution modeling and instead revised the Discussion to state explicitly that the absence of cell-composition-adjusted analyses is a major limitation.",
        "exact_edits": [
            {
                "location": "Current clean draft: page 12, paragraph 113; Discussion limitations",
                "find": "Sample-level deconvolution estimates suitable for covariate adjustment were not available...",
                "action": "Keep and strengthen the limitation wording to match Reviewer 2's request.",
                "replacement": "Validated sample-level deconvolution estimates or histopathology scores suitable for covariate adjustment were not available for incorporation into the present differential methylation models. The absence of cell-composition-adjusted analyses is therefore a major limitation of this study.",
            },
            {
                "location": "Methods/Results wherever lymphomonocytes are mentioned",
                "find": "Any wording implying lymphomonocyte low/medium/high is a validated deconvolution estimate.",
                "action": "Delete or soften; do not overinterpret lymphomonocyte categories.",
                "replacement": "The supplied lymphomonocyte category was displayed only as a descriptive annotation because its scoring definition was unavailable to the analyst; it was not used as a validated deconvolution covariate.",
            },
            {
                "location": "If Juliane supplies validated cell-composition or pathology covariates before resubmission",
                "find": "Current limitation-only route.",
                "action": "Change route: rerun relevant differential methylation models and replace limitation-only wording with adjusted-analysis wording.",
                "replacement": "If validated covariates become available, rerun differential methylation models incorporating these covariates where estimable and report both adjusted results and remaining limitations.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 2 cell-composition response.",
                "figure": "No figure should be inserted unless validated deconvolution/pathology covariates are supplied and analyzed.",
                "reason": "A figure based on undefined lymphomonocyte low/medium/high categories would be misleading.",
                "caption": "If validated covariates become available: covariate-adjusted differential methylation sensitivity by cell-composition/pathology score.",
            },
        ],
        "manuscript": [
            "Discussion: major limitation wording.",
            "Methods/Results: only mention lymphomonocytes if Juliane defines the categories.",
        ],
        "needs_structured": True,
    },
    {
        "id": "als_nma",
        "reviewer": "Reviewer 2",
        "title": "11. ALS versus non-ALS NMA: soften interpretation",
        "status": "Complete; final wording needs approval",
        "owner": "Juliane to approve clinical tone",
        "quote": "The ALS/non-ALS comparison has been retained. While that is acceptable, the language... should be further softened to avoid overinterpretation, given the small number of ALS cases.",
        "asking": [
            "Reviewer 2 allows the comparison to remain, but wants the interpretation downgraded.",
            "This is reinforced by Reviewer 1's subset and confounder concerns.",
        ],
        "decision": [
            "Keep ALS-NMA as exploratory only.",
            "Mention small ALS sample size, overlap, individual-sample influence, and biopsy-site sensitivity.",
        ],
        "did": [
            "Recomputed ALS vs non-ALS NMA subset PCA/t-SNE.",
            "Ran influence analysis.",
            "Ran differential sensitivity; biopsy-site adjustment removed FDR-significant CpGs for ALS-NMA.",
        ],
        "figures": main_fig("Figure_differential_sensitivity.png", "ALS-NMA differential sensitivity is included in the covariate sensitivity summary."),
        "supplementary": "",
        "interpretation": [
            "ALS-NMA is the least stable clinically relevant comparison.",
            "Any biological interpretation should be framed as preliminary.",
        ],
        "draft": "We have further softened the ALS versus non-ALS neurogenic atrophy interpretation. This comparison is now described as exploratory and hypothesis-generating because of the small ALS sample size, overlap in unsupervised analyses, sensitivity to individual samples and loss of FDR-significant CpGs after biopsy-site adjustment.",
        "exact_edits": [
            {
                "location": "Results sections discussing ALS versus non-ALS NMA",
                "find": "Any wording implying robust ALS-specific methylation separation or validated ALS methylation signature.",
                "action": "Delete strong wording and replace with exploratory wording.",
                "replacement": "The ALS versus non-ALS NMA comparison is retained as exploratory and hypothesis-generating. Interpretation is limited by the small ALS sample size, overlap with non-ALS NMA in unsupervised analyses, sensitivity to individual samples and loss of FDR-significant CpGs after biopsy-site adjustment.",
            },
            {
                "location": "Current clean draft: page 12, paragraph 112 or nearby Discussion paragraph",
                "find": "Although not all cases of ALS could be distinguished unequivocally...",
                "action": "Replace with cautious summary.",
                "replacement": "ALS and non-ALS NMA showed partial overlap, and the ALS versus non-ALS NMA contrast was the least stable disease-pair comparison. We therefore interpret ALS/NMA-associated findings as preliminary observations that require validation in larger, balanced cohorts.",
            },
            {
                "location": "Figure/table legends for ALS/NMA differential results",
                "find": "Any legend suggesting definitive ALS-specific biology.",
                "action": "Add limitation phrase.",
                "replacement": "ALS versus non-ALS NMA results are exploratory because of small group size and sensitivity to biopsy-site adjustment.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 2 ALS/NMA softening response.",
                "figure": "Figure_differential_sensitivity.pdf",
                "reason": "Shows that ALS/NMA significance is sensitive to biopsy-site adjustment.",
                "caption": "Differential methylation sensitivity analysis showing reduced support for ALS versus non-ALS NMA after biopsy-site adjustment.",
            },
            {
                "where": "Same response or supplementary material.",
                "figure": "subset_ALS_vs_nonALS_NMA_PCA.pdf, subset_ALS_vs_nonALS_NMA_tSNE.pdf, influential_sample_analysis.pdf",
                "reason": "Supports the cautious wording by showing overlap and individual-sample sensitivity.",
                "caption": "ALS versus non-ALS NMA subset embeddings and individual-sample influence analysis.",
            },
        ],
        "manuscript": [
            "Results and Discussion: avoid strong ALS-specific methylation signature wording.",
        ],
    },
    {
        "id": "proofreading",
        "reviewer": "Reviewer 2",
        "title": "12. Proofreading, placeholders, supplement numbering and author decisions",
        "status": "Partly covered; final author-level proofreading required",
        "owner": "Juliane / all authors",
        "quote": "The revised manuscript appears to have been written in haste... supplementary table xy... The entire manuscript should be carefully proofread before resubmission.",
        "asking": [
            "Reviewer 2 wants the manuscript cleaned thoroughly, not only statistically revised.",
            "Some remaining items require author decisions rather than analysis.",
        ],
        "decision": [
            "Correct detectable terminology and supplement placeholders.",
            "Do not guess clinical placeholders or authorship details.",
        ],
        "did": [
            "Corrected Supplementary Tables 2 and 3 placeholder where detected.",
            "Changed PM display terminology to non-IBM IIM, NOS.",
            "Added yellow decision-needed notes for unresolved clinical/authorship items.",
        ],
        "figures": "",
        "supplementary": "",
        "interpretation": [
            "The manuscript draft is not journal-ready until Juliane supplies clinical text and author decisions.",
            "A final proofreading pass should happen after those insertions.",
        ],
        "draft": "We carefully revised the manuscript language to remove diagnostic and disease-specific overstatements, corrected the supplementary table reference, and edited the supervised-learning terminology. The manuscript has also been reviewed for remaining author-level placeholders; these will be resolved before resubmission.",
        "exact_edits": [
            {
                "location": "Submitted manuscript: reviewer-stated page 25; supervised learning section",
                "find": "diagnosis / correct diagnosis / predicted diagnosis",
                "action": "Replace throughout supervised-learning text.",
                "replacement": "Use disease group, studied disease groups, or exploratory classification among the studied groups. Do not use diagnosis unless referring to the original clinical/histopathological diagnosis used for case definition.",
            },
            {
                "location": "Submitted manuscript: reviewer-stated page 28; supplement reference",
                "find": "supplementary table xy",
                "action": "Replace placeholder.",
                "replacement": "supplementary tables 2 and 3",
            },
            {
                "location": "Entire manuscript and rebuttal",
                "find": "disease-specific / entity-specific / clinical diagnostic classifier / beyond disease group / correct diagnosis",
                "action": "Delete or replace overstatements.",
                "replacement": "Use disease-group-associated, exploratory, pilot cohort, internal classification, and requires validation in larger balanced cohorts.",
            },
            {
                "location": "Title page and author list",
                "find": "Tayfun Palaz placeholder / co-last or equal-contribution wording / unresolved author order",
                "action": "Resolve before journal submission.",
                "replacement": "[AUTHORS TO CONFIRM] Final author list, author order, Tayfun Palaz status, and co-last/equal-contribution wording.",
            },
        ],
        "rebuttal_figures": [
            {
                "where": "Reviewer 2 proofreading response.",
                "figure": "No figure required.",
                "reason": "This is a manuscript-cleanup and terminology issue.",
                "caption": "Not applicable.",
            },
        ],
        "manuscript": [
            "Confirm author list/order and Tayfun Palaz placeholder.",
            "Confirm co-last-author wording.",
            "Final supplement numbering and proofreading.",
        ],
        "needs_structured": True,
    },
]


FULL_REVIEWER_COMMENTS = {
    "overall_confounding": """This study addresses an important question, whether DNA methylation profiling can reveal reproducible epigenetic profiles across non-neoplastic skeletal muscle diseases. The application of genome-wide methylation analysis to inflammatory, neurogenic, and inherited muscle disorders is relatively novel and could provide useful insights into disease biology and future diagnostic approaches. The assembled cohort and accompanying computational analyses therefore represent a potentially valuable contribution.

I thank the authors for the clarification that the unsupervised clustering (t-SNE in Figure 1E and PCA in Supplementary Figure 1) was initiated from the full dataset of 771,381 probes without prior diagnosis-based feature selection.

However, this clarification raises concerns regarding the overall methodology, results, and interpretation. The cluster separation observed in the t-SNE and PCA plots is unexpectedly strong given the number of cases and heterogeneous nature of cohort under study. It is essential to establish that this structure is robustly associated with the disease groups rather than technical, demographic, or tissue composition variables before the subsequent supervised analyses and biological interpretations can be evaluated.

My concerns about the unsupervised analysis are substantiated by the following points:

DNA methylation classification systems have generally been developed in settings where a strong and relatively stable methylation signal is expected. This includes neoplasms, where the methylome reflects cell of origin together with clonal somatic and epigenetic alterations, and Mendelian disorders, where a germline mutation may produce a reproducible epigenetic signature. Even in these settings, published classifiers rely on large reference cohorts on the order of hundreds or thousands of cases. By contrast, the authors explore a more challenging and complex cohort of predominantly acquired, non-neoplastic muscle disease groups, expected to have a much weaker and more heterogeneous epigenetic signature. The authors analyze only 73 cases, including controls, from a small number of diagnostic groups, with as few as six cases per group. In this context, the apparently near-complete cluster separation is unexpected and requires careful demonstration that it is stable and not attributable to the structural distribution of potential confounders.

The cohort is not balanced or adjusted for many variables that likely have an epigenetic effect in muscle: age, sex (despite removing sex chromosome probes, there are epigenetic sex differences on other chromosomes), biopsy site (individual muscles have different cellular compositions and physiology), comorbidities, disease duration, metabolic/exercise level, diet, and tissue handling. For example, Supplementary table 1 indicates that all controls are soleus biopsies from male adults, whereas all MMCs (a genetic disease) are quadriceps biopsies from young individuals. These confounding variables could contribute both within-group heterogeneity and between-group separation.

Supplementary Table 1 also suggests that batch effects may be a major confounder. In addition to the external datasets, in-house NMA samples are mostly concentrated on a single chip run. Even though QC and normalization were performed, batch effects can still contribute to the observed cluster separation.

The analysis also does not adequately account for biopsy cellular composition: depending on the underlying pathology, there may be varying contributions from adipose tissue, connective tissue, inflammatory cells, different fiber types, necrosis/regeneration, and fibrosis. The authors acknowledged that using bulk tissue is a limitation in their rebuttal to Reviewer 2. Nevertheless, depending on how patchy the disease process is, the measured methylation profile may primarily reflect differences in tissue or cellular composition or the proportion of histologically affected tissue rather than disease related alterations.

Because of the points above, I believe stronger scrutiny of the data shown in the unsupervised figures (t-SNE and PCA) is necessary.""",
    "metadata_annotations": """Corresponding reviewer point from Juliane's email:

In this context, the apparently near-complete cluster separation is unexpected and requires careful demonstration that it is stable and not attributable to the structural distribution of potential confounders.

For the primary t-SNE analysis and the sensitivity analyses above, please display the same coordinates with samples colored separately by potential confounder variables: dataset source (MALICoT controls, GEO, and the in-house data), batch information (chip/array/Sentrix), age, sex, biopsy site, estimated inflammatory cell fraction (lymphocytes/macrophages), fiber type estimates, denervation estimates and pathology severity using an appropriate fibrosis/necrosis score. These annotations should be provided where variables are available or can be estimated using validated methods and would help determine whether the confounding variables explain or contribute significantly to the clustering.""",
    "tsne_pca_sensitivity": """The authors state in the rebuttal that they used the entire set of 771,381 probes for the t-SNE visualization using Rtsne(t(getM(mSetSq)), perplexity = 15, theta = 0.5, dims = 2). However, according to the official documentation for Rtsne, default parameters include pca = TRUE and initial_dims = 50. Thus, although the input comprises all probes and the procedure remains unsupervised, the t-SNE is actually calculated from the first 50 internally derived principal components rather than directly from the complete probe space. Those components may themselves be dominated by the technical and biological variables described above. This initial PCA step is standard and computationally reasonable, but it should be reported explicitly. Please include a direct analysis with pca = FALSE if computationally feasible. Please provide a systematic sensitivity analysis using several feasible values of initial_dims (for example, 10, 20, 30, 50, and 72), perplexities (for example, 5, 10, 15, and 20), and random seeds. Where possible, clustering stability should also be summarized quantitatively rather than assessed solely by visual inspection.""",
    "correlation_heatmap_figure1f": """Please provide a sample-to-sample correlation heatmap calculated from the full post-QC M-value matrix to determine whether the separation structure is visible in the original methylation data, since t-SNE prioritizes local neighborhood structure and does not preserve global distances. Samples should be hierarchically clustered using a prespecified correlation-based distance without using diagnostic labels to determine their ordering. Diagnosis and potential confounders should be added only as annotations at the end of the analysis.

The heatmap in Figure 1F is misleading when shown together with the t-SNE and presented in the first paragraph of the Results. According to the code referenced in the manuscript, probes were selected using the diagnostic labels:

# Create a contrast matrix for "one vs control" comparisons
contMatrix <- makeContrasts(
ALS_vs_Control = ALS - Control,
IBM_vs_Control = IBM - Control,
Multiminicores_vs_Control = Multiminicores - Control,
NMA_vs_Control = NMA - Control,
PM_vs_Control = PM - Control,
ALS_vs_NMA = ALS - NMA,
IBM_vs_PM = IBM - PM,
levels = design)

The authors then selected the top 500 ranked CpGs from each of these seven comparisons and plotted their union. This is a supervised analysis, and separation by diagnostic group is partly expected by construction and should not be presented as independent evidence that the samples cluster according to disease. If the authors meant to show the heatmap as a supervised descriptive visualization only, that should be clearly stated in the text and figure legend. If the heatmap was meant to further support the unsupervised clustering of the disease groups, it should be replaced or supplemented by the unsupervised sample-to-sample correlation heatmap described above.""",
    "pca_scrutiny": """The PCA analysis also requires more detailed evaluation. According to the available code, PCA was performed using prcomp(t(getM(mSetSq)), scale.=TRUE). Please provide a scree plot reporting the variance explained by at least the first 20 principal components together with cumulative variance explained, and show multiple pairwise projections, including PC1-PC2, PC1-PC3, PC2-PC3, and subsequent components where relevant. Evaluation limited to PC1 and PC2 may overlook technical or biological structure represented by other major components. The PCA coordinates should be displayed with samples colored separately by diagnostic group, dataset source, Sentrix/chip, biopsy site, sex, age, and available tissue-composition or histopathologic estimates, as requested for the t-SNE above. In addition to visual inspection, please quantify the association of each of the leading PCs with these variables,. This would help determine whether the variance represented by the principal components is more strongly associated with diagnosis or with technical and demographic structure. Because the analysis uses scale.=TRUE, each CpG is standardized to unit variance before PCA. Scaling hundreds of thousands of probes may give low-variance or noisy probes equal weighting with biologically variable probes. Please explain the rationale for the primary scaling approach, and provide an analysis using centered but unscaled M-values (scale.=FALSE). The authors should also examine the CpGs with the largest positive and negative loadings on the leading PCs to assess whether those components are associated with disease biology, batch, dataset source, age, sex, biopsy site, or tissue composition.""",
    "subset_influence": """Re-run the t-SNE and PCA in subsets that remove the dominant or externally sourced groups and directly test the clinically relevant distinctions: (1) excluding MMC; (2) excluding controls; (3) in-house data only; (4) IBM versus non-IBM IIM; and (5) ALS versus non-ALS NMA. These analyses should be recomputed within each subset rather than merely removing points from an embedding calculated from the complete cohort. Given the small group sizes, the authors should also assess whether the observed structure is sensitive to individual influential samples.""",
    "downstream_validation": """The unsupervised analyses should be resolved before the downstream disease-specific claims can be interpreted confidently. The manuscript and letter of rebuttal appear to use the PCA and t-SNE findings as evidence that the methylation data contain an intrinsic structure corresponding to the diagnostic groups and then proceeds to identify differentially methylated CpGs, construct label-informed heatmaps and classifiers, and assign biological meaning to the resulting genes and pathways. If the apparent unsupervised separation is instead substantially driven by confounders, these same variables would also be expected to influence the subsequent supervised and differential analyses. Therefore, confirmation that the unsupervised structure is robust to these potential confounders is an important prerequisite for interpreting the downstream results as associated to disease groups. Even if the unsupervised findings are confirmed, the differential methylation and supervised-learning analyses will still require their own confounder validation.""",
    "supervised_wording": """On page 25, a newly added sentence states, "Next, we wanted to find out whether supervised learning can predict a correct diagnosis." Instead of "diagnosis," the correct term should be "disease group." Along the same lines, the abstract states, "Based on the CpG site methylation data, supervised learning, especially using logistic regression and random forest, even predicted diagnosis beyond disease group correctly in many cases." That's an overstatement again, since non-ALS is not a diagnosis, and neither is "non-IBM, NOS" (not to mention that other diseases that would normally be in the differential diagnosis have not yet been evaluated). Similar inconsistencies in replacing the prior "disease-specific" language with more general terms are present elsewhere in the paper, and should be corrected throughout to avoid overstatements.""",
    "inclusion_exclusion": """The inclusion and exclusion criteria are still not sufficiently detailed. For example, I would be very surprised if the authors' archive included only 6 cases of "non-IBM IIM, NOS" and just 13 cases of non-ALS NMA in the last 8 years. Assuming more cases were available, how were these specific cases selected among all others? Were all candidate cases within the 8-year period reviewed? Were slides reviewed before inclusion, or was inclusion based solely on the initial diagnosis/report? If the latter, how were differences among diagnosing pathologists controlled for? Was clinical information also evaluated, or was inclusion/exclusion based just on the histologic criteria? Etc, etc.""",
    "cell_composition": """I agree that the longitudinal disease analyses are beyond the scope of the current manuscript. However, that was raised only as an example of a scenario in which a difference in cell-type distribution may have a larger effect on the observed methylation signature than the underlying disease entity. The authors either need to perform deconvolution analyses to address the cell composition concern (by incorporating deconvolution estimates into their differential methylation models) or explicitly discuss that the absence of such analyses is a major limitation of the current study.""",
    "als_nma": """Similarly, the ALS/non-ALS comparison has been retained. While that is acceptable, the language in the relevant sections should be further softened to avoid overinterpretation, given the small number of ALS cases.""",
    "proofreading": """The revised manuscript appears to have been written in haste and contains many grammatical and typographic errors, as well as instances where revisions have not been fully implemented. To give just a few of many examples:

a. On page 25, a newly added sentence states, "Next, we wanted to find out whether supervised learning can predict a correct diagnosis." Instead of "diagnosis," the correct term should be "disease group." Along the same lines, the abstract states, "Based on the CpG site methylation data, supervised learning, especially using logistic regression and random forest, even predicted diagnosis beyond disease group correctly in many cases." That's an overstatement again, since non-ALS is not a diagnosis, and neither is "non-IBM, NOS" (not to mention that other diseases that would normally be in the differential diagnosis have not yet been evaluated). Similar inconsistencies in replacing the prior "disease-specific" language with more general terms are present elsewhere in the paper, and should be corrected throughout to avoid overstatements.

b. On page 28, the new text refers to "supplementary table xy" instead of "supplementary tables 2 and 3".

The entire manuscript should be carefully proofread before resubmission.""",
}

for chunk in CHUNKS:
    chunk["quote"] = FULL_REVIEWER_COMMENTS[chunk["id"]]


STYLE = r"""
:root {
  color-scheme: light;
  --bg: #f6f7f9;
  --paper: #ffffff;
  --ink: #1f2937;
  --muted: #5b6472;
  --line: #d8dde6;
  --blue: #1d4ed8;
  --blue-soft: #e8f0ff;
  --green: #166534;
  --green-soft: #e8f5ec;
  --yellow: #854d0e;
  --yellow-soft: #fff7d6;
  --red: #991b1b;
  --red-soft: #feecec;
  --purple: #5b21b6;
  --purple-soft: #f1e9ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
  line-height: 1.55;
}
header {
  background: #101827;
  color: white;
  padding: 28px 38px;
}
header h1 { margin: 0 0 8px; font-size: 30px; }
header p { margin: 0; color: #d1d5db; max-width: 1050px; }
.app-shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 0;
  max-width: 1500px;
  margin: 0 auto;
}
.sidebar {
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow: auto;
  align-self: start;
  padding: 18px 14px 24px 18px;
  border-right: 1px solid var(--line);
  background: #eef2f7;
}
.sidebar-title {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: #475569;
  font-weight: 800;
  margin: 0 0 10px;
}
.sidebar input {
  width: 100%;
  border: 1px solid #aeb8c8;
  border-radius: 6px;
  padding: 8px 9px;
  margin-bottom: 12px;
  background: white;
}
.sidebar a {
  display: block;
  padding: 8px 9px;
  margin: 3px 0;
  border-radius: 6px;
  color: #243044;
  text-decoration: none;
  font-size: 13px;
  line-height: 1.25;
}
.sidebar a:hover { background: #dfe8f5; }
.sidebar a.active {
  background: white;
  color: var(--blue);
  box-shadow: inset 3px 0 0 var(--blue);
  font-weight: 800;
}
.sidebar .nav-group {
  margin: 14px 0 6px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 800;
}
.content {
  min-width: 0;
}
main { max-width: 1120px; margin: 0 auto; padding: 24px; }
.toolbar {
  position: sticky;
  top: 0;
  z-index: 5;
  background: rgba(246,247,249,.96);
  border-bottom: 1px solid var(--line);
  padding: 12px 0;
  backdrop-filter: blur(8px);
}
.toolbar-inner {
  max-width: 1500px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
button {
  border: 1px solid #b8c1d1;
  background: white;
  color: var(--ink);
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-weight: 600;
}
button.primary { background: var(--blue); border-color: var(--blue); color: white; }
button:hover { filter: brightness(.97); }
.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 22px;
  margin: 18px 0;
  box-shadow: 0 1px 2px rgba(16, 24, 39, .05);
}
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}
.mini {
  border: 1px solid var(--line);
  border-left: 4px solid var(--blue);
  background: #fbfcff;
  border-radius: 6px;
  padding: 12px;
}
.mini strong { display: block; margin-bottom: 4px; }
h2 { margin: 0 0 14px; font-size: 24px; }
h3 { margin: 18px 0 8px; font-size: 17px; }
.chunk h2 { padding-bottom: 10px; border-bottom: 1px solid var(--line); }
blockquote {
  margin: 12px 0;
  padding: 12px 14px;
  background: #f8fafc;
  border-left: 4px solid #64748b;
  color: #334155;
  white-space: pre-wrap;
}
.meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 10px 0 16px;
}
.badge {
  display: inline-flex;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid var(--line);
  background: #f8fafc;
}
.badge.status { color: var(--green); background: #fbfdfc; border-color: #cfded4; }
.badge.owner { color: var(--yellow); background: #fffdf6; border-color: #e5d8aa; }
.badge.reviewer { color: var(--blue); background: #f8fbff; border-color: #c7d7f3; }
.box {
  border-radius: 8px;
  border: 1px solid var(--line);
  border-left-width: 4px;
  padding: 14px;
  margin: 12px 0;
  background: white;
}
.box.asking { border-left-color: #8ba7da; }
.box.decision { border-left-color: #a998d5; }
.box.interpretation { border-left-color: #95c5a2; }
.box.draft { border-left-color: #aeb8c8; }
.box.need { border-left-color: #d4ad45; background: #fffdf7; }
.box.edit-box { border-left-color: #4b7bec; }
.box.figure-insert { border-left-color: #5fa777; }
.subsection-label {
  margin: 14px 0 6px;
  font-weight: 800;
  color: #475569;
}
.table-wrap {
  width: 100%;
  overflow-x: auto;
  margin-top: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
th, td {
  border: 1px solid var(--line);
  padding: 8px 10px;
  vertical-align: top;
  text-align: left;
}
th {
  background: #f8fafc;
  font-weight: 700;
}
.label {
  font-weight: 800;
  margin-bottom: 6px;
}
.instruction-box {
  border: 1px solid var(--line);
  border-left: 4px solid #334155;
  border-radius: 8px;
  margin: 14px 0;
  background: white;
}
.instruction-box .label {
  padding: 13px 14px 8px;
  border-bottom: 1px solid var(--line);
}
.instruction-row {
  display: grid;
  grid-template-columns: 170px minmax(0, 1fr);
  gap: 14px;
  padding: 11px 14px;
  border-bottom: 1px solid #eef1f5;
}
.instruction-row:last-child { border-bottom: 0; }
.instruction-key {
  color: #475569;
  font-size: 13px;
  font-weight: 800;
}
.instruction-value p {
  margin: 0 0 7px;
}
.instruction-value p:last-child { margin-bottom: 0; }
.figure {
  margin: 14px 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
  background: white;
}
.figure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 12px;
  margin: 12px 0 18px;
}
.figure img {
  display: block;
  width: 100%;
  max-height: 620px;
  object-fit: contain;
}
.figure.thumb {
  margin: 0;
  padding: 8px;
}
.figure.thumb img {
  height: 260px;
  max-height: 260px;
  object-fit: contain;
}
figcaption {
  color: var(--muted);
  font-size: 13px;
  margin-top: 8px;
}
details {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  background: #fcfdff;
  margin: 12px 0;
}
summary {
  cursor: pointer;
  font-weight: 800;
}
textarea {
  width: 100%;
  min-height: 110px;
  border: 1px solid #aeb8c8;
  border-radius: 8px;
  padding: 10px;
  font: 14px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  resize: vertical;
  background: white;
}
.structured-notes {
  display: grid;
  gap: 10px;
}
.note-caption {
  color: var(--muted);
  font-size: 13px;
  margin: 4px 0 8px;
}
.toc a {
  display: block;
  padding: 6px 0;
  color: var(--blue);
  text-decoration: none;
}
.toc a:hover { text-decoration: underline; }
.warning {
  background: #fffafa;
  border: 1px solid #f4b4b4;
  border-left: 4px solid var(--red);
  color: var(--red);
  border-radius: 8px;
  padding: 12px;
}
.small { color: var(--muted); font-size: 13px; }
html { scroll-behavior: smooth; }
section[id] { scroll-margin-top: 84px; }
mark.search-hit {
  background: #fff1a8;
  color: inherit;
  padding: 0 2px;
  border-radius: 3px;
}
@media print {
  .toolbar, .sidebar, textarea, button { display: none; }
  body { background: white; }
  .app-shell { display: block; max-width: none; }
  main { max-width: none; }
  .card { box-shadow: none; break-inside: avoid; }
}
@media (max-width: 980px) {
  .app-shell { display: block; }
  .sidebar {
    position: sticky;
    top: 58px;
    z-index: 4;
    height: auto;
    max-height: 280px;
    border-right: 0;
    border-bottom: 1px solid var(--line);
    padding: 12px 16px;
  }
  .sidebar a { display: inline-block; max-width: 260px; vertical-align: top; }
  .instruction-row { grid-template-columns: 1fr; gap: 4px; }
  main { padding: 16px; }
}
"""


SCRIPT = r"""
const storageKey = "reviewer-response-workbook-notes-v1:" + location.pathname;

function allTextareas() {
  return Array.from(document.querySelectorAll("textarea[data-note-id]"));
}

function loadNotes() {
  const saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
  allTextareas().forEach(t => {
    if (saved[t.dataset.noteId]) t.value = saved[t.dataset.noteId];
    t.addEventListener("input", saveNotes);
  });
}

function saveNotes() {
  const saved = {};
  allTextareas().forEach(t => saved[t.dataset.noteId] = t.value);
  localStorage.setItem(storageKey, JSON.stringify(saved));
  const stamp = document.getElementById("save-stamp");
  if (stamp) stamp.textContent = "Notes autosaved in this browser: " + new Date().toLocaleString();
}

function collectNotes() {
  const lines = [];
  lines.push("# Juliane notes from reviewer response workbook");
  lines.push("");
  lines.push("Generated: " + new Date().toLocaleString());
  lines.push("");
  document.querySelectorAll("section.chunk").forEach(section => {
    const title = section.querySelector("h2").innerText;
    const notes = Array.from(section.querySelectorAll("textarea[data-note-id]"))
      .map(t => {
        const label = t.dataset.label || "Notes";
        const value = t.value.trim();
        return value ? `## ${title}\n\n### ${label}\n\n${value}\n` : "";
      })
      .filter(Boolean);
    if (notes.length) lines.push(notes.join("\n"));
  });
  if (lines.length <= 4) {
    lines.push("No notes were entered.");
  }
  return lines.join("\n");
}

async function copyAllNotes() {
  const text = collectNotes();
  await navigator.clipboard.writeText(text);
  alert("All notes copied to clipboard.");
}

function downloadNotes() {
  const blob = new Blob([collectNotes()], {type: "text/markdown;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "juliane_notes_reviewer_response_workbook.md";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function clearNotes() {
  if (!confirm("Clear all note boxes stored in this browser for this report?")) return;
  localStorage.removeItem(storageKey);
  allTextareas().forEach(t => t.value = "");
  const stamp = document.getElementById("save-stamp");
  if (stamp) stamp.textContent = "Notes cleared.";
}

document.addEventListener("DOMContentLoaded", loadNotes);

function setupSidebar() {
  const navLinks = Array.from(document.querySelectorAll(".sidebar a[data-target]"));
  const sections = navLinks
    .map(link => document.getElementById(link.dataset.target))
    .filter(Boolean);

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navLinks.forEach(link => link.classList.toggle("active", link.dataset.target === entry.target.id));
    });
  }, {rootMargin: "-25% 0px -65% 0px", threshold: 0.01});
  sections.forEach(section => observer.observe(section));

  const filter = document.getElementById("sidebar-filter");
  if (filter) {
    filter.addEventListener("input", () => {
      const needle = filter.value.trim().toLowerCase();
      navLinks.forEach(link => {
        link.hidden = needle && !link.textContent.toLowerCase().includes(needle);
      });
    });
  }
}

document.addEventListener("DOMContentLoaded", setupSidebar);
"""


def note_box(chunk: dict) -> str:
    base = chunk["id"]
    if chunk.get("needs_structured"):
        fields = [
            ("Juliane decision / factual answer", "decision"),
            ("Clinical or pathology text to insert", "clinical_text"),
            ("Preferred rebuttal wording", "rebuttal"),
            ("Still unresolved", "unresolved"),
        ]
        return (
            '<div class="box need"><div class="label">Juliane notes / decision</div>'
            '<p class="note-caption">These fields autosave in this browser. Use Copy all notes or Download notes before sending feedback.</p>'
            '<div class="structured-notes">'
            + "".join(
                f'<label><strong>{html.escape(label)}</strong>'
                f'<textarea data-note-id="{base}_{field}" data-label="{html.escape(label)}"></textarea></label>'
                for label, field in fields
            )
            + "</div></div>"
        )
    return (
        '<div class="box need"><div class="label">Juliane notes / approval</div>'
        '<p class="note-caption">Please write corrections, approval, or preferred rebuttal wording here. This autosaves only in this browser.</p>'
        f'<textarea data-note-id="{base}_notes" data-label="Juliane notes / approval"></textarea>'
        "</div>"
    )


def render_chunk(chunk: dict) -> str:
    parts = [
        f'<section class="card chunk" id="{chunk["id"]}">',
        f"<h2>{html.escape(chunk['title'])}</h2>",
        '<div class="meta">',
        f'<span class="badge reviewer">{html.escape(chunk["reviewer"])}</span>',
        f'<span class="badge status">Status: {html.escape(chunk["status"])}</span>',
        f'<span class="badge owner">Owner: {html.escape(chunk["owner"])}</span>',
        "</div>",
        '<h3>Reviewer comment</h3>',
        quote(chunk["quote"]),
        '<div class="box asking"><div class="label">What the reviewer is asking</div>',
        li(chunk["asking"]),
        "</div>",
        '<div class="box decision"><div class="label">Juliane/team decision line</div>',
        li(chunk["decision"]),
        "</div>",
        "<h3>What we did</h3>",
        li(chunk["did"]),
    ]
    if chunk["figures"]:
        parts += ["<h3>Figures / direct evidence</h3>", chunk["figures"]]
    if chunk["supplementary"]:
        parts += [
            "<h3>Additional figures</h3>",
            chunk["supplementary"],
        ]
    parts += [
        '<div class="box interpretation"><div class="label">Interpretation</div>',
        li(chunk["interpretation"]),
        "</div>",
        draft_rebuttal_box(chunk),
        manuscript_edits_box(chunk),
        note_box(chunk),
        "</section>",
    ]
    return "\n".join(parts)


def build() -> str:
    toc = "".join(
        f'<a href="#{c["id"]}">{html.escape(c["reviewer"])} — {html.escape(c["title"])}</a>'
        for c in CHUNKS
    )
    side_toc = "".join(
        f'<a href="#{c["id"]}" data-target="{c["id"]}">{html.escape(c["reviewer"])} — {html.escape(c["title"])}</a>'
        for c in CHUNKS
    )
    chunks = "\n".join(render_chunk(c) for c in CHUNKS)
    payload = {
        "title": "Reviewer response workbook",
        "chunks": [c["id"] for c in CHUNKS],
    }
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reviewer response workbook</title>
<style>{STYLE}</style>
</head>
<body>
<header>
  <h1>Reviewer response workbook</h1>
  <p>Interactive working report for Juliane and Joseph. The structure follows Juliane's 2026-07-08 email and labels each topic by reviewer source, with evidence, interpretation, a complete draft for the rebuttal letter, suggested manuscript modifications, and note boxes.</p>
</header>
<div class="toolbar">
  <div class="toolbar-inner">
    <button class="primary" onclick="copyAllNotes()">Copy all notes</button>
    <button onclick="downloadNotes()">Download notes as Markdown</button>
    <button onclick="saveNotes()">Save notes now</button>
    <button onclick="clearNotes()">Clear notes</button>
    <span class="small" id="save-stamp">Notes autosave in this browser only.</span>
  </div>
</div>
<div class="app-shell">
<aside class="sidebar" aria-label="Reviewer response navigation">
  <div class="sidebar-title">Navigation</div>
  <input id="sidebar-filter" type="search" placeholder="Filter topics">
  <a href="#how-to-use" data-target="how-to-use">How to use</a>
  <a href="#executive-summary" data-target="executive-summary">Executive summary</a>
  <div class="nav-group">Reviewer chunks</div>
  {side_toc}
</aside>
<div class="content">
<main>
  <section class="card" id="how-to-use">
    <h2>How to use this workbook</h2>
    <div class="warning"><strong>Important:</strong> Text typed into note boxes is stored in the browser, not written back into this HTML file. Before sending feedback, use <strong>Copy all notes</strong> or <strong>Download notes as Markdown</strong>.</div>
    <div class="summary-grid">
      <div class="mini"><strong>Main line</strong>Juliane's email defines the required response path.</div>
      <div class="mini"><strong>Each chunk</strong>One reviewer topic, one interpretation, one draft rebuttal response.</div>
      <div class="mini"><strong>Figures</strong>Main evidence is shown inline; supporting figures are shown as compact side-by-side cards with short remarks.</div>
      <div class="mini"><strong>Final goal</strong>Convert Juliane's notes into final manuscript edits and rebuttal text.</div>
    </div>
  </section>

  <section class="card" id="executive-summary">
    <h2>Executive summary</h2>
    {li([
        "The analysis response is largely complete: metadata annotation, t-SNE sensitivity, direct pca=FALSE t-SNE, label-free correlation heatmap, expanded PCA, subset/influence analyses, differential sensitivity and patient-aware supervised learning have been done.",
        "The scientific interpretation must be cautious: the cohort shows disease-group-associated methylation structure, but source, Sentrix, demographic variables and biopsy site are also aligned with major structure.",
        "The remaining blockers are clinical/pathology author inputs: archive selection workflow, exclusion counts, lymphomonocyte definition, availability of validated cell-composition/pathology scores, figure placement, authorship wording and final proofreading.",
    ])}
  </section>

  <section class="card toc">
    <h2>Table of contents</h2>
    {toc}
  </section>

  {chunks}
</main>
</div>
</div>
<script type="application/json" id="workbook-metadata">{html.escape(json.dumps(payload))}</script>
<script>{SCRIPT}</script>
</body>
</html>
"""


def main() -> None:
    missing = [
        WEB_FIG / name
        for name in [
            "Figure_unsupervised_PCA.png",
            "Figure_unsupervised_tSNE.png",
            "Figure_PC_metadata_associations.png",
            "Figure_tSNE_stability.png",
            "Figure_tSNE_direct_pca_false.png",
            "Figure_sample_correlation_heatmap.png",
            "Figure_sample_correlation_annotation_legend.png",
            "Figure_PCA_scree.png",
            "Figure_differential_sensitivity.png",
            "Figure_metadata_only_classifier.png",
            "Figure_patient_aware_ML.png",
        ]
        if not (WEB_FIG / name).exists()
    ]
    if missing:
        raise FileNotFoundError("\n".join(str(path) for path in missing))
    build_supplementary_previews()
    OUT.write_text(build(), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
