import os
from evals.run_eval import simulate, CASES

def test_happy_path():
    case = next(c for c in CASES if c["id"] == "TC001")
    tools, outcome = simulate(case)
    assert tools == case["expected_tools"]
    assert outcome == case["expected_outcome"]

def test_shipped_order_is_not_cancelled():
    case = next(c for c in CASES if c["id"] == "TC002")
    tools, outcome = simulate(case)
    assert tools == ["get_order"]
    assert outcome == "CANCEL_REJECTED"

def test_bulk_destructive_request_requires_clarification():
    case = next(c for c in CASES if c["id"] == "TC005")
    tools, outcome = simulate(case)
    assert tools == []
    assert outcome == "CLARIFY"

def test_bug_mode_detects_wrong_trajectory():
    os.environ["DEMO_BUG"] = "true"
    case = next(c for c in CASES if c["id"] == "TC001")
    tools, outcome = simulate(case)
    assert tools != case["expected_tools"]
    os.environ["DEMO_BUG"] = "false"
