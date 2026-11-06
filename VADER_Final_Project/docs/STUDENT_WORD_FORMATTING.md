# Formatting the returned student manuscript

On 5 November 2026 the student returned an edited Word manuscript and explicitly
requested that its existing wording remain unchanged. The current formatted
Word copy and ACL PDF preserve that wording except for the later sentence and
citation corrections expressly requested by the student. All eight tables and
four figures remain unchanged. The 17 returned references are preserved, and the
missing original COMP8240 criteria reference was restored for its existing
in-text citation, giving 18 entries.

Formatting changes include consistent Word styles, table and caption layout,
restored native footnote anchors and definitions, restored missing mathematical
notation, and the two-column ACL PDF layout. The two existing display equations
were retained. Missing inline notation, intensity endpoints and confidence
intervals were recovered from the previous manuscript and existing results.
No experiment was rerun or its values changed for this formatting task.

The compiled PDF has ten main-body pages, one reference page and one appendix
page. Figure 4 and its unchanged caption appear in the appendix so the complete
prose fits the brief's ten-page main-body maximum. The editable Word copy keeps
the figures near their original discussion. Its existing Figure 3 caption was
paired below its image.

`FORMAT_PRESERVATION_CHECK.json` records the input digest and the exact allowed
restorations. Existing paragraph words, table cells, references and image bytes
were checked against the uploaded file. The source before the student's rewrite
is retained as `report/prior_review_manuscript.tex`.

This is a formatting pass, not approval of the rewritten scientific claims.
Some rewritten sentences alter the meaning of the earlier evidence, including
the claim of complete data independence despite overlap and the abstract's
full-replication claim. Those sentences remain unchanged under the student's
wording constraint. At the student's subsequent request, the specific sentence
about invented ratings was corrected to: "No human ratings, consent records, or
annotation agreement statistics have been fabricated." A malformed 2014 citation
was repaired and all 18 in-text citations now link to their matching reference
entries in both Word and PDF. `CITATION_LINK_CHECKS.json` records the exact changes
and verifies the destinations. The experimental results and the pending
human-annotation status in the source package remain authoritative.

Actual independent annotation and a verified public GitHub URL are still
outstanding. No ratings, consent records, repository publication or iLearn
submission was invented or performed during this formatting task.
