"""
╔══════════════════════════════════════════════════════════════╗
║       PROJECT_MANAGER_MASTERPIECE - LAUNCHER                 ║
║       Smart launcher that detects Colab/Local/Terminal       ║
╚══════════════════════════════════════════════════════════════╝

This is the SIMPLEST way to start the app.
Just run:  python launcher.py
"""

import sys
import os


def is_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False


def is_jupyter():
    try:
        shell = get_ipython().__class__.__name__
        return "ZMQInteractiveShell" in shell
    except NameError:
        return False


def launch():
    print("⚡ PM MASTERPIECE LAUNCHER")
    print("─" * 40)

    if is_colab():
        print("🌐 Google Colab detected → GUI + Share Link")
        os.system("python main.py --gui --share")

    elif is_jupyter():
        print("📓 Jupyter detected → GUI mode")
        os.system(f"python main.py --gui")

    else:
        print("💻 Local/Terminal detected → GUI mode")
        print("   Use --cli flag for CLI mode")
        os.system("python main.py --gui")


if __name__ == "__main__":
    launch()
