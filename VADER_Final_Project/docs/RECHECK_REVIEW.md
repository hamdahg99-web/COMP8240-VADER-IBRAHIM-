# Recheck of Assessment 3

Reviewed on 4 November 2026 against the supplied six-page final-report brief,
its 40-mark rubric, the current report, source package and observed results.

## Verified evidence

- Independently recomputed accuracy and macro-F1 from all 4,320 saved DynaSent
  prediction records. All four implementation/split results agree with the JSON
  summaries to numerical precision.
- Reran the original/new-data pipeline and existing integrity checks successfully.
- The original archive and model resource SHA-256 checks pass.
- The previous source ZIP passes its archive CRC and recorded file checksums.
- The two independent human sheets each still contain 0 of 288 sentiment labels.
- The report explicitly distinguishes constructed drafting hypotheses and
  within-session assistant judgements from human reference measurements.
- A direct original-dataset URL footnote was added.
- Removed the ambiguous original-only `run-metadata.json` duplicate; kept named
  original-stage and final-stage metadata.
- Added the constructed judge versus resolved human-reference scoring path for
  use after actual annotation. Constant-vector correlations are reported as
  undefined rather than causing invalid JSON or being called zero correlation.

## Rubric review

| Component | Marks | Current assessment |
|---|---:|---|
| Paper description and justification | 4 | Present, including original evaluation, venue and source feasibility. |
| Original datasets | 4 | Counts, record format, example and direct source URL supplied. |
| Original replication | 8 | Observed results, environment, version comparison and protocol sensitivity supplied. Exact reconstruction remains partial and is disclosed. |
| Construction of new data | 4 | The 288-text corpus and fixed family split exist; actual annotation procedure remains incomplete. |
| Results on new data | 6 | DynaSent results are complete. Constructed human-reference results and judge-versus-human comparison remain pending. |
| Ethics | 4 | Discussed; new annotation consent and dates still require actual participation. |
| Code | 3 | Local checks pass; the public project repository and report URL remain unverified. |
| New-data quality | 3 | Synthetic text checks are complete; independent human validation is missing. |
| Presentation | 4 | An ACL LaTeX PDF and an editable Word review copy are prepared. Final submission must follow the required LaTeX/PDF format. |

This is an evidence checklist, not a mark prediction. No HD or other grade is
guaranteed or assigned by this review.

## Remaining material issues

1. Collect real independent ratings, compute agreement before adjudication, resolve
   or retain ambiguities, and incorporate the resulting human-reference evidence.
2. Publish the project in a publicly accessible GitHub repository, verify access,
   and put its actual URL in the report footnote.
3. The Overall Goal and Assessment Criteria page has now been supplied and
   reviewed. Its novel route depends on independent selection/justification of
   paper, code and original data, with a newly created dataset. It does not state
   a first-ever-use requirement for each existing benchmark. The unsupported
   DynaSent eligibility blocker has been removed; prior use is still acknowledged.
4. The judge is a within-session assistant pilot. Its exact model snapshot and
   decoding settings were unavailable, and constructed-data authorship was shared.
   A separately versioned independent judge run would strengthen reproducibility.
5. The student must read and verify the cited sources and the submitted report,
   as the brief states for generative AI use.

The Word copy is an editing/review copy. It does not convert a Word submission
into the required compiled ACL LaTeX PDF or complete the missing experiments.

## Alignment update after receiving the overall criteria

The current Word manuscript adds an explicit unit-tools subsection and four
observed original-corpus examples. A post-hoc initial-capital/lowercase probe for
original item 431 is preserved separately and excluded from aggregate metrics.
The previous compiled PDF is a prior review snapshot. The student will edit the
Word manuscript and return it before the final ACL PDF is rebuilt.
