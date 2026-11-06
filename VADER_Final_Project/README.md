# Reproducing VADER and testing sentiment robustness

COMP8240 Assessment 3 project package. This extends the submitted Assessment 2
notebook with pinned-source replication, a protocol audit, DynaSent test results,
288 AI-assisted authored diagnostic texts, an exploratory assistant-judge pilot,
figures, and an ACL LaTeX report.

**Status:** computational experiments are complete. Independent human annotation
of the constructed dataset is pending. The report is a review draft and must not
be represented as having human validation. A public GitHub URL must be verified
and inserted before final submission. No iLearn submission has been made.

The student returned an edited manuscript on 5 November 2026 and requested a
formatting-only pass. The current files are
`report/COMP8240_Assessment3_Formatted.docx` and `report/main.pdf` (compiled ACL
LaTeX). The PDF has ten main-body pages, one reference page and one appendix page.
The student subsequently requested correction of the sentence about fabricated
ratings and restoration of clickable in-text citations. That sentence and
citation formatting were corrected, and the missing original course-criteria
reference was restored. All other student wording was retained, including wording
that differs from the experimental evidence. Read `docs/STUDENT_WORD_FORMATTING.md` before treating
that manuscript as scientifically checked. The previous review source remains
in `report/prior_review_manuscript.tex`.

## Reproduce

Tested with Python 3.12.14 on Linux, CPU only. No VADER training is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/run_experiments.py
python src/evaluate_judge.py
python src/make_figures.py
python src/check_project.py
```

To reproduce the added original-data examples and case probe, run
`python src/inspect_original_examples.py` using the same cached author resources.

The authored data and blank rating files already exist. To reconstruct them,
`python src/build_constructed.py` regenerates the exact 288 texts. **That command
overwrites rating templates: do not run it over completed human annotations.**
The experiment runner never rewrites annotation sheets or LLM response files.

The first experiment run downloads the original author archive and maintained
code at commit `44fc044cd877310ee8278a0eadf34bcd50d41d06`, and DynaSent v1.1
at commit `707b6208978bfe7ff251a0c3263c9f0552c27b48`. Checksums are enforced.
Downloaded third-party text remains in `.cache/`, which is excluded from Git.
Public results contain IDs, gold labels and scores rather than complete source
corpora. Follow each upstream resource's terms before reuse.

## Contents

- `src/`: readable evaluation and validation scripts.
- `vendor/`: the supplied notebook's compatibility port and helper, with MIT notice.
- `data/constructed.csv`: all 48 sentence families, six variants each.
- `annotations/`: two genuinely blank independent rating sheets, guidelines,
  preserved assistant judge inputs/responses and explicit provenance metadata.
- `results/`: observed numeric outputs and machine-readable run metadata.
- `figures/`: vector PDF figures and PNG previews, generated from the outputs.
- `report/`: formatted student Word copy, compiled ACL PDF, ACL style files,
  supporting bibliography, generated tables and current LaTeX source. The current
  manuscript preserves the student's 17 reference entries and the restored
  original course-criteria reference directly in LaTeX.
- `notebooks/COMP8240_VADER_Final.ipynb`: a transparent notebook entry point.
- `docs/`: experiment protocol, limitations and submission checklist.

## Human annotation

Give each real volunteer only their own split-specific CSVs and the guidelines.
Use development sheets for a pilot before the held-out sheets. Record actual
consent and dates privately. Combine that reader's completed development and test
files into `annotator_A.csv` or `annotator_B.csv` without changing item IDs/text.

```bash
python src/merge_annotations.py
python src/evaluate_human.py
# Once human adjudication is complete, compare the preserved judge with human labels.
python src/evaluate_judge.py
# On the first complete run, fill the generated adjudication.csv for disagreements.
python src/evaluate_human.py
```

Exit code 2 with a PENDING message is intentional while ratings are blank. The
script does not generate kappa, human accuracy or human reference labels from
design tones, VADER output, or LLM output. Once actual human results are available,
update the corresponding report subsections and remove the review-draft notice
only when the remaining checklist items are resolved.

## Assistant judge provenance

The judge pilot is an actual set of textual judgements supplied by the same
ChatGPT/Codex assistant during this project. It is **not** a separate API run,
independent model replication, or a human rater. The interface did not expose an
exact model snapshot, temperature or decoding seed. Preserved responses can be
rescored exactly; identical regeneration from a closed model is not guaranteed.
On constructed texts the judge also participated in authorship. Its agreement
with VADER is model-to-model agreement, not measured human correctness.

## Compile the report

```bash
python src/export_report_tables.py
cd report
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Install a TeX distribution with ACL's standard dependencies (TeX Live is suitable).
In Overleaf, upload the `report/` directory together with `figures/` as sibling
directories, and set `report/main.tex` as the main document.

## Important scientific limits

Tweet-like and editorial correlation reproduce to the paper's three decimal
places. Movie and product correlations do not. Original F1 reconstruction remains
protocol-sensitive. DynaSent has appeared in previous work using VADER, so this
project does not claim a first-ever VADER application to DynaSent. The controlled
corpus is new, synthetic and AI-assisted. Its independent human validation is
an unfinished dependency, not a completed result.

Use `docs/SUBMISSION_CHECKLIST.md` before submitting. Read and verify the cited
sources and the final text, as required by the assessment's open-AI policy.
