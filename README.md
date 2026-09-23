Updated todo list

Here's a full runbook — commands plus exact talking points, matching the flow your own `README.md` already outlines, fleshed out with the two spotlight cases and the fixes we made along the way.

## 0. Set the stage (30 sec, no commands)
**Say:** *"This is a customer support agent built on Google ADK + Gemini. It has three tools — `get_order`, `cancel_order`, `refund_order` — and a system prompt with 7 business rules. Rule 5 says: always retrieve the order before cancelling or refunding it. Today I'll show you why that rule needs to be enforced by evaluation, not just trusted."*

## 1. Show the agent working normally
```bash
python -m app.cli "Cancel order ORD-1001"
```
**Point at the `TRACE:` output** — two tool calls: `get_order` then `cancel_order`.
**Say:** *"Notice the agent checks before it acts. That's rule 5 in practice."*

## 2. Run the deterministic eval suite — clean baseline
```bash
python -m evals.run_eval
```
**Expected:** `RESULT: 10/10 passed (100%)`
**Say:** *"This suite doesn't call the LLM at all — it's pure Python, deterministic, checking two things per case: did the right tools get called in the right order, and was the final outcome correct. Right now, everything matches expectations."*

## 3. Introduce the regression
**Say:** *"Now I'll simulate a bad prompt-engineering change — someone edits the system instruction and accidentally removes rule 5."*

Open `agent.py` and point at:
```python
if BUG:
    instruction = instruction.replace(
        "5. Always retrieve the order before any cancellation or refund.",
        "5. You may cancel an order directly without retrieving it first."
    )
```
**Say:** *"This is gated behind `DEMO_BUG=true` so I can toggle it live — but conceptually this is just one bad line landing in a prompt during a routine change."*

## 4. Re-run the full suite with the regression on
```bash
DEMO_BUG=true python -m evals.run_eval
```
**Expected:** `RESULT: 3/10 passed (30%)`
**Say:** *"Pass rate collapses. Only the read-only lookups and the clarification case survive — anything involving an actual cancel or refund now fails."*

## 5. Zoom into the two cleanest examples
```bash
python -m evals.run_eval TC001 TC003
echo '---'
DEMO_BUG=true python -m evals.run_eval TC001 TC003
```

**TC001 — "looks fine" case:**
```
FAIL TC001: Cancel order ORD-1001
      expected outcome: CANCELLED
      actual outcome:   CANCELLED      <-- identical!
      actual tools:   ['cancel_order']  <-- missing get_order
```
**Say:** *"The final answer is word-for-word what we expected. If you only read the agent's response, you'd sign off on this. The eval still fails it, because it never verified the order before touching it — it got the right answer by luck, not by process."*

**TC003 — "and sometimes it's not fine" case:**
```
FAIL TC003: Refund ORD-1003
      expected outcome: REFUNDED
      actual outcome:   REFUND_REJECTED   <-- wrong answer
      actual tools:   ['refund_order']     <-- missing get_order + cancel_order
```
**Say:** *"ORD-1003 hadn't been cancelled yet, so a correct refund actually requires two steps: cancel, then refund. Without checking status first, the agent has no way to know it needs that extra step — so it just tries to refund directly, the tool itself rejects it, and a legitimate customer refund is wrongly denied. This time skipping the check didn't just look bad — it broke the outcome."*

**Key line to land:** *"Same root cause, two different failure modes — one silent, one visible. That inconsistency is exactly why you can't spot-check outputs and call it evaluated. You need the trajectory."*

