# Research documents

Everything written about IntelliERP: the two papers, the final-year project report, the poster and the
working notes. The results they report come from `LLM/evaluation/results/`.

| Folder | What it is | Main file |
|---|---|---|
| [`journal/`](journal/) | Journal article (IEEE journal format): TRACE and its full evaluation. **Submit this first.** | `trace.tex`, `references.bib` |
| [`paper/`](paper/) | Conference paper (IEEE conference format): the system, grounding and the pattern-based verifier. The backup if the journal does not accept. | `intellierp.tex`, `references.bib`, `intellierp.pdf` |
| [`report/`](report/) | Final-year project report for INTI (Word), built from JavaScript sources | `src/*.js` (one file per chapter), `build.js` |
| [`poster/`](poster/) | A1 poster for the project presentation | `build.js` |
| [`notes/`](notes/) | Working notes: literature review, research plan, annotation guide, reviewer questions, demo script | see below |

## Building everything

```bash
bash Research/build-all.sh
```

This rebuilds both papers, the report (.docx and .pdf) and the poster, and copies them to
`~/Documents/IntelliERP/`:

```
~/Documents/IntelliERP/
├── 1-Final-Submission/   IntelliERP-FYP-Report.docx / .pdf, IntelliERP-FYP-Poster.pdf / .png
├── 2-Publication/        IntelliERP-Journal-Paper.pdf / .docx, IntelliERP-Conference-Paper.pdf / .docx
└── 3-Notes/              earlier notes and plans (not built from here)
```

Each part can also be built on its own:

| Document | Command |
|---|---|
| Journal or conference paper | in `journal/` or `paper/`: `pdflatex`, `bibtex`, then `pdflatex` twice (or upload the folder to Overleaf) |
| Report | in `report/`: `npm install` (once), `node make-figures.js`, `node render.js`, `node build.js` |
| Poster | in `poster/`: `node build.js` (uses `report/node_modules`) |
| Word versions of the papers | `node Research/word/build-docx.js` (compiles the LaTeX first, so numbers and references match the PDFs) |

Personal cover details (student ID, passport number) are read from `report/src/meta.local.js`, which is
not committed. The INTI logo for the poster (`poster/inti-mark.png`) is not committed either.

## Notes

| File | Contents |
|---|---|
| [`notes/literature-review.md`](notes/literature-review.md) | 61 verified papers, with what each means for this project; both `references.bib` files are checked against it |
| [`notes/journal-research-plan.md`](notes/journal-research-plan.md) | The plan (22 October 2026) that turned the system into the TRACE study |
| [`notes/annotation-guide.md`](notes/annotation-guide.md) | The rules the natural-error labels follow |
| [`notes/reviewer-questions.md`](notes/reviewer-questions.md) | A pre-review of the conference paper, and questions to expect in the viva |
| [`notes/demo-script.md`](notes/demo-script.md) | A five-minute demo for the viva or a screen recording |
