# Pre-review of the IntelliERP paper

A critical reading of `intellierp.tex` as a conference reviewer would make it, done before showing it to the
guide. Each point gives the likely objection, where the paper already answers it, and what to say or change.
The last section lists questions to expect in a viva.

## Likely reviewer objections

**1. "The questions were written by the authors, so 86 of 86 says little."**
Already admitted in Limitations. Answer: the keys are computed from the data at run time, not typed in;
the five E1 failures show the questions can catch real faults; the grounding ablation (32 vs 8-9) is a
comparison on the same questions, so author bias affects both arms. Improvement if time allows: ask two
classmates to write 20 questions each without seeing the system's tools.

**2. "The claim verifier is a set of regular expressions. Where is the novelty?"**
The novelty is not the matching technique but where the check sits and what it checks against: the ERP's
own facts at run time, with a correction loop and different handling for chats, recommendations, insights
and drafts. Related work either asks the model to check itself (Self-RAG, CoVe), uses an LLM as judge
(RAGAs), or checks only direction in one case study (Xue et al.). Say this sharply in the introduction if a
reviewer asks; the paper's sentence "deterministic and run against the system's own data" carries it.

**3. "Errors were injected by a model; real errors may look different."**
Admitted. The two natural errors found (U11) were both caught, but two is too few to measure. A future
experiment: collect the assistant's own wrong answers over more runs and test on those.

**4. "Scope was decided by the authors after seeing which errors were missed."**
The strongest objection. Mitigations already in place: every classification is published
(`test-v2-review.md`, `summary.md`, `test-v3b-review.md`) and the overall detection rate on all injections
(42% and 36%) is reported next to the in-scope rate. If asked, offer the overall figure as the conservative
number. Improvement: have a second person classify scope blind to detection, and report agreement.

**5. "One small model only."**
Free-tier constraint; admitted. The architecture is model-agnostic (an Anthropic provider exists in the
code). If quota allows, one run of the 86 questions on a second model would answer this.

**6. "Supply-side data is simulated."**
Admitted and explained (WWI purchasing data unusable). Sales are real.

**7. "No user study."**
Admitted. A small usability session (5 people, a task list, SUS questionnaire) would be a cheap addition
for a journal version.

**8. "The figure check flags correct derived numbers."**
Admitted; flagged, not blocked. The measured rate is small (1-3 per run of 300+ figures).

## Things to check before submission

- Replace "Author Name", department, university, email.
- Check the target venue's page limit (the paper is exactly 6 pages in IEEE conference format, references
  included) and whether it allows an extra page for references.
- Check the venue's policy on arXiv citations (eight references are arXiv preprints).
- Several references are dated 2026; confirm each still points to the same version.
- Compile on Overleaf with `figures/recommendation.png` uploaded.

## Viva questions to expect

- *Why not let the model write SQL?* Text-to-SQL is the weak point on enterprise schemas (Spider 2.0:
  21%); tools that wrap the application's services give the model only checked numbers and enforce
  permissions.
- *Why BM25 and not embeddings?* 41 short passages; BM25 needs no model, no index service and is
  deterministic. Grounding raised accuracy from 8-9 to 32 of 32 with it.
- *What stops the AI from ordering?* It has no tool that submits, approves or places an order; a draft must
  be submitted by a user with the right and approved by a different user (separation of duties).
- *How do you know the verifier was not tuned on the test?* Each version's file was hashed before scoring;
  each test used texts never read while writing that version; misses found in a test were not fixed for
  that test.
- *What is a Wilson interval and why use it?* A confidence interval for a proportion that stays sensible
  near 0% and 100% and with small samples, unlike the normal approximation.
- *What is the sign test here?* For paired questions, it counts questions passed only with grounding vs only
  without; 23-24 vs 0 is very unlikely by chance (p < 0.0001).
- *What would you do next?* Questions written by others, a second model, a user study, natural-error test
  set for the verifier, prompt-injection tests through ERP text fields.
