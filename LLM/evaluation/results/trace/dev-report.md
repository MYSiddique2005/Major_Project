# TRACE on the development sets

Extraction: gemini-3.5-flash-lite, prompt trace-extract-3. A detection is a contradiction the rewrite introduced; a false alarm is one a paraphrase introduced. In-scope means within the version-3 checker's claim kinds (hand classification in results/claims).

## perturbations-v2-test (1 paraphrase that changed the meaning: left out)

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 22 of 59 (37%, 95% CI 26%-50%) | 21 of 25 (84%, 95% CI 65%-94%) | 0 of 59 (0%, 95% CI 0%-6%) |
| TRACE-rule | 23 of 59 (39%, 95% CI 28%-52%) | 21 of 25 (84%, 95% CI 65%-94%) | 0 of 59 (0%, 95% CI 0%-6%) |
| TRACE-model | 38 of 59 (64%, 95% CI 52%-75%) | 20 of 25 (80%, 95% CI 61%-91%) | 1 of 59 (2%, 95% CI 0%-9%) |
| TRACE-hybrid | 41 of 59 (69%, 95% CI 57%-80%) | 23 of 25 (92%, 95% CI 75%-98%) | 1 of 59 (2%, 95% CI 0%-9%) |

## test-v3 (1 paraphrase that changed the meaning: left out)

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 25 of 60 (42%, 95% CI 30%-54%) | 25 of 31 (81%, 95% CI 64%-91%) | 2 of 59 (3%, 95% CI 1%-12%) |
| TRACE-rule | 28 of 60 (47%, 95% CI 35%-59%) | 25 of 31 (81%, 95% CI 64%-91%) | 2 of 59 (3%, 95% CI 1%-12%) |
| TRACE-model | 37 of 60 (62%, 95% CI 49%-73%) | 23 of 31 (74%, 95% CI 57%-86%) | 5 of 59 (8%, 95% CI 4%-18%) |
| TRACE-hybrid | 42 of 60 (70%, 95% CI 57%-80%) | 28 of 31 (90%, 95% CI 75%-97%) | 7 of 59 (12%, 95% CI 6%-23%) |

## test-v3b

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 23 of 64 (36%, 95% CI 25%-48%) | 23 of 31 (74%, 95% CI 57%-86%) | 0 of 64 (0%, 95% CI 0%-6%) |
| TRACE-rule | 28 of 64 (44%, 95% CI 32%-56%) | 23 of 31 (74%, 95% CI 57%-86%) | 0 of 64 (0%, 95% CI 0%-6%) |
| TRACE-model | 37 of 64 (58%, 95% CI 46%-69%) | 23 of 31 (74%, 95% CI 57%-86%) | 4 of 64 (6%, 95% CI 2%-15%) |
| TRACE-hybrid | 43 of 64 (67%, 95% CI 55%-77%) | 27 of 31 (87%, 95% CI 71%-95%) | 4 of 64 (6%, 95% CI 2%-15%) |

## All three sets

| Method | Detected, all valid | Detected, in scope | False alarms |
|---|---:|---:|---:|
| v3 patterns | 70 of 183 (38%, 95% CI 32%-45%) | 69 of 87 (79%, 95% CI 70%-86%) | 2 of 182 (1%, 95% CI 0%-4%) |
| TRACE-rule | 79 of 183 (43%, 95% CI 36%-50%) | 69 of 87 (79%, 95% CI 70%-86%) | 2 of 182 (1%, 95% CI 0%-4%) |
| TRACE-model | 112 of 183 (61%, 95% CI 54%-68%) | 66 of 87 (76%, 95% CI 66%-84%) | 10 of 182 (5%, 95% CI 3%-10%) |
| TRACE-hybrid | 126 of 183 (69%, 95% CI 62%-75%) | 78 of 87 (90%, 95% CI 81%-94%) | 12 of 182 (7%, 95% CI 4%-11%) |
