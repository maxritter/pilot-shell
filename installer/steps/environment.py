"""Environment step - sets up .env file with API keys."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from installer.steps.base import BaseStep

if TYPE_CHECKING:
    from installer.context import InstallContext


OBSOLETE_ENV_KEYS = [
    "MILVUS_TOKEN",
    "VECTOR_STORE_USERNAME",
    "VECTOR_STORE_PASSWORD",
    "EXA_API_KEY",
    "GEMINI_API_KEY",
]

LOCAL_MILVUS_ADDRESS = "http://host.docker.internal:19530"


def remove_env_key(key: str, env_file: Path) -> bool:
    """Remove an environment key from .env file. Returns True if key was removed."""
    if not env_file.exists():
        return False

    lines = env_file.read_text().splitlines()
    new_lines = [line for line in lines if not line.strip().startswith(f"{key}=")]

    if len(new_lines) != len(lines):
        env_file.write_text("\n".join(new_lines) + "\n" if new_lines else "")
        return True
    return False


def set_env_key(key: str, value: str, env_file: Path) -> None:
    """Set an environment key in .env file, replacing if it exists."""
    if not env_file.exists():
        env_file.write_text(f"{key}={value}\n")
        return

    lines = env_file.read_text().splitlines()
    new_lines = [line for line in lines if not line.strip().startswith(f"{key}=")]
    new_lines.append(f"{key}={value}")
    env_file.write_text("\n".join(new_lines) + "\n")


def cleanup_obsolete_env_keys(env_file: Path) -> list[str]:
    """Remove obsolete environment keys from .env file. Returns list of removed keys."""
    removed = []
    for key in OBSOLETE_ENV_KEYS:
        if remove_env_key(key, env_file):
            removed.append(key)
    return removed


def key_exists_in_file(key: str, env_file: Path) -> bool:
    """Check if key exists in .env file with a non-empty value."""
    if not env_file.exists():
        return False

    content = env_file.read_text()
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith(f"{key}="):
            value = line[len(key) + 1 :].strip()
            return bool(value)
    return False


def key_is_set(key: str, env_file: Path) -> bool:
    """Check if key exists in .env file OR is already set as environment variable."""
    if os.environ.get(key):
        return True
    return key_exists_in_file(key, env_file)


def add_env_key(key: str, value: str, env_file: Path) -> None:
    """Add environment key to .env file if it doesn't exist."""
    if key_exists_in_file(key, env_file):
        return

    with open(env_file, "a") as f:
        f.write(f"{key}={value}\n")


class EnvironmentStep(BaseStep):
    """Step that sets up the .env file for API keys."""

    name = "environment"

    def check(self, ctx: InstallContext) -> bool:
        """Always returns False - environment step should always run to check for missing keys."""
        return False

    def run(self, ctx: InstallContext) -> None:
        """Set up .env file with API keys."""
        ui = ctx.ui
        env_file = ctx.project_dir / ".env"

        if ctx.skip_env or ctx.non_interactive:
            if ui:
                ui.status("Skipping .env setup")
            return

        if ui:
            ui.section("API Keys Setup")

        append_mode = env_file.exists()

        if append_mode:
            removed_keys = cleanup_obsolete_env_keys(env_file)
            if removed_keys and ui:
                ui.print(f"  [dim]Removed obsolete keys: {', '.join(removed_keys)}[/dim]")

            set_env_key("MILVUS_ADDRESS", LOCAL_MILVUS_ADDRESS, env_file)

        if append_mode:
            if ui:
                ui.success("Found existing .env file")
                ui.print("  We'll append Claude CodePro configuration to your existing file.")
                ui.print()
        else:
            if ui:
                ui.print("  Let's set up your API keys. I'll guide you through each one.")
                ui.print()

        openai_api_key = ""
        tavily_api_key = ""
        ref_api_key = ""

        if not key_is_set("OPENAI_API_KEY", env_file):
            if ui:
                ui.print()
                ui.rule("1. OpenAI API Key - Semantic Code Search")
                ui.print()
                ui.print("  [bold]Used for:[/bold] Generating embeddings for Vexor semantic search (cheap)")
                ui.print("  [bold]Why:[/bold] Powers fast, intelligent code search across your codebase")
                ui.print("  [bold]Create at:[/bold] [cyan]https://platform.openai.com/api-keys[/cyan]")
                ui.print()

                openai_api_key = ui.input("OPENAI_API_KEY", default="")
        else:
            if ui:
                ui.success("OPENAI_API_KEY already set, skipping")

        if not key_is_set("TAVILY_API_KEY", env_file):
            if ui:
                ui.print()
                ui.rule("2. Tavily API Key - AI-Powered Web Search")
                ui.print()
                ui.print(
                    "  [bold]Used for:[/bold] Web search, code examples, documentation lookup, and URL content extraction"
                )
                ui.print("  [bold]Create at:[/bold] [cyan]https://app.tavily.com/home[/cyan]")
                ui.print()

                tavily_api_key = ui.input("TAVILY_API_KEY", default="")
        else:
            if ui:
                ui.success("TAVILY_API_KEY already set, skipping")

        if not key_is_set("REF_API_KEY", env_file):
            if ui:
                ui.print()
                ui.rule("3. Ref.Tools API Key - Library Documentation Search")
                ui.print()
                ui.print("  [bold]Used for:[/bold] Searching library and framework documentation")
                ui.print("  [bold]Create at:[/bold] [cyan]https://ref.tools/dashboard[/cyan]")
                ui.print()

                ref_api_key = ui.input("REF_API_KEY", default="")
        else:
            if ui:
                ui.success("REF_API_KEY already set, skipping")

        add_env_key("OPENAI_API_KEY", openai_api_key, env_file)
        add_env_key("TAVILY_API_KEY", tavily_api_key, env_file)
        add_env_key("REF_API_KEY", ref_api_key, env_file)

        if not append_mode:
            set_env_key("MILVUS_ADDRESS", LOCAL_MILVUS_ADDRESS, env_file)

        if ui:
            if append_mode:
                ui.success("Updated .env file with Claude CodePro configuration")
            else:
                ui.success("Created .env file with your API keys")

    def rollback(self, ctx: InstallContext) -> None:
        """No rollback for environment setup."""
        pass
