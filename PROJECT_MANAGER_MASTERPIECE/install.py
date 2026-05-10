"""
╔══════════════════════════════════════════════════════════════╗
║       PROJECT_MANAGER_MASTERPIECE - AUTO INSTALLER           ║
║       Sets up environment, installs deps, runs the app       ║
╚══════════════════════════════════════════════════════════════╝

Run this first:
    python install.py
"""

import subprocess
import sys
import os
from pathlib import Path


def run(cmd: list, desc: str) -> bool:
    print(f"  ⏳ {desc}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ {desc} — Done")
        return True
    else:
        print(f"  ❌ {desc} — Failed")
        if result.stderr:
            print(f"     {result.stderr[:200]}")
        return False


def main():
    print("\n" + "═" * 60)
    print("  ⚡  PM MASTERPIECE — AUTO INSTALLER")
    print("═" * 60)
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Path:   {Path.cwd()}")
    print("═" * 60 + "\n")

    # Upgrade pip
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-q"], "Upgrading pip")

    # Install requirements
    reqs = Path("requirements.txt")
    if reqs.exists():
        lines = [
            l.strip() for l in reqs.read_text().splitlines()
            if l.strip() and not l.startswith("#") and not l.startswith("//")
        ]
        for pkg in lines:
            run([sys.executable, "-m", "pip", "install", pkg, "-q"], f"Installing {pkg}")
    else:
        # Fallback: install essentials
        for pkg in ["gradio", "rich", "gitpython", "typer"]:
            run([sys.executable, "-m", "pip", "install", pkg, "-q"], f"Installing {pkg}")

    # Create directory structure
    print("\n  📁 Creating directories...")
    dirs = ["projects", "configs", "logs", "temp", "assets"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"     ✅ {d}/")

    # Create sample project
    sample = Path("projects") / "sample-project"
    if not sample.exists():
        sample.mkdir(parents=True)
        (sample / "main.py").write_text(
            '"""Sample Project"""\n\ndef main():\n    print("Hello from PM Masterpiece!")\n\nif __name__ == "__main__":\n    main()\n'
        )
        (sample / "README.md").write_text("# Sample Project\n\nThis is a sample project.\n")
        print("  ✅ Created sample-project/")

    print("\n" + "═" * 60)
    print("  ✅  Installation Complete!")
    print("═" * 60)
    print("\n  🚀 To start:")
    print("     GUI:  python main.py --gui")
    print("     CLI:  python main.py --cli")
    print("     Auto: python main.py\n")
    print("  💡 For Google Colab:")
    print("     python main.py --gui --share\n")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
