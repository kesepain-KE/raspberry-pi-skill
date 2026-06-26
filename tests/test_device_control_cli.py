import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEVICE_SCRIPT = ROOT / "scripts" / "device_control.py"
EXAMPLE_CONFIG = ROOT / "config" / "pins.example.json"


def run_cli(*args, fake_gpio=False):
    env = os.environ.copy()
    if fake_gpio:
        env["RASPBERRY_PI_SKILL_FAKE_GPIO"] = "1"
    return subprocess.run(
        [sys.executable, *map(str, args)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def parse_json(result):
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def test_device_list_json_without_gpio():
    result = run_cli(DEVICE_SCRIPT, "--config", EXAMPLE_CONFIG, "--list", "--json")
    assert result.returncode == 0, result.stderr
    data = parse_json(result)
    assert data["ok"] is True
    assert data["action"] == "list"
    names = {device["name"] for device in data["devices"]}
    assert {"bedroom_led", "buzzer", "relay_fan", "button_1"}.issubset(names)


def test_missing_device_json_error():
    result = run_cli(DEVICE_SCRIPT, "--config", EXAMPLE_CONFIG, "--action", "on", "--json")
    assert result.returncode != 0
    data = parse_json(result)
    assert data["ok"] is False
    assert "--device" in data["error"]


def test_missing_action_json_error():
    result = run_cli(DEVICE_SCRIPT, "--config", EXAMPLE_CONFIG, "--device", "bedroom_led", "--json")
    assert result.returncode != 0
    data = parse_json(result)
    assert data["ok"] is False
    assert "--action" in data["error"]


def test_unknown_device_json_error():
    result = run_cli(DEVICE_SCRIPT, "--config", EXAMPLE_CONFIG, "--device", "ghost", "--action", "on", "--json")
    assert result.returncode != 0
    data = parse_json(result)
    assert data["ok"] is False
    assert data["device"] == "ghost"
    assert "available" in data


def test_unknown_action_json_error_with_fake_gpio():
    result = run_cli(
        DEVICE_SCRIPT,
        "--config", EXAMPLE_CONFIG,
        "--device", "bedroom_led",
        "--action", "sing",
        "--json",
        fake_gpio=True,
    )
    assert result.returncode != 0
    data = parse_json(result)
    assert data["ok"] is False
    assert data["action"] == "sing"


def test_no_gpio_backend_returns_json_error():
    result = run_cli(DEVICE_SCRIPT, "--config", EXAMPLE_CONFIG, "--device", "bedroom_led", "--action", "on", "--json")
    if result.returncode != 0:
        data = parse_json(result)
        assert data["ok"] is False
        assert "GPIO" in data["error"] or "RPi.GPIO" in data["error"]
    else:
        data = parse_json(result)
        assert data["ok"] is True


def test_led_on_with_fake_gpio():
    result = run_cli(
        DEVICE_SCRIPT,
        "--config", EXAMPLE_CONFIG,
        "--device", "bedroom_led",
        "--action", "on",
        "--json",
        fake_gpio=True,
    )
    assert result.returncode == 0, result.stderr
    data = parse_json(result)
    assert data["ok"] is True
    assert data["device"] == "bedroom_led"
    assert data["state"] == "on"
    assert data["level"] == "HIGH"


def test_active_low_relay_mapping_with_fake_gpio():
    result = run_cli(
        DEVICE_SCRIPT,
        "--config", EXAMPLE_CONFIG,
        "--device", "relay_fan",
        "--action", "on",
        "--json",
        fake_gpio=True,
    )
    assert result.returncode == 0, result.stderr
    data = parse_json(result)
    assert data["ok"] is True
    assert data["type"] == "relay"
    assert data["state"] == "on"
    assert data["active_high"] is False
    assert data["value"] == 0
    assert data["level"] == "LOW"


def test_button_read_with_fake_gpio():
    result = run_cli(
        DEVICE_SCRIPT,
        "--config", EXAMPLE_CONFIG,
        "--device", "button_1",
        "--action", "read",
        "--json",
        fake_gpio=True,
    )
    assert result.returncode == 0, result.stderr
    data = parse_json(result)
    assert data["ok"] is True
    assert data["type"] == "button"
    assert data["pull"] == "up"
    assert data["pressed"] is False
