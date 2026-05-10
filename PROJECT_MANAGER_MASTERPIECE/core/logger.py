"""
╔══════════════════════════════════════════════════════════════╗
║         PROJECT_MANAGER_MASTERPIECE - LOGGER                 ║
║         Persistent operation logging & audit trail           ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
import logging
import os
from pathlib import Path
from datetime import datetime


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pm_masterpiece.log"
AUDIT_FILE = LOG_DIR / "audit.json"


def get_logger(name: str = "PM_Masterpiece") -> logging.Logger:
    """Get a configured logger with file and console handlers."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)

    # File handler (full debug logs)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    # Console handler (warnings and above only)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


class AuditLog:
    """Records all file/git/terminal operations for history."""

    def __init__(self, audit_file: str = None):
        self.file = Path(audit_file) if audit_file else AUDIT_FILE
        self._entries = self._load()

    def _load(self) -> list:
        if self.file.exists():
            try:
                return json.loads(self.file.read_text())
            except Exception:
                return []
        return []

    def record(self, operation: str, target: str, status: str, detail: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "target": target,
            "status": status,  # "success" | "failure" | "blocked"
            "detail": detail
        }
        self._entries.append(entry)
        # Keep last 1000 entries
        if len(self._entries) > 1000:
            self._entries = self._entries[-1000:]
        self._save()

    def _save(self):
        try:
            self.file.write_text(json.dumps(self._entries, indent=2))
        except Exception:
            pass

    def get_recent(self, n: int = 50) -> list:
        return self._entries[-n:]

    def get_by_operation(self, op: str) -> list:
        return [e for e in self._entries if e["operation"] == op]

    def format_recent(self, n: int = 20) -> str:
        entries = self.get_recent(n)
        if not entries:
            return "No operations logged yet"
        lines = []
        for e in reversed(entries):
            ts = e["timestamp"][:19].replace("T", " ")
            icon = "✅" if e["status"] == "success" else "❌"
            lines.append(f"{icon} [{ts}] {e['operation']:15} → {e['target']}")
            if e["detail"]:
                lines.append(f"   {e['detail']}")
        return "\n".join(lines)
