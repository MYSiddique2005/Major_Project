module.exports = [
  { h1: 'Chapter 7: Conclusion' },
  { h2: '7.1 Overview' },
  { p: 'This chapter concludes the project. It points to the user manual, discusses the significance of the work, states its limitations, proposes future enhancements and summarises how each objective and research question was addressed.' },

  { h2: '7.2 User Manual' },
  { p: 'Appendix A explains how to install and run IntelliERP: starting the database, loading the Wide World Importers data, starting the back end and the front end, signing in with the four demonstration accounts and using the AI assistant, the insights and AI-drafted purchase orders. The same steps are kept in the `README.md` file of the project repository, together with the commands that repeat every evaluation in Chapter 6.' },

  { h2: '7.3 Significance of the Project' },
  { p: 'IntelliERP shows that an LLM assistant can be placed inside an ERP system without trusting the model with the facts. The work matters in four ways.' },
  { bullets: [
    '**A complete, working system.** Unlike most AI-ERP research, which proposes frameworks without building or testing them [@hurbean2026erp], IntelliERP is a full ERP system with role-based access control, deterministic analytics, an AI assistant, proactive insights and controlled AI actions, running on a realistic dataset.',
    '**Evidence that grounding prevents most errors.** With the knowledge base, 2.4% of checkable statements were false; without it, 25.9% were. Paired questions rose from 8–9 to 32 of 32. For a business, this means the company\'s own rules must be given to the model, not left for it to guess.',
    '**A verifier whose decisions can be explained.** TRACE moves the decision of truth from the model to code. On held-out errors it was not significantly behind two LLM judges in detection, with a quarter of the false alarms of one and about as many as the other, and every miss and false alarm could be traced to its cause. An auditor can therefore see *why* a statement was accepted or flagged.',
    '**Honest measurement of the limits.** The project measured not only where verification works but where it does not: natural errors that are definitions, false alarms that can make a correct answer wrong, and run-to-run variation of the extraction step. These results are useful to anyone designing verification for business AI.',
  ] },
  { p: 'The design also limits the damage a remaining error can do. The AI can only create a draft purchase order, which goes through the same validation, review and approval by a different person as any other order, with the AI\'s reasoning and the check results attached.' },

  { h2: '7.4 Project Limitations' },
  { bullets: [
    '**No user study.** No user acceptance test was carried out, so the usefulness of the assistant to real managers, and whether the check results shown under each answer reduce over-reliance, were not measured.',
    '**One dataset, simulated supply.** All experiments use one company\'s data. The sales are real, but purchase orders, deliveries and stock levels were simulated from them.',
    '**Free API only.** Only free-tier models were used. Daily limits and overload errors limited the size of the experiments (for example, 211 answers in the natural-error detection study instead of all 590) and made latency figures noisy.',
    '**Limited language.** TRACE can only check what its assertion language can express. Definitions, reasons and statements about what the system can do are outside it, and so are relations between figures, which is why it found only 4 of 19 natural errors.',
    '**Extraction varies.** The extraction step is an LLM call. Given an extraction, verdicts are fully reproducible, but two extractions of the same text agreed on the flag decision in 47 of 50 cases and on the full assertion list in only 6 of 50.',
    '**Single annotator.** The natural-error labels were made by one annotator, a language model that is not one of the evaluated models. Each label records its evidence so it can be checked, but no agreement between annotators was measured, and nine labels had to be corrected after a consistency check.',
    '**Model-written test errors.** The held-out errors were written by language models and may be easier or harder to detect than errors that occur naturally, as the natural-error results suggest.',
  ] },

  { h2: '7.5 Future Enhancements' },
  { numbered: [
    '**A user study** with managers and procurement staff, measuring task accuracy, time and reliance on the AI with and without the check results.',
    '**A wider assertion language** that covers definitions and status meanings, so the natural errors found in this project can be checked; for example, by checking a stated definition against the knowledge-base passage it should match.',
    '**A more stable extractor**: several extractions of the same text combined by vote, or a smaller model fine-tuned for extraction, to reduce run-to-run variation and missed statements.',
    '**Warnings instead of automatic correction** when a flag rests on a single, uncertain assertion, so that a false alarm cannot make a correct answer wrong.',
    '**More data and models**: other ERP datasets with real supply data, and paid or locally hosted models without free-tier limits.',
    '**Engineering improvements** listed in the README: streaming answers, server-side conversation history, SQL-level pagination, a user-management page and front-end tests.',
  ] },

  { h2: '7.6 Summary of Objectives and Outcomes' },
  { table: { caption: 'Research questions, objectives and outcomes', widths: [1.2, 3.6, 4.2],
    head: ['RQ', 'Objective', 'Outcome'],
    rows: [
      ['RQ1', 'Build a complete ERP system with role-based access control on a realistic dataset', 'Achieved: eight modules, four roles, Wide World Importers data; 269 automated tests pass (Chapters 4–6)'],
      ['RQ1', 'Design a grounded assistant: rules decide, the LLM explains through permission-checked tools', 'Achieved: 15 tools, knowledge base generated partly from code; 84, 86 and 86 of 86 questions passed; Gemma 86 of 86'],
      ['RQ1', 'Measure the effect of grounding', 'Achieved: 32 of 32 paired questions with grounding against 8–9 without (p < 0.0001); false statements 2.4% against 25.9%'],
      ['RQ2', 'Design a typed assertion language for enterprise statements', 'Achieved: 64 attributes, 24 rule keys and 21 actions in three families'],
      ['RQ2', 'Implement TRACE with deterministic verification', 'Achieved: frozen before the held-out test; no miss or false alarm caused by a verification function'],
      ['RQ2', 'Evaluate TRACE against baselines on held-out and natural errors', 'Achieved: 70 of 102 detected with 4% false alarms, against 15 (patterns), 80 with 17% false alarms (Gemini judge), 76 with 7% (Gemma judge) and 38 with 21% (MiniCheck); natural errors 4 of 19'],
      ['RQ3', 'Measure the effect on false premises and on ordinary answers', 'Achieved: no significant change in rebuttals (89–93%); harm check showed false alarms can make correct answers wrong'],
      ['RQ3', 'Measure time, tokens and repeatability', 'Achieved: one extraction call per answer (median 6,028 input tokens, 2.0 s); verdicts reproducible given an extraction; end-to-end flag decision 47 of 50'],
      ['RQ3', 'Keep the AI\'s only action behind validation, permissions, separation of duties and audit', 'Achieved: AI can only draft; tested by TC-03, TC-09 and TC-10'],
    ] } },

  { h2: '7.7 Conclusion' },
  { p: 'This project set out to reduce hallucination in LLM-based ERP decision support. It answered the problem with two defences. The first, **prevention by grounding**, lets deterministic analytics decide what is wrong, gives the model the company\'s own rules through a knowledge base generated from the code, and lets it reach data only through permission-checked tools. This was the largest single factor in correctness. The second, **detection by verification**, uses TRACE: the model only turns its statements into typed assertions, and code decides whether they are true. TRACE detected most model-written errors with few false alarms, and every failure could be explained, but it missed most of the assistant\'s own errors, which were definitions outside its language, and its false alarms can do harm when answers are corrected automatically.' },
  { p: 'The main lesson is that the facts in an AI answer should be decided by the system that owns them, not by the model. Where that is possible, grounding and typed verification make an assistant\'s answers checkable and its mistakes visible; where it is not yet possible, the remaining errors are now clearly identified as work for the future.' },
];
