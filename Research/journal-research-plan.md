# Journal research plan: from IntelliERP v1 to an international-journal contribution

Prepared 22 October 2026. Builds on the literature review (Part 1: papers 1-30; Part 2: papers 31-61, all
verified). Numbers in square brackets refer to that review.

## 0. Summary

IntelliERP v1 already does something the newest ERP-agent research does not: it checks what the assistant
*says* against the company's data before anyone sees it. The 2026 competitors either let agents act and
judge them with another LLM [31], score only their actions [32], or reduce hallucination by prompting
and measure it with an LLM judge [37]. The closest one states openly that hallucination frequency was
never measured [31].

To be an international-journal contribution, the work needs four upgrades:

1. **A stronger method.** Replace hand-written claim patterns with **TRACE** (Typed Run-time Assertion
   Checking for Enterprise assistants): every factual sentence becomes a typed assertion, which tested
   code evaluates against the system of record, the company's executable rules, or its analytics.
2. **Baselines.** Compare TRACE with an LLM judge given the same evidence, a trained small fact-checker
   (MiniCheck [49]) and, optionally, LLM-written SQL as in the database literature [42, 43].
3. **Natural errors.** Test on the assistant's own mistakes, not only on errors planted by a model.
4. **End-to-end effect.** Show that verification plus correction changes what the user finally sees,
   using false-premise questions [55].

## 1. Where we stand, and what a journal reviewer will say

| v1 result | What a reviewer will ask | How the plan answers it |
|---|---|---|
| Claim verifier: 48 of 62 planted errors caught *within its 12 claim kinds* (77%), 2 of 124 false alarms | "Only 36-42% of all planted errors were caught. The 12 kinds are hand-picked." | TRACE covers the error types v1 missed (section 4.2); report recall over all planted errors, by type |
| Verifier built from regular expressions | "Brittle; will it generalise to other phrasings or languages?" | LLM-based typed extraction, validated by a schema; patterns kept as a high-precision cross-check |
| No comparison | "Why not ask an LLM to judge? Why not MiniCheck? Why not SQL, as CEDAR does?" | Three baselines on the same items, with cost and repeatability (section 5) |
| Errors planted by Gemini | "Planted errors may not look like real ones." | A natural-error set from 590 stored answers, annotated by two people (section 5.2) |
| Verifier evaluated offline | "Does it change what users see?" | False-premise questions with verification on and off (RQ4) |
| Questions written by the authors; one provider | "Author bias; Google only." | Second annotator; stratified and generated question sets; an optional third model family (section 6) |
| Simulated supply data | "Not real." | Kept and stated; WWI sales are real; the claim language is schema-driven and portable |

## 2. What the newest research shows (short version)

- **ERP agents, 2025-2026 [31-38]:** agents now execute ERP workflows [31, 35] and are benchmarked on
  outcomes [32-34]. Safety comes from risk tiers [31] or admissibility checks on actions [38]. Nobody
  verifies the content of the agent's statements against live ERP data.
- **Claims over databases [40-43]:** a decade of work checks claims in published documents by translating
  them to SQL; CEDAR and Thucy now use LLMs for the translation. All of it is offline, document-oriented,
  and depends on generated SQL.
- **Hallucination detection [46-52]:** self-consistency [46], semantic entropy [47], search-based
  checking [48], trained checkers [49], annotated corpora [50], claim extraction [51], tool-based
  self-correction [52]. All judge text against text, or a model against itself; none uses business rules.
- **Runtime enforcement [56, 57]:** guards for agent *actions* (code, robots, vehicles), not statements.
- **LLM judges [58]:** known problems with consistency and bias, which is the argument for deterministic
  verdicts.
- **Human reliance [60, 61]:** explanations alone can make people accept wrong advice; signals that make
  checking cheap reduce over-reliance, which supports showing verification results to users.

## 3. The gap

| | Content of statements checked | Against the live system of record | Deterministic verdict | Inside the assistant, with correction | Business-rule and what-if claims | Hallucination measured |
|---|---|---|---|---|---|---|
| Agentic ERP [31] | no (LLM judge) | no | no | partly (LLM reflector) | no | **no** (stated) |
| ERPBench [32], EnterpriseBench [33], EnterpriseArena [34] | no (actions, outcomes) | n/a | n/a | no | no | no |
| Epistemic Stability [37] | via LLM judge | no | no | no | no | via LLM judge |
| ADMITBench [38] | actions | plant profile | yes (rule checks) | no (offline) | partly (procedure) | not reported |
| AggChecker, Scrutinizer, CEDAR, Thucy [40-43] | yes | static database | SQL execution, LLM-written query | no (offline documents) | no | yes, on documents |
| MiniCheck, SAFE, RAGTruth detectors [48-50] | yes | documents or web | no (model) | no | no | yes, on text |
| CRITIC [52], AgentSpec [56] | self / actions | tools / no | no / rules on actions | yes | no | no |
| **IntelliERP v1** | yes | **yes** | **yes** | **yes** | no (12 state kinds) | yes |
| **IntelliERP + TRACE (planned)** | yes | **yes** | **yes**, given the extraction | **yes** | **yes** | yes, injected and natural |

## 4. The proposed innovation: TRACE

### 4.1 The idea in one sentence

Treat each factual sentence an assistant writes as a **run-time assertion** about the business, written in
a typed language, and evaluate it with the company's own tested code against the source that is
authoritative for it, so that the LLM never decides whether its own statement is true.

This borrows run-time assertion checking from software engineering (design by contract), with the LLM's
answer as the program state being checked.

### 4.2 Three families of assertion, three sources of truth

| Family | Authoritative source in IntelliERP | Examples from our data | Verdict |
|---|---|---|---|
| **State** (what the data says now) | the database, through the repository layer | "P082 has 0 units on hand"; "P059 is at Low stockout risk"; "Product P999 exists"; "P082 is supplied by Fabrikam (S004)" | supported; contradicted (it is Critical); contradicted (it does not exist); supported |
| **Policy** (what the company's rules say) | the executable rule registry: code constants, status and risk rules, the permission map | "Demand is rising sharply above 15%"; "A procurement manager cannot submit orders"; "The assistant can approve purchase orders" | supported; contradicted; contradicted |
| **Derived** (what follows from the data) | the analytics engine: reorder rule, forecasts, what-if simulation, rankings | "The suggested order is 1,400 units"; "P184 will run out first"; "If demand rises 25%, 328.4 units go unmet over 60 days" | supported; checked by ranking days of cover; checked by re-running the simulation |

Why these three: the 33 planted errors that v1 could not check (`results/claims/test-v3b-review.md`) were
about permissions, existence, scenario premises, changed numbers, comparisons between products, groups,
locations, supplier relations, validation rules and forecast methods. Every one of these is a state,
policy or derived assertion. The hallucinations seen without the knowledge base were invented thresholds,
which are policy assertions. Because these error categories come from the v2/v3 test sets, those sets
become development data for TRACE, and TRACE must be tested on new texts (section 5).

### 4.3 How it works

1. **Extract.** An LLM turns each sentence into zero or more typed assertions (JSON, validated by a
   schema): family, subject (product, supplier, order, role), attribute, comparator, value, scope
   (current, projected, hypothetical, past) and polarity (affirmed or negated). The v1 patterns run
   alongside as a high-precision second extractor.
2. **Resolve.** Subjects are resolved to IDs by exact lookup; unresolvable subjects make the assertion
   unverifiable, never contradicted.
3. **Evaluate.** One deterministic function per attribute computes the true value from the authoritative
   source and compares it: supported, contradicted, or unverifiable (missing fact, past event without
   history, outside the language).
4. **Correct.** As in v1: chat answers are returned once with the contradicted assertions and the true
   values; recommendations must be re-recorded; insights are not stored; drafts are flagged.

### 4.4 Definitions and the guarantee (for the paper's formal section)

- System of record **S = (D, R, F)**: database state D, rule registry R, deterministic analytics F.
- Assertion **a = (family, subject, attribute, comparator, value, scope, polarity)**.
- Verdict **V(a, S)** in {supported, contradicted, unverifiable}, computed only from S.
- **Conditional soundness:** if the extracted assertion faithfully represents the sentence, a verdict of
  supported or contradicted is correct with respect to S. The LLM can cause only two kinds of error, and
  both can be measured separately: **extraction errors** (missed, wrongly typed, wrong polarity or scope)
  and **language coverage** (sentences no assertion can express).
- So every miss and every false alarm can be attributed to one of: not extracted, mis-extracted, not
  expressible, or a defect in a verification function. This error decomposition is itself a result
  reviewers value, and LLM-judge approaches cannot provide it.

### 4.5 Why it is new

- Against **CEDAR and Thucy [42, 43]:** they check published documents offline by having an LLM write
  SQL. TRACE checks the assistant's own answer before it is shown, uses tested business functions instead
  of generated SQL, and covers rule and what-if claims that plain SQL cannot express.
- Against **ProgramFC, Claimify, Contract2Plan [44, 51, 36]:** same direction (structure first), but the
  verdict comes from the enterprise's executable semantics, at run time, with correction.
- Against **MiniCheck, SAFE, RAGTruth detectors, LLM judges [48-50, 58]:** no model decides the truth;
  verdicts are repeatable and explainable by the value they were compared with.
- Against **Agentic ERP and ADMITBench [31, 38]:** they control actions; TRACE verifies statements, and
  measures hallucination, which [31] names as missing.

## 5. Experiments

### 5.1 Research questions

| RQ | Question | Data |
|---|---|---|
| RQ1 | How accurate is the grounded assistant, and is it stable across runs and model families? | Existing: 86 questions, 5 runs, 2 models; optional third model family |
| RQ2 | How well does TRACE detect false statements, compared with the v1 patterns, an LLM judge, MiniCheck and (optionally) LLM-written SQL? | Held-out planted errors; paraphrases; natural errors |
| RQ3 | Which errors remain undetected, and why? | Error decomposition (4.4); coverage of the assertion language on a sample of sentences |
| RQ4 | Does verification plus correction change what users finally see? | False-premise questions, verification on vs off, two models; the 86 questions to check for harm |
| RQ5 | What does verification cost? | Latency, LLM calls and tokens per answer; repeatability across three repeats |
| RQ6 (optional) | Do verification signals help people catch wrong answers? | Small study with classmates, answers shown with and without signals [60, 61] |

### 5.2 Test data

- **Held-out planted errors (new).** Texts never used before: 43 Gemma answers that name a product and 9
  insights from scans after SCAN-0007, plus answers produced in RQ4. Errors written by **two** models
  (Gemini and Gemma) to reduce one writer's style, and **stratified** across the three families and the
  v1 error types, plus paraphrases for false alarms. TRACE is frozen (hash recorded) before scoring.
- **Natural errors (new).** All 590 stored answers (430 with and 160 without the knowledge base).
  Pooling, as in information-retrieval evaluation: every statement flagged by any method is checked by
  hand; a random sample of about 300 sentences is fully annotated to estimate how many errors all methods
  miss. A second annotator (a classmate) labels 20% blind, for Cohen's kappa.
- **False-premise questions (new).** About 60 questions generated from the database, each with a known
  false premise: state ("Why is P082 overstocked?"), policy ("Since procurement managers cannot approve
  orders, who approves them?") and derived ("Why does the reorder rule suggest no order for P082?").
  Scored automatically: does the final answer endorse the premise?

### 5.3 Methods compared (all on the same items)

| Method | What it is | LLM calls per answer |
|---|---|---|
| v1 patterns | the frozen 12-kind verifier (sha256 36154591) | 0 |
| TRACE-rule | patterns extended to the three families where possible | 0 |
| TRACE-LLM | typed extraction by an LLM, deterministic verdicts | 1 |
| TRACE-hybrid | both extractors, conflicts resolved conservatively | 1 |
| LLM judge | the same evidence given to an LLM that labels each sentence (Gemini and Gemma), three repeats on a subset | 1 per repeat |
| MiniCheck [49] | a trained small checker run locally on the CPU, against a textual fact sheet | 0 (local model) |
| SQL check (optional) | an LLM writes SQL over the schema to test each claim, as in [42, 43] | 1 or more |

### 5.4 Measures and statistics

Recall overall and by family and error type; false-alarm rate on paraphrases; precision on natural
flags; F1 with bootstrap 95% intervals; McNemar's exact test for paired comparisons between methods,
with Holm correction; repeatability (share of identical verdicts across repeats, Fleiss' kappa);
latency per answer; calls and tokens per answer. Wilson intervals for every rate, as in v1.

### 5.5 Hypotheses (to test, not promises)

- H1: TRACE-hybrid catches clearly more of *all* planted errors than v1 (36-42%), with false alarms
  still at or below about 5%.
- H2: TRACE verdicts are fully repeatable; LLM-judge verdicts are not.
- H3: with verification on, answers endorse false premises less often than with it off, without hurting
  accuracy on the 86 ordinary questions.
- H4: TRACE-rule costs no LLM call; TRACE-LLM costs one extraction call, comparable to one judge call
  but with deterministic, explainable verdicts.

### 5.6 Free-tier budget (estimates)

| Task | Requests (approx.) |
|---|---|
| Writing planted errors and paraphrases (two writers, five texts per request) | ~25 |
| TRACE-LLM extraction over all test items | ~1,000 |
| LLM judge, two models, plus repeats on a subset | ~2,400 |
| RQ4 false-premise runs (60 questions x on/off x 2 models) | ~900 |

At the rates seen so far (several hundred requests a day per model for `gemini-3.5-flash-lite` and
`gemma-4-31b-it`, separate quotas), this is two to three weeks of background running. MiniCheck runs
locally and needs no quota.

## 6. Work plan

| Phase | Time | Deliverables |
|---|---|---|
| 1. Build TRACE | about 1 week | Assertion schema; state, policy and derived verifiers using existing services; LLM extractor with schema validation; entity resolution; correction loop extended; unit tests; development on v1-v3 texts; hash frozen |
| 2. Build the test data | about 1 week (overlaps) | Held-out planted set (two writers, stratified); natural-error pool and annotation sheets; false-premise question generator with computed truth; coverage sample |
| 3. Run | 2-3 weeks, mostly in the background | All methods on all sets; RQ4 on and off; repeats; MiniCheck locally; optional third model |
| 4. Analyse and write | about 1 week | Tables and figures; journal manuscript (about 10,000 words, the journal's LaTeX template); data and code package; cover letter |

Optional third model family (answers "Google only"): a local open model such as Qwen 2.5 7B through
Ollama, run on the CPU overnight (about 6 GB to download; no account or cost), or a free API key from a
non-Google provider if one is available.

## 7. Target journals and paper outline

Candidate journals (all have a subscription route, which normally has no author fee; check each journal's
current scope, fees and review times before choosing):

| Journal | Publisher | Fit |
|---|---|---|
| Decision Support Systems | Elsevier | Decision support with human oversight; values evaluation of reliance (RQ6 helps) |
| Expert Systems with Applications | Elsevier | Applied AI systems with strong experiments |
| Enterprise Information Systems | Taylor & Francis | ERP-specific |
| Information Systems Frontiers | Springer | IS with AI; accepts system-plus-evaluation papers |
| Journal of Enterprise Information Management | Emerald | Enterprise systems management |
| Computers in Industry | Elsevier | Industrial information systems |

Relation to the 6-page conference paper: it can still be submitted to an IEEE conference as an early
version. The journal paper will be substantially extended (new method, new data, baselines) and must
disclose the conference version in the cover letter; check the chosen journal's policy on extended
conference papers. Alternatively, skip the conference and submit only the journal paper. This is a
decision for the authors and the guide.

Outline: 1 Introduction; 2 Related work (ERP agents; data-claim verification; hallucination detection;
runtime enforcement; human reliance); 3 Problem formulation (definitions, assertion language,
guarantee, error model); 4 IntelliERP; 5 TRACE; 6 Evaluation design; 7 Results (RQ1-RQ5/6);
8 Discussion and threats to validity; 9 Conclusion. Appendices: assertion schema, prompts, annotation
guide, full tables.

## 8. Risks and honest limits

- TRACE-LLM uses an LLM for extraction, so it is deterministic only given the extraction. Mitigation:
  schema validation, fixed decoding settings, caching, measuring extraction variability, and the pattern
  extractor as a cross-check. Structured output is known to fail on complex schemas [59], so the schema
  stays flat and small.
- Free-tier limits and unstable internet slow the runs; all scripts resume where they stopped.
- Annotation by the authors can be biased; the blind second annotator and published labels address it.
- Supply data remains simulated; the claim language and verifiers are tied to the schema, not the data.
- Expected results are hypotheses. If a hypothesis fails, the paper reports it.

## 9. What the authors need to decide or do

1. Agree this direction with the guide (Prof. Ashish K. Soni) and the supervisor (Dr. Zeyad Ahmed), and
   settle the author list.
2. Find one classmate for blind annotation (about 2-3 hours, with a prepared sheet).
3. Decide on the optional third model family (local download, or a free non-Google API key).
4. Choose the target journal, and whether the conference paper goes first.
