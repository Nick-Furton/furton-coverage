"""Make scripts/ importable and expose the fixtures dir to tests."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

FIXTURES = Path(__file__).resolve().parent / "fixtures"
