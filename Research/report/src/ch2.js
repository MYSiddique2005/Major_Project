module.exports = [
  { h1: 'Chapter 2: Literature Review' },
  { h2: '2.0 Introduction' },
  { p: 'This chapter reviews more than sixty published works in six areas that bear on the project\'s problem: AI in ERP systems; LLMs over enterprise data; LLM agents in supply chain and ERP; grounding and tool use; hallucination and its detection; and the verification of claims against data. Every paper was checked against the publisher, arXiv or the conference proceedings. The chapter ends with a critical comparison of existing approaches, the research gaps that IntelliERP addresses and a literature review matrix.' },

  { h2: '2.1 AI in ERP Systems' },
  { p: 'A systematic review of 183 academic and 35 industry documents found that research on AI in ERP grows by 11.3% a year and is dominated by automation (41% of studies), while ethics and governance appear in under 2% of studies and 93% stress benefits [@hurbean2026erp]. A review of LLMs in supply chain management similarly describes the field as fragmented and exploratory, without a unified framework for deployment [@song2026scm]. Both reviews point to the same weakness: trust and control receive far less attention than capability.' },

  { h2: '2.2 LLMs over Enterprise Data' },
  { h3: '2.2.1 Text-to-SQL and its limits' },
  { p: 'The most common way to connect an LLM to a database is to let it write SQL. On Spider 2.0, a benchmark of 632 real enterprise text-to-SQL tasks, the best agent solved 21.3% of tasks, against 91.2% on the earlier Spider 1.0 [@lei2025spider2]. On BIRD, GPT-4 reached 54.89% against 92.96% for humans, and the authors identify external business knowledge as the main gap [@li2023bird]. @biswal2025tag argue that text-to-SQL and retrieval cover only narrow question types and that many questions need reasoning beyond relational algebra. @sequeda2023kg showed that giving GPT-4 the business context of an insurance schema as a knowledge graph raised accuracy from 16.7% to 54.2%.' },
  { h3: '2.2.2 Conversational ERP' },
  { p: 'The closest earlier system, "Chatting with your ERP", uses a reasoning agent and a critic to write SQL over a production ERP database and answered 10 of 11 test questions [@ruizgomez2025erp]. It is read-only, depends on a hand-written expert description of the database, and does not verify its answers. IntelliERP avoids SQL generation altogether: the model calls tools that wrap the application\'s own tested services.' },

  { h2: '2.3 LLM Agents in Supply Chain and ERP' },
  { h3: '2.3.1 Advisory systems' },
  { p: 'OptiGuide keeps an optimisation solver in charge of the numbers while the LLM explains and runs what-if scenarios [@li2023optiguide]; IntelliERP follows the same division of labour. @simchilevi2025decisions report that LLMs cut supply-chain decision time from days to hours, and even advocate use without a human in the loop. Industrial planning agents at JD.com decompose planning intents for human planners [@qi2025planning]. @xue2026xai use an LLM to explain a graph model\'s risk predictions and check that 99.6% of explanations agree in direction with the evidence, in a single case study.' },
  { h3: '2.3.2 Autonomous agents' },
  { p: 'InvAgent lets zero-shot LLM agents place orders in a simulated supply chain and claims explainability without measuring it [@quan2024invagent]. @yoshizato2026agents improve ordering agents with structured prompts and retrieval of past decisions. @long2026reliability found that autonomous agents in the Beer Game cut cost by up to 80% against humans on average, but their decisions varied widely between runs, with large worst-case costs; guardrails were a training-free way to limit extreme decisions.' },
  { h3: '2.3.3 ERP agents and benchmarks (2025–2026)' },
  { p: 'The newest work lets agents act on real ERP systems. Agentic ERP runs GPT-4o-mini agents that execute writes on Odoo with risk tiers: low-risk writes run automatically and high-risk ones need a human [@liu2026agenticerp]. Its authors state that hallucination frequency was not measured and that their gate is not a bound on hallucinated decisions. ERPBench [@zhang2026erpbench], EnterpriseBench [@vishwakarma2025enterprisebench] and EnterpriseArena [@han2026cfo] score agents on actions and outcomes; none checks whether the agent\'s statements are true. FinRobot builds finance workflows with inserted risk controls [@yang2025finrobot], and @freeman2026epistemic compare prompting methods against hallucination in industrial settings, judged by an LLM. The work closest in spirit is ADMITBench, which judges whether each proposed action of an industrial advisory is supported, permitted and safe [@misra2026admitbench], and Contract2Plan, which extracts a typed constraint schema from contracts and verifies it with a solver before a plan is emitted [@agarwal2026contract2plan]. Neither verifies an assistant\'s statements against a live system of record.' },

  { h2: '2.4 Grounding and Tool Use' },
  { p: 'Retrieval-augmented generation gives a model relevant passages from an external collection together with the question, which improves factual accuracy on knowledge-intensive tasks [@lewis2020rag]. IntelliERP retrieves passages with BM25, a well-established keyword ranking function [@robertson2009bm25], because its collection is small and written in the vocabulary users ask in. ReAct interleaves reasoning with tool actions and reduces hallucination compared with reasoning alone [@yao2023react]; Toolformer showed that models can learn when to call tools [@schick2023toolformer]. Enterprise agent benchmarks show how far this still is from reliable: on CRMArena the best agents succeed on under 58% of CRM tasks and follow business rules poorly [@huang2025crmarena]; WorkArena finds a large gap to automating knowledge work [@drouin2024workarena]; and τ-bench introduced pass^k, success in all of k repeated tries, under which reliability drops sharply [@yao2024taubench].' },

  { h2: '2.5 Hallucination and its Detection' },
  { h3: '2.5.1 What hallucination is' },
  { p: 'Hallucination is text that is fluent but unfaithful to its source or to the facts [@ji2023survey]. In LLM agents it can arise at every stage, from planning to tool use and memory [@lin2025agenthallucination]. Business settings are especially exposed: on FinanceBench, GPT-4-Turbo with retrieval answered wrongly or refused 81% of financial questions [@islam2023financebench].' },
  { h3: '2.5.2 Detection without external data' },
  { p: 'SelfCheckGPT samples several answers and treats facts that vary between them as likely invented [@manakul2023selfcheckgpt]; semantic entropy measures uncertainty over meanings [@farquhar2024semantic]. Both need no external data, but both miss errors that the model makes consistently, and a model can be consistently wrong about a company\'s own rules.' },
  { h3: '2.5.3 Detection against evidence' },
  { p: 'FActScore splits an answer into atomic facts and scores the share supported by a source [@min2023factscore]. SAFE checks each fact of a long answer with Google Search [@wei2024longform]. MiniCheck is a small fact-checker that reaches GPT-4 accuracy on grounding documents at about 400 times lower cost [@tang2024minicheck], and is used as a baseline in this project. RAGTruth annotates about 18,000 naturally generated answers at word level [@niu2024ragtruth]; its approach to annotating natural errors informs the natural-error study in Chapter 6. RAGAs scores faithfulness with an LLM as judge [@es2024ragas], but a survey of LLM judges reports problems of consistency, bias and robustness [@gu2024judge].' },

  { h2: '2.6 Verifying Claims against Structured Data' },
  { p: 'Checking claims against data is an established database problem. TabFact provides 118,000 statements over tables labelled entailed or refuted [@chen2020tabfact]. AggChecker translates claims in articles into SQL queries and found erroneous claims in about a third of 392 claims [@jo2019aggchecker]; Scrutinizer helps human fact-checkers translate claims into SQL [@karagiannis2020scrutinizer]. In the LLM era, CEDAR lets LLMs write the verifying SQL with a cost-based cascade [@jayasekara2025cedar], and Thucy uses agents across several databases [@theologitis2025thucy]. ProgramFC has an LLM write a reasoning program whose steps are handled by specialised modules [@pan2023programfc], and QuanTemp shows that real numerical claims are hard to check [@venktesh2024quantemp]. Claimify studies the extraction of factual claims from text and extracts a claim only when its interpretation is clear [@metropolitansky2025claimify]. CRITIC lets an LLM check and revise its own output with tools [@gou2024critic]; Self-RAG [@asai2024selfrag] and Chain-of-Verification [@dhuliawala2024cove] let a model critique itself. In all of these the verdict is either made by a model or depends on model-written queries, and none runs inside an assistant against business rules before the user sees the answer.' },

  { h2: '2.7 Run-time Verification and Safety' },
  { p: 'Software engineering has long checked programs at run time against assertions: design by contract [@meyer1992contract] and run-time assertion checking [@clarke2006rac] evaluate a typed condition when the program runs. TRACE applies this idea to statements in text. Run-time enforcement has recently been applied to LLM agents, but to their *actions*: AgentSpec enforces rules on agent actions and prevents over 90% of unsafe code-agent executions [@wang2026agentspec], and ProbGuard predicts violations from execution traces [@wang2026probguard]. Two further risks shape the design. Instructions hidden in data that an application retrieves can take over an LLM [@greshake2023injection; @debenedetti2024agentdojo], which is one reason the assistant cannot act beyond a draft. Structured output remains hard for LLMs [@geng2025jsonschemabench], which is why every extracted assertion is validated against a schema.' },

  { h2: '2.8 People, Reliance and Proactive Assistance' },
  { p: 'Explanations made people accept AI recommendations more often whether they were right or wrong [@bansal2021whole], while explanations that make checking easier reduced over-reliance [@vasconcelos2023overreliance]; this motivates showing users which statements were checked against the data. Design guidelines ask that a system make clear why it did what it did [@amershi2019guidelines]. Abstention, declining to answer when the data cannot support an answer, is an open problem [@wen2025abstention], and questions built on false premises are a known weakness of LLMs [@hu2023falseqa], which motivates the false-premise experiment. InsightBench evaluates agents that generate business insights [@sahu2025insightbench], and ProactiveBench studies when an agent should offer help [@lu2025proactive].' },

  { h2: '2.9 Critical Analysis of Existing Systems' },
  { p: 'The reviewed work falls into four categories, compared in Table 2.1.' },
  { table: { caption: 'Comparison of existing approaches with IntelliERP', widths: [2.2, 2.2, 2.3, 2.3],
    head: ['Category', 'Examples', 'Strength', 'What is missing'],
    rows: [
      ['Read-only enterprise question answering', 'Chatting with your ERP; text-to-SQL agents', 'Natural-language access to data', 'Answers are not verified; SQL generation is error-prone; no actions'],
      ['Autonomous ERP and supply-chain agents', 'Agentic ERP, InvAgent, Beer Game agents', 'Can act and optimise', 'Hallucination not measured; explanations unchecked; unstable across runs'],
      ['Hallucination detectors', 'SelfCheckGPT, MiniCheck, LLM judges, SAFE', 'General, work on any text', 'No business-rule semantics; verdict made by a model; not inside the product'],
      ['Claim verification over databases', 'AggChecker, CEDAR, Thucy', 'Checks claims against data', 'Offline documents; depends on model-written SQL; no rules or permissions'],
      ['IntelliERP (this project)', 'Grounded assistant + TRACE', 'Checks every statement against the system\'s own code before the user sees it; draft-only actions', 'Coverage of definitions; extraction errors (measured in Chapter 6)'],
    ] } },

  { h2: '2.10 Research Gap Identification' },
  { h3: '2.10.1 Gap 1: Statements are not verified against the system of record' },
  { p: 'ERP assistants and agents are evaluated on whether their actions succeed, not on whether what they say is true; the closest system explicitly did not measure hallucination [@liu2026agenticerp].' },
  { h3: '2.10.2 Gap 2: Verdicts depend on a model' },
  { p: 'Existing detectors either ask another LLM or rely on model-written queries, so their verdicts can be wrong, vary between runs and cannot be traced to a specific fact [@gu2024judge].' },
  { h3: '2.10.3 Gap 3: Business rules and permissions are not checked' },
  { p: 'Claim-verification systems check figures in documents, but not the company\'s rules, the analytics\' derived results or the user\'s permissions, which are exactly what an ERP assistant talks about.' },
  { h3: '2.10.4 Gap 4: Natural errors and end-to-end effect are rarely measured' },
  { p: 'Most detectors are evaluated on injected or benchmark errors; few measure the errors a deployed assistant actually makes, or whether verification changes what the user finally sees.' },

  { h2: '2.11 Literature Review Matrix' },
  { table: { caption: 'Literature review matrix', widths: [2, 2.4, 2, 2.6],
    head: ['Reference', 'Focus / contribution', 'Method / technology', 'Limitation addressed by IntelliERP'],
    rows: [
      ['@ruizgomez2025erp', 'Conversational access to a production ERP', 'ReAct agent writing SQL, with a critic', 'Read-only and unverified; IntelliERP verifies every statement and allows controlled drafts'],
      ['@liu2026agenticerp', 'Autonomous multi-agent ERP on Odoo', 'Planner-executor agents with risk tiers', 'Hallucination not measured; IntelliERP measures and detects it'],
      ['@sequeda2023kg', 'Business context improves enterprise QA', 'Knowledge graph over SQL', 'Hand-built context; IntelliERP generates its knowledge base partly from code'],
      ['@li2023optiguide', 'LLM explains, solver computes', 'Code generation for what-if', 'No verification of explanations; no approval workflow'],
      ['@quan2024invagent', 'LLM agents manage inventory', 'Zero-shot multi-agent ordering', 'Explanations never checked; no human oversight'],
      ['@tang2024minicheck', 'Efficient grounding fact-checker', 'Small trained model', 'No business semantics; used as a baseline here'],
      ['@jayasekara2025cedar', 'Data-driven claim verification', 'LLM-written SQL, cost cascade', 'Offline; correctness depends on LLM-written SQL'],
      ['@wang2026agentspec', 'Run-time enforcement for agents', 'Rule language over actions', 'Governs actions, not the truth of statements'],
      ['@gu2024judge', 'Reliability of LLM judges', 'Survey', 'Motivates a deterministic verdict and the repeatability test'],
    ] } },

  { h2: '2.12 Summary' },
  { p: 'The literature shows strong progress in giving LLMs access to enterprise data and letting them act, but little on checking whether what they say is true. Where statements are checked, the verdict is made by a model or by model-written SQL, outside the product and without business rules. IntelliERP addresses these gaps by grounding the assistant in the system\'s own data and rules and by verifying every statement with the system\'s own code at run time. The next chapter describes how the system was designed.' },
];
