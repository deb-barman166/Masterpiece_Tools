"""
╔══════════════════════════════════════════════════════════════╗
║          PROJECT_MANAGER_MASTERPIECE - CLI SHELL             ║
║          Full Command-Line Interface with Rich Output        ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
from pathlib import Path

# Attempt rich import for beautiful CLI output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    from rich.text import Text
    from rich.columns import Columns
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from core.file_manager import FileManager
from core.terminal_engine import TerminalManager
from core.git_manager import GitManager
from core.zip_manager import ZipManager

# Colors for non-rich fallback
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
DIM = "\033[2m"


class PMShell:
    """
    Interactive CLI shell for PROJECT_MANAGER_MASTERPIECE.
    Supports all pm commands with colored output.
    """

    BANNER = """
╔══════════════════════════════════════════════════════════════╗
║  ██████╗ ███╗   ███╗    ███╗   ███╗ █████╗ ███████╗████████╗║
║  ██╔══██╗████╗ ████║    ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝║
║  ██████╔╝██╔████╔██║    ██╔████╔██║███████║███████╗   ██║   ║
║  ██╔═══╝ ██║╚██╔╝██║    ██║╚██╔╝██║██╔══██║╚════██║   ██║   ║
║  ██║     ██║ ╚═╝ ██║    ██║ ╚═╝ ██║██║  ██║███████║   ██║   ║
║  ╚═╝     ╚═╝     ╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ║
║                                                              ║
║         PROJECT MANAGER MASTERPIECE  v1.0.0                  ║
║         Python-only Cloud Dev Environment                    ║
╚══════════════════════════════════════════════════════════════╝
"""

    HELP_TEXT = """
╔══════════════════════ PM COMMANDS ══════════════════════════╗
║                                                             ║
║  FILE OPERATIONS                                            ║
║    pm create-file <name>      Create a new file             ║
║    pm delete-file <path>      Delete file or folder         ║
║    pm rename-file <old> <new> Rename a file                 ║
║    pm move-file <src> <dest>  Move a file                   ║
║    pm open <file>             Open/view a file              ║
║    pm tree [path]             Show folder tree              ║
║    pm search <query>          Search files/content          ║
║    pm ls [path]               List directory contents       ║
║                                                             ║
║  PROJECT MANAGEMENT                                         ║
║    pm projects                List all projects             ║
║    pm new-project <name>      Create a new project          ║
║    pm upload <zip>            Upload and extract a ZIP      ║
║    pm zip <project>           Compress a project            ║
║    pm unzip <file>            Extract a ZIP file            ║
║                                                             ║
║  EXECUTION                                                  ║
║    pm run <script.py>         Run a Python script           ║
║    pm install <package>       Install pip package           ║
║    pm shell                   Open interactive shell        ║
║                                                             ║
║  GIT / GITHUB                                               ║
║    pm git-init                Initialize git repo           ║
║    pm git-status              Show git status               ║
║    pm git-add [files]         Stage files                   ║
║    pm git-commit <msg>        Commit changes                ║
║    pm git-push [branch]       Push to remote                ║
║    pm git-pull [branch]       Pull from remote              ║
║    pm clone <url>             Clone a repository            ║
║    pm git-log                 Show commit history           ║
║    pm git-branch              List branches                 ║
║    pm git-config              Set Git credentials           ║
║    pm git-sync <msg>          Stage + commit + push         ║
║                                                             ║
║  SYSTEM                                                     ║
║    pm help                    Show this help                ║
║    pm clear                   Clear the screen              ║
║    pm exit                    Exit the shell                ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝
"""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.current_project = None

        # Initialize managers
        self.files = FileManager(str(self.base_dir))
        self.terminal = TerminalManager(str(self.base_dir))
        self.git = GitManager(str(self.base_dir))
        self.zipper = ZipManager(str(self.base_dir))

        # Rich console
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    # ══════════════════════════════════════════
    # MAIN LOOP
    # ══════════════════════════════════════════

    def run(self):
        """Start the interactive CLI shell."""
        self._print_banner()
        self._info("Type 'pm help' for commands. Type 'pm exit' to quit.")
        self._info(f"Working directory: {self.base_dir}")

        while True:
            try:
                prompt = self._build_prompt()
                line = input(prompt).strip()

                if not line:
                    continue

                self.execute_line(line)

            except KeyboardInterrupt:
                print()
                self._warn("Use 'pm exit' to quit.")
            except EOFError:
                self._info("Goodbye! 👋")
                break

    def execute_line(self, line: str) -> bool:
        """Execute a single CLI line. Returns False if exit."""
        parts = line.split()
        if not parts:
            return True

        # Handle 'pm <command>' format or direct command
        if parts[0] == "pm" and len(parts) > 1:
            cmd = parts[1]
            args = parts[2:]
        elif parts[0] == "pm":
            self.cmd_help([])
            return True
        else:
            # Pass raw commands to terminal engine
            result = self.terminal.execute(line)
            self._print_terminal_result(result)
            return True

        return self._dispatch(cmd, args)

    def _dispatch(self, cmd: str, args: list) -> bool:
        """Dispatch command to handler."""
        handlers = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "clear": self.cmd_clear,
            "projects": self.cmd_projects,
            "ls": self.cmd_ls,
            "tree": self.cmd_tree,
            "create-file": self.cmd_create_file,
            "delete-file": self.cmd_delete_file,
            "rename-file": self.cmd_rename_file,
            "move-file": self.cmd_move_file,
            "open": self.cmd_open,
            "search": self.cmd_search,
            "new-project": self.cmd_new_project,
            "run": self.cmd_run,
            "install": self.cmd_install,
            "shell": self.cmd_shell,
            "upload": self.cmd_upload,
            "zip": self.cmd_zip,
            "unzip": self.cmd_unzip,
            "git-init": self.cmd_git_init,
            "git-status": self.cmd_git_status,
            "git-add": self.cmd_git_add,
            "git-commit": self.cmd_git_commit,
            "git-push": self.cmd_git_push,
            "git-pull": self.cmd_git_pull,
            "git-log": self.cmd_git_log,
            "git-branch": self.cmd_git_branch,
            "clone": self.cmd_clone,
            "git-config": self.cmd_git_config,
            "git-sync": self.cmd_git_sync,
        }

        handler = handlers.get(cmd)
        if handler:
            return handler(args)
        else:
            self._error(f"Unknown command: pm {cmd}. Type 'pm help' for commands.")
            return True

    # ══════════════════════════════════════════
    # COMMAND HANDLERS
    # ══════════════════════════════════════════

    def cmd_help(self, args):
        if RICH_AVAILABLE:
            self.console.print(Panel(self.HELP_TEXT, title="[bold cyan]PM Help[/]", border_style="cyan"))
        else:
            print(self.HELP_TEXT)
        return True

    def cmd_exit(self, args):
        self._success("Goodbye! 👋")
        sys.exit(0)

    def cmd_clear(self, args):
        os.system("clear" if os.name != "nt" else "cls")
        return True

    def cmd_projects(self, args):
        projects = self.files.list_projects()
        if not projects:
            self._warn("No projects found. Create one with: pm new-project <name>")
            return True

        if RICH_AVAILABLE:
            table = Table(title="📁 Projects", header_style="bold cyan", border_style="blue")
            table.add_column("Name", style="bold white")
            table.add_column("Files", style="cyan", justify="right")
            table.add_column("Size", style="green", justify="right")
            table.add_column("Modified", style="dim")
            for p in projects:
                table.add_row(p["name"], str(p["files"]), p["size"], p["modified"])
            self.console.print(table)
        else:
            print(f"\n{'Name':<25} {'Files':>8} {'Size':>10} {'Modified':>20}")
            print("-" * 65)
            for p in projects:
                print(f"{p['name']:<25} {p['files']:>8} {p['size']:>10} {p['modified']:>20}")
        return True

    def cmd_ls(self, args):
        path = args[0] if args else str(self.base_dir)
        result = self.terminal.execute(f"ls -la {path}")
        self._print_terminal_result(result)
        return True

    def cmd_tree(self, args):
        path = args[0] if args else str(self.base_dir)
        tree_text = self.files.get_tree_text(path)
        if RICH_AVAILABLE:
            self.console.print(Panel(tree_text, title="[bold cyan]File Tree[/]", border_style="blue"))
        else:
            print(tree_text)
        return True

    def cmd_create_file(self, args):
        if not args:
            self._error("Usage: pm create-file <name> [project]")
            return True
        name = args[0]
        result = self.files.create_file(name)
        self._print_result(result)
        return True

    def cmd_delete_file(self, args):
        if not args:
            self._error("Usage: pm delete-file <path>")
            return True
        path = args[0]
        if RICH_AVAILABLE:
            if not Confirm.ask(f"Delete [red]{path}[/]?"):
                self._warn("Cancelled")
                return True
        else:
            confirm = input(f"Delete '{path}'? [y/N] ").strip().lower()
            if confirm != "y":
                self._warn("Cancelled")
                return True
        result = self.files.delete_file(path)
        self._print_result(result)
        return True

    def cmd_rename_file(self, args):
        if len(args) < 2:
            self._error("Usage: pm rename-file <old-path> <new-name>")
            return True
        result = self.files.rename_file(args[0], args[1])
        self._print_result(result)
        return True

    def cmd_move_file(self, args):
        if len(args) < 2:
            self._error("Usage: pm move-file <src> <dest>")
            return True
        result = self.files.move_file(args[0], args[1])
        self._print_result(result)
        return True

    def cmd_open(self, args):
        if not args:
            self._error("Usage: pm open <file>")
            return True
        result = self.files.read_file(args[0])
        if result["success"]:
            data = result["data"]
            if RICH_AVAILABLE:
                syntax = Syntax(
                    data["content"],
                    data["language"],
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True
                )
                self.console.print(Panel(
                    syntax,
                    title=f"[bold cyan]{data['name']}[/] [dim]({data['lines']} lines, {data['size']})[/]"
                ))
            else:
                print(f"\n--- {data['name']} ---")
                print(data["content"])
        else:
            self._error(result["message"])
        return True

    def cmd_search(self, args):
        if not args:
            self._error("Usage: pm search <query>")
            return True
        query = " ".join(args)
        self._info(f"Searching for: '{query}'...")
        result = self.files.search(query)
        if result["success"]:
            results = result["data"]["results"]
            if not results:
                self._warn("No results found")
                return True
            if RICH_AVAILABLE:
                table = Table(title=f"Search: '{query}'", header_style="bold cyan")
                table.add_column("File", style="white")
                table.add_column("Type", style="cyan")
                table.add_column("Preview", style="dim")
                for r in results:
                    preview = r.get("preview", "")
                    table.add_row(r["name"], r["match_type"], preview[:60])
                self.console.print(table)
            else:
                for r in results:
                    print(f"  {r['icon']} {r['name']} [{r['match_type']}]")
        return True

    def cmd_new_project(self, args):
        if not args:
            self._error("Usage: pm new-project <name>")
            return True
        name = args[0]
        result = self.files.create_folder(name)
        if result["success"]:
            # Create basic project structure
            project_path = Path(result["data"]["path"])
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "README.md").write_text(f"# {name}\n\nProject created with PM Masterpiece.\n")
            (project_path / ".gitignore").write_text("__pycache__/\n*.pyc\n*.egg-info/\ndist/\n.env\n")
            self._success(f"✅ Project '{name}' created with basic structure!")
            self.current_project = str(project_path)
        else:
            self._error(result["message"])
        return True

    def cmd_run(self, args):
        if not args:
            self._error("Usage: pm run <script.py>")
            return True
        script = args[0]
        extra_args = " ".join(args[1:])
        self._info(f"Running: {script}")
        result = self.terminal.execute(f"python {script} {extra_args}")
        self._print_terminal_result(result)
        return True

    def cmd_install(self, args):
        if not args:
            self._error("Usage: pm install <package>")
            return True
        packages = " ".join(args)
        self._info(f"Installing: {packages}")
        result = self.terminal.execute(f"pip install {packages}")
        self._print_terminal_result(result)
        return True

    def cmd_shell(self, args):
        """Drop into interactive terminal mode."""
        self._info("Interactive shell mode. Type 'exit' to return to PM shell.")
        session = self.terminal.get_session()
        while True:
            try:
                cmd = input(session.prompt)
                if cmd.strip() in ["exit", "quit"]:
                    break
                result = session.execute(cmd)
                out = result["stdout"]
                err = result["stderr"]
                if out:
                    print(out)
                if err:
                    print(f"\033[91m{err}\033[0m")
            except (KeyboardInterrupt, EOFError):
                break
        self._info("Returned to PM shell.")
        return True

    def cmd_upload(self, args):
        if not args:
            self._error("Usage: pm upload <zip-path>")
            return True
        result = self.zipper.handle_upload(args[0])
        self._print_result(result)
        return True

    def cmd_zip(self, args):
        if not args:
            self._error("Usage: pm zip <project-path>")
            return True
        result = self.zipper.create_zip(args[0])
        self._print_result(result)
        if result["success"]:
            self._info(f"ZIP saved to: {result['data']['zip_path']}")
        return True

    def cmd_unzip(self, args):
        if not args:
            self._error("Usage: pm unzip <zip-file>")
            return True
        result = self.zipper.extract_zip(args[0])
        self._print_result(result)
        return True

    def cmd_git_init(self, args):
        path = args[0] if args else (self.current_project or str(self.base_dir))
        result = self.git.init(path)
        self._print_result(result)
        return True

    def cmd_git_status(self, args):
        path = args[0] if args else (self.current_project or str(self.base_dir))
        result = self.git.status(path)
        if result["success"]:
            data = result["data"]
            if RICH_AVAILABLE:
                self.console.print(Panel(
                    data["full_status"],
                    title=f"[bold cyan]Git Status — {data['branch']}[/]",
                    border_style="green" if data["is_clean"] else "yellow"
                ))
            else:
                print(data["full_status"])
        else:
            self._error(result["message"])
        return True

    def cmd_git_add(self, args):
        path = self.current_project or str(self.base_dir)
        files = args if args else None
        result = self.git.add(path, files)
        self._print_result(result)
        return True

    def cmd_git_commit(self, args):
        if not args:
            self._error("Usage: pm git-commit <message>")
            return True
        path = self.current_project or str(self.base_dir)
        message = " ".join(args)
        result = self.git.commit(path, message)
        self._print_result(result)
        return True

    def cmd_git_push(self, args):
        path = self.current_project or str(self.base_dir)
        branch = args[0] if args else "main"
        result = self.git.push(path, branch)
        self._print_result(result)
        return True

    def cmd_git_pull(self, args):
        path = self.current_project or str(self.base_dir)
        branch = args[0] if args else ""
        result = self.git.pull(path, branch)
        self._print_result(result)
        return True

    def cmd_git_log(self, args):
        path = self.current_project or str(self.base_dir)
        result = self.git.get_log(path)
        if result["success"]:
            commits = result["data"]["commits"]
            if not commits:
                self._warn("No commits yet")
                return True
            if RICH_AVAILABLE:
                table = Table(title="Git Log", header_style="bold cyan", border_style="blue")
                table.add_column("Hash", style="yellow", width=10)
                table.add_column("Author", style="cyan")
                table.add_column("Time", style="dim")
                table.add_column("Message", style="white")
                for c in commits:
                    table.add_row(c["hash"], c["author"], c["time"], c["message"])
                self.console.print(table)
            else:
                for c in commits:
                    print(f"  [{c['hash']}] {c['author']} ({c['time']}) — {c['message']}")
        else:
            self._error(result["message"])
        return True

    def cmd_git_branch(self, args):
        path = self.current_project or str(self.base_dir)
        result = self.git.list_branches(path)
        if result["success"]:
            for b in result["data"]["branches"]:
                marker = "* " if b["current"] else "  "
                print(f"{marker}{b['name']}")
        else:
            self._error(result["message"])
        return True

    def cmd_clone(self, args):
        if not args:
            self._error("Usage: pm clone <repo-url> [target-name]")
            return True
        url = args[0]
        name = args[1] if len(args) > 1 else None
        self._info(f"Cloning {url}...")
        result = self.git.clone(url, name)
        self._print_result(result)
        return True

    def cmd_git_config(self, args):
        if RICH_AVAILABLE:
            username = Prompt.ask("[cyan]GitHub username[/]")
            email = Prompt.ask("[cyan]GitHub email[/]")
            token = Prompt.ask("[cyan]GitHub personal access token[/]", password=True)
        else:
            username = input("GitHub username: ").strip()
            email = input("GitHub email: ").strip()
            token = input("GitHub token (hidden): ").strip()
        result = self.git.set_credentials(username, email, token)
        self._print_result(result)
        return True

    def cmd_git_sync(self, args):
        if not args:
            self._error("Usage: pm git-sync <commit-message>")
            return True
        path = self.current_project or str(self.base_dir)
        message = " ".join(args)
        self._info("Syncing with GitHub...")
        result = self.git.sync(path, message)
        self._print_result(result)
        return True

    # ══════════════════════════════════════════
    # OUTPUT HELPERS
    # ══════════════════════════════════════════

    def _print_banner(self):
        if RICH_AVAILABLE:
            self.console.print(self.BANNER, style="bold cyan")
        else:
            print(f"{CYAN}{self.BANNER}{RESET}")

    def _build_prompt(self) -> str:
        project = Path(self.current_project).name if self.current_project else "~"
        if RICH_AVAILABLE:
            return f"[bold cyan]pm[/] [dim]({project})[/] [bold green]❯[/] "
        return f"{CYAN}pm{RESET} {DIM}({project}){RESET} {GREEN}❯{RESET} "

    def _success(self, msg: str):
        if RICH_AVAILABLE:
            self.console.print(f"[bold green]✅ {msg}[/]")
        else:
            print(f"{GREEN}✅ {msg}{RESET}")

    def _error(self, msg: str):
        if RICH_AVAILABLE:
            self.console.print(f"[bold red]❌ {msg}[/]")
        else:
            print(f"{RED}❌ {msg}{RESET}")

    def _warn(self, msg: str):
        if RICH_AVAILABLE:
            self.console.print(f"[bold yellow]⚠️  {msg}[/]")
        else:
            print(f"{YELLOW}⚠️  {msg}{RESET}")

    def _info(self, msg: str):
        if RICH_AVAILABLE:
            self.console.print(f"[dim]{msg}[/]")
        else:
            print(f"{DIM}{msg}{RESET}")

    def _print_result(self, result: dict):
        if result["success"]:
            self._success(result["message"])
        else:
            self._error(result["message"])

    def _print_terminal_result(self, result: dict):
        if result["stdout"]:
            print(result["stdout"])
        if result["stderr"]:
            if RICH_AVAILABLE:
                self.console.print(f"[red]{result['stderr']}[/]")
            else:
                print(f"{RED}{result['stderr']}{RESET}")
