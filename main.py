"""
Interactive demo of the Multi-Memory Agent.

Usage:
  python main.py

Commands during chat:
  stats   — show memory statistics
  reset   — clear short-term memory
  profile — print current user profile
  quit    — exit
"""

import os
import sys

from dotenv import load_dotenv

from memory_agent.graph import MemoryAgent
from benchmark.conversations import KNOWLEDGE_BASE

load_dotenv()


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
        print("  Create a .env file: OPENAI_API_KEY=sk-your-key")
        sys.exit(1)

    agent = MemoryAgent(session_id="demo", openai_api_key=api_key)
    agent.seed_knowledge_base(KNOWLEDGE_BASE)

    print("\nMulti-Memory Agent — Lab #17 Demo")
    print("=" * 50)
    print(f"Knowledge base: {len(KNOWLEDGE_BASE)} documents loaded into ChromaDB")
    print("Commands: stats | reset | profile | quit")
    print("=" * 50 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd == "quit":
            print("Goodbye!")
            break
        elif cmd == "stats":
            stats = agent.get_memory_stats()
            print(f"\n[Memory Stats]")
            for k, v in stats.items():
                print(f"  {k}: {v}")
            print()
        elif cmd == "reset":
            agent.reset_short_term()
            print("[Short-term memory cleared]\n")
        elif cmd == "profile":
            profile = agent.profile_mem.get_all()
            if profile:
                print("\n[User Profile]")
                for k, v in profile.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print("[No profile data yet]\n")
        else:
            response = agent.chat(user_input)
            print(f"Agent: {response}\n")


if __name__ == "__main__":
    main()
