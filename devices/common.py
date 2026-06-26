from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT_DIR / "config" / "pins.json"

GPIO = None

BCM_TO_PHYSICAL = {
    0: 27, 1: 28, 2: 3, 3: 5, 4: 7,
    5: 29, 6: 31, 7: 26, 8: 24, 9: 21,
    10: 19, 11: 23, 12: 32, 13: 33, 14: 8,
    15: 10, 16: 36, 17: 11, 18: 12, 19: 35,
    20: 38, 21: 40, 22: 15, 23: 16, 24: 18,
    25: 22, 26: 37, 27: 13,
}

SUPPORTED_DEVICE_TYPES = {"led", "buzzer", "relay", "button"}


class FakeGPIO:
    """Small test backend enabled by RASPBERRY_PI_SKILL_FAKE_GPIO=1."""

    BCM = "BCM"
    OUT = "OUT"
    IN = "IN"
    HIGH = 1
    LOW = 0
    PUD_UP = "PUD_UP"
    PUD_DOWN = "PUD_DOWN"

    def __init__(self) -> None:
        self.values: Dict[int, int] = {}

    def setmode(self, mode: Any) -> None:
        self.mode = mode

    def setup(self, bcm: int, mode: Any, pull_up_down: Optional[Any] = None) -> None:
        if mode == self.IN:
            self.values.setdefault(int(bcm), 1 if pull_up_down == self.PUD_UP else 0)
        else:
            self.values.setdefault(int(bcm), 0)

    def output(self, bcm: int, value: int) -> None:
        self.values[int(bcm)] = int(value)

    def input(self, bcm: int) -> int:
        return int(self.values.get(int(bcm), 0))


class DeviceError(Exception):
    """Expected device-layer error that can be returned as JSON."""

    def __init__(self, message: str, **extra: Any) -> None:
        super().__init__(message)
        self.message = message
        self.extra = extra


def emit_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def fail(message: str, as_json: bool, code: int = 1, **extra: Any) -> None:
    if as_json:
        payload = {"ok": False, "error": message}
        payload.update(extra)
        emit_json(payload)
    else:
        print(f"错误: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_gpio_backend():
    global GPIO
    if GPIO is not None:
        return GPIO
    if os.environ.get("RASPBERRY_PI_SKILL_FAKE_GPIO") == "1":
        GPIO = FakeGPIO()
        return GPIO
    try:
        import RPi.GPIO as gpio  # type: ignore
    except Exception as exc:
        raise DeviceError(
            "GPIO 后端不可用。Pi 3/4 请安装 RPi.GPIO；Pi 5 建议安装 rpi-lgpio 或 gpiozero/lgpio。",
            raw_error=str(exc),
        ) from exc
    GPIO = gpio
    return GPIO


def normalize_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "high"}
    return default


def normalize_device(name: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    device = dict(raw)
    device["name"] = name
    device_type = str(device.get("type", "")).lower()
    if device_type not in SUPPORTED_DEVICE_TYPES:
        raise DeviceError(
            f"设备 {name} 的 type 不受支持: {device_type or 'missing'}",
            device=name,
            supported=sorted(SUPPORTED_DEVICE_TYPES),
        )
    if "bcm" not in device:
        raise DeviceError(f"设备 {name} 缺少 bcm 字段", device=name)
    try:
        bcm = int(device["bcm"])
    except (TypeError, ValueError) as exc:
        raise DeviceError(f"设备 {name} 的 bcm 必须是整数", device=name, bcm=device.get("bcm")) from exc
    if bcm not in BCM_TO_PHYSICAL:
        raise DeviceError(f"设备 {name} 的 BCM{bcm} 不在 40-pin 对照表中", device=name, bcm=bcm)

    device["type"] = device_type
    device["bcm"] = bcm
    device.setdefault("physical", BCM_TO_PHYSICAL.get(bcm))
    device.setdefault("active_high", True)
    device["active_high"] = normalize_bool(device.get("active_high"), True)
    device.setdefault("description", "")
    if device_type == "button":
        pull = str(device.get("pull", "down")).lower()
        if pull not in {"up", "down", "none"}:
            raise DeviceError(f"设备 {name} 的 pull 必须是 up/down/none", device=name, pull=pull)
        device["pull"] = pull
    return device


def pin_entry_to_device(key: str, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    device_type = str(raw.get("device_type") or raw.get("kind") or raw.get("device", "")).lower()
    if device_type not in SUPPORTED_DEVICE_TYPES:
        return None
    name = str(raw.get("name") or raw.get("id") or raw.get("device") or f"{device_type}_{key}")
    data = dict(raw)
    data["type"] = device_type
    data.setdefault("description", raw.get("notes", ""))
    return normalize_device(name, data)


class DeviceRegistry:
    def __init__(self, devices: Dict[str, Dict[str, Any]], config_path: Path) -> None:
        self.devices = devices
        self.config_path = config_path

    def list_devices(self) -> List[Dict[str, Any]]:
        return [self.devices[name] for name in sorted(self.devices)]

    def get(self, name: str) -> Dict[str, Any]:
        if name not in self.devices:
            raise DeviceError(
                f"未知设备: {name}",
                device=name,
                available=sorted(self.devices.keys()),
            )
        return self.devices[name]


def load_device_registry(config_path: Path = DEFAULT_CONFIG) -> DeviceRegistry:
    if not config_path.exists():
        return DeviceRegistry({}, config_path)

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    devices: Dict[str, Dict[str, Any]] = {}
    raw_devices = data.get("devices", {})
    if raw_devices:
        if not isinstance(raw_devices, dict):
            raise DeviceError("config/pins.json 中的 devices 必须是对象", config=str(config_path))
        for name, raw in raw_devices.items():
            if not isinstance(raw, dict):
                continue
            devices[str(name)] = normalize_device(str(name), raw)

    raw_pins = data.get("pins", {})
    if isinstance(raw_pins, dict):
        for key, raw in raw_pins.items():
            if not isinstance(raw, dict):
                continue
            derived = pin_entry_to_device(str(key), raw)
            if derived:
                devices.setdefault(derived["name"], derived)

    return DeviceRegistry(devices, config_path)


def setup_output(gpio: Any, bcm: int) -> None:
    gpio.setmode(gpio.BCM)
    gpio.setup(bcm, gpio.OUT)


def setup_input(gpio: Any, bcm: int, pull: str) -> None:
    gpio.setmode(gpio.BCM)
    if pull == "up":
        gpio.setup(bcm, gpio.IN, pull_up_down=gpio.PUD_UP)
    elif pull == "down":
        gpio.setup(bcm, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    else:
        gpio.setup(bcm, gpio.IN)


def logical_to_level(device: Dict[str, Any], enabled: bool) -> int:
    active_high = bool(device.get("active_high", True))
    high = enabled if active_high else not enabled
    return 1 if high else 0


def level_name(value: int) -> str:
    return "HIGH" if value else "LOW"


def base_payload(device: Dict[str, Any], action: str) -> Dict[str, Any]:
    return {
        "ok": True,
        "device": device["name"],
        "type": device["type"],
        "action": action,
        "bcm": device["bcm"],
        "physical": device.get("physical"),
        "active_high": device.get("active_high", True),
        "description": device.get("description", ""),
    }
