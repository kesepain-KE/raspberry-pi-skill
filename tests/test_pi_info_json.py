import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PI_INFO_SCRIPT = ROOT / "scripts" / "pi_info.py"


def test_pi_info_json_shape():
    result = subprocess.run(
        [sys.executable, str(PI_INFO_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    for key in ["timestamp", "system", "cpu", "memory", "disk", "network", "gpio"]:
        assert key in data
    assert "hostname" in data["system"]
    assert "library" in data["gpio"]
