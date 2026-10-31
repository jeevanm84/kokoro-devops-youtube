"""Episode hook: run every on-screen Git behaviour for real (pipeline 'validate' stage)."""
import pathlib, subprocess, sys
sys.exit(subprocess.run([sys.executable, str(pathlib.Path(__file__).with_name("verify_git_undo.py"))]).returncode)
