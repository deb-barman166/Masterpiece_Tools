"""
╔══════════════════════════════════════════════════════════════╗
║        PROJECT_MANAGER_MASTERPIECE - TERMINAL ENGINE         ║
║        Real-Time Command Execution & Output Streaming        ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import subprocess
import threading
import queue
import shlex
from pathlib import Path
from datetime import datetime
from core.security import SecurityGuard


class TerminalSession:
    """
    A single terminal session with its own working directory,
    command history, and output buffer.
    """

    def __init__(self, session_id: str = "default", base_dir: str = None):
        self.session_id = session_id
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.cwd = self.base_dir  # Start in base directory
        self.history = []
        self.output_buffer = []
        self.security = SecurityGuard(str(self.base_dir))
        self.env = os.environ.copy()
        self.env["TERM"] = "xterm-256color"

    # ──────────────────────────────────────────
    # Execute a command
    # ──────────────────────────────────────────
    def execute(self, command: str, timeout: int = 30) -> dict:
        """
        Execute a terminal command and return structured result.

        Returns:
            dict with keys: success, stdout, stderr, return_code, timestamp
        """
        command = command.strip()
        if not command:
            return self._result(True, "", "", 0)

        # Log to history
        self.history.append({
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "cwd": str(self.cwd)
        })

        # Security check
        is_safe, reason = self.security.is_command_safe(command)
        if not is_safe:
            return self._result(False, "", reason, 1)

        # Handle built-in commands (cd, clear, etc.)
        builtin = self._handle_builtin(command)
        if builtin is not None:
            return builtin

        # Execute external command
        return self._run_subprocess(command, timeout)

    # ──────────────────────────────────────────
    # Handle built-in shell commands
    # ──────────────────────────────────────────
    def _handle_builtin(self, command: str) -> dict | None:
        """Handle shell built-ins like cd, clear, history."""
        parts = shlex.split(command)
        cmd = parts[0].lower() if parts else ""

        # cd — change directory
        if cmd == "cd":
            target = parts[1] if len(parts) > 1 else str(Path.home())
            return self._change_dir(target)

        # pwd — print working directory
        if cmd == "pwd":
            return self._result(True, str(self.cwd), "", 0)

        # clear — clear terminal
        if cmd == "clear":
            return self._result(True, "\033[2J\033[H", "", 0)

        # history — show command history
        if cmd == "history":
            hist = "\n".join([
                f"  {i+1:3}  {h['command']}"
                for i, h in enumerate(self.history[:-1])  # exclude 'history' itself
            ])
            return self._result(True, hist or "No history yet", "", 0)

        # exit — not allowed inside embedded terminal
        if cmd == "exit":
            return self._result(True, "💡 Use the Exit button to close the app.", "", 0)

        return None  # Not a built-in

    # ──────────────────────────────────────────
    # Change directory
    # ──────────────────────────────────────────
    def _change_dir(self, target: str) -> dict:
        """Change current working directory safely."""
        try:
            if target == "~":
                new_dir = Path.home()
            elif target == "-":
                new_dir = self.base_dir
            elif target.startswith("/"):
                new_dir = Path(target)
            else:
                new_dir = (self.cwd / target).resolve()

            if not new_dir.exists():
                return self._result(False, "", f"cd: {target}: No such file or directory", 1)
            if not new_dir.is_dir():
                return self._result(False, "", f"cd: {target}: Not a directory", 1)

            self.cwd = new_dir
            return self._result(True, f"📂 {self.cwd}", "", 0)
        except Exception as e:
            return self._result(False, "", f"cd error: {e}", 1)

    # ──────────────────────────────────────────
    # Run subprocess
    # ──────────────────────────────────────────
    def _run_subprocess(self, command: str, timeout: int) -> dict:
        """Run an external command as a subprocess."""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=str(self.cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self.env,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            stdout, stderr = process.communicate(timeout=timeout)
            return_code = process.returncode

            return self._result(
                success=(return_code == 0),
                stdout=stdout,
                stderr=stderr,
                return_code=return_code
            )

        except subprocess.TimeoutExpired:
            process.kill()
            return self._result(False, "", f"⏱️ Command timed out after {timeout}s", 124)
        except FileNotFoundError:
            cmd_name = command.split()[0]
            return self._result(False, "", f"Command not found: {cmd_name}", 127)
        except Exception as e:
            return self._result(False, "", f"Execution error: {e}", 1)

    # ──────────────────────────────────────────
    # Streaming execute (for real-time output)
    # ──────────────────────────────────────────
    def execute_streaming(self, command: str, output_queue: queue.Queue, timeout: int = 60):
        """
        Execute a command and stream output line-by-line into a queue.
        Used for long-running commands (pip install, python scripts, etc.)
        """
        command = command.strip()
        is_safe, reason = self.security.is_command_safe(command)
        if not is_safe:
            output_queue.put(("error", reason))
            output_queue.put(("done", 1))
            return

        def _stream():
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=str(self.cwd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=self.env,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1
                )

                for line in iter(process.stdout.readline, ""):
                    output_queue.put(("output", line.rstrip()))

                process.wait()
                output_queue.put(("done", process.returncode))

            except Exception as e:
                output_queue.put(("error", str(e)))
                output_queue.put(("done", 1))

        thread = threading.Thread(target=_stream, daemon=True)
        thread.start()

    # ──────────────────────────────────────────
    # Helper: build result dict
    # ──────────────────────────────────────────
    @staticmethod
    def _result(success: bool, stdout: str, stderr: str, return_code: int) -> dict:
        return {
            "success": success,
            "stdout": stdout.strip() if stdout else "",
            "stderr": stderr.strip() if stderr else "",
            "return_code": return_code,
            "timestamp": datetime.now().isoformat()
        }

    # ──────────────────────────────────────────
    # Format output for display
    # ──────────────────────────────────────────
    def format_output(self, result: dict, command: str = "") -> str:
        """Format command result for terminal display."""
        lines = []
        if command:
            lines.append(f"$ {command}")

        if result["stdout"]:
            lines.append(result["stdout"])

        if result["stderr"]:
            lines.append(f"[stderr] {result['stderr']}")

        if not result["success"] and result["return_code"] != 0:
            lines.append(f"[exit code: {result['return_code']}]")

        return "\n".join(lines)

    @property
    def prompt(self) -> str:
        """Get the shell prompt string."""
        try:
            rel = self.cwd.relative_to(Path.home())
            path_str = f"~/{rel}"
        except ValueError:
            path_str = str(self.cwd)
        return f"📁 {path_str} $ "


# ─────────────────────────────────────────────
# Terminal Manager — manages multiple sessions
# ─────────────────────────────────────────────
class TerminalManager:
    """Manages multiple terminal sessions (tabs)."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or str(Path.cwd() / "projects")
        self.sessions: dict[str, TerminalSession] = {}
        self.active_session = "main"
        self._create_session("main")

    def _create_session(self, name: str) -> TerminalSession:
        session = TerminalSession(name, self.base_dir)
        self.sessions[name] = session
        return session

    def get_session(self, name: str = None) -> TerminalSession:
        name = name or self.active_session
        if name not in self.sessions:
            self._create_session(name)
        return self.sessions[name]

    def new_session(self, name: str = None) -> str:
        name = name or f"terminal_{len(self.sessions) + 1}"
        self._create_session(name)
        self.active_session = name
        return name

    def execute(self, command: str, session: str = None) -> dict:
        return self.get_session(session).execute(command)

    def list_sessions(self) -> list[str]:
        return list(self.sessions.keys())
