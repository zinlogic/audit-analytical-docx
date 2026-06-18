---
name: audit-analytical-docx
description: Audit analytical data integrity between DOCX result tables and DOCX chromatogram reports using the bundled deterministic Python script. Use when Codex needs to run, explain, validate, or maintain the `main_v1.py`-style workflow that compares tabla/resumen files against cromatograma/detalle files, generates Markdown reports and PDF artifacts when the PDF dependency is available, or investigates inconsistencies in analytical chemistry sequence reports.
---

# Audit Analytical DOCX

## Overview

Use this skill to audit analytical `.docx` reports by comparing a result table (`tabla`/`resumen`) against a chromatogram detail report (`cromatograma`/`detalle`). Prefer the bundled deterministic script over LLM-based comparison when the user asks for reproducible validation, report generation, or field-level inconsistency detection.

The bundled script mirrors the project workflow from `main_v1.py`: extract structured data from both DOCX files, compare the configured fields sample by sample, tolerate equivalent numeric formats, and write a Markdown report plus a PDF only when `markdown_pdf` is installed and the PDF file is actually created. By default, reports are saved next to the input DOCX files, using the table file directory.

PDF generation applies bundled table CSS so correspondence tables align flush left, use predictable cell padding, and avoid renderer-default indentation before the first column.

Important artifact rule: never assume the `.pdf` exists just because the script prints a PDF path. After every run, verify the generated files on disk. If the PDF is missing, say so plainly and ask before creating a replacement PDF from the Markdown, unless the user has explicitly asked to generate one.

## Quick Start

Run the bundled script from the skill folder or by absolute path:

```bash
python C:/Users/ingar/.codex/skills/audit-analytical-docx/scripts/main_v1.py --tabla "datos/Tabla Secuencia 4-EZPC.docx" --cromatograma "datos/Cromatogramas Secuencia 4-EZPC.docx"
```

### Runner (venv primero)

In real projects, prefer running the script with the project's virtualenv interpreter so dependencies are already available. On Windows this is typically one of:

```bash
<repo>\.venv\Scripts\python.exe  C:/Users/ingar/.codex/skills/audit-analytical-docx/scripts/main_v1.py ...
<repo>\.venv_win\Scripts\python.exe  C:/Users/ingar/.codex/skills/audit-analytical-docx/scripts/main_v1.py ...
```

If the user environment cannot install packages over the network (common TLS/cert issues), do NOT default to `pip install` globally; instead switch to the project's venv (or any known-good Python runtime that already has `python-docx`).

Use `--output` when the user wants a specific report path:

```bash
python C:/Users/ingar/.codex/skills/audit-analytical-docx/scripts/main_v1.py --tabla "datos/Tabla Secuencia 4-EZPC.docx" --cromatograma "datos/Cromatogramas Secuencia 4-EZPC.docx" --output "out_json/reporte_auditoria_v1_Secuencia 4-EZPC.md"
```

If `--output` is omitted, the script writes `reporte_auditoria_v1_<suffix>.md` in the same directory as the table DOCX and attempts to create the matching `.pdf` there. Use `--output` only when the user wants a different Markdown destination; the PDF is always created beside that Markdown path.

## Workflow

1. Confirm the user provided or implied both DOCX inputs:
   - Tabla/resumen: analytical result table.
   - Cromatograma/detalle: chromatogram detail report.
2. Choose the Python runner:
   - Prefer the project's venv interpreter (it usually already has `python-docx` and any pinned deps).
   - Only if no venv is available, fall back to another known-good Python runtime with `python-docx` installed.
3. Run `scripts/main_v1.py` with `--tabla` and `--cromatograma`; omit `--output` for normal analysis so artifacts are saved beside the DOCX files.
4. If you hit `ModuleNotFoundError: No module named 'docx'`, it means `python-docx` is missing in the selected interpreter. Prefer switching to the project's venv rather than attempting a global `pip install` in restricted environments. If only `markdown-pdf` is missing, the PDF artifact cannot be produced by the bundled script; do not inject fake modules or imply a PDF was generated.
5. Read the generated Markdown report before summarizing results to the user.
6. If the user asks to keep/export/save the report elsewhere, rerun with `--output` pointing to the requested Markdown destination or copy only the artifacts that actually exist. For a requested PDF, first verify the source `.pdf` with a filesystem check; if it is absent, explain that only the Markdown exists and ask whether to generate a PDF conversion.
7. Report the high-level result: total samples, samples without errors, samples with errors, and notable inconsistencies. Mention report paths when useful.

## Comparison Rules

The script compares each table sample with the corresponding chromatogram sample by extraction order. It audits:

- `Sample Name`
- `Sample Type`
- `Acquisition Date`
- `Area (cps)`
- `IS Area (cps)`
- `RT (min)`
- `Calculated Conc. (ng/mL)`
- `Acquisition Method`
- `Project`
- `Instrument`

Comparison behavior:

- Exact text matches pass.
- Numeric values are converted to floats when exact text differs.
- Numeric values pass when `math.isclose(..., rel_tol=1e-4)` is true, which avoids false errors for decimal vs scientific notation.
- Differences are listed with sample ID, sample name, field, table value, and chromatogram value.

## Maintenance

When the source project improves `main_v1.py`, update the skill deliberately:

- If only internal implementation changes and the CLI remains compatible, replace `scripts/main_v1.py`.
- If extractor behavior changes, also replace `scripts/extractors.py`.
- If new imports or dependencies are added, update this SKILL.md dependency note and validate the script.
- If arguments, temporary-output behavior, comparison fields, or report structure change, update this SKILL.md so future Codex runs call the script correctly.

After updating the skill, run:

```bash
python C:/Users/ingar/.codex/skills/.system/skill-creator/scripts/quick_validate.py C:/Users/ingar/.codex/skills/audit-analytical-docx
```

Then run the audit on a known pair of DOCX files to verify the script still works end to end.
