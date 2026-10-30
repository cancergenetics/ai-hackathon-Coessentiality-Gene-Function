# Prompts used for the agent-only (non-scriptable) steps

Verbatim task prompts given by the PI agent to sub-agents for the blinded / judgement steps (2026-10-29 to 2026-10-31).
Batch-specific file names are shown as `<batch>`; otherwise the text is exactly as issued. Models: recall probes and the
adjudicator ran on Claude Opus 5.5; literature agents L and judges J1/J2 on Claude Sonnet 5.5; red-team reviewers and
report writers on Claude Opus 5.5. Outputs: `results/audit/`, `results/m7/`, `reports/`, `reports/redteam/`.

## Closed-book recall probe (results/audit/recall_probe_random50.tsv; results/m7/recall_probe_90.tsv)

> You are the closed-book recall probe (role "probe"). Use NO tools except: (1) Read the single file
> `<project>/results/m7/probe_list.tsv`, and (2) Write your answer to `<project>/results/m7/recall_probe_90.tsv`. Do not
> search the web, read any other file, or run commands. For each gene (symbol, previous symbols and aliases only), state
> from memory what you believe its molecular/cellular function is (name complexes/pathways if you know them), or
> "unknown". Columns: hgnc_id, symbol, recalled_function (one sentence or "unknown"), confidence (none/low/medium/high),
> recognised (yes if medium/high, else no). Be honest — "unknown" is fine.

## Literature agent L (blind; results/m7/L/)

> You are literature agent L (blind role). You may read ONLY: `results/m7/L_batches/<batch>` (list of 20 packet
> filenames) and the corresponding files in `results/m7/gene_packets/` (each: hgnc_id, symbol, previous symbols,
> aliases, UniProt, cytoband). You must NOT read any other project file (in particular nothing under results/ledger/,
> results/m7/statements.tsv, results/m7/answer_key*, results/m7/s20.tsv, top40*, extra30, hval10, data/, or external/) —
> you must stay blind to any computational prediction about these genes. Write only `results/m7/L/<HGNC_xxxx>.md` (one
> per gene) and append one line per gene to `results/m7/L/index_<batch>.tsv`.
> For each gene: search the literature with WebSearch/WebFetch and the Europe PMC REST API (incl. preprints) and UniProt
> REST, using the current symbol, ALL previous symbols and aliases, and the UniProt accession. Watch for symbol
> collisions and exclude them. Write a structured evidence list: each item = claim, source (PMID/DOI/UniProt), year,
> VERBATIM supporting sentence copied from the retrieved text, evidence level (functional / high-throughput / mention),
> and DepMap-derived (yes/no). Then assign a novelty class: N1 = function established by focused experimental work;
> N2 = partial/indirect; N3 = no functional literature. Cite ONLY sources you actually retrieved; never rely on memory.

## Judges J1 and J2 (blind; results/m7/judge/scores/)

> You are blinded judge J1 [J2] (role "judge"). Read ONLY: `results/m7/judge/batches/<batch>.txt` and the packet files
> it lists in `results/m7/judge/packets/`. Do not read any other file, do not search the web, do not use background
> knowledge about genes — judge only from each packet's evidence, following the instructions inside each packet
> exactly. Write ONE file: `results/m7/judge/scores/J1_<batch>.tsv` with header packet_id, slot, score, justification
> (4 rows per packet; score ∈ {1,0,-1}).

Instruction header inside every packet (verbatim):

> You are judging whether published literature supports four candidate statements about an anonymised human gene
> (GENE_X). Use ONLY the evidence listed below — do not use your own background knowledge and do not search. For each
> statement A–D, score +1 if the evidence directly supports the statement (the gene is reported to function in the
> stated process or module, or a closely equivalent one), −1 if the evidence contradicts it (the gene is shown to
> function in an incompatible process/compartment), and 0 if the evidence does not address it. Evidence flagged
> DepMap-derived = yes must be ignored (treat as absent). Give one line of justification per statement citing the
> evidence row(s). Output a 4-row table: slot | score | justification.

## Adjudicator (blind)

> You are the blinded adjudicator (role "judge", third judge). Read ONLY `results/m7/judge/disagreements.tsv` (3 rows:
> batch, packet_id, slot, two judges' scores and justifications) and the packet files named there. Read no other file,
> do not search the web, do not use background knowledge. For each row, decide the final score (+1/0/−1) for that slot
> using the packet's instructions and evidence only.

## Red-team reviewers (reports/redteam/)

> You are an adversarial red-team reviewer (role "red_team") of two candidate reports: reports/<A>.md and
> reports/<B>.md. You did not write them. You may read: the reports, reports/data/<GENE>/bundle.md and figures,
> results/m7/L/ files, results/ledger/, results/holdout_eval/SUMMARY.md, DESIGN.md, DEVIATIONS.md, and use Europe
> PMC/Crossref/UniProt/WebSearch to check claims. Do NOT edit the reports. For each report: (1) Spot-check ≥ 10 ledger
> entries: does the PMID/DOI exist, does the verbatim span appear in that source, does it support the claim as worded?
> (2) Check every number against the project files it cites. (3) Attack the hypothesis: strongest alternative
> explanations, overclaiming, missing key literature, weak or non-falsifiable experiments, wrong cell-line choices.
> (4) Verdict: ACCEPT / ACCEPT WITH REVISIONS (concrete fixes) / REJECT.

(Each red-team prompt also listed gene-specific points to check; see reports/redteam/<GENE>.md for what was examined.)

## Curation-lag auditor (results/audit/curation_lag_audit.*)

> You are a literature auditor (role "audit"). Read ONLY: DESIGN.md §1.5 and §6.3 (classes),
> results/audit/random50_U_sample.tsv. You must NOT read anything under data/derived/, results/ other than that sample
> file, or external/ — you must have no access to any co-essentiality output. For each of the 50 genes, search the
> literature (PubMed, Europe PMC incl. preprints/bioRxiv, UniProt entry text) using current symbol, ALL previous
> symbols and aliases, and the UniProt accession. Classify: N1 / N2 / N3. Cite only papers you actually retrieved, with
> PMID/DOI and a verbatim supporting sentence.
