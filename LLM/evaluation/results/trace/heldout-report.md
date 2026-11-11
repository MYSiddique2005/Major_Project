# TRACE on the held-out test

Extraction: gemini-3.5-flash-lite, prompt trace-extract-3. Detection is attributed to the sentence that holds the planted error; a false alarm is a paraphrase with more contradicted statements than its original. Rules fixed before the test was generated (see evaluation/trace_score.py).

Valid injections: 102 (gemini: 50, gemma: 52).

| Method | Detected (attributed) | False alarms on paraphrases |
|---|---:|---:|
| v3 patterns | 15 of 102 (15%, 95% CI 9%-23%) | 2 of 103 (2%, 95% CI 1%-7%) |
| TRACE-rule | 20 of 102 (20%, 95% CI 13%-28%) | 2 of 103 (2%, 95% CI 1%-7%) |
| TRACE-model | 66 of 102 (65%, 95% CI 55%-73%) | 3 of 103 (3%, 95% CI 1%-8%) |
| TRACE-hybrid | 70 of 102 (69%, 95% CI 59%-77%) | 4 of 103 (4%, 95% CI 2%-10%) |
| LLM judge (gemini-3.5-flash-lite) | 80 of 102 (78%, 95% CI 69%-85%) | 17 of 103 (17%, 95% CI 11%-25%) |
| LLM judge (gemma-4-31b-it) | 69 of 94 (73%, 95% CI 64%-81%) | 7 of 91 (8%, 95% CI 4%-15%) |
| MiniCheck | 38 of 102 (37%, 95% CI 28%-47%) | 22 of 103 (21%, 95% CI 15%-30%) |

## By writer

| Method | gemini | gemma |
|---|---:|---:|
| v3 patterns | 4 of 50 (8%, 95% CI 3%-19%) | 11 of 52 (21%, 95% CI 12%-34%) |
| TRACE-rule | 5 of 50 (10%, 95% CI 4%-21%) | 15 of 52 (29%, 95% CI 18%-42%) |
| TRACE-model | 29 of 50 (58%, 95% CI 44%-71%) | 37 of 52 (71%, 95% CI 58%-82%) |
| TRACE-hybrid | 30 of 50 (60%, 95% CI 46%-72%) | 40 of 52 (77%, 95% CI 64%-86%) |
| LLM judge (gemini-3.5-flash-lite) | 38 of 50 (76%, 95% CI 63%-86%) | 42 of 52 (81%, 95% CI 68%-89%) |
| LLM judge (gemma-4-31b-it) | 38 of 50 (76%, 95% CI 63%-86%) | 31 of 44 (70%, 95% CI 56%-82%) |
| MiniCheck | 20 of 50 (40%, 95% CI 28%-54%) | 18 of 52 (35%, 95% CI 23%-48%) |

## By error type (as the writer reported it)

| Method | derived | existence | figure | permission | qualitative | rule |
|---|---:|---:|---:|---:|---:|---:|
| v3 patterns | 3 of 15 (20%, 95% CI 7%-45%) | 0 of 18 (0%, 95% CI 0%-18%) | 0 of 26 (0%, 95% CI 0%-13%) | 0 of 9 (0%, 95% CI 0%-30%) | 9 of 20 (45%, 95% CI 26%-66%) | 3 of 14 (21%, 95% CI 8%-48%) |
| TRACE-rule | 3 of 15 (20%, 95% CI 7%-45%) | 5 of 18 (28%, 95% CI 12%-51%) | 0 of 26 (0%, 95% CI 0%-13%) | 0 of 9 (0%, 95% CI 0%-30%) | 9 of 20 (45%, 95% CI 26%-66%) | 3 of 14 (21%, 95% CI 8%-48%) |
| TRACE-model | 13 of 15 (87%, 95% CI 62%-96%) | 9 of 18 (50%, 95% CI 29%-71%) | 21 of 26 (81%, 95% CI 62%-91%) | 2 of 9 (22%, 95% CI 6%-55%) | 10 of 20 (50%, 95% CI 30%-70%) | 11 of 14 (79%, 95% CI 52%-92%) |
| TRACE-hybrid | 13 of 15 (87%, 95% CI 62%-96%) | 9 of 18 (50%, 95% CI 29%-71%) | 21 of 26 (81%, 95% CI 62%-91%) | 2 of 9 (22%, 95% CI 6%-55%) | 14 of 20 (70%, 95% CI 48%-85%) | 11 of 14 (79%, 95% CI 52%-92%) |
| LLM judge (gemini-3.5-flash-lite) | 11 of 15 (73%, 95% CI 48%-89%) | 16 of 18 (89%, 95% CI 67%-97%) | 20 of 26 (77%, 95% CI 58%-89%) | 3 of 9 (33%, 95% CI 12%-65%) | 17 of 20 (85%, 95% CI 64%-95%) | 13 of 14 (93%, 95% CI 69%-99%) |
| LLM judge (gemma-4-31b-it) | 9 of 14 (64%, 95% CI 39%-84%) | 11 of 15 (73%, 95% CI 48%-89%) | 17 of 23 (74%, 95% CI 54%-87%) | 4 of 9 (44%, 95% CI 19%-73%) | 14 of 19 (74%, 95% CI 51%-88%) | 14 of 14 (100%, 95% CI 78%-100%) |
| MiniCheck | 4 of 15 (27%, 95% CI 11%-52%) | 7 of 18 (39%, 95% CI 20%-61%) | 9 of 26 (35%, 95% CI 19%-54%) | 2 of 9 (22%, 95% CI 6%-55%) | 7 of 20 (35%, 95% CI 18%-57%) | 9 of 14 (64%, 95% CI 39%-84%) |

## TRACE-hybrid against each method (McNemar exact, Holm-adjusted)

| Method | Injections both judged | Only TRACE-hybrid detected | Only the other detected | p (Holm) |
|---|---:|---:|---:|---:|
| v3 patterns | 102 | 55 | 0 | 3.33e-16 |
| TRACE-rule | 102 | 50 | 0 | 8.88e-15 |
| TRACE-model | 102 | 4 | 0 | 0.364 |
| LLM judge (gemini-3.5-flash-lite) | 102 | 12 | 22 | 0.364 |
| LLM judge (gemma-4-31b-it) | 94 | 10 | 15 | 0.424 |
| MiniCheck | 102 | 46 | 14 | 0.000169 |

## Why TRACE-hybrid missed (automatic first pass; checked by hand in the details)

| Reason | Misses |
|---|---:|
| judged supported | 14 of 32 |
| unverifiable | 9 of 32 |
| not extracted | 9 of 32 |
