import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from .tools import get_order, cancel_order, refund_order

load_dotenv()

MODEL = os.getenv("MODEL", "gemini-3.8-flash")
BUG = os.getenv("DEMO_BUG", "false").lower() == "true"

instruction = """
You are a customer support agent.

Business rules:
1. Never cancel a shipped order.
2. Only PROCESSING orders can be cancelled.
3. A refund is allowed only after an order is cancelled.
4. Never claim an action succeeded unless the corresponding tool succeeded.
5. Always retrieve the order before any cancellation or refund.
6. If a request is ambiguous or asks for bulk destructive actions, ask for clarification.
7. Be concise and cite the observed order status when relevant.
"""

if BUG:
    instruction = instruction.replace(
        "5. Always retrieve the order before any cancellation or refund.",
        "5. You may cancel an order directly without retrieving it first."
    )

root_agent = Agent(
    name="customer_support_agent",
    model=Gemini(model=MODEL),
    instruction=instruction,
    tools=[get_order, cancel_order, refund_order],
)
