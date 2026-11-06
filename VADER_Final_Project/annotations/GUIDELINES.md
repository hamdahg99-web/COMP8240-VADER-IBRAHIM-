# Independent human annotation

These sheets require real human readers. They contain no pre-filled ratings.
An AI assistant must not fill them while claiming to be a human annotator.

## Before rating

Two English-reading adult volunteers should each rate their own file, A or B.
Record consent, annotation date, English-reading background and an anonymous
annotator code separately in `annotation_metadata.json`. Do not publish names,
contact details or other identifying information. Participation is voluntary.
Do not view VADER predictions, family names, drafting intentions or the other
reader's ratings. Complete the development items before the remaining items;
the coordinator can provide the split-specific files if needed. Freeze the
guidelines after the development pilot and preserve the original independent
ratings before discussing disagreements.

## Fields

- `sentiment`: exactly `negative`, `neutral` or `positive`. Judge the overall
  sentiment conveyed, not whether an event is factually good or bad for you.
- `intensity`: integer from -4 (extremely negative) through 0 (neutral) to
  +4 (extremely positive). Mild sentiment can be -1 or +1. Keep the sign
  consistent with the chosen class, using 0 for neutral.
- `confidence`: `low`, `medium` or `high`.
- `notes`: optional short explanation, particularly for mixed or ambiguous text.

Examples for practice, excluded from the dataset:

| Sentence | Example class | Example intensity |
|---|---|---|
| I love this quiet garden. | positive | 3 |
| The office is on the second floor. | neutral | 0 |
| The experience was disappointing. | negative | -2 |

Negation can weaken or reverse sentiment, but does not always do so. Capitals
and punctuation can change intensity without changing the class. For contrasting
clauses, judge the full sentence; do not apply an automatic rule for the word
"but". Write low confidence and a note when there is no clear overall reading.

## After independent rating

Run `python src/evaluate_human.py` to validate ratings and obtain raw agreement,
Cohen's kappa, confusion matrices and an adjudication worksheet. Discuss each
disagreement only after the independent files are frozen. Enter the agreed
class in `adjudication.csv`; use `ambiguous` if no agreement is reached. Never
force an unresolved case into a class merely to improve model performance.

The evaluation uses the held-out 216 texts for final class metrics and resamples
families, not individual related variants, for uncertainty intervals. Average
the two independently supplied intensity scores for correlation analysis.
The script records exclusions and will not label missing ratings as neutral.
