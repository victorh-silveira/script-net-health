import os
import sys
from pathlib import Path


os.environ.setdefault("SNH_DISABLE_DOTENV", "1")

_OPERATIONS = Path(__file__).resolve().parents[1] / "scripts" / "operations"
if str(_OPERATIONS) not in sys.path:
    sys.path.insert(0, str(_OPERATIONS))
