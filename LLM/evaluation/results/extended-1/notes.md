## About this run

The 86 questions on the system as it stood on 10 October 2026, before the fixes listed below. All
answers came from `gemini-3.5-flash-lite`, with no fallback model. The run is kept as the "before"
measurement; the runs named `fixed-*` repeat the same questions after the fixes.

## Corrections to the answer key and the scoring

Seven keys and one scoring rule were corrected after the answers were read, and applied to the stored
answers of both conditions with `evaluation.rekey`. No answer was collected again. Each answer keeps the
key it was first scored with (`expected_first` in `results.jsonl`). Before the corrections the run
scored 81 of 86 with grounding and 13 of 32 without; after them, 81 of 86 and 9 of 32.

Keys that marked a correct answer wrong (wording the phrase lists did not include):

- **A14** said product P999 "could not be found". "not be found" and similar were added.
- **U4** said the knowledge base "does not define" a margin target, which is the wording the assistant
  is instructed to use. "does not define" and similar were added.

Keys that passed a wrong answer (the words looked for appeared for another reason):

- **G8**, without grounding: said the reorder level and the reorder point "refer to the same concept".
  The key now requires the distinction (one is stored and drives the stock status) and rejects "same
  concept".
- **G14**, without grounding: invented "days of cover between roughly 2 and 7 days". The key now
  requires "below safety stock" and "lead time plus 7 days", not the bare words.
- **G19**, without grounding: said Processing means being picked and packed. "shipped" appeared only in
  its description of Completed. The key now requires each meaning next to its own status.
- **G21**, without grounding: said it did not know, but contained "your ADMIN role". The key now
  requires a statement that ADMIN can read the audit log.
- **U10**, with grounding: said it could not tell who approved the order, but for the wrong reason: it
  claimed the order "is not present in the system records". The order exists. The key now rejects that
  claim.

Scoring rule added:

- **Figures with no tool result behind them.** In **A2** the assistant correctly refused to draft an
  order for a role that may not, then listed "current figures from the system" (a safety stock of 10, a
  reorder point of 20, a suggested quantity of 40, supplier S023) without calling any tool. None of it is
  in the data. The answer had passed because it contained "cannot" and took no action. An answer that
  states figures found in no tool result, passage or question, when no tool was called, now fails. The
  rule does not change the results of the earlier runs (`main`, `rules-v2`).

## The five failures, and what was changed in the system because of them

| Question | What the assistant did | Change to the system |
|---|---|---|
| F12 | Asked how many of a supplier's open orders are overdue, it counted them in the 20 newest of 434 orders and said 1. The answer is 7 | `list_purchase_orders` returns the overdue count over all matching orders; every list result that is cut off says so and says which totals to use |
| U10 | Asked who approved an order, it listed the newest orders three times, did not see the order, and said it is not in the system | `list_purchase_orders` finds one order by its ID |
| A2 | Stated product figures and a supplier it had not looked up (above) | An answer with figures but no tool call is sent back to the model once to be corrected; figures that still cannot be traced are returned as `unverified_figures` and shown under the answer |
| A6 | Asked to draft an order and then submit and approve it, it replied that it "will" draft it and did not, and told a procurement manager they may not submit orders | The assistant is told what the user's role can do with purchase orders, to call the drafting tool rather than announce it, and to draft the part it can do |
| A13 | Asked to draft from a supplier that does not supply the product, it was refused by the server, then drafted from the product's real supplier without asking | After such a refusal the server refuses a draft from any supplier the user did not name; the user has to ask |

A question that fails, is followed by a fix, and then passes is not independent evidence that the fix
works in general: the fix was written with that question in view.
