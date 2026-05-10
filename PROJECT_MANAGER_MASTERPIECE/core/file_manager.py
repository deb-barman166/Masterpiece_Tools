"""
╔══════════════════════════════════════════════════════════════╗
║         PROJECT_MANAGER_MASTERPIECE - FILE MANAGER          ║
║         Complete File System Operations Controller           ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from core.security import SecurityGuard


# ─────────────────────────────────────────────
# File type categories for icons and syntax
# ─────────────────────────────────────────────
FILE_ICONS = {
    # Code files
    ".py": "🐍", ".js": "🟨", ".ts": "🔷", ".html": "🌐",
    ".css": "🎨", ".json": "📋", ".yaml": "⚙️", ".yml": "⚙️",
    ".sh": "💻", ".bash": "💻", ".md": "📝", ".txt": "📄",
    ".xml": "📰", ".toml": "⚙️", ".ini": "⚙️", ".env": "🔐",
    # Data files
    ".csv": "📊", ".xlsx": "📊", ".sql": "🗄️", ".db": "🗄️",
    # Image files
    ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🎞️",
    ".svg": "🎨", ".ico": "🖼️", ".webp": "🖼️",
    # Archive files
    ".zip": "📦", ".tar": "📦", ".gz": "📦", ".rar": "📦",
    # Config / build
    ".dockerfile": "🐳", ".gitignore": "🔧", ".lock": "🔒",
    # Default
    "default": "📄",
}

SYNTAX_LANGUAGES = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".html": "html", ".css": "css", ".json": "json",
    ".yaml": "yaml", ".yml": "yaml", ".sh": "bash",
    ".md": "markdown", ".xml": "xml", ".toml": "toml",
    ".sql": "sql", ".txt": "text",
}

# Max file size for preview (5 MB)
MAX_PREVIEW_SIZE = 5 * 1024 * 1024
# Max editable file size (10 MB)
MAX_EDIT_SIZE = 10 * 1024 * 1024


class FileManager:
    """
    Complete file system manager with full CRUD operations,
    tree visualization, and search capabilities.
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd() / "projects"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.security = SecurityGuard(str(self.base_dir))
        self._operation_log = []

    # ══════════════════════════════════════════
    # DIRECTORY TREE
    # ══════════════════════════════════════════

    def get_tree(self, path: str = None, max_depth: int = 6) -> dict:
        """
        Build a recursive file/folder tree structure.
        Returns JSON-serializable dict.
        """
        root = Path(path) if path else self.base_dir
        return self._build_tree_node(root, 0, max_depth)

    def _build_tree_node(self, path: Path, depth: int, max_depth: int) -> dict:
        """Recursively build tree node."""
        if depth > max_depth:
            return None

        stat = path.stat()
        node = {
            "name": path.name,
            "path": str(path),
            "type": "directory" if path.is_dir() else "file",
            "icon": "📁" if path.is_dir() else self._get_icon(path),
            "size": stat.st_size if path.is_file() else 0,
            "size_human": self._human_size(stat.st_size) if path.is_file() else "",
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "extension": path.suffix.lower() if path.is_file() else "",
            "children": []
        }

        if path.is_dir():
            try:
                children = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                for child in children:
                    if child.name.startswith('.') and child.name not in ['.gitignore', '.env']:
                        continue  # Skip most hidden files
                    child_node = self._build_tree_node(child, depth + 1, max_depth)
                    if child_node:
                        node["children"].append(child_node)
            except PermissionError:
                node["error"] = "Permission denied"

        return node

    def get_tree_text(self, path: str = None, prefix: str = "") -> str:
        """Return ASCII tree representation."""
        root = Path(path) if path else self.base_dir
        lines = [f"📁 {root.name}/"]
        self._ascii_tree(root, lines, "")
        return "\n".join(lines)

    def _ascii_tree(self, path: Path, lines: list, prefix: str, depth: int = 0, max_depth: int = 5):
        if depth > max_depth:
            return
        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            visible = [i for i in items if not (i.name.startswith('.') and i.name not in ['.gitignore'])]
            for idx, item in enumerate(visible):
                is_last = (idx == len(visible) - 1)
                connector = "└── " if is_last else "├── "
                icon = "📁 " if item.is_dir() else self._get_icon(item) + " "
                lines.append(f"{prefix}{connector}{icon}{item.name}")
                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    self._ascii_tree(item, lines, prefix + extension, depth + 1, max_depth)
        except PermissionError:
            lines.append(f"{prefix}└── [Permission Denied]")

    # ══════════════════════════════════════════
    # FILE OPERATIONS
    # ══════════════════════════════════════════

    def create_file(self, path: str, content: str = "") -> dict:
        """Create a new file with optional content."""
        try:
            file_path = self._resolve(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.exists():
                return self._err(f"File already exists: {file_path.name}")
            file_path.write_text(content, encoding="utf-8")
            self._log("create_file", str(file_path))
            return self._ok(f"✅ Created: {file_path.name}", {"path": str(file_path)})
        except Exception as e:
            return self._err(f"Create failed: {e}")

    def read_file(self, path: str) -> dict:
        """Read file content for editing/preview."""
        try:
            file_path = self._resolve(path)
            if not file_path.exists():
                return self._err(f"File not found: {path}")
            if not file_path.is_file():
                return self._err(f"Not a file: {path}")

            size = file_path.stat().st_size
            if size > MAX_PREVIEW_SIZE:
                return self._err(f"File too large to preview ({self._human_size(size)}). Max: 5MB")

            # Detect if binary
            try:
                content = file_path.read_text(encoding="utf-8")
                language = SYNTAX_LANGUAGES.get(file_path.suffix.lower(), "text")
                return self._ok("File read successfully", {
                    "content": content,
                    "language": language,
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": self._human_size(size),
                    "lines": len(content.splitlines())
                })
            except UnicodeDecodeError:
                return self._err(f"Binary file cannot be previewed: {file_path.name}")

        except Exception as e:
            return self._err(f"Read failed: {e}")

    def write_file(self, path: str, content: str) -> dict:
        """Save/update file content."""
        try:
            file_path = self._resolve(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Backup before writing
            if file_path.exists() and file_path.stat().st_size < MAX_EDIT_SIZE:
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                shutil.copy2(file_path, backup_path)

            file_path.write_text(content, encoding="utf-8")
            self._log("write_file", str(file_path))
            return self._ok(f"✅ Saved: {file_path.name}", {"path": str(file_path)})
        except Exception as e:
            return self._err(f"Write failed: {e}")

    def delete_file(self, path: str) -> dict:
        """Delete a file or empty directory."""
        try:
            target = self._resolve(path)
            if not target.exists():
                return self._err(f"Not found: {path}")
            name = target.name
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            self._log("delete", str(target))
            return self._ok(f"🗑️ Deleted: {name}")
        except Exception as e:
            return self._err(f"Delete failed: {e}")

    def rename_file(self, path: str, new_name: str) -> dict:
        """Rename a file or directory."""
        try:
            target = self._resolve(path)
            if not target.exists():
                return self._err(f"Not found: {path}")
            new_name = self.security.sanitize_filename(new_name)
            new_path = target.parent / new_name
            if new_path.exists():
                return self._err(f"Name already exists: {new_name}")
            target.rename(new_path)
            self._log("rename", f"{target} → {new_path}")
            return self._ok(f"✏️ Renamed: {target.name} → {new_name}", {"new_path": str(new_path)})
        except Exception as e:
            return self._err(f"Rename failed: {e}")

    def move_file(self, src: str, dest: str) -> dict:
        """Move a file or directory to a new location."""
        try:
            src_path = self._resolve(src)
            dest_path = self._resolve(dest)
            if not src_path.exists():
                return self._err(f"Source not found: {src}")
            dest_path.mkdir(parents=True, exist_ok=True) if dest_path.suffix == "" else None
            result = shutil.move(str(src_path), str(dest_path))
            self._log("move", f"{src_path} → {result}")
            return self._ok(f"📦 Moved: {src_path.name} → {dest_path}", {"new_path": result})
        except Exception as e:
            return self._err(f"Move failed: {e}")

    def copy_file(self, src: str, dest: str) -> dict:
        """Copy a file or directory."""
        try:
            src_path = self._resolve(src)
            dest_path = self._resolve(dest)
            if not src_path.exists():
                return self._err(f"Source not found: {src}")
            if src_path.is_dir():
                shutil.copytree(str(src_path), str(dest_path))
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_path), str(dest_path))
            self._log("copy", f"{src_path} → {dest_path}")
            return self._ok(f"📋 Copied: {src_path.name}", {"new_path": str(dest_path)})
        except Exception as e:
            return self._err(f"Copy failed: {e}")

    def create_folder(self, path: str) -> dict:
        """Create a new directory."""
        try:
            folder = self._resolve(path)
            folder.mkdir(parents=True, exist_ok=True)
            self._log("mkdir", str(folder))
            return self._ok(f"📁 Created folder: {folder.name}", {"path": str(folder)})
        except Exception as e:
            return self._err(f"Create folder failed: {e}")

    # ══════════════════════════════════════════
    # SEARCH
    # ══════════════════════════════════════════

    def search(self, query: str, path: str = None, extensions: list = None) -> dict:
        """Search files by name or content."""
        root = Path(path) if path else self.base_dir
        results = []
        query_lower = query.lower()

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if extensions and file_path.suffix.lower() not in extensions:
                continue

            # Match by filename
            if query_lower in file_path.name.lower():
                results.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "match_type": "filename",
                    "icon": self._get_icon(file_path)
                })
                continue

            # Match by content (text files only, reasonable size)
            if file_path.stat().st_size < 1 * 1024 * 1024:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if query_lower in content.lower():
                        # Find line numbers
                        for i, line in enumerate(content.splitlines(), 1):
                            if query_lower in line.lower():
                                results.append({
                                    "path": str(file_path),
                                    "name": file_path.name,
                                    "match_type": "content",
                                    "line": i,
                                    "preview": line.strip()[:100],
                                    "icon": self._get_icon(file_path)
                                })
                                break
                except Exception:
                    pass

        return self._ok(f"Found {len(results)} results", {"results": results, "count": len(results)})

    # ══════════════════════════════════════════
    # PROJECT MANAGEMENT
    # ══════════════════════════════════════════

    def list_projects(self) -> list[dict]:
        """List all projects in the projects directory."""
        projects = []
        try:
            for item in sorted(self.base_dir.iterdir()):
                if item.is_dir():
                    # Count files
                    file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                    stat = item.stat()
                    projects.append({
                        "name": item.name,
                        "path": str(item),
                        "files": file_count,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "size": self._human_size(self._dir_size(item))
                    })
        except Exception:
            pass
        return projects

    def get_file_info(self, path: str) -> dict:
        """Get detailed file information."""
        try:
            file_path = self._resolve(path)
            if not file_path.exists():
                return self._err("File not found")
            stat = file_path.stat()
            return self._ok("File info", {
                "name": file_path.name,
                "path": str(file_path),
                "type": "directory" if file_path.is_dir() else "file",
                "size": self._human_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "extension": file_path.suffix,
                "language": SYNTAX_LANGUAGES.get(file_path.suffix.lower(), "unknown"),
                "icon": self._get_icon(file_path)
            })
        except Exception as e:
            return self._err(str(e))

    # ══════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════

    def _resolve(self, path: str) -> Path:
        """Resolve path relative to base_dir."""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.base_dir / path

    @staticmethod
    def _get_icon(path: Path) -> str:
        return FILE_ICONS.get(path.suffix.lower(), FILE_ICONS["default"])

    @staticmethod
    def _human_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def _dir_size(path: Path) -> int:
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

    def _log(self, operation: str, target: str):
        self._operation_log.append({
            "operation": operation,
            "target": target,
            "timestamp": datetime.now().isoformat()
        })

    @staticmethod
    def _ok(message: str, data: dict = None) -> dict:
        return {"success": True, "message": message, "data": data or {}}

    @staticmethod
    def _err(message: str) -> dict:
        return {"success": False, "message": message, "data": {}}
