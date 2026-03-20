from __future__ import annotations

from collections.abc import Callable


def run_cli(process_command: Callable[[str], str]) -> None:
    print("Robot CLI ready. Type a command, or 'exit' to quit.")
    while True:
        try:
            user_input = input("robot> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            return

        output = process_command(user_input)
        print(output)
