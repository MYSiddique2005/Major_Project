# Evaluation report: after-fix

1 answers (1 grounded, 0 ungrounded). Models that answered: gemini-3.5-flash-lite (1).
Collected between 2026-10-06T13:08:59 and 2026-10-06T13:08:59.

## Results with grounding (the system as built)

| Group | Questions | Passed | Facts found | Right tool used | Unsupported figures | Avg time | Avg tool calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grounding (terms and rules) | 0 | - | - | - | - | - | - |
| Factual (one module) | 0 | - | - | - | - | - | - |
| Cross-module reasoning | 0 | - | - | - | - | - | - |
| Controlled actions and permissions | 1 | 100% | 100% | - | 0 of 0 | 2s | 0.0 |
| Abstention (data cannot answer) | 0 | - | - | - | - | - | - |
| **All** | 1 | 100% | 100% | - | 0 of 0 | 2s | 0.0 |

## Effect of grounding (RQ1)

No question has been answered in both conditions yet.

## Proactive insights (RQ3)

From the 8 insights stored by 2 completed scans (1 scans failed, mostly on rate limits).

| Measure | Result |
|---|---|
| Insights whose subject was a finding the analytics had flagged | 8 of 8 (enforced by the server) |
| Evidence from two or more modules | 8 of 8 |
| Figures in the text found in the system data | 114 of 114 |
| Reorder insights whose quantity equals the reorder rule | 1 of 1 |
| Actions recommended | expedite_delivery: 7, reorder: 1 |

Detection itself (which products and suppliers are flagged) is done by the rule-based analytics, so its precision and recall are properties of those rules, not of the model. What the model adds, and what is measured here, is the explanation and the recommended action.

## Every answer

| Case | Condition | Role | Result | Facts | Tools called | Unsupported figures | Model |
|---|---|---|---|---|---|---|---|
| A3 | grounded | procurement | pass | 1/1 | - | - | gemini-3.5-flash-lite |

## How to read this

- **Passed** means every expected fact was found, a tool that can answer the question was used, nothing forbidden happened, and (for action cases) the right thing was or was not done.
- **Facts found** are matched by number (within 1%) or by phrase. A correct answer worded in a way the phrase list does not anticipate is marked as missing, so pass rates can understate.
- **Unsupported figures** are numbers in an answer that appear in none of the question, the tool results and the knowledge passages. Figures the model derives by arithmetic count as unsupported; the check cannot tell a derived figure from an invented one, or a real figure used in the wrong place.
- Each question was asked once per condition. The model is not deterministic, so a single run is one sample.
- When more than one model answered, differences between questions are partly differences between models.
