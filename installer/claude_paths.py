"""Claude config-directory resolution for the installer package.

Stdlib-only and free of installer imports so any step can use it without
creating an import cycle.

⛔ Deliberate duplicate of ``launcher/config.py``'s resolvers. The two packages
may not import each other (``launcher/`` ships as a Cython binary; ``installer/``
runs in a separate process where the launcher tree is absent) - see
``.claude/rules/pilot-shell-package-boundaries.md``. Keep the two in lockstep.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_claude_config_dir() -> Path:
    """Resolve the Claude config directory from the ``CLAUDE_CONFIG_DIR`` env var.

    Returns ``Path(CLAUDE_CONFIG_DIR)`` when set to an absolute path, otherwise
    ``~/.claude``.

    Raises ``ValueError`` when the variable is set but empty or relative. Failing
    closed is deliberate: silently falling back to ``~/.claude`` would point the
    installer at the user's personal profile precisely when they were trying to
    target a different one.
    """
    env_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if env_dir is None:
        return Path.home() / ".claude"

    if not env_dir.strip():
        raise ValueError("CLAUDE_CONFIG_DIR is set but empty; unset it to use the default ~/.claude")

    path = Path(env_dir)
    if not path.is_absolute():
        raise ValueError(f"CLAUDE_CONFIG_DIR must be an absolute path, got: {env_dir}")
    return path


def get_claude_app_config_path() -> Path:
    """Resolve Claude Code's app-config JSON (``mcpServers`` and app preferences).

    Mirrors Claude Code 2.1.220, which resolves it as::

        if exists(<config_dir>/.config.json): -> <config_dir>/.config.json
        else:                                -> (CLAUDE_CONFIG_DIR or $HOME)/.claude.json

    Note the base differs from :func:`get_claude_config_dir`: when the variable is
    unset the file is ``~/.claude.json`` at the home root, **not**
    ``~/.claude/.claude.json``. Do not "normalize" that away - doing so would move
    the app config for every existing default-directory install.
    """
    config_dir = get_claude_config_dir()
    override = config_dir / ".config.json"
    if override.exists():
        return override

    env_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(env_dir) if env_dir else Path.home()
    return base / ".claude.json"
