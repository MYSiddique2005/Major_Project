# Natural errors in the stored answers

686 of 686 pooled sentences labelled by annotator 1; 0 by annotator 2.

## all answers

| Method | Precision of flags | Recall on the random sample |
|---|---:|---:|
| LLM judge (gemini-3.5-flash-lite) | 28 of 117 (24%, 95% CI 17%-32%) | 10 of 19 (53%, 95% CI 32%-73%) |
| MiniCheck | 41 of 503 (8%, 95% CI 6%-11%) | 14 of 19 (74%, 95% CI 51%-88%) |
| LLM judge (gemma-4-31b-it) | 25 of 145 (17%, 95% CI 12%-24%) | 11 of 14 (79%, 95% CI 52%-92%) |
| TRACE-model | 12 of 78 (15%, 95% CI 9%-25%) | 4 of 19 (21%, 95% CI 9%-43%) |
| TRACE-hybrid | 12 of 78 (15%, 95% CI 9%-25%) | 4 of 19 (21%, 95% CI 9%-43%) |
| v3 patterns | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 19 (11%, 95% CI 3%-31%) |
| TRACE-rule | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 19 (11%, 95% CI 3%-31%) |

False sentences in the random sample: 19 of 300 (6%, 95% CI 4%-10%).

## answers TRACE was developed on

| Method | Precision of flags | Recall on the random sample |
|---|---:|---:|
| LLM judge (gemini-3.5-flash-lite) | 12 of 74 (16%, 95% CI 10%-26%) | 3 of 9 (33%, 95% CI 12%-65%) |
| MiniCheck | 33 of 366 (9%, 95% CI 6%-12%) | 9 of 9 (100%, 95% CI 70%-100%) |
| LLM judge (gemma-4-31b-it) | 11 of 67 (16%, 95% CI 9%-27%) | 4 of 5 (80%, 95% CI 38%-96%) |
| TRACE-model | 9 of 66 (14%, 95% CI 7%-24%) | 4 of 9 (44%, 95% CI 19%-73%) |
| TRACE-hybrid | 9 of 66 (14%, 95% CI 7%-24%) | 4 of 9 (44%, 95% CI 19%-73%) |
| v3 patterns | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 9 (22%, 95% CI 6%-55%) |
| TRACE-rule | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 9 (22%, 95% CI 6%-55%) |

False sentences in the random sample: 9 of 148 (6%, 95% CI 3%-11%).

## answers TRACE never saw (Gemma run)

| Method | Precision of flags | Recall on the random sample |
|---|---:|---:|
| LLM judge (gemini-3.5-flash-lite) | 0 of 12 (0%, 95% CI 0%-24%) | - |
| MiniCheck | 0 of 91 (0%, 95% CI 0%-4%) | - |
| LLM judge (gemma-4-31b-it) | 0 of 49 (0%, 95% CI 0%-7%) | - |
| TRACE-model | 0 of 6 (0%, 95% CI 0%-39%) | - |
| TRACE-hybrid | 0 of 6 (0%, 95% CI 0%-39%) | - |
| v3 patterns | - | - |
| TRACE-rule | - | - |

False sentences in the random sample: 0 of 55 (0%, 95% CI 0%-7%).
