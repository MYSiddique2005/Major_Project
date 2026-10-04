"""Seed data for the in-memory repositories (Phase 1 stand-in for a database).

All records are related: the same product/supplier IDs appear across products,
inventory, sales and procurement so cross-module questions have real answers.
Dates are generated relative to REFERENCE_DATE so the demo always looks current;
everything else is deterministic.
"""
from datetime import date

REFERENCE_DATE = date.today()
