# Evaluation protocol and provenance

1. Archived VADER is the primary replication implementation. The compatibility
   port comes unchanged from the supplied Assessment 2 notebook; its SHA-256 is
   verified by the original helper. Python 2 syntax was converted for Python 3;
   the archived lexicon uses Latin-1 decoding. Maintained VADER is a comparison.
2. Pearson r compares compound scores with the released sentence-level mean
   intensity. It is unaffected by a positive linear rescaling of the human mean.
3. Primary original-data classification is explicitly provisional: human mean/4,
   thresholds -0.05 and +0.05, macro-F1 over negative/neutral/positive with
   zero_division=0. Raw-mean and VADER-normalised human-score alternatives are
   diagnostic sensitivity analyses, not threshold search or a recovered protocol.
4. DynaSent official Round 1 and Round 2 test splits are used without fitting or
   threshold selection. Only Unicode whitespace is normalised. Case, negation,
   punctuation and all words are retained. All released labels in the two test
   splits are valid three-class labels. Class order is negative, neutral, positive.
5. The constructed corpus was AI-assisted authored on 2026-11-04. The family
   split was fixed in code before prediction. It has 12 development families and
   36 held-out families. Design tones are hypotheses rather than gold labels.
6. Bootstrap intervals use 2,000 paired resamples and seed 8240. Benchmark
   intervals resample sentences; eventual constructed human intervals resample
   families. Uncertainty concerns these datasets, not all English language use.
7. The assistant judged 60 DynaSent texts (20 per class) without gold labels in
   the input file and 60 constructed texts from 10 held-out families. The same
   conversation context and authorship make this exploratory, not an independent
   blind trial. No human rater was simulated.
8. The DynaSent eligibility check found prior published VADER use. See Wang et al.
   (2026), doi:10.3390/electronics15184230. This updates the proposal's provisional
   novelty claim. DynaSent is presented as transfer evidence, not a first use.
9. No LLM output was used to alter released human labels, set VADER thresholds,
   invent missing human ratings, or retroactively remove difficult items.

The dataset generator encodes drafting expectations. Numerical diagnostic
checks against these expectations describe model behaviour; they must not be
called human validation or held-out accuracy.
