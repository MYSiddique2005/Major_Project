# TRACE on the development sets

Extraction: gemini-3.5-flash-lite, prompt trace-extract-2. A detection is a contradiction the rewrite introduced; a false alarm is one a paraphrase introduced. In-scope means within the version-3 checker's claim kinds (hand classification in results/claims).

## perturbations-v2-test (1 paraphrase that changed the meaning: left out)

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 22 of 59 (37%, 95% CI 26%-50%) | 21 of 25 (84%, 95% CI 65%-94%) | 0 of 59 (0%, 95% CI 0%-6%) |
| TRACE-rule | 23 of 59 (39%, 95% CI 28%-52%) | 21 of 25 (84%, 95% CI 65%-94%) | 0 of 59 (0%, 95% CI 0%-6%) |
| TRACE-model | 30 of 59 (51%, 95% CI 38%-63%) | 15 of 25 (60%, 95% CI 41%-77%) | 2 of 59 (3%, 95% CI 1%-12%) |
| TRACE-hybrid | 37 of 59 (63%, 95% CI 50%-74%) | 22 of 25 (88%, 95% CI 70%-96%) | 2 of 59 (3%, 95% CI 1%-12%) |

## test-v3 (1 paraphrase that changed the meaning: left out)

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 25 of 60 (42%, 95% CI 30%-54%) | 25 of 31 (81%, 95% CI 64%-91%) | 2 of 59 (3%, 95% CI 1%-12%) |
| TRACE-rule | 28 of 60 (47%, 95% CI 35%-59%) | 25 of 31 (81%, 95% CI 64%-91%) | 2 of 59 (3%, 95% CI 1%-12%) |
| TRACE-model | 32 of 60 (53%, 95% CI 41%-65%) | 21 of 31 (68%, 95% CI 50%-81%) | 2 of 59 (3%, 95% CI 1%-12%) |
| TRACE-hybrid | 38 of 60 (63%, 95% CI 51%-74%) | 27 of 31 (87%, 95% CI 71%-95%) | 4 of 59 (7%, 95% CI 3%-16%) |

## test-v3b

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 23 of 64 (36%, 95% CI 25%-48%) | 23 of 31 (74%, 95% CI 57%-86%) | 0 of 64 (0%, 95% CI 0%-6%) |
| TRACE-rule | 28 of 64 (44%, 95% CI 32%-56%) | 23 of 31 (74%, 95% CI 57%-86%) | 0 of 64 (0%, 95% CI 0%-6%) |
| TRACE-model | 33 of 64 (52%, 95% CI 40%-63%) | 20 of 31 (65%, 95% CI 47%-79%) | 3 of 64 (5%, 95% CI 2%-13%) |
| TRACE-hybrid | 40 of 64 (62%, 95% CI 50%-73%) | 25 of 31 (81%, 95% CI 64%-91%) | 3 of 64 (5%, 95% CI 2%-13%) |

## All three sets

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 70 of 183 (38%, 95% CI 32%-45%) | 69 of 87 (79%, 95% CI 70%-86%) | 2 of 182 (1%, 95% CI 0%-4%) |
| TRACE-rule | 79 of 183 (43%, 95% CI 36%-50%) | 69 of 87 (79%, 95% CI 70%-86%) | 2 of 182 (1%, 95% CI 0%-4%) |
| TRACE-model | 95 of 183 (52%, 95% CI 45%-59%) | 56 of 87 (64%, 95% CI 54%-74%) | 7 of 182 (4%, 95% CI 2%-8%) |
| TRACE-hybrid | 115 of 183 (63%, 95% CI 56%-70%) | 74 of 87 (85%, 95% CI 76%-91%) | 9 of 182 (5%, 95% CI 3%-9%) |
