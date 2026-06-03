from __future__ import annotations

import argparse
from collections.abc import Sequence

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from viola.config import load_settings
from viola.dialogue.manager import DialogueManager
from viola.prompts.examples import SAMPLE_PROMPTS

EXIT_COMMANDS = {":exit", ":quit", "exit", "quit"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Viola, a LangChain personal assistant.")
    parser.add_argument("-m", "--message", help="Send one message and exit.")
    parser.add_argument("--thread-id", help="Conversation thread ID to reuse.")
    parser.add_argument("--user-id", default="local-user", help="User identifier for run metadata.")
    parser.add_argument("--env-file", help="Path to a .env file.")
    parser.add_argument("--examples", action="store_true", help="Print sample prompts and exit.")
    return parser


def print_examples(console: Console) -> None:
    lines = "\n".join(f"- {prompt}" for prompt in SAMPLE_PROMPTS)
    console.print(Panel(lines, title="Sample prompts", border_style="cyan"))


def main(argv: Sequence[str] | None = None) -> int:
    console = Console()
    args = build_parser().parse_args(argv)

    if args.examples:
        print_examples(console)
        return 0

    try:
        settings = load_settings(args.env_file)
        manager = DialogueManager(settings)
    except Exception as exc:
        console.print(f"[bold red]Startup error:[/] {exc}")
        return 2

    session = manager.new_session(user_id=args.user_id, thread_id=args.thread_id)
    console.print(
        Panel(
            f"Viola is ready.\nThread: {session.thread_id}\nType ':quit' to exit.",
            title="Viola",
            border_style="magenta",
        )
    )

    if args.message:
        reply = manager.ask(args.message, session)
        console.print(Markdown(reply.content))
        return 0

    while True:
        try:
            user_message = Prompt.ask("[bold cyan]You[/]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/]")
            return 0

        if user_message.strip().lower() in EXIT_COMMANDS:
            console.print("[dim]Goodbye.[/]")
            return 0

        if not user_message.strip():
            continue

        try:
            reply = manager.ask(user_message, session)
        except Exception as exc:
            console.print(f"[bold red]Viola hit an error:[/] {exc}")
            continue

        console.print(Markdown(reply.content))

