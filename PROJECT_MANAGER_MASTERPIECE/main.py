"""
╔══════════════════════════════════════════════════════════════╗
║        PROJECT_MANAGER_MASTERPIECE - MAIN ENTRY POINT       ║
║        Auto-detects environment and launches correct mode    ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python main.py              → Auto-detect best mode
    python main.py --gui        → Launch Gradio GUI
    python main.py --cli        → Launch CLI shell
    python main.py --port 7860  → GUI on custom port
    python main.py --share      → GUI with public share link
"""

import sys
import os
import argparse
from pathlib import Path


# ─────────────────────────────────────────────
# ENVIRONMENT DETECTION
# ─────────────────────────────────────────────
def detect_environment() -> str:
    """Detect where we're running and suggest mode."""
    # Google Colab
    try:
        import google.colab
        return "colab"
    except ImportError:
        pass

    # Jupyter Notebook
    try:
        shell = get_ipython().__class__.__name__
        if "ZMQInteractiveShell" in shell:
            return "jupyter"
    except NameError:
        pass

    # Check if running interactively
    if sys.stdin.isatty():
        return "terminal"

    return "terminal"


def check_dependencies():
    """Check for required packages and warn about missing ones."""
    required = {
        "gradio": "pip install gradio",
        "rich": "pip install rich",
    }
    optional = {
        "git": "pip install gitpython",
        "typer": "pip install typer",
    }

    missing_required = []
    missing_optional = []

    for pkg, install in required.items():
        try:
            __import__(pkg)
        except ImportError:
            missing_required.append((pkg, install))

    for pkg, install in optional.items():
        try:
            __import__(pkg)
        except ImportError:
            missing_optional.append((pkg, install))

    return missing_required, missing_optional


def print_startup_info(mode: str, env: str):
    """Print startup information."""
    print("\n" + "═" * 62)
    print("⚡  PROJECT MANAGER MASTERPIECE  v1.0.0")
    print("═" * 62)
    print(f"  Mode:        {mode.upper()}")
    print(f"  Environment: {env.upper()}")
    print(f"  Python:      {sys.version.split()[0]}")
    print(f"  Platform:    {sys.platform}")
    print(f"  Projects:    {Path.cwd() / 'projects'}")
    print("═" * 62 + "\n")


# ─────────────────────────────────────────────
# LAUNCH MODES
# ─────────────────────────────────────────────
def launch_gui(port: int = 7860, share: bool = False, base_dir: str = None):
    """Launch the Gradio GUI interface."""
    try:
        from gui.app import build_gui
        print("🚀 Starting GUI mode...")
        print(f"   → Opening on http://localhost:{port}")
        if share:
            print("   → Public share link will be generated...")
        print("   → Press Ctrl+C to stop\n")

        app = build_gui(base_dir)
        app.launch(
            server_port=port,
            share=share,
            server_name="0.0.0.0",  # Allow external access
            show_error=True,
            favicon_path=None,
            quiet=False
        )
    except ImportError as e:
        print(f"❌ Gradio not installed. Run: pip install gradio")
        print(f"   Error: {e}")
        print("\n💡 Falling back to CLI mode...\n")
        launch_cli(base_dir)
    except Exception as e:
        print(f"❌ GUI failed to start: {e}")
        sys.exit(1)


def launch_cli(base_dir: str = None):
    """Launch the interactive CLI shell."""
    try:
        from cli.shell import PMShell
        print("🚀 Starting CLI mode...")
        shell = PMShell(base_dir)
        shell.run()
    except ImportError as e:
        print(f"❌ CLI module error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ CLI failed to start: {e}")
        sys.exit(1)


def launch_colab(share: bool = True, port: int = 7860, base_dir: str = None):
    """Launch optimized for Google Colab (with share link)."""
    print("📡 Detected Google Colab — enabling public share link...")
    launch_gui(port=port, share=True, base_dir=base_dir)


# ─────────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        prog="PM Masterpiece",
        description="⚡ PROJECT_MANAGER_MASTERPIECE — Python Cloud Dev Environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    Auto-detect mode
  python main.py --gui              Launch GUI on port 7860
  python main.py --gui --port 8080  GUI on port 8080
  python main.py --gui --share      GUI with public share link
  python main.py --cli              CLI interactive shell
  python main.py --dir /my/projects Use custom projects directory
        """
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--gui", action="store_true", help="Launch Gradio GUI")
    mode_group.add_argument("--cli", action="store_true", help="Launch CLI shell")

    parser.add_argument("--port", type=int, default=7860, help="Port for GUI (default: 7860)")
    parser.add_argument("--share", action="store_true", help="Enable public share link (for Colab)")
    parser.add_argument("--dir", type=str, default=None, help="Custom projects directory")
    parser.add_argument("--version", action="version", version="PM Masterpiece v1.0.0")

    return parser.parse_args()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    args = parse_args()
    env = detect_environment()

    # Check dependencies
    missing_req, missing_opt = check_dependencies()

    if missing_req:
        print("⚠️  Missing required packages:")
        for pkg, cmd in missing_req:
            print(f"   {pkg}: run '{cmd}'")
        print("\nRun: pip install -r requirements.txt\n")

    if missing_opt:
        print("💡 Optional packages not installed (some features may be limited):")
        for pkg, cmd in missing_opt:
            print(f"   {pkg}: {cmd}")
        print()

    # Determine mode
    if args.cli:
        mode = "cli"
    elif args.gui:
        mode = "gui"
    elif env == "colab":
        mode = "colab"
    else:
        # Default: GUI if gradio available, else CLI
        try:
            import gradio
            mode = "gui"
        except ImportError:
            mode = "cli"

    print_startup_info(mode, env)

    # Launch
    base_dir = args.dir

    if mode == "gui":
        launch_gui(port=args.port, share=args.share, base_dir=base_dir)
    elif mode == "cli":
        launch_cli(base_dir=base_dir)
    elif mode == "colab":
        launch_colab(port=args.port, base_dir=base_dir)
    else:
        launch_cli(base_dir=base_dir)


if __name__ == "__main__":
    main()
