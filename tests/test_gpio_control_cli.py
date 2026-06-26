import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GPIO_SCRIPT = ROOT / "scripts" / "gpio_control.py"
PI_INFO_SCRIPT = ROOT / "scripts" / "pi_info.py"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_json_output(result):
    assert result.returncode == 0, result.stderr or result.stdout
    return json.loads(result.stdout)


def test_gpio_list_json():
    data = parse_json_output(run_cli(GPIO_SCRIPT, "--list", "--json"))
    assert data["ok"] is True
    assert data["action"] == "list"
    assert isinstance(data["pins"], list)
    assert any(pin.get("bcm") == 17 for pin in data["pins"])


def test_gpio_status_json():
    data = parse_json_output(run_cli(GPIO_SCRIPT, "--status", "--json"))
    assert data["ok"] is True
    assert data["action"] == "status"
    assert "pins" in data


def test_gpio_missing_action_json_error():
    result = run_cli(GPIO_SCRIPT, "--pin", "17", "--json")
    assert result.returncode != 0
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert "error" in data


def test_gpio_read_without_backend_returns_json_error():
    result = run_cli(GPIO_SCRIPT, "--pin", "17", "--read", "--json")
    if result.returncode == 0:
        data = json.loads(result.stdout)
        assert data["ok"] is True
    else:
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert "GPIO" in data["error"] or "RPi.GPIO" in data["error"]


def test_py_compile_scripts():
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(GPIO_SCRIPT), str(PI_INFO_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
