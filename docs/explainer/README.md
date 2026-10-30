# Explainer: predicting functions of uncharacterised human genes from co-essentiality

> This project, including this explainer, was produced by AI agents and has not been verified by a human.

**What it does.** To propose functions for human genes that databases call "uncharacterised", the method takes a gene
list frozen in advance plus DepMap CRISPR knockout screens, and returns for each gene one predicted Gene Ontology (GO)
function, a calibrated probability that curators will later confirm it, and labels that say when not to trust it.

**In three sentences.** Each gene's 25 strongest co-essential partners are found with a published co-essentiality tool
(zavg_BEF), and the GO term carried by the most strongly linked partners becomes the prediction. Genes whose partner
list does not reproduce in two halves of the cell lines are flagged and kept off the shortlist (their prediction is still
written). Confidence is learned from the future:
a calibration model is fitted on 809 genes that were uncharacterised in 2018 and annotated since, after removing
annotations from papers that used DepMap. The top predictions are checked against independent data and, blind, against
the literature with three decoy statements per gene.

![Pipeline: 19,296 genes → 4,924 pre-registered (4,271 scorable) → co-essentiality scores → 646 with usable signal (at least ~322 real) → 4,137 with a top GO term → calibrated on the 2018 hold-out (3.0% vs 0.5% null; max p_cal 0.141) → top 40 of 245 eligible → 18/40 supported by blinded judges vs 3/120 decoys](figures/pipeline.svg)

**The seven steps** (each explained, with its reason and evidence, in [METHOD.md](METHOD.md#steps)):

1. **Pre-register** 4,924 uncharacterised genes from annotation databases and freeze the list by hash before any
   gene–gene score ([Step 1](METHOD.md#step-1)).
2. **Score co-essentiality** with the published zavg_BEF tool, unchanged ([Step 2](METHOD.md#step-2)).
3. **Flag whether the signal is usable:** the top-25 partner list must reproduce in split halves of the cell lines, and
   the gene must be expressed; genes that fail are labelled and cannot enter the shortlist ([Step 3](METHOD.md#step-3)).
4. **Assign a candidate function:** the GO term with the highest summed partner score and at least 2 supporting partners,
   after removing same-chromosome-arm genes and paralogues ([Step 4](METHOD.md#step-4)).
5. **Calibrate confidence** on genes annotated after 2018, with DepMap-citing annotations removed, to get p_cal
   ([Step 5](METHOD.md#step-5)).
6. **Add orthogonal evidence and prioritise:** rank by p_cal; independent data and robustness checks become labels
   ([Step 6](METHOD.md#step-6)).
7. **Check the literature blind:** two judges, redacted evidence, three decoys per gene ([Step 7](METHOD.md#step-7)).

**Key results.**
- 646 of 4,924 genes (13%) pass the usable-signal rule; allowing for false passes, at least ~322 (6.5%) carry real
  signal *[post-review estimate, untested assumption]*.
- On 809 genes annotated after 2018, the top term was right for **3.0%** (95% CI 1.8–4.3%), against 0.5% for matched
  genes: the pre-registered test passes. It is no better than GLS, the older corrected-correlation score of Wainberg 2021 (2.3%), and far below homology (21.8%);
  it reaches 11.7% in the strongest-signal fifth of genes.
- The highest calibrated probability is 0.141, so no gene reached the pre-set tiers. About 4.9 (2.2–8.1) top terms are
  expected to be confirmed among 2,583 calibrated genes, but about 82% of that comes from genes that fail the
  usable-signal rule; for the 269 assessable genes it is about 0.9 *[derived for this explainer]*.
- Blinded judges supported 18 of the top 40 predictions against 3 of 120 decoys (p = 0.0002), but 31 of the 40 genes
  already had a published function, and 34 had a link in earlier catalogues.

**Limitations.**
- "Uncharacterised" in databases often means "uncurated": 42% of a random 50 already had a published function.
- The probability is thin and conditional: it rests on 24 correct hold-out calls and applies only to genes that get
  annotated at all.
- Nothing was tested at the bench or checked by a human; about 87% of the pre-registered genes have no usable signal
  (their predictions are written but flagged).

## The documents

| File | What it is |
|---|---|
| [METHOD.md](METHOD.md) | The method in full: why each step exists, a worked example, pseudocode, results, limitations, glossary |
| [JOURNEY.md](JOURNEY.md) | How we got here: the eight turning points that shaped the method, with a timeline |
| [INSIGHTS.md](INSIGHTS.md) | What the project learned, for biologists and for methodologists |
| [DISCREPANCIES.md](DISCREPANCIES.md) | Where project documents disagree with each other or with the code and results, and what this explainer uses |
| [explainer.html](explainer.html) | METHOD, JOURNEY and INSIGHTS as one interactive page (clickable pipeline, timeline, step-by-step worked example). **Download it and open it in a browser**; GitHub shows only its source. It is self-contained and makes no network requests. |
| [worked_example_notes.md](worked_example_notes.md) | The worked example in full detail: ANKRD52 through the pipeline and the TMEM242 hold-out control, with a 159-value reproduction check |
| [worked_example.py](worked_example.py), [worked_example_output/](worked_example_output/) | The script that recomputes the worked example from the pipeline's own functions, and its tables |

To rebuild the HTML page after editing the Markdown: `./.env/bin/python -I docs/explainer/build_html.py` (needs only the
project environment). The timeline figure is drawn by [journey_figure.py](journey_figure.py) from
[journey_data.json](journey_data.json).
