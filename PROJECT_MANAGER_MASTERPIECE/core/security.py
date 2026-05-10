"""
╔══════════════════════════════════════════════════════════════╗
║           PROJECT_MANAGER_MASTERPIECE - SECURITY             ║
║           Sandboxed Command & File Access Controller         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import re
from pathlib import Path


# ─────────────────────────────────────────────
# BLOCKED COMMANDS — System-destroying commands
# ─────────────────────────────────────────────
BLOCKED_COMMANDS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+~",
    r"rm\s+--no-preserve-root",
    r"shutdown",
    r"reboot",
    r"halt",
    r"poweroff",
    r"mkfs",
    r"fdisk",
    r"dd\s+if=",
    r":(){ :\|:& };:",        # Fork bomb
    r"chmod\s+-R\s+777\s+/",
    r"chown\s+-R\s+root\s+/",
    r"wget\s+.*\|\s*bash",
    r"curl\s+.*\|\s*bash",
    r"curl\s+.*\|\s*sh",
    r"> /dev/sda",
    r"mv\s+/",
    r"sudo\s+rm",
]

# ─────────────────────────────────────────────
# ALLOWED SAFE COMMANDS
# ─────────────────────────────────────────────
SAFE_COMMANDS = [
    "ls", "pwd", "cd", "mkdir", "rm", "mv", "cp", "cat",
    "touch", "python", "python3", "pip", "pip3", "git",
    "echo", "grep", "find", "head", "tail", "wc", "sort",
    "uniq", "chmod", "chown", "ps", "kill", "top", "df",
    "du", "uname", "whoami", "date", "clear", "history",
    "zip", "unzip", "tar", "nano", "vim", "less", "more",
    "curl", "wget", "npm", "node", "java", "javac",
]


class SecurityGuard:
    """
    Sandboxed security controller.
    Blocks dangerous terminal commands and unsafe file paths.
    """

    def __init__(self, base_dir: str = None):
        # The safe root directory — all file ops confined here
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────
    # Command Safety Check
    # ──────────────────────────────────────────
    def is_command_safe(self, command: str) -> tuple[bool, str]:
        """
        Returns (is_safe: bool, reason: str)
        """
        cmd = command.strip()

        # Check against blocked patterns
        for pattern in BLOCKED_COMMANDS:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False, f"⛔ BLOCKED: Dangerous command pattern detected → '{pattern}'"

        # Check for pipe-to-shell attacks
        if re.search(r"\|\s*(bash|sh|zsh|fish|dash)", cmd):
            return False, "⛔ BLOCKED: Pipe-to-shell execution detected"

        # Check for command chaining with dangerous patterns
        if "&&" in cmd or ";" in cmd:
            parts = re.split(r"&&|;", cmd)
            for part in parts:
                safe, reason = self.is_command_safe(part.strip())
                if not safe:
                    return False, reason

        return True, "✅ Command is safe"

    # ──────────────────────────────────────────
    # Path Safety Check (prevent directory traversal)
    # ──────────────────────────────────────────
    def is_path_safe(self, path: str) -> tuple[bool, str]:
        """
        Ensure path stays within the projects directory.
        Prevents directory traversal attacks like ../../etc/passwd
        """
        try:
            resolved = Path(path).resolve()
            base_resolved = self.base_dir.resolve()

            # Allow absolute paths within base_dir
            if str(resolved).startswith(str(base_resolved)):
                return True, "✅ Path is safe"

            # Allow relative paths from CWD that don't escape
            cwd_resolved = Path.cwd().resolve()
            if str(resolved).startswith(str(cwd_resolved)):
                return True, "✅ Path is safe"

            return False, f"⛔ BLOCKED: Path escapes sandbox → {resolved}"

        except Exception as e:
            return False, f"⛔ Path check error: {e}"

    # ──────────────────────────────────────────
    # Sanitize filename
    # ──────────────────────────────────────────
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Remove dangerous characters from filenames."""
        # Remove null bytes, path separators, and control chars
        sanitized = re.sub(r"[^\w\s\-_\.\(\)]", "_", name)
        sanitized = sanitized.strip(". ")
        return sanitized or "unnamed_file"

    # ──────────────────────────────────────────
    # Validate ZIP file
    # ──────────────────────────────────────────
    @staticmethod
    def validate_zip_content(zip_path: str) -> tuple[bool, str]:
        """Prevent Zip Slip attacks and malicious archives."""
        import zipfile
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for name in zf.namelist():
                    if name.startswith('/') or '..' in name:
                        return False, f"⛔ BLOCKED: Zip Slip attack detected in: {name}"
            return True, "✅ ZIP is safe"
        except Exception as e:
            return False, f"⛔ Invalid ZIP: {e}"
