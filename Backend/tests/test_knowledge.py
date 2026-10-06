"""Enterprise grounding: the knowledge base, its retrieval, and how the assistant uses it."""
import pytest

from app.api.deps import get_knowledge
from app.db.base import Base
from app.knowledge.base import CATEGORIES, tokenize
from app.knowledge.content import COLUMN_DESCRIPTIONS, TABLE_DESCRIPTIONS, get_knowledge_base
from app.main import app
from app.models.enums import Role
from tests.conftest import API
from tests.test_ai import ask, call, llm, reply  # noqa: F401  (llm is a fixture)

KB = get_knowledge_base()


def test_every_table_and_column_is_described():
    """A column added to the database without a description here fails, so the schema passages cannot fall behind."""
    for table in Base.metadata.sorted_tables:
        assert table.name in TABLE_DESCRIPTIONS
        assert set(COLUMN_DESCRIPTIONS[table.name]) == {column.name for column in table.columns}, table.name
        passage = KB.get(f"schema.{table.name}").text
        assert all(f"- {column.name}" in passage for column in table.columns)


def test_entries_are_well_formed():
    assert {entry.category for entry in KB.entries} == set(CATEGORIES)
    assert all(KB.get(f"access.{role.value.lower()}") for role in Role)
    assert all(len(entry.text) > 80 and entry.title for entry in KB.entries)
    # The foreign keys of the schema are spelled out, which is what links the modules.
    assert "product_id (refers to products.id)" in KB.get("schema.sales_orders").text


def test_passages_state_the_numbers_the_code_uses():
    from app.analytics import demand, stock_risk

    assert f"last {demand.TREND_WINDOW_DAYS} days" in KB.get("def.avg-daily-demand").text
    assert f"{stock_risk.REVIEW_PERIOD_DAYS} days review period" in KB.get("rule.reorder-suggestion").text
    assert f"multiple of {stock_risk.ORDER_MULTIPLE}" in KB.get("rule.reorder-suggestion").text
    assert "procurement:approve" in KB.get("access.procurement_manager").text
    assert "procurement:view" not in KB.get("access.inventory_manager").text


def test_tokenizer_normalises_words():
    assert tokenize("Which suppliers are delivering orders late?") == ["supplier", "deliver", "order", "late"]
    assert tokenize("safety_stock") == ["safety", "stock"]


# Questions a user might ask, and the passage that answers each. The passage must rank in the top three.
RETRIEVAL_CASES = [
    ("What does safety stock mean?", "def.safety-stock"),
    ("What is the difference between reorder level and reorder point?", "def.reorder-level"),
    ("How long will our stock last?", "def.days-of-cover"),
    ("How is the demand trend worked out?", "def.avg-daily-demand"),
    ("How is lead time measured?", "def.lead-time"),
    ("What counts as inbound units?", "def.units-on-order"),
    ("How do you measure whether a supplier delivers on time?", "def.on-time-rate"),
    ("What is included in total revenue?", "def.revenue"),
    ("How do I work out the profit margin on a product?", "def.margin"),
    ("How accurate is the forecast?", "def.forecast-error"),
    ("What does Low Stock mean?", "rule.stock-status"),
    ("Why is a product at high risk of stockout?", "rule.stockout-risk"),
    ("How many units should we order?", "rule.reorder-suggestion"),
    ("Why is this supplier rated high risk?", "rule.supplier-risk"),
    ("What does the what-if scenario assume?", "rule.what-if"),
    ("What checks does a purchase order have to pass?", "rule.po-validation"),
    ("Can the assistant create a purchase order?", "rule.ai-assistant"),
    ("What does the status Ordered mean on a purchase order?", "flow.purchase-order"),
    ("Who can approve a purchase order?", "flow.approval"),
    ("What does Processing mean for a sales order?", "flow.sales-order"),
    ("How are sales, inventory and procurement connected?", "data.identifiers"),
    ("Is this real data or simulated?", "data.dataset"),
    ("What columns does the inventory table have?", "schema.inventory"),
    ("Which table stores the expected delivery date?", "schema.purchase_orders"),
    ("What can the inventory manager see?", "access.inventory_manager"),
    ("What is an employee allowed to do?", "access.employee"),
]


@pytest.mark.parametrize("question, expected", RETRIEVAL_CASES)
def test_retrieval_finds_the_passage_that_answers(question, expected):
    top = [match.entry.id for match in KB.search(question, limit=3)]
    assert expected in top, f"{question!r} retrieved {top}"


def test_retrieval_accuracy_overall():
    first = sum(KB.search(question, limit=1)[0].entry.id == expected for question, expected in RETRIEVAL_CASES)
    assert first / len(RETRIEVAL_CASES) >= 0.8  # the answering passage is ranked first for most questions


def test_search_ignores_unrelated_text_and_respects_category():
    assert KB.search("zzz qqq xylophone") == []
    assert all(match.entry.category == "schema" for match in KB.search("purchase order status", category="schema"))


def test_relevant_passages_are_given_to_the_model(client, auth, llm):
    scripted = llm(reply("Safety stock is a buffer."))
    body = ask(client, auth("admin"), "What does safety stock mean?").json()

    sent = scripted.conversations[0]
    assert '<passage id="def.safety-stock"' in sent.message and sent.message.endswith("What does safety stock mean?")
    assert "Company knowledge:" in sent.system
    assert "search_knowledge" in sent.tool_names
    assert body["knowledge"][0]["id"] == "def.safety-stock" and body["knowledge"][0]["score"] > 0
    assert len(body["knowledge"]) == 4


def test_follow_up_question_is_retrieved_with_the_question_before_it(client, auth, llm):
    llm(reply("ok"))
    history = [{"role": "user", "content": "What does safety stock mean?"}, {"role": "assistant", "content": "A buffer."}]
    body = ask(client, auth("admin"), "And why does it matter?", history=history).json()
    assert "def.safety-stock" in [entry["id"] for entry in body["knowledge"]]


def test_model_can_search_the_knowledge_base(client, auth, llm):
    scripted = llm(
        reply("", call("search_knowledge", {"query": "who can approve", "limit": 2})),
        reply("Procurement managers."),
    )
    ask(client, auth("inventory"), "hello")
    result = scripted.conversations[0].results[0][0]
    assert not result.is_error and result.content[0]["id"] == "flow.approval" and len(result.content) == 2


def test_grounding_can_be_switched_off(client, auth, llm):
    app.dependency_overrides[get_knowledge] = lambda: None
    try:
        scripted = llm(reply("ok"))
        body = ask(client, auth("admin"), "What does safety stock mean?").json()
    finally:
        app.dependency_overrides.pop(get_knowledge, None)
    sent = scripted.conversations[0]
    assert "<knowledge>" not in sent.message and "Company knowledge:" not in sent.system
    assert "search_knowledge" not in sent.tool_names
    assert body["knowledge"] == []


def test_knowledge_endpoint(client, auth):
    headers = auth("procurement")
    everything = client.get(f"{API}/ai/knowledge", headers=headers).json()
    assert len(everything) == len(KB.entries)
    rules = client.get(f"{API}/ai/knowledge", params={"category": "rule"}, headers=headers).json()
    assert rules and all(entry["category"] == "rule" for entry in rules)
    found = client.get(f"{API}/ai/knowledge", params={"search": "reorder quantity", "limit": 2}, headers=headers).json()
    assert len(found) == 2 and found[0]["score"] >= found[1]["score"]
    assert client.get(f"{API}/ai/knowledge", headers=auth("employee")).status_code == 403
