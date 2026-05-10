"""
╔══════════════════════════════════════════════════════════════╗
║       PROJECT_MANAGER_MASTERPIECE - CONFIG MANAGER          ║
║       Persistent settings and preferences storage           ║
╚══════════════════════════════════════════════════════════════╝
"""

import json
from pathlib import Path
from datetime import datetime

CONFIG_DIR = Path("configs")
CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "settings.json"


# ─────────────────────────────────────────────
# DEFAULT CONFIGURATION
# ─────────────────────────────────────────────
DEFAULTS = {
    "version": "1.0.0",
    "theme": "dark",
    "language": "python",
    "editor": {
        "tab_size": 4,
        "word_wrap": True,
        "line_numbers": True,
        "font_size": 14,
        "font_family": "JetBrains Mono"
    },
    "terminal": {
        "max_history": 500,
        "timeout": 30,
        "shell": "bash"
    },
    "projects": {
        "base_dir": "projects",
        "auto_git_init": False,
        "create_readme": True,
        "create_gitignore": True
    },
    "git": {
        "default_branch": "main",
        "auto_stage_all": True,
        "push_on_commit": False
    },
    "gui": {
        "port": 7860,
        "share": False,
        "show_hidden_files": False
    },
    "security": {
        "sandbox_terminal": True,
        "block_dangerous_commands": True,
        "allow_pip_install": True,
        "max_file_size_mb": 50
    },
    "last_project": None,
    "recent_files": [],
    "created_at": datetime.now().isoformat()
}


class ConfigManager:
    """
    Loads and saves app configuration.
    Provides typed access to settings with defaults.
    """

    def __init__(self, config_file: str = None):
        self.path = Path(config_file) if config_file else CONFIG_FILE
        self._config = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                saved = json.loads(self.path.read_text())
                # Deep merge with defaults (new keys from defaults added)
                return self._deep_merge(DEFAULTS.copy(), saved)
            except Exception:
                return DEFAULTS.copy()
        # First run: save defaults
        self._save(DEFAULTS.copy())
        return DEFAULTS.copy()

    def _save(self, config: dict):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(config, indent=2))
        except Exception as e:
            print(f"⚠️  Config save failed: {e}")

    def _deep_merge(self, base: dict, override: dict) -> dict:
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                base[key] = self._deep_merge(base[key], val)
            else:
                base[key] = val
        return base

    def get(self, key: str, default=None):
        """Get a config value. Supports dot notation: 'editor.tab_size'"""
        parts = key.split(".")
        val = self._config
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return default
        return val if val is not None else default

    def set(self, key: str, value) -> bool:
        """Set a config value. Supports dot notation."""
        parts = key.split(".")
        config = self._config
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        config[parts[-1]] = value
        self._save(self._config)
        return True

    def get_all(self) -> dict:
        return self._config.copy()

    def reset(self):
        """Reset to defaults."""
        self._config = DEFAULTS.copy()
        self._save(self._config)

    def add_recent_file(self, path: str, max_recent: int = 20):
        """Track recently opened files."""
        recent = self.get("recent_files", [])
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.set("recent_files", recent[:max_recent])

    def set_last_project(self, path: str):
        self.set("last_project", path)

    def get_last_project(self) -> str:
        return self.get("last_project", "")

    def export_json(self) -> str:
        """Export config as formatted JSON string."""
        import json
        return json.dumps(self._config, indent=2)

    def import_json(self, json_str: str) -> bool:
        """Import config from JSON string."""
        try:
            new_config = json.loads(json_str)
            self._config = self._deep_merge(DEFAULTS.copy(), new_config)
            self._save(self._config)
            return True
        except Exception:
            return False

    def summary(self) -> str:
        """Human-readable config summary."""
        lines = [
            "⚙️  PM Masterpiece Configuration",
            "─" * 40,
            f"  Theme:        {self.get('theme')}",
            f"  Projects dir: {self.get('projects.base_dir')}",
            f"  Editor font:  {self.get('editor.font_family')} {self.get('editor.font_size')}pt",
            f"  Tab size:     {self.get('editor.tab_size')} spaces",
            f"  GUI port:     {self.get('gui.port')}",
            f"  Git branch:   {self.get('git.default_branch')}",
            f"  Last project: {self.get('last_project') or 'None'}",
            "─" * 40,
        ]
        return "\n".join(lines)
