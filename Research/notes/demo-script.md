# IntelliERP demo script (about 5 minutes)

For a screen recording or a live demo in the viva. Record with any screen recorder (on Ubuntu: press
`Ctrl+Shift+Alt+R` to start and stop GNOME's built-in recorder, or use OBS Studio). Use a browser window of
about 1280x800 and zoom to 110% so text is readable.

## Before recording

```bash
cd ~/Major_Project/Backend && ./scripts/dev_db.sh start
source .venv/bin/activate && uvicorn app.main:app --reload        # terminal 1
cd ~/Major_Project/Frontend && npm run dev                       # terminal 2
```

Open http://localhost:5173. The assistant needs the Gemini key in `Backend/.env`; ask each question once
before recording so you know the free tier is answering (it can take up to a minute when busy).

## Scenes

| # | Time | Log in as | Show | Say |
|---|---|---|---|---|
| 1 | 0:00 | `admin` / `admin123` | Dashboard | "IntelliERP brings sales, inventory and procurement into one system. The data is Microsoft's Wide World Importers: 227 products, 72,696 sales lines." |
| 2 | 0:30 | admin | Analytics: open a product at Critical risk | "Risk is decided by fixed rules, not by the AI: stock, safety stock, demand trend, lead time and deliveries due." |
| 3 | 1:00 | admin | AI Insights | "A scheduled scan takes every High or Critical finding and has the AI explain it with evidence from several modules. The AI cannot raise an insight the analytics did not flag." |
| 4 | 1:30 | log out, `procurement` / `procurement123` | AI Assistant: ask *"Should we reorder P082 now? Recommend a quantity."* | "The assistant calls permission-checked tools, never writes SQL, and every figure and statement is checked against the data." Point at: *All 20 figures match*, *All 5 statements agree*, the evidence by module, *Data used* and *Company rules consulted*. |
| 5 | 2:30 | procurement | Click *Create draft purchase order*, then open Procurement | "The only thing the AI can create is a draft. It passes the same validation as any order and records that it came from the AI." |
| 6 | 3:00 | procurement | Try to approve your own submitted order | "A different user must approve it: separation of duties." |
| 7 | 3:30 | `employee` / `employee123` | AI page is not available; ask nothing | "Roles limit what each user, and the AI acting for them, can see." |
| 8 | 4:00 | — | Settings page (version 1.0), then the poster's held-out chart | "Grounding cut false statements in the assistant's own answers from 25.9% to 2.4%. On 102 errors written after it was frozen, TRACE detected 69% with false alarms on 4% of correct texts; every miss could be traced to its cause. 272 automated tests pass." |

## If something goes wrong

- *The assistant is slow or says the model is busy:* the free tier is overloaded; wait a minute and ask again,
  or show the screenshot in `Research/paper/figures/recommendation.png`.
- *Empty pages:* the database is not running; run `./scripts/dev_db.sh start`.
