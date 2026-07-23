#!/usr/bin/env python3
"""Build a clean highlighted manuscript draft with softened ALS/NMA wording.

The goal is not to comprehensively rewrite the manuscript, but to make the
ALS versus non-ALS NMA and supervised-learning language internally consistent
with the round-2 rebuttal strategy:

- retain ALS/NMA analyses,
- describe them as exploratory/hypothesis-generating,
- avoid diagnostic-validation language,
- use disease-group classification terminology.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.shared import Pt


ANALYSIS_REPO = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ANALYSIS_REPO.parents[1]
MANUSCRIPTS = PROJECT_ROOT / "manuscripts"
BASE_DOCX = MANUSCRIPTS / "Bremer_manuscript_changes not marked.docx"
OUT_DIR = MANUSCRIPTS / "reviewer_round_2" / "to_Juliane_2026-07-23"
OUT_DOCX = OUT_DIR / "Bremer_manuscript_clean_highlighted_ALS_NMA_wording_draft.docx"
CHANGE_LOG = OUT_DIR / "MANUSCRIPT_ALS_NMA_WORDING_CHANGES.md"


REPLACEMENTS = {
    1: (
        "Title: avoid disease-group-specific overclaim.",
        "Disease group-associated DNA methylation patterns",
    ),
    48: (
        "Abstract: replace overstatement about diagnosis prediction with disease-group classification and validation caveat.",
        "Unsupervised t-SNE analysis and full-matrix sample-to-sample correlation analysis revealed disease-group-associated methylation structure, with partial overlap between ALS and non-ALS NMA. Using leakage-controlled supervised learning, methylation data classified disease groups in held-out samples within this selected pilot cohort, but these internal performance estimates require validation in independent cohorts. Gene set enrichment analysis pointed at commonly dysregulated pathways, including cytoskeletal maintenance, cell adhesion, muscle and neural development, Wnt-signaling as well as proteostasis. In inflammatory myopathies, sites linked to immune system activation were hypomethylated. Analysis of CpG methylation of individual preselected genes involved in ALS and inflammatory myopathies, respectively, pointed at certain genes, whose differential expression might be in part regulated by methylation, including T cell differentiation and cytotoxicity markers. Correlation of CpG site methylation and expression data in IBM revealed a potential mechanism involving epigenetic regulation of DMWD and HDAC4 expression through which muscle stem cells and regeneration can be controlled in IBM. Analyzing RNA expression data, we found further evidence that stem cells fail to activate the regeneration program in IBM.",
    ),
    59: (
        "Introduction aim: avoid claiming disease-specific diagnostic methylome patterns as the established target.",
        "Non-neoplastic muscle disorders are a heterogeneous group of disorders, including genetic, metabolic and toxic diseases as well as autoimmune-mediated inflammatory myopathies and neurogenic atrophy. Although some epigenetic changes have been described for example in dermatomyositis [53, 64], a clear correlation between the muscle methylome and specific muscular disorders has not been established yet. In the present study, we aimed at identifying disease-group-associated methylome patterns in non-neoplastic muscle pathology. Furthermore, we sought to determine whether the methylome alterations are pointing at pathophysiological mechanisms. We also applied leakage-controlled supervised learning to explore whether methylome data can classify disease groups within this selected pilot cohort.",
    ),
    71: (
        "Methods heading: replace diagnosis prediction with disease-group classification.",
        "Supervised learning for disease-group classification",
    ),
    87: (
        "Figure 1 legend: describe t-SNE/correlation heatmap cautiously and explicitly retain ALS/NMA overlap.",
        "Figure 1. Disease group-associated and overlapping histological and epigenetic features. Cases were classified based on clinical and histopathological features. Groups of partially atrophic (diameter 20-40 µm) and atrophic (diameter <20 µm) as well as hypertrophic (diameter >80 µm) muscle fibers in neurogenic atrophy due to ALS (a) and sensorimotor neuropathy (b). Arrows in (b): target regions. Cryostat sections, H&E. Scale bars = 50 µm. (c) Marked endomysial inflammatory infiltration with many cytotoxic T cells immunoreactive for CD8 (brown) and focal infiltration of a muscle fiber (arrow) in a case of IBM. Paraffin section, hematoxylin counterstain. Scale bar = 50 µm. (d) Rimmed vacuoles (arrows) in an IBM case. Cryostat sections, H&E. Scale bar = 25 µm. (e) Unsupervised t-SNE visualization of the full post-QC filtered methylation matrix shows disease-group-associated structure, while ALS and non-ALS NMA remain partially overlapping. (f) Label-free sample-to-sample correlation heatmap calculated from the full post-QC M-value matrix and ordered by unsupervised hierarchical clustering; diagnostic and metadata annotations were added only after clustering.",
    ),
    111: (
        "ALS/NMA Results: retain analysis but make it exploratory and avoid implying robust diagnostic separation.",
        "While inflammatory myopathies can in many cases be well differentiated from neurogenic atrophies, including the one occurring in ALS, the distinction within neurogenic atrophy, i.e. ALS NMA versus NMA due to other causes, can be challenging or even impossible solely based on histopathological data. In this pilot cohort, ALS and non-ALS NMA showed partially overlapping methylation profiles, and reviewer-requested subset analyses indicated that this was the least stable disease-pair comparison. We therefore treated the ALS NMA versus non-ALS NMA analysis as exploratory and hypothesis-generating. To explore possible biological correlates of differential methylation within related neurogenic atrophy groups, we performed a CpG site-associated gene set enrichment analysis for the comparison “ALS NMA versus non-ALS NMA”. There were only two GO terms associated with hypermethylated sites, both related to cell adhesion via plasma-membrane adhesion molecules (GO:0007156 and GO:0098742), suggesting possible involvement of cell-adhesion-related methylation differences in this exploratory comparison. Comparing IBM versus non-IBM IIM, NOS revealed that CpG sites associated with genes encoding proteins that are involved in immune system activation, especially T cell/ lymphocyte differentiation/ activation were significantly enriched amongst hypomethylated sites, as were associated with protein degradation and autophagy. Hypermethylated sites in IBM were mostly associated with GO terms linked to the development and differentiation of stem cells/precursor cells, blood vessels and neuronal tissue as well as cell-cell interaction/junctions (Supplementary Table 4).",
    ),
    125: (
        "Results heading: replace diagnosis prediction with disease-group classification.",
        "Supervised learning classifies disease groups in held-out samples within this selected pilot cohort",
    ),
    126: (
        "Supervised learning Results: use leakage-controlled disease-group wording and validation caveat.",
        "Next, we explored whether supervised learning could classify disease groups based on methylation data in this selected pilot cohort. We first split our cases into a training set (60% of the data) and a held-out test set (40%), maintaining the class proportions. Using the training set only, we filtered and preprocessed the data and selected the most discriminative features — removing low-variance CpG sites, then applying univariate and mutual-information selection and Random Forest recursive feature elimination to obtain the 50 most distinct CpG sites. The fitted selectors were applied unchanged to the held-out test set. The training set served to train and tune the individual models (with stratified cross-validation), while the test set was used solely to evaluate the performance of the different supervised learning algorithms. We tested four alternative supervised learning algorithms: logistic regression, decision trees, random forest and SVM (support vector machine). All models classified disease groups in the held-out test set with an accuracy of at least 73% (decision tree, lowest). Logistic regression and random forest performed best, each with an accuracy of 93.3% and a weighted precision of 95.2% (recall 93.3%, F1 92.2%); SVM reached 86.7% accuracy, 92.5% weighted precision, 86.7% recall and F1 86.1%. These performance estimates are internal to this selected cohort and should not be interpreted as validation of a clinical diagnostic classifier. Validation in larger independent cohorts will be required.",
    ),
    128: (
        "Figure 6 legend: avoid true diagnosis/predicted diagnosis wording.",
        "Figure 6. Supervised learning algorithms for disease-group classification. Heatmaps of the correlation matrices are shown for logistic regression (a), decision tree (b), random forest (c) and SVM (d). Logistic regression and random forest showed the highest agreement between clinicopathological disease group and methylation-based disease-group prediction in the held-out test set. Table showing accuracy, precision, recall frequency and F1 score for the different supervised learning models applied to the dataset (e).",
    ),
    132: (
        "Discussion opening: avoid diagnostic-value overclaim and frame as pilot cohort evidence.",
        "In this cohort consisting of inclusion body myositis (IBM), non-IBM inflammatory myopathy (non-IBM IIM, NOS), amyotrophic lateral sclerosis (ALS), non-ALS neuromuscular atrophy (NMA), and multi-minicore myopathy (MMC), as well as normal controls, we observed disease-group-associated CpG methylation patterns that may aid future diagnostic studies and may point at pathophysiological mechanisms in inflammatory and neurogenic atrophy. The diagnostic value for complex cases, mixed pathology, and ALS versus non-ALS NMA requires validation in larger independent cohorts.",
    ),
    133: (
        "Discussion diagnostic tools: soften diagnostic-workup claim.",
        "Methylation profile-based diagnostic tools work particularly well for neoplastic diseases, because these are characterized by expansion of a mutated cell clone. Hence, cells are often more homogenous; minor contamination by the infiltrated host tissue is usually well tolerated. The inhomogeneous nature of healthy and diseased muscle tissue may complicate methylation profiling-based diagnostic tools. Nevertheless, our results suggest that analysis of epigenetic, i.e. DNA methylation patterns, may provide useful complementary information for the study and future diagnostic evaluation of muscle biopsies in selected contexts.",
    ),
    135: (
        "ALS/NMA Discussion: explicitly mark as exploratory and small-cohort limited.",
        "Although not all ALS cases could be distinguished unequivocally from neurogenic atrophy due to other causes, we observed partial separation of several ALS cases from other NMA cases in this pilot study. Because this comparison involved a small number of ALS cases and was sensitive to individual samples, we interpret the ALS versus non-ALS NMA findings as exploratory and hypothesis-generating rather than as evidence of validated diagnostic separation.",
    ),
    136: (
        "Discussion diagnostic application: avoid implying immediate diagnostic-workup use.",
        "In future diagnostic studies, DNA methylation parameters could be evaluated together with histopathological hallmarks of skeletal muscle. In this context, it is interesting to note that fiber type grouping due to collateral reinnervation is often rather weak and only detected in approximately half but not all of the muscle biopsies in ALS [1, 32, 60], whereas NMA in peripheral neuropathy often shows a more chronic course with a more pronounced fiber type grouping. Due to the more rapid onset, muscle biopsies in patients with suspected ALS are frequently taken earlier in the course of the disease than in neurogenic atrophy due to polyneuropathy. Furthermore, unaffected motoneurons in peripheral neuropathies (CMT) have been reported to have a better capacity for reinnervation of adjacent denervated muscle fibers than their counterparts in ALS[60]. In fact, muscle reinnervation in ALS can be impaired. These pathophysiological mechanisms may explain why fiber type grouping is not always present in ALS (detected in approximately half of the cases) and often rather mild, an observation shared by others in comparison to other motor neuron diseases or CMT [1, 32, 60]. Histological distinction of ALS-induced NMA compared to CMT could therefore theoretically be aided by additional molecular features, but this requires validation in larger and clinically balanced cohorts.",
    ),
    138: (
        "ALS biology Discussion: remove diagnostic-role phrasing and keep biological interpretation cautious.",
        "In addition to their possible future diagnostic relevance, exploratory epigenetic differences in ALS muscle may support the hypothesis that skeletal muscle cells in ALS are not only passive bystanders that are simply denervated secondary to motor neuron damage. Hence, independent of muscle denervation, muscle differentiation or energy metabolism may be affected cell-autonomously in ALS, reviewed in [55], which could lead to epigenetic alterations as well. In line with our findings, DNA methylation changes have been identified in spinal cord and skeletal muscle of mouse models of ALS and were found to be therapeutic targets [42, 66].",
    ),
    141: (
        "Conclusion: replace entity-specific profile claim with proof-of-principle disease-group-associated evidence.",
        "In conclusion, the present study provides proof-of-principle evidence that non-neoplastic muscle disorders can show disease-group-associated CpG methylation patterns in a selected cohort of well-defined cases. Furthermore, the observed methylation changes reflect the activation of known pathways in muscle disease pathophysiology, including regulation of stemness, Wnt-signaling, inflammation and altered proteostasis.",
    ),
    142: (
        "Limitations: add explicit cohort/confounder/ALS validation caveat.",
        "Even in this small cohort, we observed disease-group-associated DNA methylation patterns. However, for the most part, we cannot differentiate between primary changes in muscle cells and secondary changes such as muscle regeneration, inflammatory infiltrates, fibrosis, biopsy-site differences or other tissue-composition effects. In addition, disease group, sample source, Sentrix ID and clinical variables partly overlap in this retrospective pilot cohort and cannot be fully disentangled. Performance estimates of the supervised learning are based on an internal held-out split and may depend on the specific data partitioning and cohort structure. The ALS versus non-ALS NMA comparison is particularly limited by small sample size and individual-sample influence. Hence, validation in larger, independent cohorts using repeated or nested cross-validation will be needed. Furthermore, the application of this method to larger cohorts, the correlation with clinical features such as disease duration, autoantibody status and treatment responses, as well as the inclusion of less well-defined cases and those with dual pathologies will provide more systematic information on its applicability in diagnostic workup and pathophysiological relevance, including the differentiation between primary and secondary changes in the future.",
    ),
}


def replace_with_highlight(paragraph, text: str) -> None:
    paragraph.clear()
    run = paragraph.add_run(text)
    run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    run.font.name = "Arial"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    run.font.size = Pt(10)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document(BASE_DOCX)
    log_lines = [
        "# Manuscript ALS/NMA and supervised-learning wording changes",
        "",
        f"Base manuscript: `{BASE_DOCX}`",
        f"Output manuscript: `{OUT_DOCX}`",
        "",
        "Changed paragraphs are highlighted in yellow in the generated DOCX.",
        "",
    ]

    for idx, (reason, replacement) in REPLACEMENTS.items():
        old = " ".join(doc.paragraphs[idx].text.split())
        if not old:
            raise ValueError(f"Paragraph {idx} is empty; expected text to replace.")
        replace_with_highlight(doc.paragraphs[idx], replacement)
        log_lines.extend(
            [
                f"## Paragraph {idx}",
                "",
                f"Reason: {reason}",
                "",
                "Old text excerpt:",
                "",
                f"> {old[:800]}{'...' if len(old) > 800 else ''}",
                "",
                "Replacement:",
                "",
                replacement,
                "",
            ]
        )

    doc.save(OUT_DOCX)
    CHANGE_LOG.write_text("\n".join(log_lines), encoding="utf-8")
    print(OUT_DOCX)
    print(CHANGE_LOG)


if __name__ == "__main__":
    main()
