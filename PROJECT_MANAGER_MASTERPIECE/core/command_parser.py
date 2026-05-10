"""
╔══════════════════════════════════════════════════════════════╗
║       PROJECT_MANAGER_MASTERPIECE - COMMAND PARSER           ║
║       Parses and routes CLI commands with validation         ║
╚══════════════════════════════════════════════════════════════╝
"""

import shlex
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedCommand:
    """Represents a fully parsed CLI command."""
    raw: str
    program: str          # e.g. "pm"
    command: str          # e.g. "git-push"
    args: list            # positional args
    flags: dict           # --key value flags
    is_pm_command: bool   # True if starts with 'pm'
    is_valid: bool = True
    error: str = ""


class CommandParser:
    """
    Parses CLI commands in the format:
        pm <command> [args...] [--flags...]

    Also handles raw shell commands that don't start with 'pm'.
    """

    PM_COMMANDS = {
        # File operations
        "create-file":  {"min_args": 1, "max_args": 2, "desc": "Create a new file"},
        "delete-file":  {"min_args": 1, "max_args": 1, "desc": "Delete a file/folder"},
        "rename-file":  {"min_args": 2, "max_args": 2, "desc": "Rename a file"},
        "move-file":    {"min_args": 2, "max_args": 2, "desc": "Move a file"},
        "copy-file":    {"min_args": 2, "max_args": 2, "desc": "Copy a file"},
        "open":         {"min_args": 1, "max_args": 1, "desc": "Open/view a file"},
        "create-folder":{"min_args": 1, "max_args": 1, "desc": "Create a folder"},
        "tree":         {"min_args": 0, "max_args": 1, "desc": "Show file tree"},
        "ls":           {"min_args": 0, "max_args": 1, "desc": "List directory"},
        "search":       {"min_args": 1, "max_args": -1,"desc": "Search files/content"},

        # Project management
        "projects":     {"min_args": 0, "max_args": 0, "desc": "List all projects"},
        "new-project":  {"min_args": 1, "max_args": 1, "desc": "Create new project"},
        "upload":       {"min_args": 1, "max_args": 2, "desc": "Upload ZIP project"},
        "zip":          {"min_args": 1, "max_args": 2, "desc": "Compress project"},
        "unzip":        {"min_args": 1, "max_args": 2, "desc": "Extract ZIP"},

        # Execution
        "run":          {"min_args": 1, "max_args": -1,"desc": "Run Python script"},
        "install":      {"min_args": 1, "max_args": -1,"desc": "Install pip packages"},
        "shell":        {"min_args": 0, "max_args": 0, "desc": "Interactive shell"},

        # Git
        "git-init":     {"min_args": 0, "max_args": 1, "desc": "Initialize git repo"},
        "git-status":   {"min_args": 0, "max_args": 1, "desc": "Show git status"},
        "git-add":      {"min_args": 0, "max_args": -1,"desc": "Stage files"},
        "git-commit":   {"min_args": 1, "max_args": -1,"desc": "Commit changes"},
        "git-push":     {"min_args": 0, "max_args": 2, "desc": "Push to remote"},
        "git-pull":     {"min_args": 0, "max_args": 2, "desc": "Pull from remote"},
        "git-log":      {"min_args": 0, "max_args": 1, "desc": "Show commit log"},
        "git-branch":   {"min_args": 0, "max_args": 1, "desc": "List/manage branches"},
        "clone":        {"min_args": 1, "max_args": 2, "desc": "Clone repository"},
        "git-config":   {"min_args": 0, "max_args": 0, "desc": "Set git credentials"},
        "git-sync":     {"min_args": 1, "max_args": -1,"desc": "Stage+commit+push"},

        # System
        "help":         {"min_args": 0, "max_args": 1, "desc": "Show help"},
        "clear":        {"min_args": 0, "max_args": 0, "desc": "Clear screen"},
        "exit":         {"min_args": 0, "max_args": 0, "desc": "Exit shell"},
        "quit":         {"min_args": 0, "max_args": 0, "desc": "Exit shell"},
    }

    def parse(self, raw_input: str) -> ParsedCommand:
        """Parse a raw input string into a ParsedCommand."""
        raw = raw_input.strip()
        if not raw:
            return ParsedCommand(
                raw=raw, program="", command="", args=[], flags={},
                is_pm_command=False, is_valid=False, error="Empty command"
            )

        try:
            tokens = shlex.split(raw)
        except ValueError as e:
            return ParsedCommand(
                raw=raw, program="", command="", args=[], flags={},
                is_pm_command=False, is_valid=False, error=f"Parse error: {e}"
            )

        # Parse flags (--key value or --flag)
        args = []
        flags = {}
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.startswith("--"):
                key = tok[2:]
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                    flags[key] = tokens[i + 1]
                    i += 2
                else:
                    flags[key] = True
                    i += 1
            elif tok.startswith("-") and len(tok) == 2:
                key = tok[1:]
                if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                    flags[key] = tokens[i + 1]
                    i += 2
                else:
                    flags[key] = True
                    i += 1
            else:
                args.append(tok)
                i += 1

        if not args:
            return ParsedCommand(
                raw=raw, program="", command="", args=[], flags=flags,
                is_pm_command=False, is_valid=False, error="No command found"
            )

        program = args[0]
        is_pm = (program == "pm")

        if is_pm:
            command = args[1] if len(args) > 1 else "help"
            cmd_args = args[2:]
        else:
            command = program
            cmd_args = args[1:]

        # Validate PM commands
        if is_pm and command in self.PM_COMMANDS:
            spec = self.PM_COMMANDS[command]
            min_a = spec["min_args"]
            max_a = spec["max_args"]
            n = len(cmd_args)
            if n < min_a:
                return ParsedCommand(
                    raw=raw, program=program, command=command,
                    args=cmd_args, flags=flags, is_pm_command=is_pm,
                    is_valid=False,
                    error=f"'{command}' requires at least {min_a} argument(s), got {n}"
                )
            if max_a != -1 and n > max_a:
                return ParsedCommand(
                    raw=raw, program=program, command=command,
                    args=cmd_args, flags=flags, is_pm_command=is_pm,
                    is_valid=False,
                    error=f"'{command}' takes at most {max_a} argument(s), got {n}"
                )

        return ParsedCommand(
            raw=raw,
            program=program,
            command=command,
            args=cmd_args,
            flags=flags,
            is_pm_command=is_pm,
            is_valid=True
        )

    def get_suggestions(self, partial: str) -> list[str]:
        """Return command suggestions for tab-completion."""
        partial = partial.lower()
        return [
            f"pm {cmd}" for cmd in self.PM_COMMANDS
            if cmd.startswith(partial)
        ]

    def get_command_help(self, command: str) -> str:
        """Get help for a specific command."""
        if command in self.PM_COMMANDS:
            spec = self.PM_COMMANDS[command]
            return f"pm {command} — {spec['desc']}"
        return f"Unknown command: {command}"
