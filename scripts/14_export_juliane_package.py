from pathlib import Path
import shutil
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
FINAL = PROJECT / "manuscripts" / "reviewer_round_2" / "final_drafts"
EXPORT = PROJECT / "manuscripts" / "reviewer_round_2" / "to_Juliane_2026-07-13"
ZIP = EXPORT.with_suffix(".zip")

if EXPORT.exists():
    shutil.rmtree(EXPORT)
EXPORT.mkdir(parents=True)
(EXPORT / "figures_review_pdf").mkdir()

files = {
    FINAL / "reports" / "juliane_revision.html":
        EXPORT / "01_Juliane_revision_report.html",
    FINAL / "Bremer_manuscript_reviewer_round_2_clean_draft.docx":
        EXPORT / "02_Bremer_manuscript_revision_draft.docx",
    FINAL / "Point_by_point_rebuttal_draft.docx":
        EXPORT / "03_Point_by_point_rebuttal_draft.docx",
    FINAL / "tables" / "Reviewer_round_2_analysis_tables.xlsx":
        EXPORT / "04_Reviewer_round_2_analysis_tables.xlsx",
    FINAL / "Figure_revision_map.md":
        EXPORT / "05_Figure_revision_map.md",
    FINAL / "Email_to_Juliane_draft.txt":
        EXPORT / "06_Email_text.txt",
}

for source, destination in files.items():
    if not source.exists():
        raise FileNotFoundError(source)
    shutil.copy2(source, destination)

for source in sorted((FINAL / "figures_main").glob("*.pdf")):
    shutil.copy2(source, EXPORT / "figures_review_pdf" / source.name)

readme = """REVIEWER-ROUND REVISION PACKAGE FOR JULIANE

Recommended reading order
1. Open 01_Juliane_revision_report.html in a browser. It is self-contained and works offline.
2. Review the yellow decision items in 02_Bremer_manuscript_revision_draft.docx.
3. Review 03_Point_by_point_rebuttal_draft.docx after supplying the missing clinical/pathology facts.
4. Use 05_Figure_revision_map.md together with figures_review_pdf/ to approve the figure changes.

Status
- All currently feasible bioinformatic analyses are complete.
- All 73 samples (72 patients) were retained; disease-group assignments were not changed.
- The manuscript and rebuttal remain drafts until Juliane supplies the clinical/pathology details listed in the report.
- PDF figures are included for convenient review. Publication TIFF files remain in the project workspace and are intentionally excluded from this email-sized package.
- Raw methylation data and large intermediate files are not included.

The proposed email body is saved as 06_Email_text.txt and should be pasted into the email rather than attached.
"""
(EXPORT / "00_README.txt").write_text(readme, encoding="utf-8")

if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(EXPORT.rglob("*")):
        if path.is_file():
            archive.write(path, Path(EXPORT.name) / path.relative_to(EXPORT))

with zipfile.ZipFile(ZIP) as archive:
    bad = archive.testzip()
    if bad is not None:
        raise RuntimeError(f"Corrupt ZIP member: {bad}")

print(EXPORT)
print(ZIP)
