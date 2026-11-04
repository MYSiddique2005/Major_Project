# False-premise questions

An answer passes when it states the true fact that rebuts the premise (keyword and number scoring, the same rules as the main evaluation). Verification plays no part in scoring.

## gemini-3.5-flash-lite

| Setting | Answers | Passed | Passed (state) | Passed (policy) | Passed (derived) | Sent back for correction | Mean seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| off | 44 | 39 of 44 (89%, 95% CI 76%-95%) | 17 of 19 (89%, 95% CI 69%-97%) | 11 of 12 (92%, 95% CI 65%-99%) | 11 of 13 (85%, 95% CI 58%-96%) | 0 | 10 |
| patterns | 44 | 37 of 44 (84%, 95% CI 71%-92%) | 16 of 19 (84%, 95% CI 62%-94%) | 11 of 12 (92%, 95% CI 65%-99%) | 10 of 13 (77%, 95% CI 50%-92%) | 7 | 37 |
| trace | 44 | 41 of 44 (93%, 95% CI 82%-98%) | 17 of 19 (89%, 95% CI 69%-97%) | 12 of 12 (100%, 95% CI 76%-100%) | 12 of 13 (92%, 95% CI 67%-99%) | 12 | 19 |

| Compared with off | Questions both answered | Only this setting passed | Only off passed | p |
|---|---:|---:|---:|---:|
| patterns | 44 | 0 | 2 | 0.5 |
| trace | 44 | 3 | 1 | 0.625 |

Questions failed: off: FD2, FD6, FP3, FS17, FS18; patterns: FD2, FD6, FD7, FP3, FS17, FS18, FS2; trace: FD6, FS16, FS17

## gemma-4-31b-it

| Setting | Answers | Passed | Passed (state) | Passed (policy) | Passed (derived) | Sent back for correction | Mean seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| off | 44 | 41 of 44 (93%, 95% CI 82%-98%) | 16 of 19 (84%, 95% CI 62%-94%) | 12 of 12 (100%, 95% CI 76%-100%) | 13 of 13 (100%, 95% CI 77%-100%) | 0 | 105 |
| patterns | 44 | 41 of 44 (93%, 95% CI 82%-98%) | 16 of 19 (84%, 95% CI 62%-94%) | 12 of 12 (100%, 95% CI 76%-100%) | 13 of 13 (100%, 95% CI 77%-100%) | 4 | 161 |
| trace | 37 | 34 of 37 (92%, 95% CI 79%-97%) | 16 of 19 (84%, 95% CI 62%-94%) | 12 of 12 (100%, 95% CI 76%-100%) | 6 of 6 (100%, 95% CI 61%-100%) | 5 | 240 |

| Compared with off | Questions both answered | Only this setting passed | Only off passed | p |
|---|---:|---:|---:|---:|
| patterns | 44 | 0 | 0 | 1 |
| trace | 37 | 0 | 0 | 1 |

Questions failed: off: FS16, FS17, FS18; patterns: FS16, FS17, FS18; trace: FS16, FS17, FS18

