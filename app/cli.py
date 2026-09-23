import asyncio
import sys
from google.adk.runners import InMemoryRunner
from google.genai import types
from .agent import root_agent
from .tools import reset_data

async def main():
    reset_data()
    runner = InMemoryRunner(agent=root_agent, app_name="agent_evaluation_demo")
    user_id = "demo-user"
    session = await runner.session_service.create_session(
        app_name="agent_evaluation_demo",
        user_id=user_id,
    )
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("You: ")
    content = types.Content(role="user", parts=[types.Part(text=prompt)])

    print(f"\nUSER: {prompt}\n")
    print("TRACE:")
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.get_function_calls():
            for call in event.get_function_calls():
                print(f"  TOOL → {call.name}({call.args})")
        if event.get_function_responses():
            for response in event.get_function_responses():
                print(f"  RESULT ← {response.name}: {response.response}")
        if event.is_final_response() and event.content:
            print("\nAGENT:")
            print(event.content.parts[0].text if event.content.parts else "(no text)")

if __name__ == "__main__":
    asyncio.run(main())
