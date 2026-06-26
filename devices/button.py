from __future__ import annotations

from typing import Any, Dict

from .common import DeviceError, base_payload, level_name, load_gpio_backend, setup_input


def run(device: Dict[str, Any], action: str, count: int = 1, interval: float = 0.2, duration: float = 1.0) -> Dict[str, Any]:
    if action != "read":
        raise DeviceError("按钮第一版仅支持 read", device=device["name"], action=action, supported=["read"])

    gpio = load_gpio_backend()
    bcm = int(device["bcm"])
    pull = str(device.get("pull", "down"))
    setup_input(gpio, bcm, pull)
    value = int(gpio.input(bcm))

    # pull-up buttons are usually pressed when the GPIO reads LOW.
    if pull == "up":
        pressed = value == 0
    else:
        pressed = value == 1

    payload = base_payload(device, action)
    payload.update({"value": value, "level": level_name(value), "pressed": pressed, "pull": pull})
    return payload
