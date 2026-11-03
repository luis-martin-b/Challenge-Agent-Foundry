"""
SkyNova Airlines - terminal chat with the Foundry agent.

Usage:
    python app/cli.py
Commands:
    /new   start a new conversation      /help  show help      /exit  quit
"""
import platform
import subprocess
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from skynova_client import SkyNovaAgent

console = Console()
ICONS = {"knowledge": "🔎 Knowledge base", "code": "🐍 Code Interpreter", "github": "🐙 GitHub", "other": "🔧 Tool"}
HELP = "[bold]/new[/] new conversation   [bold]/help[/] help   [bold]/exit[/] quit"


def open_file(path):
    """Open a generated chart with the default image viewer."""
    try:
        cmd = {"Darwin": ["open"], "Windows": ["cmd", "/c", "start", ""]}.get(platform.system(), ["xdg-open"])
        subprocess.Popen(cmd + [str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def show_reply(reply):
    if reply.tools:
        used = []
        for t in reply.tools:
            label = ICONS[t.kind] + (f" · {t.name}" if t.kind == "github" else "") + (f" ({t.detail})" if t.detail else "")
            used.append(f"[red]{label} ✗[/]" if t.error else label)
        console.print("[dim]" + "  |  ".join(dict.fromkeys(used)) + "[/]")
    console.print(Panel(Markdown(reply.text or "_(empty answer)_"), title="✈️  Nova · SkyNova", title_align="left",
                        border_style="cyan", padding=(0, 1)))
    if reply.sources:
        console.print("[dim]📄 Sources: " + "; ".join(reply.sources) + "[/]")
    for f in reply.files:
        console.print(f"[green]📊 Chart saved:[/] {f}")
        if sys.stdin.isatty():
            open_file(f)


def main():
    console.print(Panel.fit("[bold cyan]SkyNova Airlines[/] · Customer Care Agent\n[dim]Microsoft Foundry · terminal client[/]",
                            border_style="cyan"))
    with console.status("Signing in with Microsoft Entra ID and connecting to the agent..."):
        try:
            agent = SkyNovaAgent()
            agent.new_conversation()
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]Could not connect to the agent:[/] {e}\n"
                          "[dim]Check your .env file and run `az login` with the account of your Foundry project.[/]")
            sys.exit(1)
    console.print(f"[green]✓ Connected[/] to agent [bold]{agent.agent_name}[/] (version {agent.agent_version}, "
                  f"model {agent.model})\n{HELP}\n")

    try:
        while True:
            message = Prompt.ask("[bold yellow]You[/]").strip()
            if not message:
                continue
            if message.lower() in ("/exit", "/quit", "exit", "quit"):
                break
            if message.lower() == "/help":
                console.print(HELP)
                continue
            if message.lower() == "/new":
                agent.new_conversation()
                console.print("[green]✓ New conversation started[/]\n")
                continue
            with console.status("Nova is typing..."):
                try:
                    reply = agent.ask(message)
                except Exception as e:  # noqa: BLE001
                    console.print(f"[red]Error:[/] {e}\n")
                    continue
            show_reply(reply)
            console.print()
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        agent.close()
        console.print("\n[cyan]Thank you for flying with SkyNova. Goodbye! ✈️[/]")


if __name__ == "__main__":
    main()
