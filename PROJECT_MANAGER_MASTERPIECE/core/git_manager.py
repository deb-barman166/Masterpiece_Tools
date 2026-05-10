"""
╔══════════════════════════════════════════════════════════════╗
║         PROJECT_MANAGER_MASTERPIECE - GIT MANAGER           ║
║         Full GitHub Integration & Repository Control         ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class GitManager:
    """
    Complete Git/GitHub integration manager.
    Handles init, clone, commit, push, pull, branches, and status.
    Works via subprocess (no GitPython dependency required).
    Optionally uses GitPython if available.
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._token = None
        self._username = None
        self._email = None

        # Try to import GitPython
        try:
            import git
            self._git_module = git
            self._has_gitpython = True
        except ImportError:
            self._has_gitpython = False

    # ══════════════════════════════════════════
    # CONFIGURATION
    # ══════════════════════════════════════════

    def set_credentials(self, username: str, email: str, token: str) -> dict:
        """Store GitHub credentials securely in memory."""
        self._token = token.strip()
        self._username = username.strip()
        self._email = email.strip()

        # Configure global git user
        self._run_git(["git", "config", "--global", "user.name", self._username])
        self._run_git(["git", "config", "--global", "user.email", self._email])

        # Store credentials helper
        self._run_git(["git", "config", "--global", "credential.helper", "store"])

        return self._ok("✅ Git credentials configured", {
            "username": self._username,
            "email": self._email,
            "token_set": bool(self._token)
        })

    def get_config(self) -> dict:
        """Get current git global config."""
        name_result = self._run_git(["git", "config", "--global", "user.name"])
        email_result = self._run_git(["git", "config", "--global", "user.email"])
        return self._ok("Git config", {
            "name": name_result.get("stdout", "Not set"),
            "email": email_result.get("stdout", "Not set"),
            "token_configured": bool(self._token)
        })

    # ══════════════════════════════════════════
    # REPOSITORY OPERATIONS
    # ══════════════════════════════════════════

    def init(self, project_path: str) -> dict:
        """Initialize a new git repository."""
        try:
            path = self._resolve(project_path)
            if (path / ".git").exists():
                return self._err(f"Already a git repository: {path.name}")
            path.mkdir(parents=True, exist_ok=True)
            result = self._run_git(["git", "init"], cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Initialized git repo in {path.name}", {"path": str(path)})
            return self._err(result["stderr"])
        except Exception as e:
            return self._err(f"Init failed: {e}")

    def clone(self, repo_url: str, target_name: str = None) -> dict:
        """Clone a repository into the projects directory."""
        try:
            # Inject token for private repos
            url = self._inject_token(repo_url)

            if target_name:
                target = self.base_dir / target_name
            else:
                # Extract name from URL
                name = repo_url.rstrip("/").split("/")[-1]
                if name.endswith(".git"):
                    name = name[:-4]
                target = self.base_dir / name

            # Handle existing directory
            if target.exists():
                return self._err(f"Directory already exists: {target.name}")

            result = self._run_git(
                ["git", "clone", url, str(target)],
                cwd=self.base_dir
            )

            if result["return_code"] == 0:
                return self._ok(f"✅ Cloned → {target.name}", {
                    "path": str(target),
                    "name": target.name,
                    "url": repo_url
                })
            return self._err(self._clean_token_from_error(result["stderr"]))

        except Exception as e:
            return self._err(f"Clone failed: {e}")

    def status(self, project_path: str) -> dict:
        """Get git status of a project."""
        try:
            path = self._resolve(project_path)
            if not (path / ".git").exists():
                return self._err("Not a git repository")

            result = self._run_git(["git", "status", "--porcelain", "-b"], cwd=path)
            full_status = self._run_git(["git", "status"], cwd=path)

            if result["return_code"] != 0:
                return self._err(result["stderr"])

            lines = result["stdout"].splitlines()
            branch = ""
            staged = []
            modified = []
            untracked = []

            for line in lines:
                if line.startswith("## "):
                    branch = line[3:].split("...")[0]
                elif line.startswith("A "):
                    staged.append(line[3:])
                elif line.startswith("M "):
                    modified.append(line[3:])
                elif line.startswith("??"):
                    untracked.append(line[3:])

            return self._ok("Git status", {
                "branch": branch,
                "staged": staged,
                "modified": modified,
                "untracked": untracked,
                "full_status": full_status["stdout"],
                "is_clean": len(staged) + len(modified) + len(untracked) == 0
            })

        except Exception as e:
            return self._err(f"Status failed: {e}")

    def add(self, project_path: str, files: list = None) -> dict:
        """Stage files for commit. None = git add -A (all)."""
        try:
            path = self._resolve(project_path)
            if not (path / ".git").exists():
                return self._err("Not a git repository")

            if files:
                cmd = ["git", "add"] + files
            else:
                cmd = ["git", "add", "-A"]

            result = self._run_git(cmd, cwd=path)
            if result["return_code"] == 0:
                label = ", ".join(files) if files else "all files"
                return self._ok(f"✅ Staged: {label}")
            return self._err(result["stderr"])

        except Exception as e:
            return self._err(f"Add failed: {e}")

    def commit(self, project_path: str, message: str) -> dict:
        """Create a git commit."""
        try:
            path = self._resolve(project_path)
            if not (path / ".git").exists():
                return self._err("Not a git repository")

            if not message.strip():
                message = f"Update ({datetime.now().strftime('%Y-%m-%d %H:%M')})"

            result = self._run_git(["git", "commit", "-m", message], cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Committed: {message}", {"output": result["stdout"]})
            return self._err(result["stderr"] or result["stdout"])

        except Exception as e:
            return self._err(f"Commit failed: {e}")

    def push(self, project_path: str, branch: str = "main", remote: str = "origin") -> dict:
        """Push commits to remote."""
        try:
            path = self._resolve(project_path)
            if not (path / ".git").exists():
                return self._err("Not a git repository")

            # Set remote URL with token if available
            if self._token and self._username:
                remote_url_result = self._run_git(
                    ["git", "remote", "get-url", remote], cwd=path
                )
                if remote_url_result["return_code"] == 0:
                    raw_url = remote_url_result["stdout"]
                    auth_url = self._inject_token(raw_url)
                    self._run_git(["git", "remote", "set-url", remote, auth_url], cwd=path)

            result = self._run_git(["git", "push", remote, branch], cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Pushed to {remote}/{branch}", {"output": result["stdout"]})
            return self._err(self._clean_token_from_error(result["stderr"]))

        except Exception as e:
            return self._err(f"Push failed: {e}")

    def pull(self, project_path: str, branch: str = "", remote: str = "origin") -> dict:
        """Pull latest changes from remote."""
        try:
            path = self._resolve(project_path)
            if not (path / ".git").exists():
                return self._err("Not a git repository")

            cmd = ["git", "pull", remote]
            if branch:
                cmd.append(branch)

            result = self._run_git(cmd, cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Pulled from {remote}", {"output": result["stdout"]})
            return self._err(self._clean_token_from_error(result["stderr"]))

        except Exception as e:
            return self._err(f"Pull failed: {e}")

    def get_log(self, project_path: str, limit: int = 15) -> dict:
        """Get commit history."""
        try:
            path = self._resolve(project_path)
            if not (path / ".git").exists():
                return self._err("Not a git repository")

            result = self._run_git([
                "git", "log",
                f"--max-count={limit}",
                "--pretty=format:%H|%an|%ae|%ar|%s",
                "--no-merges"
            ], cwd=path)

            commits = []
            if result["return_code"] == 0 and result["stdout"]:
                for line in result["stdout"].splitlines():
                    parts = line.split("|", 4)
                    if len(parts) == 5:
                        commits.append({
                            "hash": parts[0][:8],
                            "full_hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "time": parts[3],
                            "message": parts[4]
                        })

            return self._ok(f"Showing {len(commits)} commits", {"commits": commits})

        except Exception as e:
            return self._err(f"Log failed: {e}")

    # ══════════════════════════════════════════
    # BRANCH MANAGEMENT
    # ══════════════════════════════════════════

    def list_branches(self, project_path: str) -> dict:
        """List all branches."""
        try:
            path = self._resolve(project_path)
            result = self._run_git(["git", "branch", "-a"], cwd=path)
            branches = []
            current = ""
            for line in result["stdout"].splitlines():
                line = line.strip()
                if line.startswith("* "):
                    current = line[2:]
                    branches.append({"name": current, "current": True, "remote": False})
                elif line.startswith("remotes/"):
                    branches.append({"name": line, "current": False, "remote": True})
                elif line:
                    branches.append({"name": line, "current": False, "remote": False})
            return self._ok(f"{len(branches)} branches", {"branches": branches, "current": current})
        except Exception as e:
            return self._err(f"Branch list failed: {e}")

    def create_branch(self, project_path: str, branch_name: str) -> dict:
        """Create and switch to a new branch."""
        try:
            path = self._resolve(project_path)
            result = self._run_git(["git", "checkout", "-b", branch_name], cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Created branch: {branch_name}")
            return self._err(result["stderr"])
        except Exception as e:
            return self._err(f"Create branch failed: {e}")

    def switch_branch(self, project_path: str, branch_name: str) -> dict:
        """Switch to an existing branch."""
        try:
            path = self._resolve(project_path)
            result = self._run_git(["git", "checkout", branch_name], cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Switched to: {branch_name}")
            return self._err(result["stderr"])
        except Exception as e:
            return self._err(f"Switch branch failed: {e}")

    def add_remote(self, project_path: str, url: str, name: str = "origin") -> dict:
        """Add a remote repository."""
        try:
            path = self._resolve(project_path)
            result = self._run_git(["git", "remote", "add", name, url], cwd=path)
            if result["return_code"] == 0:
                return self._ok(f"✅ Remote '{name}' added → {url}")
            return self._err(result["stderr"])
        except Exception as e:
            return self._err(f"Add remote failed: {e}")

    def get_remotes(self, project_path: str) -> dict:
        """List all remotes."""
        try:
            path = self._resolve(project_path)
            result = self._run_git(["git", "remote", "-v"], cwd=path)
            return self._ok("Remotes", {"output": result["stdout"]})
        except Exception as e:
            return self._err(str(e))

    # ══════════════════════════════════════════
    # ONE-CLICK: STAGE + COMMIT + PUSH
    # ══════════════════════════════════════════

    def sync(self, project_path: str, message: str, branch: str = "main") -> dict:
        """Stage all, commit, and push in one operation."""
        results = []

        add_result = self.add(project_path)
        results.append(f"Stage: {add_result['message']}")
        if not add_result["success"]:
            return self._err(" | ".join(results))

        commit_result = self.commit(project_path, message)
        results.append(f"Commit: {commit_result['message']}")
        if not commit_result["success"]:
            return self._err(" | ".join(results))

        push_result = self.push(project_path, branch)
        results.append(f"Push: {push_result['message']}")

        if push_result["success"]:
            return self._ok("✅ Sync complete! " + " | ".join(results))
        return self._err(" | ".join(results))

    # ══════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════

    def _inject_token(self, url: str) -> str:
        """Inject GitHub token into HTTPS URL for authentication."""
        if not self._token or not self._username:
            return url
        if url.startswith("https://github.com/"):
            return url.replace(
                "https://github.com/",
                f"https://{self._username}:{self._token}@github.com/"
            )
        return url

    def _clean_token_from_error(self, error_msg: str) -> str:
        """Remove sensitive token from error messages."""
        if self._token:
            return error_msg.replace(self._token, "***")
        return error_msg

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / path

    def _run_git(self, cmd: list, cwd: Path = None) -> dict:
        """Run a git command via subprocess."""
        try:
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"  # Disable interactive prompts
            if self._token:
                env["GIT_ASKPASS"] = "echo"

            result = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            return {
                "return_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"return_code": 124, "stdout": "", "stderr": "Git command timed out"}
        except FileNotFoundError:
            return {"return_code": 127, "stdout": "", "stderr": "Git not installed. Run: apt install git"}
        except Exception as e:
            return {"return_code": 1, "stdout": "", "stderr": str(e)}

    @staticmethod
    def _ok(message: str, data: dict = None) -> dict:
        return {"success": True, "message": message, "data": data or {}}

    @staticmethod
    def _err(message: str) -> dict:
        return {"success": False, "message": message, "data": {}}
