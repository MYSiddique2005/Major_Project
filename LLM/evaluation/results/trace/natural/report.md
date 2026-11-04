# Natural errors in the stored answers

435 of 435 pooled sentences labelled by annotator 1; 0 by annotator 2.

## all answers

| Method | Precision of flags | Recall on the random sample |
|---|---:|---:|
| LLM judge (gemma-4-31b-it) | - | - |
| LLM judge (gemini-3.5-flash-lite) | 24 of 117 (21%, 95% CI 14%-29%) | 10 of 14 (71%, 95% CI 45%-88%) |
| MiniCheck | - | - |
| TRACE-model | 12 of 78 (15%, 95% CI 9%-25%) | 4 of 14 (29%, 95% CI 12%-55%) |
| TRACE-hybrid | 12 of 78 (15%, 95% CI 9%-25%) | 4 of 14 (29%, 95% CI 12%-55%) |
| v3 patterns | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 14 (14%, 95% CI 4%-40%) |
| TRACE-rule | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 14 (14%, 95% CI 4%-40%) |

False sentences in the random sample: 14 of 300 (5%, 95% CI 3%-8%).

## answers TRACE was developed on

| Method | Precision of flags | Recall on the random sample |
|---|---:|---:|
| LLM judge (gemma-4-31b-it) | - | - |
| LLM judge (gemini-3.5-flash-lite) | 8 of 74 (11%, 95% CI 6%-20%) | 3 of 4 (75%, 95% CI 30%-95%) |
| MiniCheck | - | - |
| TRACE-model | 9 of 66 (14%, 95% CI 7%-24%) | 4 of 4 (100%, 95% CI 51%-100%) |
| TRACE-hybrid | 9 of 66 (14%, 95% CI 7%-24%) | 4 of 4 (100%, 95% CI 51%-100%) |
| v3 patterns | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 4 (50%, 95% CI 15%-85%) |
| TRACE-rule | 2 of 2 (100%, 95% CI 34%-100%) | 2 of 4 (50%, 95% CI 15%-85%) |

False sentences in the random sample: 4 of 148 (3%, 95% CI 1%-7%).

## answers TRACE never saw (Gemma run)

| Method | Precision of flags | Recall on the random sample |
|---|---:|---:|
| LLM judge (gemma-4-31b-it) | - | - |
| LLM judge (gemini-3.5-flash-lite) | 0 of 12 (0%, 95% CI 0%-24%) | - |
| MiniCheck | - | - |
| TRACE-model | 0 of 6 (0%, 95% CI 0%-39%) | - |
| TRACE-hybrid | 0 of 6 (0%, 95% CI 0%-39%) | - |
| v3 patterns | - | - |
| TRACE-rule | - | - |

False sentences in the random sample: 0 of 55 (0%, 95% CI 0%-7%).
