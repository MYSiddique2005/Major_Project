## About this run

The 86 questions (and the 32 asked again without the knowledge base) on the same system as `fixed-1` to
`fixed-3`, unchanged, on the open-weight `gemma-4-31b-it` through the Gemini API, with no fallback model.
Asked 17-18 October 2026; the run was interrupted once (the computer stopped) and continued without asking
any question twice. One run only: it shows whether the results depend on the model, not how consistent
Gemma is from run to run.

## Results

- With grounding: 86 of 86 (95% CI 96-100%), every group full.
- Paired questions: 32 of 32 with the knowledge base, 6 of 32 without (26 only with, none only without,
  p < 0.0001). Without it: 6 of the 7 cross-module questions, none of the 25 on terms and rules. One of
  the failures without it (G1) is the assistant running out of steps, not a wrong answer.
- Figures not found in the data: 1 of 251 with grounding, a correct difference of two projections (C4:
  328.4 - 246.8 = 81.6); 0 of 47 without.

## Read by hand

- **U11, grounded** (false premise: "why did P032 run out of stock last week?"; it is in stock): the answer
  gives the correct stock, 125 units, which is what the key checks, so it passed. It then says the product
  "experienced a temporary stockout last week" and "remained out of stock until" a delivery, reasoning from a
  few deliveries and weekly sales without knowing the stock on those days. The data does not show a stockout;
  this is an error the keyword scoring missed. The claim verifier (unchanged, sha256 36154591) flagged it,
  through "remained out of stock", a past-tense sentence it reads as a current claim; the catch is real but
  partly fortunate.
- C11, A4 and others read: correct.

## Not completed: gemini-3.8-flash

A run on `gemini-3.8-flash` was started at the same time. Its free tier allows 20 requests per day per
model, about 15 answers, so a full run would take two to three weeks; it was stopped after 15 answers and
is not reported.
