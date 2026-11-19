# Circuit design review, 18 November 2026

A review of 28 KiCad circuits of the lab (Supertime clock multiplexer and external trigger, digital buffer
evaluation boards, lattice intensity lock boards, bias coil drivers, summing circuits, filters and others).

- `circuits_merged.json`: per circuit, a plain description, its status (finished, superseded, unfinished),
  the design issues found with the evidence (net names, reference designators, pin numbers) and suggested fixes,
  unknown parts and open questions.
- `REVIEW_BRIEF.md`: the instructions the review followed.
- `work/mk*.py`, `tools/merge.py`: the scripts that assembled the review data.

**How to read it.** The review was done with an AI assistant from the schematics, netlists and ERC/DRC reports.
Nothing in it was checked on the bench. Treat each issue as a pointer to look at, with the confidence it states,
not as a verified defect. Several of the reviewed projects are not in this repository yet.

The parsing helpers it used are in `tools/review/` (KiCad s-expression parser, net and board summaries, net tracing).
