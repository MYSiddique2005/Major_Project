module.exports = [
  { h1: 'Chapter 5: System Development' },
  { h2: '5.1 Overview' },
  { p: 'This chapter explains how the design of Chapter 3 was turned into a working system. It describes the tools and configuration, then six parts of the system that make it unique, each with its development approach, the actual code and its advantages. The last sections describe the problems met during development and how they were solved. All code excerpts are taken unchanged from the project repository, shortened only where marked.' },

  { h2: '5.2 System Development Tools and Configuration' },
  { h3: '5.2.1 Technology stack' },
  { table: { caption: 'System technology stack', widths: [1.8, 3.2, 4],
    head: ['Layer', 'Technologies', 'Purpose in the system'],
    rows: [
      ['Frontend', 'React 19, TypeScript, Vite, React Router, Axios, Tailwind CSS v4, Recharts, Lucide', 'Web interface, charts, role-aware navigation'],
      ['Backend', 'Python 3, FastAPI, Pydantic v2, PyJWT, bcrypt, Uvicorn', 'REST API, validation, authentication, business logic'],
      ['Database', 'PostgreSQL, SQLAlchemy 2, Alembic, psycopg 3', 'Persistent ERP data, migrations, constraints'],
      ['LLM', 'Google Gemini API (`google-genai`); Anthropic Claude supported', 'Assistant, insights, TRACE extraction'],
      ['Testing', 'pytest (269 tests)', 'Automated tests of services, analytics, permissions, AI plumbing, TRACE'],
      ['Evaluation', 'Python scripts in `LLM/evaluation`; MiniCheck (PyTorch, Transformers) on the CPU', 'Experiments of Chapter 6'],
    ] } },
  { h3: '5.2.2 Hardware and environment' },
  { table: { caption: 'Development hardware and environment', widths: [2, 3, 4],
    head: ['Component', 'Specification', 'Purpose'],
    rows: [
      ['Processor', '12th Gen Intel Core i7-1255U (12 threads)', 'Back end, database, MiniCheck baseline on the CPU'],
      ['Memory', '14 GB usable RAM', 'Database, servers and the MiniCheck model'],
      ['Storage', 'NVMe SSD (468 GB partition)', 'Code, dataset, evaluation results'],
      ['Operating system', 'Ubuntu Linux', 'Development and experiments'],
      ['GPU', 'None used', 'All model inference runs on the Gemini API'],
    ] } },
  { h3: '5.2.3 Choice of language model' },
  { p: 'Two options were considered: a small local model or a cloud API. A small local model would keep data on the machine, but models that fit on a laptop are weak at tool calling and structured output, and the project\'s claims would then be about a weak model. The project therefore uses the Gemini API on its free tier, with `gemini-3.5-flash-lite` for all evaluation runs and the open-weight `gemma-4-31b-it` as a second model. The free tier limits requests per minute and per day and is often overloaded. The assistant was therefore built to wait out the per-minute limit and to move to a fallback model when one is overloaded, and every evaluation script records its progress so that it resumes where it stopped.' },
  { h3: '5.2.4 Architecture' },
  { p: 'Figure 5.1 shows the layered architecture. A request flows from a React page through an Axios service to a FastAPI router, a service, a repository interface and PostgreSQL. The repository interface has two implementations, PostgreSQL and in-memory, so the full test suite runs without a database.' },
  { fig: { file: 'fig-architecture.png', caption: 'Layered architecture of IntelliERP', width: 6 } },

  { h2: '5.3 Uniqueness of System 1: Deterministic Analytics with Evidence' },
  { h3: '5.3.1 Development Approach' },
  { p: 'Agents that decide on their own vary greatly between runs [@long2026reliability]. IntelliERP therefore lets rules, not the AI, decide what is at risk. The analytics are pure functions with no AI involved: average daily demand over 28 days and its trend against the previous 28 days; days of cover; the supplier\'s lead time observed from its deliveries; a four-level stockout risk; an order-up-to reorder quantity; weekly forecasts chosen by back-test error; supplier performance; and day-by-day what-if projections. Each result carries the facts that produced it.' },
  { h3: '5.3.2 Code Development' },
  { code: { caption: 'Stockout risk rule with its evidence', source: 'Backend/app/analytics/stock_risk.py', text:
`def assess(position: StockPosition, today: date) -> StockRisk:
    p = position
    selling = p.avg_daily_demand > 0
    days_of_cover = round(p.on_hand / p.avg_daily_demand, 1) if selling else None
    ...
    below_safety = p.on_hand < p.safety_stock
    rising = p.demand_trend_pct is not None and p.demand_trend_pct >= RISING_DEMAND_PCT
    runs_out_before_resupply = days_of_cover is not None and days_of_cover < p.lead_time_days
    inbound_in_time = (p.inbound_units > 0 and p.next_inbound_date is not None
        and (stockout_date is None or p.next_inbound_date <= stockout_date))

    if p.on_hand == 0 and selling:
        level = RiskLevel.CRITICAL
    elif (runs_out_before_resupply or (below_safety and rising)) and not inbound_in_time:
        level = RiskLevel.HIGH
    elif (below_safety
          or (days_of_cover is not None and days_of_cover < p.lead_time_days + REVIEW_BUFFER_DAYS
              and not inbound_in_time)
          or (runs_out_before_resupply and p.supplier_high_risk)):
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    # Evidence: every statement is a fact from the inputs, so it can be shown or cited as-is.
    drivers = []
    if p.on_hand == 0:
        drivers.append("Out of stock.")
    elif below_safety:
        drivers.append(f"Stock on hand ({p.on_hand}) is below safety stock ({p.safety_stock}).")` } },
  { h3: '5.3.3 Advantages of the Approach' },
  { p: 'The same inputs always give the same risk level, every level can be explained by its evidence, and the rules are covered by automated tests. The thresholds (for example, rising demand at 15% or more) are constants in the code, which the knowledge base reads (Section 5.5), so the assistant\'s description of a rule cannot drift from the rule itself.' },

  { h2: '5.4 Uniqueness of System 2: Permission-checked Tool Calling' },
  { h3: '5.4.1 Development Approach' },
  { p: 'The assistant never writes SQL. It answers by calling 15 tools that wrap the same services the web pages use (Table 5.3), following the reason-and-act pattern [@yao2023react]. For each question, the model is offered only the tools the user\'s role permits, and the permission is checked again when a tool runs. Lists return at most 50 rows but always report the totals over everything that matched, so the model does not count the rows it happens to see.' },
  { table: { caption: 'Tools available to the AI assistant', widths: [3, 3.6, 2],
    head: ['Tool', 'Returns', 'Permission'],
    rows: [
      ['list_stock_risk, get_stock_risk', 'Stockout risk with evidence, reorder point, suggested order', 'analytics:view'],
      ['get_demand_forecast', 'Weekly demand history and forecast', 'analytics:view'],
      ['list_supplier_performance', 'On-time rate, delays, lead time, overdue orders', 'analytics:view'],
      ['list_risk_alerts', 'Current high and critical alerts', 'analytics:view'],
      ['run_what_if', 'Stock projection under changed demand, delay or order', 'analytics:view'],
      ['get_product_overview', 'One product\'s facts grouped by module', 'analytics:view'],
      ['propose_recommendation', 'Records a recommendation and returns the server\'s checks', 'analytics:view'],
      ['search_products', 'Product master data and stock status', 'products:view'],
      ['get_inventory', 'Stock records of a product', 'inventory:view'],
      ['get_sales_summary', 'Units, revenue, weekly units, top customers', 'sales:view'],
      ['list_purchase_orders', 'Purchase orders, delivery dates, overdue count', 'procurement:view'],
      ['list_suppliers', 'Supplier master data', 'suppliers:view'],
      ['search_knowledge', 'Passages from the knowledge base', 'ai:use'],
      ['draft_purchase_order', 'Creates a draft purchase order', 'procurement:create'],
    ] } },
  { h3: '5.4.2 Code Development' },
  { code: { caption: 'Every tool call is checked against the user\'s permissions', source: 'Backend/app/llm/tools.py', text:
`def run(self, user: User, name: str, arguments: Any) -> Any:
    self._user = user
    tool = self._tools.get(name)
    if tool is None:
        raise ToolError(f"Unknown tool '{name}'.")
    if not has_permission(user.role, tool.permission):
        raise ToolError(f"The user's role does not have the '{tool.permission}' permission.")
    try:
        return tool.handler(tool.input_model.model_validate(arguments))
    except ValidationError as error:
        raise ToolError(f"Invalid input: {error.errors(include_url=False, include_input=False)}") from error
    except DomainError as error:
        raise ToolError(error.message) from error` } },
  { h3: '5.4.3 Advantages of the Approach' },
  { p: 'Because the tools run the application\'s own tested services, every figure the model sees is correct by construction, and the model cannot see or do anything the user could not do through the pages. Tool inputs are validated with Pydantic, so a malformed call becomes an error message to the model rather than a crash.' },

  { h2: '5.5 Uniqueness of System 3: Enterprise Grounding' },
  { h3: '5.5.1 Development Approach' },
  { p: 'A general model does not know what "safety stock", "Low Stock" or "High risk" mean in this company. The knowledge base gives it 41 passages: 11 describing every table and column (generated from the database models), 11 definitions, 8 rules, 4 workflows, 4 role descriptions (generated from the permission map) and 3 data notes. Thresholds in the written passages are filled from the constants of the code that applies them, and a test fails if a database column has no description. For each question the four best-matching passages are retrieved with BM25 [@robertson2009bm25] and placed before the question; the model can also search the knowledge base itself.' },
  { h3: '5.5.2 Code Development' },
  { code: { caption: 'BM25 retrieval over the knowledge base', source: 'Backend/app/knowledge/base.py', text:
`def search(self, query: str, limit: int = 4, category: str | None = None) -> list[Match]:
    """The entries most relevant to \`query\`, best first. Entries sharing no word with it are left out."""
    query_terms = set(tokenize(query))
    count = len(self.entries)
    average_length = sum(self._lengths) / count if count else 0
    matches = []
    for entry, terms, length in zip(self.entries, self._terms, self._lengths):
        if category and entry.category != category:
            continue
        score = 0.0
        for term in query_terms:
            frequency = terms.get(term, 0)
            if not frequency:
                continue
            containing = self._document_frequency[term]
            inverse = math.log(1 + (count - containing + 0.5) / (containing + 0.5))
            score += inverse * frequency * (K1 + 1) / (frequency + K1 * (1 - B + B * length / average_length))
        if score > 0:
            matches.append(Match(entry, round(score, 3)))
    matches.sort(key=lambda match: match.score, reverse=True)
    return matches[:limit]` } },
  { h3: '5.5.3 Advantages of the Approach' },
  { p: 'Keyword retrieval needs no second external service and works well on a small collection written in the vocabulary users ask in: on 26 test questions, the answering passage was ranked first for 24 and in the top three for all 26. Generating the schema and permission passages from the code means the assistant\'s knowledge is updated whenever the system changes. Chapter 6 shows that grounding is the single largest factor in the assistant\'s correctness.' },

  { h2: '5.6 Uniqueness of System 4: Figure Tracing and Pattern-based Claim Checking' },
  { h3: '5.6.1 Development Approach' },
  { p: 'The first verifier had two parts. **Figure tracing** looks up every number in an answer, recommendation or insight among the tool results, the knowledge passages, the question and the earlier turns, allowing for rounding. An answer that states figures although no tool was called is sent back once; figures that still cannot be traced are shown to the user as unverified. **Claim checking** finds twelve kinds of qualitative statement by hand-written patterns and checks each against the same facts (Table 5.4).' },
  { table: { caption: 'Claims checked by the pattern-based verifier', widths: [4, 5],
    head: ['Claim', 'Checked against'],
    rows: [
      ['below / above safety stock', 'stock on hand vs. safety stock'], ['out of stock / in stock', 'stock on hand = 0 / > 0'],
      ['demand rising / falling', '28-day demand trend > 0 / < 0'], ['units overdue / on time', 'overdue units or orders'],
      ['delivery in time / too late', 'next delivery vs. stockout date'], ['cover below / above lead time', 'days of cover vs. lead time'],
      ['below / above reorder level', 'stock on hand vs. reorder level'], ['below / above reorder point', 'stock + on order vs. reorder point'],
      ['stock status', 'status rule on the stock record'], ['stockout risk level', 'assessed risk level'],
      ['supplier delivery risk level', 'supplier risk level'], ['supplier delay trend', 'worsening / improving / stable'],
    ] } },
  { h3: '5.6.2 Advantages and limits' },
  { p: 'The pattern verifier needs no model call and caught 77% of the in-scope errors on unseen text (Chapter 6). Its weakness is coverage: patterns recognise only the statements they were written for, so it detected only 38% of all errors on the development sets. This limit led to TRACE.' },

  { h2: '5.7 Uniqueness of System 5: TRACE, Typed Run-time Assertion Checking' },
  { h3: '5.7.1 Development Approach' },
  { p: 'TRACE applies the idea of run-time assertion checking from software engineering [@meyer1992contract; @clarke2006rac] to the statements in an answer. Each factual statement is turned into a **typed assertion** in a language of 64 attributes, 24 rule keys and 21 actions, grouped in three families according to their source of truth (Table 5.5). An LLM is used only to extract the assertions, as JSON validated against a schema; **whether an assertion is true is decided by deterministic code** that reads the same services the application uses. A rule-based extractor (the twelve patterns of Section 5.6) runs alongside, and the two are combined in "hybrid" mode. Figure 5.2 shows the pipeline.' },
  { table: { caption: 'The three families of the assertion language', widths: [1.6, 3, 4.4],
    head: ['Family', 'Source of truth', 'Example statements'],
    rows: [
      ['State', 'The database', 'stock on hand, safety stock, units on order, overdue units, supplier of a product, order status'],
      ['Derived', 'Results the analytics compute', 'demand trend, days of cover, stockout risk level, reorder point, suggested quantity, forecast, what-if stockout date'],
      ['Policy', 'Executable rules and the permission map', 'rising-demand threshold, review period, drafts per message, what a role or the assistant may do'],
    ] } },
  { fig: { file: 'fig-trace.png', caption: 'The TRACE verification pipeline', width: 6.4 } },
  { h3: '5.7.2 Code Development' },
  { p: 'The assertion schema is kept flat and small, because structured output is least reliable on deep schemas [@geng2025jsonschemabench]; every field the model does not have to fill is one it cannot get wrong.' },
  { code: { caption: 'The typed assertion schema (shortened)', source: 'Backend/app/llm/trace/schema.py', text:
`Comparator = Literal["eq", "ne", "lt", "le", "gt", "ge"]
Status = Literal["supported", "contradicted", "unverifiable"]

class Assertion(BaseModel):
    quote: str = Field(min_length=1, max_length=400,
                       description="The exact words of the statement, copied from the text")
    subject: str = Field(default="", max_length=120,
                         description="Product, supplier or order ID; for rules the rule key; ...")
    attribute: Literal[NAMES] = Field(description="One attribute name from the catalogue")
    comparator: Comparator = Field(default="eq", description="eq, ne, lt, le, gt or ge")
    value: str = Field(max_length=120, description="Number without units, date as YYYY-MM-DD, ...")
    tense: Literal["present", "past"] = Field(default="present", ...)
    horizon_weeks: int | None = Field(default=None, ge=1, le=26, ...)
    demand_change_pct: float | None = Field(default=None, ge=-100, le=500, ...)   # what-if
    delay_days: int | None = Field(default=None, ge=-30, le=90, ...)             # what-if` } },
  { p: 'Each valid assertion is then verified. The safeguards that development added are visible at the start of the function: a past event is not judged against current data, a statement about data the user\'s role may not see is not judged, and a product or supplier that the text never names (supplied by the extractor, not the writer) is not judged.' },
  { code: { caption: 'Verifying one assertion (shortened)', source: 'Backend/app/llm/trace/verify.py', text:
`def verify(assertion: Assertion, source: FactSource, role: Role | None = None, origin: str = "model",
           named_in: str | None = None, siblings: bool = True) -> Verdict:
    attribute = BY_NAME[assertion.attribute]
    ...
    if assertion.tense == "past" and not attribute.recorded:
        return verdict("unverifiable", None, "a past event the system does not keep as current data")
    if attribute.permission is not None and role is not None and not has_permission(role, attribute.permission):
        return verdict("unverifiable", None, "the user's role may not see this data")
    try:
        subject, written_as_id = _resolve_subject(attribute, assertion.subject, source)
    except Unresolved as error:
        return verdict("unverifiable", None, str(error))
    if named_in is not None and attribute.subject in _IDS and not _named(attribute.subject, subject, named_in, source):
        return verdict("unverifiable", None, f"the text does not name {subject}", subject)
    ...
    actual = read(attribute, subject, assertion, source, role)   # the system's own value
    ...                                                          # supported / contradicted by comparison` } },
  { h3: '5.7.3 Development by error analysis' },
  { p: 'TRACE was developed on three development sets of model-written errors and paraphrases. Every false alarm and every miss was traced to its assertion, and each recurring cause led to a safeguard: grounding (an extracted subject must be named in the text), groups of ambiguous terms (for example, "reorder threshold" may mean the reorder level or the reorder point), type checks (a date is never compared with a number, units are not orders, warehouse names are not products), and drafts created during the conversation are not judged against older data. The extraction prompt went through three versions; the third added eleven detections over the second. When development was complete, TRACE was **frozen**: the hashes of its source files were recorded before the held-out test was generated, and every result in Chapter 6 was computed against those hashes.' },
  { h3: '5.7.4 Advantages of the Approach' },
  { p: 'Given an extraction, a verdict is correct whenever the extraction is faithful, and every error can be attributed to one of three places: the extractor, the coverage of the language, or a verification function. Each verdict carries the asserted and the actual value, so a flag can always be explained ("the data says 1,400"). Chapter 6 shows that these properties held in every experiment: no error came from a verification function.' },

  { h2: '5.8 Uniqueness of System 6: Controlled Actions with Human Approval' },
  { h3: '5.8.1 Development Approach' },
  { p: 'The AI side can cause exactly one change to the ERP data: a purchase order in status Draft. A reorder recommendation names a product, a supplier and a quantity; the server checks it again against the reorder rule, the supplier and the system\'s figures; the draft is created through the same validation as any order and records its AI origin, the recommendation and the check results; a user with `procurement:create` reviews and submits it; and a **different** user with `procurement:approve` approves or rejects it. Table 5.6 lists the controls.' },
  { table: { caption: 'Controls on AI-drafted purchase orders', widths: [3.2, 5.8],
    head: ['Control', 'How it is enforced'],
    rows: [
      ['Only a draft', 'The assistant has no tool that submits, approves, cancels or places an order; a test asserts this'],
      ['Only for users who could do it themselves', 'The tool is offered, and the endpoints open, only with procurement:create'],
      ['Same rules as any order', 'Supplier must be active and supply the product; quantity and price limits apply'],
      ['Bounded', 'At most 3 drafts per chat message; one draft per insight'],
      ['A different quantity is visible', 'A quantity that differs from the reorder rule is flagged for the reviewer and approver'],
      ['No substitute supplier', 'If a named supplier is refused, a draft from another supplier is refused for the rest of the message'],
      ['A second person decides', 'Whoever the draft was made for cannot approve it (separation of duties)'],
      ['Traceable', 'The audit log records the draft with its AI origin, and every later step'],
    ] } },
  { h3: '5.8.2 Code Development' },
  { code: { caption: 'Separation of duties when an order is approved', source: 'Backend/app/services/approval_service.py', text:
`def _decide(self, approval_id: str, user: User, comment: str | None, *, approved: bool) -> ApprovalResponse:
    approval = self._get(approval_id)
    if approval.status != ApprovalStatus.PENDING:
        raise BusinessRuleError(f"Approval {approval.id} has already been {approval.status.lower()}")
    po = self._purchase_orders.get(approval.purchase_order_id)
    if po is None or po.status != PurchaseOrderStatus.PENDING_APPROVAL:
        raise BusinessRuleError(f"Purchase order {approval.purchase_order_id} is not pending approval")
    # Separation of duties: an order needs a second person to approve it. This also covers a draft the
    # AI assistant prepared for someone, which is created in that person's name. Rejecting is allowed.
    if approved and self._separation_of_duties and user.username in (po.created_by, approval.requested_by):
        raise BusinessRuleError(
            f"You created or submitted {po.id}, so another approver must approve it. You may still reject it.")` } },
  { h3: '5.8.3 Advantages of the Approach' },
  { p: 'A false statement by the assistant cannot become a transaction on its own: in the worst case it becomes a draft that a person reviews, with the AI\'s reasoning and any check warnings attached, and that a second person must approve. This addresses the governance gap in AI-ERP research [@hurbean2026erp] and the instability of autonomous agents [@long2026reliability].' },

  { h2: '5.9 Problems Met during Development and their Solutions' },
  { table: { caption: 'Main development problems and solutions', widths: [3.2, 5.8],
    head: ['Problem', 'Solution'],
    rows: [
      ['Free-tier API limits and overload (503 errors) interrupted answers and experiments', 'Waiting out per-minute limits, fallback models, and evaluation scripts that resume where they stopped'],
      ['The model counted overdue orders in a list cut off at 20 rows (1 instead of 7)', 'List tools return totals over all matching rows and a note when rows were cut off'],
      ['The model stated figures and a supplier without calling any tool', 'Answers with figures but no tool call are sent back once; untraced figures are shown as unverified'],
      ['The model announced a draft without creating it, and misdescribed the user\'s rights', 'The user\'s rights are stated with each question; the model is told to call the tool rather than say it will'],
      ['After a supplier was refused, the model drafted from another supplier without asking', 'Substitute suppliers are refused for the rest of the message'],
      ['The pattern verifier recognised only 12 kinds of statement', 'TRACE: LLM extraction into a typed language, deterministic verification'],
      ['The extractor attached products the text did not name, and confused similar terms', 'Grounding of subjects, ambiguous-term groups and type checks'],
      ['The MiniCheck baseline scored every sentence as supported', 'A tokenisation bug ("0" is two tokens in its vocabulary) was found and fixed, and all scores were recomputed'],
    ] } },

  { h2: '5.10 Summary' },
  { p: 'This chapter described how IntelliERP was developed: deterministic analytics with evidence, permission-checked tool calling, grounding generated from the code, figure tracing and pattern checking, TRACE, and controlled actions with separation of duties. Together they implement the two defences of the project: prevention by grounding and detection by verification. The next chapter tests and evaluates them.' },
];
