# ⚡ PROJECT_MANAGER_MASTERPIECE

> **A complete Python-only Cloud Developer Environment**
> Mini VS Code · Linux Terminal · GitHub Desktop · Cloud IDE — All in ONE

---

## 🎯 What is This?

**PROJECT_MANAGER_MASTERPIECE** is a professional-grade developer environment built entirely in Python.
It gives you a full IDE-like experience directly in your browser, local machine, or Google Colab.

### ✨ Features at a Glance

| Category | Features |
|---|---|
| 📁 **File Manager** | Create, Delete, Rename, Move, Copy, Search, Tree View |
| 📝 **Code Editor** | Syntax highlighting, multi-file, save/load |
| 💻 **Terminal** | Real Linux terminal, command history, sandboxed |
| 🐙 **GitHub** | Clone, Push, Pull, Commit, Branch, Sync |
| 📦 **ZIP Manager** | Upload ZIP, Extract, Compress projects |
| 🖥️ **GUI Mode** | VS Code dark theme, browser-based Gradio UI |
| ⌨️ **CLI Mode** | Rich-powered terminal with colored output |
| 🔒 **Security** | Sandboxed commands, path protection, dangerous cmd blocking |

---

## 🚀 Quick Start

### Option 1: Local Installation

```bash
# 1. Clone or download the project
git clone https://github.com/your-repo/PROJECT_MANAGER_MASTERPIECE.git
cd PROJECT_MANAGER_MASTERPIECE

# 2. Install dependencies
python install.py

# 3. Launch!
python main.py
```

### Option 2: Google Colab

```python
# In a Colab cell:
!git clone https://github.com/your-repo/PROJECT_MANAGER_MASTERPIECE.git
%cd PROJECT_MANAGER_MASTERPIECE
!pip install -r requirements.txt -q
!python main.py --gui --share
```

### Option 3: Android Termux

```bash
pkg install python git
pip install gradio rich gitpython
python main.py --cli  # Use CLI mode on Termux
```

---

## 🖥️ GUI Mode (Recommended)

Launch the browser-based VS Code-inspired interface:

```bash
python main.py --gui                  # Open on localhost:7860
python main.py --gui --port 8080      # Custom port
python main.py --gui --share          # Public share link (Colab)
```

### GUI Tabs

| Tab | Description |
|---|---|
| 🏠 **Dashboard** | Project overview, quick actions, upload ZIP |
| 📁 **Files** | Full file manager with tree, create/delete/rename/search |
| 📝 **Editor** | Open, edit, and save any file with syntax highlighting |
| 💻 **Terminal** | Interactive Linux terminal with Python runner & pip installer |
| 🐙 **GitHub** | Full Git integration — clone, commit, push, pull, branches |

---

## ⌨️ CLI Mode

Interactive shell with colored output:

```bash
python main.py --cli
```

### CLI Commands Reference

```
FILE OPERATIONS
  pm create-file <name>         Create a new file
  pm delete-file <path>         Delete file or folder
  pm rename-file <old> <new>    Rename a file
  pm move-file <src> <dest>     Move a file
  pm open <file>                Open/view a file with syntax highlighting
  pm tree [path]                Show folder tree
  pm search <query>             Search files and content
  pm ls [path]                  List directory contents

PROJECT MANAGEMENT
  pm projects                   List all projects
  pm new-project <name>         Create project with structure
  pm upload <zip>               Upload and extract a ZIP
  pm zip <project>              Compress a project to ZIP
  pm unzip <file>               Extract a ZIP file

EXECUTION
  pm run <script.py>            Run a Python script
  pm install <package>          Install pip packages
  pm shell                      Drop into interactive shell

GIT / GITHUB
  pm git-config                 Set GitHub credentials (interactive)
  pm git-init [path]            Initialize git repository
  pm git-status [path]          Show git status
  pm git-add [files...]         Stage files (default: all)
  pm git-commit <message>       Create a commit
  pm git-push [branch]          Push to remote
  pm git-pull [branch]          Pull from remote
  pm clone <url> [name]         Clone a repository
  pm git-log [path]             Show commit history
  pm git-branch [path]          List all branches
  pm git-sync <message>         Stage + Commit + Push (one command)

SYSTEM
  pm help                       Show all commands
  pm clear                      Clear the screen
  pm exit                       Exit the shell
```

---

## 🐙 GitHub Setup

### Step 1: Create a Personal Access Token
1. Go to: **GitHub → Settings → Developer Settings → Personal Access Tokens**
2. Click **"Generate new token (classic)"**
3. Select scopes: `repo`, `workflow`
4. Copy the token

### Step 2: Set Credentials

**GUI:** Go to `🐙 GitHub` tab → `🔑 Credentials` → enter username, email, and token.

**CLI:**
```bash
pm git-config
# Follow interactive prompts
```

### Step 3: Use Git

```bash
pm clone https://github.com/user/repo.git
pm git-status my-repo
pm git-sync "feat: add new feature"
```

---

## 📁 Project Structure

```
PROJECT_MANAGER_MASTERPIECE/
│
├── core/                       ← Core engine modules
│   ├── __init__.py
│   ├── terminal_engine.py      ← Linux terminal executor
│   ├── file_manager.py         ← File system operations
│   ├── git_manager.py          ← GitHub integration
│   ├── zip_manager.py          ← ZIP archive handler
│   ├── command_parser.py       ← CLI command parser
│   ├── security.py             ← Sandboxed security guard
│   └── logger.py               ← Logging & audit trail
│
├── gui/                        ← Gradio GUI interface
│   ├── __init__.py
│   └── app.py                  ← VS Code-themed Gradio app
│
├── cli/                        ← CLI shell interface
│   ├── __init__.py
│   └── shell.py                ← Rich-powered CLI shell
│
├── configs/                    ← Configuration files
│   └── config_manager.py       ← Settings persistence
│
├── projects/                   ← Your projects live here
├── logs/                       ← Operation logs
├── temp/                       ← Temporary files (auto-cleaned)
├── assets/                     ← Static assets
│
├── main.py                     ← Main entry point
├── launcher.py                 ← Smart auto-launcher
├── install.py                  ← Auto-installer
├── requirements.txt            ← Python dependencies
└── README.md                   ← This file
```

---

## 🔒 Security

The security system blocks dangerous commands automatically:

| Blocked | Reason |
|---|---|
| `rm -rf /` | System destruction |
| `shutdown`, `reboot` | System control |
| `mkfs`, `fdisk` | Disk formatting |
| `: (){ :\|:& };:` | Fork bomb |
| `curl ... \| bash` | Remote code execution |
| `chmod -R 777 /` | Permission escalation |

All file operations are sandboxed to the `projects/` directory.
Directory traversal attacks (../../etc/passwd) are detected and blocked.
ZIP Slip attacks are detected during archive extraction.

---

## ⚙️ Dependencies

| Package | Purpose | Required |
|---|---|---|
| `gradio` | Browser-based GUI | Yes (for GUI mode) |
| `rich` | Colored CLI output | Yes (for CLI mode) |
| `gitpython` | Git operations | Optional (uses subprocess fallback) |
| `typer` | CLI framework | Optional |

```bash
pip install gradio rich gitpython typer
# or
pip install -r requirements.txt
```

---

## 🌍 Platform Support

| Platform | GUI Mode | CLI Mode | Notes |
|---|---|---|---|
| Windows | ✅ | ✅ | Full support |
| Linux | ✅ | ✅ | Full support |
| macOS | ✅ | ✅ | Full support |
| Google Colab | ✅ | ✅ | Use `--share` flag |
| Jupyter | ✅ | ✅ | Auto-detected |
| Android Termux | ⚠️ | ✅ | CLI recommended |
| Mobile Browser | ✅ | — | Responsive GUI |

---

## 🔧 Configuration

Settings are stored in `configs/settings.json`. Edit via the app or manually:

```json
{
  "theme": "dark",
  "editor": {
    "tab_size": 4,
    "font_size": 14,
    "font_family": "JetBrains Mono"
  },
  "gui": {
    "port": 7860,
    "share": false
  },
  "git": {
    "default_branch": "main"
  }
}
```

---

## 📜 License

MIT License — Free to use, modify, and distribute.

---

## 👨‍💻 Built With

- **Python 3.10+** — Pure Python, no JS/Node required
- **Gradio 4.x** — Browser UI framework
- **Rich** — Terminal styling
- **GitPython / subprocess** — Git operations
- **Standard Library** — os, shutil, pathlib, subprocess, zipfile

---

*Built with ⚡ by PROJECT_MANAGER_MASTERPIECE*
