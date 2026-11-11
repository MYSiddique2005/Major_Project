# LLM judge repeatability: the same texts asked twice

The first 50 distinct held-out texts written by Gemini, same prompt and evidence, temperature 0.

| Judge | Texts with both runs | Same flag decision | Same set of contradicted statements | Same set, among texts flagged in either run |
|---|---:|---:|---:|---:|
| gemini-3.5-flash-lite | 50 | 47 | 34 | 12 of 28 |
| gemma-4-31b-it | 0 | 0 | 0 | 0 of 0 |
