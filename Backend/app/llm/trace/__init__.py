"""TRACE: Typed Run-time Assertion Checking for Enterprise assistants.

Each factual sentence an assistant writes is treated as a run-time assertion about the business, in a
typed language (catalogue.py), and evaluated by the system's own tested code against the source that is
authoritative for it (facts.py, policy.py): the database for state, the analytics for derived values,
the code's constants and the permission map for rules. The model may extract assertions
(extract_llm.py), but it never decides whether one is true (verify.py).

    from app.llm.trace import FactSource, TraceVerifier
    result = TraceVerifier(source, checker, provider, mode="hybrid", role=user.role).check(answer)
    result.contradicted()  # verdicts the data contradicts, each with what the data says
"""
from app.llm.trace.engine import TraceResult, TraceVerifier
from app.llm.trace.facts import FactSource
from app.llm.trace.schema import Assertion, Verdict

__all__ = ["Assertion", "FactSource", "TraceResult", "TraceVerifier", "Verdict"]
