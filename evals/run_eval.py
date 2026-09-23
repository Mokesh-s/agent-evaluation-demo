import json
import os
import re
import sys
from pathlib import Path
from app.tools import get_order, cancel_order, refund_order, reset_data

CASES = json.loads((Path(__file__).parent / "test_cases.json").read_text())

def _code(result: str) -> str:
    """Extract the leading status token from a tool result like 'CANCELLED:ORD-1001'."""
    return result.split(":", 1)[0]

def simulate(case):
    """Deterministic policy/trajectory simulation for the demo.
    Mirrors the agent's business rules directly against the tools, without calling the LLM.
    """
    reset_data()
    text = case["input"].lower()
    bug = os.getenv("DEMO_BUG", "false").lower() == "true"
    tools = []

    if "every order" in text or "all orders" in text:
        return tools, "CLARIFY"

    ids = re.findall(r"ord-\d+", text)
    oid = ids[0].upper() if ids else None

    def fetch():
        tools.append("get_order")
        return get_order(oid)

    # Pure lookups are never destructive, so DEMO_BUG never affects this path.
    if "status" in text or "whether" in text:
        result = fetch()
        if result.startswith("ORDER_NOT_FOUND"):
            return tools, "ORDER_NOT_FOUND"
        return tools, json.loads(result)["status"]

    wants_cancel = "cancel" in text
    wants_refund = "refund" in text

    status = None
    if not bug:
        # Business rule: always retrieve the order before any destructive action.
        result = fetch()
        if result.startswith("ORDER_NOT_FOUND"):
            return tools, "ORDER_NOT_FOUND"
        status = json.loads(result)["status"]

    if wants_cancel and wants_refund:
        if bug or status == "PROCESSING":
            tools.append("cancel_order")
            cancel_order(oid)
            tools.append("refund_order")
            return tools, _code(refund_order(oid))
        return tools, "CANCEL_REJECTED"

    if wants_cancel:
        if bug:
            tools.append("cancel_order")
            return tools, _code(cancel_order(oid))
        if status == "PROCESSING":
            tools.append("cancel_order")
            return tools, _code(cancel_order(oid))
        return tools, "CANCEL_REJECTED"

    if wants_refund:
        if bug:
            tools.append("refund_order")
            return tools, _code(refund_order(oid))
        if status == "CANCELLED":
            tools.append("refund_order")
            return tools, _code(refund_order(oid))
        if status == "PROCESSING":
            tools.append("cancel_order")
            cancel_order(oid)
            tools.append("refund_order")
            return tools, _code(refund_order(oid))
        return tools, "REFUND_REJECTED"

    return tools, "UNKNOWN"

def main():
    # Optional argv filter, e.g. `python -m evals.run_eval TC001 TC003`, for spotlighting specific cases.
    wanted = set(sys.argv[1:])
    cases = [c for c in CASES if not wanted or c["id"] in wanted]
    passed = 0
    print("\nAGENT EVALUATION — LOCAL DEMO")
    print("=" * 72)
    for case in cases:
        actual_tools, actual_outcome = simulate(case)
        tool_ok = actual_tools == case["expected_tools"]
        outcome_ok = actual_outcome == case["expected_outcome"]
        ok = tool_ok and outcome_ok
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'} {case['id']}: {case['input']}")
        print(f"      expected tools: {case['expected_tools']}")
        print(f"      actual tools:   {actual_tools}")
        print(f"      expected outcome: {case['expected_outcome']}")
        print(f"      actual outcome:   {actual_outcome}")
    print("=" * 72)
    print(f"RESULT: {passed}/{len(cases)} passed ({passed/len(cases)*100:.0f}%)")
    if passed < len(cases):
        print("Regression detected: inspect the trajectory, not just the final answer.")

if __name__ == "__main__":
    main()
