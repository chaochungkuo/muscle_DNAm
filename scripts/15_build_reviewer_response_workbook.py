from __future__ import annotations

import base64
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
PACKAGE = PROJECT / "manuscripts" / "reviewer_round_2" / "to_Juliane_2026-07-16"
OUT = PACKAGE / "reviewer_response_workbook.html"
WEB_FIG = ROOT / "figures" / "web"


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


def main_fig(name: str, caption: str) -> str:
    return (
        '<figure class="figure">'
        f'<img src="{png_data(name)}" alt="{html.escape(caption)}">'
        f"<figcaption>{html.escape(caption)}</figcaption>"
        "</figure>"
    )


def pdf_links(names: list[str]) -> str:
    if not names:
        return ""
    return (
        '<div class="pdf-grid">'
        + "".join(
            f'<a href="figures_review_pdf/supplementary/{html.escape(name)}" target="_blank">{html.escape(name)}</a>'
            for name in names
        )
        + "</div>"
    )


def main_pdf_links(names: list[str]) -> str:
    if not names:
        return ""
    return (
        '<div class="pdf-grid">'
        + "".join(
            f'<a href="figures_review_pdf/main/{html.escape(name)}" target="_blank">{html.escape(name)}</a>'
            for name in names
        )
        + "</div>"
    )


CHUNKS = [
    {
        "id": "overall_confounding",
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
        "supplementary": pdf_links([
            "pca_scaled_by_display_group.pdf",
            "pca_scaled_by_dataset_source.pdf",
            "pca_scaled_by_sentrix_id.pdf",
            "tsne_baseline_by_display_group.pdf",
            "tsne_baseline_by_dataset_source.pdf",
            "tsne_baseline_by_sentrix_id.pdf",
        ]),
        "interpretation": [
            "The methylation matrix contains strong structure, but the leading structure is not cleanly separable from source, Sentrix, demographic variables, and biopsy site in this cohort.",
            "This supports a pilot, hypothesis-generating interpretation and argues against disease-entity-specific or clinical diagnostic wording.",
        ],
        "draft": "We agree that the strong separation in the unsupervised plots required additional scrutiny. We therefore reanalyzed the cohort using the revised metadata table, annotated PCA and t-SNE coordinates by disease group and available confounders, and quantified associations between leading PCs and metadata variables. These analyses show disease-group-associated structure, but also substantial alignment with dataset source, Sentrix array, demographic variables and biopsy site. We therefore revised the manuscript to avoid disease-intrinsic or clinical-diagnostic claims and now present the findings as pilot, group-associated observations requiring validation in larger balanced cohorts.",
        "manuscript": [
            "Title/abstract/results/discussion should use disease-group-associated wording.",
            "Avoid intrinsic, disease-specific entity, or diagnostic classifier claims.",
        ],
    },
    {
        "id": "metadata_annotations",
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
        "figures": main_fig("Figure_unsupervised_PCA.png", "PCA overview; detailed confounder views are in supplementary PDFs.")
        + main_fig("Figure_unsupervised_tSNE.png", "t-SNE overview; detailed confounder views are in supplementary PDFs."),
        "supplementary": pdf_links([
            "pca_scaled_by_age_group.pdf",
            "pca_scaled_by_gender.pdf",
            "pca_scaled_by_muscle_location_group.pdf",
            "pca_scaled_by_city_of_origin.pdf",
            "pca_scaled_by_lymphomonocytes.pdf",
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
        "manuscript": [
            "Add explicit statement that unavailable tissue-composition variables were not inferred.",
            "Add major limitation wording if Juliane confirms no validated estimates are available.",
        ],
    },
    {
        "id": "tsne_pca_sensitivity",
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
        "manuscript": [
            "Methods: explicitly state Rtsne pca=TRUE, initial_dims=50.",
            "Results/supplement: add pca=FALSE and sensitivity summaries.",
        ],
    },
    {
        "id": "correlation_heatmap_figure1f",
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
        "figures": main_fig("Figure_sample_correlation_heatmap.png", "Label-free full-matrix Pearson sample-correlation heatmap."),
        "supplementary": main_pdf_links(["Figure_sample_correlation_heatmap.pdf"]),
        "interpretation": [
            "This directly answers the reviewer because ordering is not label-informed.",
            "The former heatmap should not be presented as independent evidence of natural clustering.",
        ],
        "draft": "We agree that the previous top-CpG heatmap was label-informed and therefore should not be presented as independent unsupervised evidence. We replaced/supplemented this panel with a sample-to-sample Pearson correlation heatmap calculated from the complete post-QC M-value matrix. Samples were ordered by hierarchical clustering using 1 minus Pearson correlation and complete linkage; diagnostic and metadata annotations were added only after clustering. The previous top-CpG heatmap is now described only as supervised descriptive visualization.",
        "manuscript": [
            "Figure 1F: use label-free correlation heatmap.",
            "Move label-informed heatmap to supplement or relabel as supervised descriptive.",
        ],
    },
    {
        "id": "pca_scrutiny",
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
        "supplementary": pdf_links([
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
        ]),
        "interpretation": [
            "Scaled and unscaled PCA both show structure, so the observation is not solely a scaling artifact.",
            "However, leading PCs also align with source/Sentrix and other cohort variables, so disease-only interpretation is not justified.",
        ],
        "draft": "We expanded the PCA evaluation substantially. We now provide scree and cumulative-variance plots for the leading PCs, multiple pairwise projections, centered-scaled and centered-unscaled analyses, quantitative associations between leading PCs and available metadata variables, and annotation of the strongest positive and negative loadings. The unscaled analysis supports the presence of structure beyond the original scaling choice, but the leading components remain associated with technical and cohort variables as well as disease group.",
        "manuscript": [
            "Methods: explain scaled PCA and unscaled sensitivity.",
            "Results: avoid reading PC1/PC2 as disease-only axes.",
        ],
    },
    {
        "id": "subset_influence",
        "title": "6. Subset and influential-sample analyses",
        "status": "Complete",
        "owner": "Joseph drafted; Juliane to approve wording",
        "quote": "Re-run the t-SNE and PCA in subsets... excluding MMC; excluding controls; institutional archive samples only; IBM versus non-IBM IIM; ALS versus non-ALS NMA... assess whether the observed structure is sensitive to individual influential samples.",
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
        "supplementary": pdf_links([
            "subset_excluding_MMC_PCA.pdf",
            "subset_excluding_MMC_tSNE.pdf",
            "subset_excluding_controls_PCA.pdf",
            "subset_excluding_controls_tSNE.pdf",
            "subset_institutional_archive_PCA.pdf",
            "subset_institutional_archive_tSNE.pdf",
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
        "draft": "We recomputed PCA and t-SNE independently for all requested subsets rather than removing samples from the full-cohort embedding. The institutional-only and disease-pair analyses show weaker structure than the full mixed-source cohort. ALS versus non-ALS neurogenic atrophy was the least stable comparison and was sensitive to individual samples; we therefore revised the manuscript to describe this contrast as exploratory.",
        "manuscript": [
            "Add supplementary subset figure references.",
            "Soften ALS-NMA claims in Results and Discussion.",
        ],
    },
    {
        "id": "downstream_validation",
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
        "manuscript": [
            "Methods/Results: state which covariates were estimable.",
            "Discussion: state source/Sentrix confounding cannot be fully removed in this cohort.",
        ],
    },
    {
        "id": "supervised_wording",
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
        "manuscript": [
            "Search entire manuscript for diagnosis, diagnostic, disease-specific, entity-specific.",
            "Final proofreading after Juliane fills clinical placeholders.",
        ],
    },
    {
        "id": "inclusion_exclusion",
        "title": "9. Reviewer 2: inclusion/exclusion criteria and archive selection",
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
        "manuscript": [
            "Add factual archive selection paragraph from Juliane.",
            "Replace remaining xxx placeholders.",
        ],
        "needs_structured": True,
    },
    {
        "id": "cell_composition",
        "title": "10. Reviewer 2: deconvolution and cell-composition limitation",
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
        "supplementary": pdf_links([
            "pca_scaled_by_lymphomonocytes.pdf",
            "pca_unscaled_by_lymphomonocytes.pdf",
            "tsne_baseline_by_lymphomonocytes.pdf",
        ]),
        "interpretation": [
            "This point should be answered transparently; overstating the lymphomonocyte variable would be risky.",
            "If Juliane has validated scores, we would need to rerun relevant models.",
        ],
        "draft": "We agree that cell composition is a major concern for bulk skeletal-muscle methylation. Validated sample-level deconvolution estimates or histopathology scores suitable for covariate adjustment were not available for the current analysis. We therefore did not add unsupported deconvolution modeling and instead revised the Discussion to state explicitly that the absence of cell-composition-adjusted analyses is a major limitation.",
        "manuscript": [
            "Discussion: major limitation wording.",
            "Methods/Results: only mention lymphomonocytes if Juliane defines the categories.",
        ],
        "needs_structured": True,
    },
    {
        "id": "als_nma",
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
        "supplementary": pdf_links([
            "subset_ALS_vs_nonALS_NMA_PCA.pdf",
            "subset_ALS_vs_nonALS_NMA_tSNE.pdf",
            "influential_sample_analysis.pdf",
        ]),
        "interpretation": [
            "ALS-NMA is the least stable clinically relevant comparison.",
            "Any biological interpretation should be framed as preliminary.",
        ],
        "draft": "We have further softened the ALS versus non-ALS neurogenic atrophy interpretation. This comparison is now described as exploratory and hypothesis-generating because of the small ALS sample size, overlap in unsupervised analyses, sensitivity to individual samples and loss of FDR-significant CpGs after biopsy-site adjustment.",
        "manuscript": [
            "Results and Discussion: avoid strong ALS-specific methylation signature wording.",
        ],
    },
    {
        "id": "proofreading",
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
        "manuscript": [
            "Confirm author list/order and Tayfun Palaz placeholder.",
            "Confirm co-last-author wording.",
            "Final supplement numbering and proofreading.",
        ],
        "needs_structured": True,
    },
]


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
.badge.status { color: var(--green); background: var(--green-soft); border-color: #bbebc9; }
.badge.owner { color: var(--yellow); background: var(--yellow-soft); border-color: #f1d98d; }
.box {
  border-radius: 8px;
  border: 1px solid var(--line);
  padding: 14px;
  margin: 12px 0;
}
.box.asking { background: var(--blue-soft); border-color: #c9dafd; }
.box.decision { background: var(--purple-soft); border-color: #d8c5ff; }
.box.interpretation { background: var(--green-soft); border-color: #bfe7cb; }
.box.draft { background: #fbfbfc; border-color: #cfd6df; }
.box.need { background: var(--yellow-soft); border-color: #efcf77; }
.label {
  font-weight: 800;
  margin-bottom: 6px;
}
.figure {
  margin: 14px 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
  background: white;
}
.figure img {
  display: block;
  width: 100%;
  max-height: 760px;
  object-fit: contain;
}
figcaption {
  color: var(--muted);
  font-size: 13px;
  margin-top: 8px;
}
.pdf-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 8px;
  margin-top: 8px;
}
.pdf-grid a {
  display: block;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: white;
  color: var(--blue);
  text-decoration: none;
  font-size: 13px;
}
.pdf-grid a:hover { text-decoration: underline; }
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
  background: var(--red-soft);
  border: 1px solid #f4b4b4;
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
            "<details><summary>Supplementary or source figure links</summary>",
            chunk["supplementary"],
            "</details>",
        ]
    parts += [
        '<div class="box interpretation"><div class="label">Interpretation</div>',
        li(chunk["interpretation"]),
        "</div>",
        '<div class="box draft"><div class="label">Draft rebuttal response</div>',
        p(chunk["draft"]),
        "</div>",
        "<h3>Manuscript action</h3>",
        li(chunk["manuscript"]),
        note_box(chunk),
        "</section>",
    ]
    return "\n".join(parts)


def build() -> str:
    toc = "".join(f'<a href="#{c["id"]}">{html.escape(c["title"])}</a>' for c in CHUNKS)
    side_toc = "".join(
        f'<a href="#{c["id"]}" data-target="{c["id"]}">{html.escape(c["title"])}</a>'
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
  <p>Interactive working report for Juliane and Joseph. The structure follows Juliane's 2026-07-08 email and breaks reviewer comments into one-topic chunks with evidence, interpretation, draft rebuttal text and note boxes.</p>
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
      <div class="mini"><strong>Figures</strong>Main evidence is shown inline; dense supplementary figures are hidden in expandable sections.</div>
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
            "Figure_PCA_scree.png",
            "Figure_differential_sensitivity.png",
            "Figure_metadata_only_classifier.png",
            "Figure_patient_aware_ML.png",
        ]
        if not (WEB_FIG / name).exists()
    ]
    if missing:
        raise FileNotFoundError("\n".join(str(path) for path in missing))
    OUT.write_text(build(), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
