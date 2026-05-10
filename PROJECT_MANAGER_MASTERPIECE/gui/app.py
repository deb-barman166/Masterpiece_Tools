"""
╔══════════════════════════════════════════════════════════════╗
║         PROJECT_MANAGER_MASTERPIECE - GRADIO GUI            ║
║         VS Code Inspired Professional Dark Interface         ║
╚══════════════════════════════════════════════════════════════╝
"""

import gradio as gr
import os
import json
import threading
import queue
from pathlib import Path
from datetime import datetime

from core.file_manager import FileManager
from core.terminal_engine import TerminalManager
from core.git_manager import GitManager
from core.zip_manager import ZipManager


# ─────────────────────────────────────────────
# VS CODE DARK THEME CSS
# ─────────────────────────────────────────────
CUSTOM_CSS = """
/* ═══════════════════════════════════════════
   VS Code Dark+ Theme for PM Masterpiece
   ═══════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --vsc-bg:         #1e1e1e;
    --vsc-sidebar:    #252526;
    --vsc-panel:      #1e1e1e;
    --vsc-border:     #3c3c3c;
    --vsc-accent:     #007acc;
    --vsc-accent2:    #0098ff;
    --vsc-green:      #4ec9b0;
    --vsc-yellow:     #dcdcaa;
    --vsc-red:        #f44747;
    --vsc-orange:     #ce9178;
    --vsc-purple:     #c586c0;
    --vsc-text:       #d4d4d4;
    --vsc-text-dim:   #858585;
    --vsc-text-bright:#ffffff;
    --vsc-tab-active: #1e1e1e;
    --vsc-tab-bg:     #2d2d2d;
    --vsc-terminal:   #0c0c0c;
    --vsc-hover:      #2a2d2e;
    --vsc-select:     #094771;
    --mono: 'JetBrains Mono', 'Fira Code', monospace;
    --sans: 'Inter', system-ui, sans-serif;
}

/* ─── Base ─── */
.gradio-container {
    background: var(--vsc-bg) !important;
    font-family: var(--sans) !important;
    max-width: 100% !important;
    padding: 0 !important;
}

body { background: var(--vsc-bg) !important; }

/* ─── Title Bar ─── */
.pm-titlebar {
    background: #323233;
    border-bottom: 1px solid #000;
    padding: 6px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #cccccc;
    font-family: var(--sans);
    user-select: none;
}

.pm-titlebar .dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    display: inline-block;
}
.dot-red { background: #ff5f57; }
.dot-yellow { background: #febc2e; }
.dot-green { background: #28c840; }

/* ─── Activity Bar (left icon rail) ─── */
.pm-activity {
    background: #333333;
    border-right: 1px solid var(--vsc-border);
    width: 48px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px 0;
    gap: 4px;
}

/* ─── Tabs ─── */
.gr-tab-nav {
    background: var(--vsc-tab-bg) !important;
    border-bottom: 1px solid var(--vsc-border) !important;
    padding: 0 !important;
    gap: 0 !important;
}

.gr-tab-nav button {
    background: var(--vsc-tab-bg) !important;
    color: var(--vsc-text-dim) !important;
    border: none !important;
    border-right: 1px solid var(--vsc-border) !important;
    border-radius: 0 !important;
    padding: 8px 20px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    transition: all 0.1s ease !important;
    margin: 0 !important;
}

.gr-tab-nav button:hover {
    background: var(--vsc-hover) !important;
    color: var(--vsc-text) !important;
}

.gr-tab-nav button.selected {
    background: var(--vsc-tab-active) !important;
    color: var(--vsc-text-bright) !important;
    border-bottom: 2px solid var(--vsc-accent) !important;
    font-weight: 500 !important;
}

/* ─── Panels & Blocks ─── */
.gr-panel, .gr-block, .gr-box {
    background: var(--vsc-sidebar) !important;
    border: 1px solid var(--vsc-border) !important;
    border-radius: 4px !important;
}

/* ─── Labels ─── */
label, .gr-label, .label-wrap {
    color: var(--vsc-text-dim) !important;
    font-family: var(--sans) !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ─── Textareas & Inputs ─── */
textarea, input[type="text"], input[type="password"] {
    background: var(--vsc-bg) !important;
    color: var(--vsc-text) !important;
    border: 1px solid var(--vsc-border) !important;
    border-radius: 3px !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    line-height: 1.5 !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: var(--vsc-accent) !important;
    outline: none !important;
    box-shadow: 0 0 0 1px var(--vsc-accent) !important;
}

/* ─── Terminal Textarea ─── */
.terminal-output textarea {
    background: var(--vsc-terminal) !important;
    color: #00ff41 !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    border: none !important;
    border-top: 1px solid var(--vsc-border) !important;
    border-radius: 0 !important;
    padding: 12px !important;
    min-height: 220px !important;
    line-height: 1.6 !important;
}

/* ─── Code Editor ─── */
.code-editor textarea {
    background: #1e1e1e !important;
    color: #d4d4d4 !important;
    font-family: var(--mono) !important;
    font-size: 14px !important;
    min-height: 400px !important;
    border: none !important;
    padding: 16px !important;
    tab-size: 4 !important;
    line-height: 1.6 !important;
}

/* ─── File Tree ─── */
.file-tree textarea {
    background: var(--vsc-sidebar) !important;
    color: var(--vsc-text) !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    border: none !important;
    min-height: 500px !important;
    line-height: 1.7 !important;
    padding: 8px !important;
}

/* ─── Buttons ─── */
button.primary-btn, .gr-button.primary {
    background: var(--vsc-accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
}

button.primary-btn:hover { background: var(--vsc-accent2) !important; }

.gr-button {
    background: #3c3c3c !important;
    color: var(--vsc-text) !important;
    border: 1px solid #555 !important;
    border-radius: 3px !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    transition: all 0.1s ease !important;
}

.gr-button:hover {
    background: #505050 !important;
    border-color: var(--vsc-accent) !important;
    color: white !important;
}

/* ─── Status Bar ─── */
.status-bar {
    background: var(--vsc-accent) !important;
    color: white !important;
    padding: 3px 12px !important;
    font-size: 12px !important;
    font-family: var(--sans) !important;
    display: flex !important;
    align-items: center !important;
    gap: 16px !important;
}

/* ─── Accordion ─── */
.gr-accordion {
    background: var(--vsc-sidebar) !important;
    border: 1px solid var(--vsc-border) !important;
    border-radius: 3px !important;
}

.gr-accordion-header {
    color: var(--vsc-text) !important;
    background: #2d2d2d !important;
    font-family: var(--sans) !important;
    font-size: 13px !important;
}

/* ─── Dropdowns ─── */
.gr-dropdown select, select {
    background: var(--vsc-bg) !important;
    color: var(--vsc-text) !important;
    border: 1px solid var(--vsc-border) !important;
    border-radius: 3px !important;
    font-family: var(--sans) !important;
}

/* ─── Dataframes/Tables ─── */
.gr-dataframe {
    background: var(--vsc-bg) !important;
    color: var(--vsc-text) !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
}

/* ─── Markdown output ─── */
.gr-markdown {
    color: var(--vsc-text) !important;
    font-family: var(--sans) !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
}

.gr-markdown code {
    background: #2d2d2d !important;
    color: var(--vsc-orange) !important;
    font-family: var(--mono) !important;
    padding: 2px 6px !important;
    border-radius: 3px !important;
}

/* ─── Section Headers ─── */
.section-header {
    color: var(--vsc-text-dim);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 4px 0;
    border-bottom: 1px solid var(--vsc-border);
    margin-bottom: 8px;
}

/* ─── Git Status Colors ─── */
.git-clean { color: #4ec9b0; }
.git-dirty { color: #dcdcaa; }
.git-error { color: #f44747; }

/* ─── Scrollbars ─── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--vsc-bg); }
::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #777; }

/* ─── Row/Column overrides ─── */
.gr-row { gap: 8px !important; }
.gr-col { padding: 4px !important; }

/* ─── Upload ─── */
.gr-file-upload {
    background: var(--vsc-bg) !important;
    border: 2px dashed var(--vsc-border) !important;
    border-radius: 6px !important;
    color: var(--vsc-text-dim) !important;
}

.gr-file-upload:hover {
    border-color: var(--vsc-accent) !important;
}
"""

# ─────────────────────────────────────────────
# HEADER HTML
# ─────────────────────────────────────────────
HEADER_HTML = """
<div style="
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 1px solid #007acc;
    padding: 0;
    margin: 0;
    font-family: 'JetBrains Mono', monospace;
">
  <div style="
    display: flex; align-items: center; gap: 12px;
    padding: 8px 16px;
    background: #2c2c2c;
    border-bottom: 1px solid #111;
  ">
    <span style="display:flex;gap:6px;">
      <span style="width:13px;height:13px;border-radius:50%;background:#ff5f57;display:inline-block;"></span>
      <span style="width:13px;height:13px;border-radius:50%;background:#febc2e;display:inline-block;"></span>
      <span style="width:13px;height:13px;border-radius:50%;background:#28c840;display:inline-block;"></span>
    </span>
    <span style="color:#cccccc;font-size:13px;margin-left:8px;letter-spacing:0.02em;">
      PROJECT_MANAGER_MASTERPIECE — v1.0.0
    </span>
    <span style="margin-left:auto;color:#555;font-size:11px;">Python Cloud Dev Environment</span>
  </div>
  <div style="
    display: flex; align-items: center;
    padding: 12px 24px 16px;
    gap: 16px;
  ">
    <div style="display:flex;flex-direction:column;gap:2px;">
      <span style="
        font-size: 22px; font-weight: 700; color: #ffffff;
        letter-spacing: -0.03em; line-height: 1;
      ">⚡ PM Masterpiece</span>
      <span style="
        font-size: 12px; color: #007acc; letter-spacing: 0.1em;
        text-transform: uppercase; font-weight: 500;
      ">
        Mini VS Code · Linux Terminal · GitHub Desktop · Cloud IDE
      </span>
    </div>
    <div style="margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;">
      <span style="background:#007acc22;color:#007acc;padding:3px 10px;border-radius:12px;font-size:11px;border:1px solid #007acc44;">Python-Only</span>
      <span style="background:#4ec9b022;color:#4ec9b0;padding:3px 10px;border-radius:12px;font-size:11px;border:1px solid #4ec9b044;">Cross-Platform</span>
      <span style="background:#c586c022;color:#c586c0;padding:3px 10px;border-radius:12px;font-size:11px;border:1px solid #c586c044;">GitHub Ready</span>
    </div>
  </div>
</div>
"""

STATUS_HTML = """
<div style="
    background: #007acc; color: white; padding: 3px 16px;
    font-family: 'Inter', sans-serif; font-size: 12px;
    display: flex; align-items: center; gap: 20px;
    border-top: 1px solid #005f9e;
">
  <span>⎇ main</span>
  <span>📁 projects/</span>
  <span>Python 3.x</span>
  <span style="margin-left:auto;">PM Masterpiece v1.0.0</span>
</div>
"""


def build_gui(base_dir: str = None):
    """Build and return the complete Gradio interface."""

    # Initialize managers
    base = Path(base_dir) if base_dir else Path.cwd() / "projects"
    base.mkdir(parents=True, exist_ok=True)

    fm = FileManager(str(base))
    tm = TerminalManager(str(base))
    gm = GitManager(str(base))
    zm = ZipManager(str(base))

    terminal_history = []  # Store terminal output

    # ══════════════════════════════════════════
    # FILE MANAGER FUNCTIONS
    # ══════════════════════════════════════════

    def refresh_tree():
        tree = fm.get_tree_text()
        projects = fm.list_projects()
        proj_list = "\n".join([
            f"📁 {p['name']}  ({p['files']} files, {p['size']}, modified {p['modified']})"
            for p in projects
        ]) or "No projects yet. Upload a ZIP or create a new project."
        return tree, proj_list

    def do_create_file(name, content, project):
        if not name:
            return "❌ Please enter a file name", *refresh_tree()
        path = f"{project}/{name}" if project else name
        result = fm.create_file(path, content)
        tree, proj = refresh_tree()
        return result["message"], tree, proj

    def do_delete_file(path):
        if not path:
            return "❌ Please enter a path", *refresh_tree()
        result = fm.delete_file(path)
        tree, proj = refresh_tree()
        return result["message"], tree, proj

    def do_rename_file(old_path, new_name):
        if not old_path or not new_name:
            return "❌ Both path and new name are required", *refresh_tree()
        result = fm.rename_file(old_path, new_name)
        tree, proj = refresh_tree()
        return result["message"], tree, proj

    def do_open_file(path):
        if not path:
            return "❌ Enter a file path", ""
        result = fm.read_file(path)
        if result["success"]:
            data = result["data"]
            info = f"📄 {data['name']} | {data['lines']} lines | {data['size']} | {data['language']}"
            return info, data["content"]
        return result["message"], ""

    def do_save_file(path, content):
        if not path:
            return "❌ No file path specified"
        result = fm.write_file(path, content)
        return result["message"]

    def do_search(query):
        if not query:
            return "❌ Enter a search query"
        result = fm.search(query)
        if result["success"]:
            items = result["data"]["results"]
            if not items:
                return "🔍 No results found"
            lines = [f"🔍 Found {len(items)} results for '{query}':"]
            for r in items:
                icon = r.get("icon", "📄")
                match_type = r["match_type"]
                preview = r.get("preview", "")
                line_no = f":{r['line']}" if "line" in r else ""
                lines.append(f"  {icon} {r['name']}{line_no} [{match_type}]")
                if preview:
                    lines.append(f"      → {preview[:80]}")
            return "\n".join(lines)
        return result["message"]

    def do_new_project(name):
        if not name:
            return "❌ Enter a project name", *refresh_tree()
        result = fm.create_folder(name)
        if result["success"]:
            project_path = Path(result["data"]["path"])
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "README.md").write_text(
                f"# {name}\n\nCreated with PM Masterpiece.\n\n## Setup\n\n```bash\npython main.py\n```\n"
            )
            (project_path / ".gitignore").write_text(
                "__pycache__/\n*.pyc\n*.egg-info/\ndist/\nbuild/\n.env\n.venv/\n"
            )
            (project_path / "main.py").write_text(
                f'"""\n{name} - Main Entry Point\nCreated with PM Masterpiece\n"""\n\ndef main():\n    print("Hello from {name}!")\n\nif __name__ == "__main__":\n    main()\n'
            )
            msg = f"✅ Project '{name}' created with README, .gitignore, main.py"
        else:
            msg = result["message"]
        tree, proj = refresh_tree()
        return msg, tree, proj

    def do_create_folder(path):
        if not path:
            return "❌ Enter a folder path", *refresh_tree()
        result = fm.create_folder(path)
        tree, proj = refresh_tree()
        return result["message"], tree, proj

    # ══════════════════════════════════════════
    # ZIP FUNCTIONS
    # ══════════════════════════════════════════

    def do_upload_zip(file, proj_name):
        if file is None:
            return "❌ No file uploaded", *refresh_tree()
        name = proj_name.strip() if proj_name else None
        result = zm.handle_upload(file.name, name)
        tree, proj = refresh_tree()
        return result["message"], tree, proj

    def do_zip_project(path, zip_name):
        if not path:
            return "❌ Enter a project path"
        result = zm.create_zip(path, zip_name or None)
        if result["success"]:
            return f"{result['message']}\n💾 Saved to: {result['data']['zip_path']}"
        return result["message"]

    # ══════════════════════════════════════════
    # TERMINAL FUNCTIONS
    # ══════════════════════════════════════════

    def run_terminal_cmd(command, history_text):
        if not command.strip():
            return history_text, ""

        timestamp = datetime.now().strftime("%H:%M:%S")
        result = tm.execute(command)
        session = tm.get_session()

        lines = [f"\n[{timestamp}] {session.prompt}{command}"]

        if result["stdout"]:
            lines.append(result["stdout"])
        if result["stderr"]:
            lines.append(f"[ERR] {result['stderr']}")
        if not result["success"]:
            lines.append(f"[exit: {result['return_code']}]")

        new_output = history_text + "\n".join(lines)

        # Keep last 200 lines
        all_lines = new_output.splitlines()
        if len(all_lines) > 200:
            new_output = "\n".join(all_lines[-200:])

        return new_output, ""  # Clear input

    def clear_terminal():
        return ""

    def run_python_script(path):
        if not path:
            return "❌ Enter a Python script path"
        result = tm.execute(f"python {path}")
        out = ""
        if result["stdout"]:
            out += result["stdout"]
        if result["stderr"]:
            out += f"\n[stderr]\n{result['stderr']}"
        return out or "Script ran with no output"

    def install_package(package):
        if not package:
            return "❌ Enter a package name"
        result = tm.execute(f"pip install {package}")
        out = result["stdout"] or result["stderr"] or "Done"
        return out

    # ══════════════════════════════════════════
    # GIT FUNCTIONS
    # ══════════════════════════════════════════

    def save_git_config(username, email, token):
        if not all([username, email, token]):
            return "❌ All fields required"
        result = gm.set_credentials(username, email, token)
        return result["message"]

    def do_git_status(project):
        if not project:
            return "❌ Enter a project path"
        result = gm.status(project)
        if result["success"]:
            data = result["data"]
            lines = [
                f"Branch: {data['branch']}",
                f"Status: {'✅ Clean' if data['is_clean'] else '⚠️ Changes present'}",
                "",
                data["full_status"]
            ]
            return "\n".join(lines)
        return result["message"]

    def do_git_init(project):
        if not project:
            return "❌ Enter a project path"
        result = gm.init(project)
        return result["message"]

    def do_git_clone(url, name):
        if not url:
            return "❌ Enter repository URL"
        result = gm.clone(url, name or None)
        return result["message"]

    def do_git_add_commit_push(project, message, branch):
        if not project:
            return "❌ Enter a project path"
        if not message:
            message = f"Update ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        result = gm.sync(project, message, branch or "main")
        return result["message"]

    def do_git_pull(project, branch):
        if not project:
            return "❌ Enter a project path"
        result = gm.pull(project, branch or "")
        return result["message"]

    def do_git_log(project):
        if not project:
            return "❌ Enter a project path"
        result = gm.get_log(project)
        if result["success"]:
            commits = result["data"]["commits"]
            if not commits:
                return "No commits yet"
            lines = []
            for c in commits:
                lines.append(f"● {c['hash']}  {c['author']}  {c['time']}")
                lines.append(f"  {c['message']}")
                lines.append("")
            return "\n".join(lines)
        return result["message"]

    def do_git_branches(project):
        if not project:
            return "❌ Enter a project path"
        result = gm.list_branches(project)
        if result["success"]:
            branches = result["data"]["branches"]
            lines = []
            for b in branches:
                marker = "* " if b["current"] else "  "
                lines.append(f"{marker}{b['name']}")
            return "\n".join(lines) or "No branches"
        return result["message"]

    def do_add_remote(project, url, remote_name):
        if not project or not url:
            return "❌ Project path and URL required"
        result = gm.add_remote(project, url, remote_name or "origin")
        return result["message"]

    # ══════════════════════════════════════════
    # BUILD THE GRADIO INTERFACE
    # ══════════════════════════════════════════

    with gr.Blocks(
        css=CUSTOM_CSS,
        title="⚡ PM Masterpiece",
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        )
    ) as app:

        # ── Header ──
        gr.HTML(HEADER_HTML)

        # ── Main Tabs ──
        with gr.Tabs():

            # ════════════════════════════════
            # TAB 1: PROJECT DASHBOARD
            # ════════════════════════════════
            with gr.Tab("🏠 Dashboard"):
                gr.Markdown("## Project Dashboard")

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📁 Projects")
                        project_list = gr.Textbox(
                            label="Your Projects",
                            value=refresh_tree()[1],
                            lines=12,
                            interactive=False,
                            elem_classes=["file-tree"]
                        )
                        refresh_btn = gr.Button("🔄 Refresh", size="sm")

                    with gr.Column(scale=2):
                        gr.Markdown("### ✨ Quick Actions")

                        with gr.Row():
                            with gr.Column():
                                new_proj_name = gr.Textbox(label="New Project Name", placeholder="my-awesome-project")
                                new_proj_btn = gr.Button("📁 Create Project", variant="primary")

                            with gr.Column():
                                upload_zip = gr.File(label="Upload ZIP Project", file_types=[".zip"])
                                upload_name = gr.Textbox(label="Project Name (optional)", placeholder="auto-detect from ZIP")
                                upload_btn = gr.Button("📤 Upload & Extract", variant="primary")

                        dashboard_status = gr.Textbox(label="Status", lines=3, interactive=False)

                        gr.Markdown("### 📊 System Info")
                        sys_info = gr.Markdown(f"""
| Property | Value |
|---------|-------|
| **Platform** | {__import__('platform').system()} {__import__('platform').release()} |
| **Python** | {__import__('sys').version.split()[0]} |
| **Projects Dir** | `{base}` |
| **Git** | Available |
                        """)

                # Events
                refresh_btn.click(
                    fn=lambda: refresh_tree()[1],
                    outputs=[project_list]
                )
                new_proj_btn.click(
                    fn=do_new_project,
                    inputs=[new_proj_name],
                    outputs=[dashboard_status, gr.Textbox(visible=False), project_list]
                )
                upload_btn.click(
                    fn=do_upload_zip,
                    inputs=[upload_zip, upload_name],
                    outputs=[dashboard_status, gr.Textbox(visible=False), project_list]
                )

            # ════════════════════════════════
            # TAB 2: FILE MANAGER
            # ════════════════════════════════
            with gr.Tab("📁 Files"):
                with gr.Row():
                    # ── Left: File Tree ──
                    with gr.Column(scale=1, min_width=280):
                        gr.Markdown("### Explorer")
                        file_tree_display = gr.Textbox(
                            label="File Tree",
                            value=refresh_tree()[0],
                            lines=20,
                            interactive=False,
                            elem_classes=["file-tree"]
                        )
                        tree_refresh_btn = gr.Button("🔄 Refresh Tree", size="sm")

                    # ── Right: File Operations ──
                    with gr.Column(scale=2):
                        gr.Markdown("### File Operations")

                        with gr.Tabs():
                            with gr.Tab("➕ Create"):
                                cf_project = gr.Textbox(label="Project Path", placeholder="my-project")
                                cf_name = gr.Textbox(label="File Name", placeholder="script.py")
                                cf_content = gr.Textbox(
                                    label="Initial Content (optional)",
                                    lines=8,
                                    placeholder="# Your code here...",
                                    elem_classes=["code-editor"]
                                )
                                cf_btn = gr.Button("➕ Create File", variant="primary")
                                cf_status = gr.Textbox(label="Result", lines=2, interactive=False)

                                cf_folder_path = gr.Textbox(label="Folder Path", placeholder="project/subfolder")
                                mkdir_btn = gr.Button("📁 Create Folder", variant="secondary")
                                mkdir_status = gr.Textbox(label="Result", lines=2, interactive=False)

                            with gr.Tab("🗑️ Delete"):
                                del_path = gr.Textbox(label="File/Folder Path", placeholder="project/file.py")
                                del_btn = gr.Button("🗑️ Delete", variant="stop")
                                del_status = gr.Textbox(label="Result", lines=2, interactive=False)

                            with gr.Tab("✏️ Rename / Move"):
                                rn_old = gr.Textbox(label="Current Path", placeholder="project/old_name.py")
                                rn_new = gr.Textbox(label="New Name", placeholder="new_name.py")
                                rn_btn = gr.Button("✏️ Rename", variant="primary")
                                rn_status = gr.Textbox(label="Result", lines=2, interactive=False)

                            with gr.Tab("🔍 Search"):
                                search_query = gr.Textbox(label="Search Query", placeholder="def main")
                                search_btn = gr.Button("🔍 Search", variant="primary")
                                search_results = gr.Textbox(
                                    label="Results",
                                    lines=12,
                                    interactive=False,
                                    elem_classes=["terminal-output"]
                                )

                            with gr.Tab("📦 ZIP"):
                                zip_path_input = gr.Textbox(label="Project/Path to ZIP", placeholder="my-project")
                                zip_output_name = gr.Textbox(label="ZIP Name (optional)", placeholder="my-project.zip")
                                zip_btn = gr.Button("📦 Create ZIP", variant="primary")
                                zip_status = gr.Textbox(label="Result", lines=3, interactive=False)

                file_op_status = gr.Textbox(label="Operation Status", lines=2, interactive=False, visible=False)

                # Events
                tree_refresh_btn.click(fn=lambda: refresh_tree()[0], outputs=[file_tree_display])
                cf_btn.click(
                    fn=do_create_file,
                    inputs=[cf_name, cf_content, cf_project],
                    outputs=[cf_status, file_tree_display, file_op_status]
                )
                mkdir_btn.click(
                    fn=do_create_folder,
                    inputs=[cf_folder_path],
                    outputs=[mkdir_status, file_tree_display, file_op_status]
                )
                del_btn.click(
                    fn=do_delete_file,
                    inputs=[del_path],
                    outputs=[del_status, file_tree_display, file_op_status]
                )
                rn_btn.click(
                    fn=do_rename_file,
                    inputs=[rn_old, rn_new],
                    outputs=[rn_status, file_tree_display, file_op_status]
                )
                search_btn.click(fn=do_search, inputs=[search_query], outputs=[search_results])
                zip_btn.click(fn=do_zip_project, inputs=[zip_path_input, zip_output_name], outputs=[zip_status])

            # ════════════════════════════════
            # TAB 3: CODE EDITOR
            # ════════════════════════════════
            with gr.Tab("📝 Editor"):
                gr.Markdown("### Code Editor")

                with gr.Row():
                    editor_path = gr.Textbox(
                        label="File Path",
                        placeholder="project/src/main.py",
                        scale=4
                    )
                    open_file_btn = gr.Button("📂 Open", scale=1)
                    save_file_btn = gr.Button("💾 Save", variant="primary", scale=1)

                editor_info = gr.Textbox(label="File Info", interactive=False, lines=1)

                editor_content = gr.Textbox(
                    label="Editor",
                    lines=30,
                    placeholder="Open a file or start typing...",
                    elem_classes=["code-editor"],
                    show_copy_button=True
                )

                editor_status = gr.Textbox(label="Status", lines=1, interactive=False)

                open_file_btn.click(
                    fn=do_open_file,
                    inputs=[editor_path],
                    outputs=[editor_info, editor_content]
                )
                save_file_btn.click(
                    fn=do_save_file,
                    inputs=[editor_path, editor_content],
                    outputs=[editor_status]
                )

            # ════════════════════════════════
            # TAB 4: TERMINAL
            # ════════════════════════════════
            with gr.Tab("💻 Terminal"):
                gr.Markdown("### Linux Terminal")

                terminal_output = gr.Textbox(
                    label="Terminal",
                    value="⚡ PM Masterpiece Terminal\n$ Ready. Type commands below.\n",
                    lines=20,
                    interactive=False,
                    elem_classes=["terminal-output"]
                )

                with gr.Row():
                    terminal_input = gr.Textbox(
                        label="Command",
                        placeholder="ls -la | python script.py | pip install numpy | git status",
                        scale=5,
                        lines=1
                    )
                    run_btn = gr.Button("▶ Run", variant="primary", scale=1)
                    clear_btn = gr.Button("🗑 Clear", scale=1)

                gr.Markdown("**Quick Commands:**")
                with gr.Row():
                    for cmd in ["ls -la", "pwd", "python --version", "pip list", "git status"]:
                        quick_btn = gr.Button(cmd, size="sm")
                        quick_btn.click(
                            fn=run_terminal_cmd,
                            inputs=[gr.Textbox(value=cmd, visible=False), terminal_output],
                            outputs=[terminal_output, terminal_input]
                        )

                with gr.Accordion("⚡ Python Runner", open=False):
                    py_script = gr.Textbox(label="Script Path", placeholder="project/main.py")
                    py_run_btn = gr.Button("▶ Run Python Script", variant="primary")
                    py_output = gr.Textbox(label="Output", lines=10, interactive=False,
                                          elem_classes=["terminal-output"])
                    py_run_btn.click(fn=run_python_script, inputs=[py_script], outputs=[py_output])

                with gr.Accordion("📦 Package Installer", open=False):
                    pkg_name = gr.Textbox(label="Package Name(s)", placeholder="numpy pandas matplotlib")
                    pkg_btn = gr.Button("📦 Install", variant="primary")
                    pkg_output = gr.Textbox(label="Output", lines=8, interactive=False,
                                           elem_classes=["terminal-output"])
                    pkg_btn.click(fn=install_package, inputs=[pkg_name], outputs=[pkg_output])

                # Terminal events
                run_btn.click(
                    fn=run_terminal_cmd,
                    inputs=[terminal_input, terminal_output],
                    outputs=[terminal_output, terminal_input]
                )
                terminal_input.submit(
                    fn=run_terminal_cmd,
                    inputs=[terminal_input, terminal_output],
                    outputs=[terminal_output, terminal_input]
                )
                clear_btn.click(fn=clear_terminal, outputs=[terminal_output])

            # ════════════════════════════════
            # TAB 5: GITHUB
            # ════════════════════════════════
            with gr.Tab("🐙 GitHub"):
                gr.Markdown("### GitHub Integration")

                with gr.Tabs():
                    with gr.Tab("🔑 Credentials"):
                        gr.Markdown("Set your GitHub credentials once per session.")
                        git_username = gr.Textbox(label="GitHub Username", placeholder="your-username")
                        git_email = gr.Textbox(label="GitHub Email", placeholder="you@email.com")
                        git_token = gr.Textbox(
                            label="Personal Access Token (PAT)",
                            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
                            type="password"
                        )
                        git_cred_btn = gr.Button("💾 Save Credentials", variant="primary")
                        git_cred_status = gr.Textbox(label="Status", lines=2, interactive=False)
                        git_cred_btn.click(
                            fn=save_git_config,
                            inputs=[git_username, git_email, git_token],
                            outputs=[git_cred_status]
                        )
                        gr.Markdown("""
> **How to get a GitHub Token:**
> 1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
> 2. Click "Generate new token (classic)"
> 3. Select scopes: `repo`, `workflow`
> 4. Copy and paste the token above
                        """)

                    with gr.Tab("📥 Clone"):
                        clone_url = gr.Textbox(label="Repository URL", placeholder="https://github.com/user/repo.git")
                        clone_name = gr.Textbox(label="Local Name (optional)", placeholder="my-repo")
                        clone_btn = gr.Button("📥 Clone Repository", variant="primary")
                        clone_status = gr.Textbox(label="Output", lines=4, interactive=False)
                        clone_btn.click(fn=do_git_clone, inputs=[clone_url, clone_name], outputs=[clone_status])

                    with gr.Tab("📊 Status"):
                        status_project = gr.Textbox(label="Project Path", placeholder="projects/my-repo")
                        status_btn = gr.Button("📊 Git Status", variant="primary")
                        git_init_btn = gr.Button("🔧 Git Init", variant="secondary")
                        git_status_out = gr.Textbox(label="Status Output", lines=12, interactive=False,
                                                    elem_classes=["terminal-output"])
                        status_btn.click(fn=do_git_status, inputs=[status_project], outputs=[git_status_out])
                        git_init_btn.click(fn=do_git_init, inputs=[status_project], outputs=[git_status_out])

                    with gr.Tab("⬆️ Push"):
                        push_project = gr.Textbox(label="Project Path", placeholder="projects/my-repo")
                        push_message = gr.Textbox(label="Commit Message", placeholder="feat: add new feature")
                        push_branch = gr.Textbox(label="Branch", value="main", placeholder="main")
                        push_btn = gr.Button("⬆️ Stage + Commit + Push", variant="primary")
                        gr.Markdown("> This will run: `git add -A` → `git commit` → `git push`")
                        push_status = gr.Textbox(label="Output", lines=6, interactive=False)
                        push_btn.click(
                            fn=do_git_add_commit_push,
                            inputs=[push_project, push_message, push_branch],
                            outputs=[push_status]
                        )

                    with gr.Tab("⬇️ Pull"):
                        pull_project = gr.Textbox(label="Project Path", placeholder="projects/my-repo")
                        pull_branch = gr.Textbox(label="Branch", value="main")
                        pull_btn = gr.Button("⬇️ Pull", variant="primary")
                        pull_status = gr.Textbox(label="Output", lines=4, interactive=False)
                        pull_btn.click(fn=do_git_pull, inputs=[pull_project, pull_branch], outputs=[pull_status])

                    with gr.Tab("📜 History"):
                        log_project = gr.Textbox(label="Project Path", placeholder="projects/my-repo")
                        log_btn = gr.Button("📜 Show Commit Log", variant="primary")
                        branch_btn = gr.Button("⎇ List Branches", variant="secondary")
                        log_output = gr.Textbox(label="Log", lines=16, interactive=False,
                                               elem_classes=["terminal-output"])
                        log_btn.click(fn=do_git_log, inputs=[log_project], outputs=[log_output])
                        branch_btn.click(fn=do_git_branches, inputs=[log_project], outputs=[log_output])

                    with gr.Tab("🔗 Remote"):
                        remote_project = gr.Textbox(label="Project Path", placeholder="projects/my-repo")
                        remote_url = gr.Textbox(label="Remote URL", placeholder="https://github.com/user/repo.git")
                        remote_name = gr.Textbox(label="Remote Name", value="origin")
                        remote_btn = gr.Button("🔗 Add Remote", variant="primary")
                        remote_status = gr.Textbox(label="Status", lines=3, interactive=False)
                        remote_btn.click(
                            fn=do_add_remote,
                            inputs=[remote_project, remote_url, remote_name],
                            outputs=[remote_status]
                        )

        # ── Status Bar ──
        gr.HTML(STATUS_HTML)

    return app
