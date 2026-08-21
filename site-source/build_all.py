"""Regenerate every page in ../public from these templates.
Run with: python3 build_all.py   (from inside site-source/)
Requires Python 3 with no third-party packages."""
import subprocess, sys, pathlib

HERE = pathlib.Path(__file__).parent
SCRIPTS = [
    "build_home.py",
    "build_services.py",
    "build_about.py",
    "build_contact.py",
    "build_authorization.py",
    "build_thankyou.py",
]

for script in SCRIPTS:
    subprocess.run([sys.executable, str(HERE / script)], check=True, cwd=HERE)

print("\nAll pages regenerated in ../public/")
