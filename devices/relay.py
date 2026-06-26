from __future__ import annotations

import time
from typing import Any, Dict

from .common import DeviceError, base_payload, level_name, load_gpio_backend, logical_to_level, setup_output


def run(device: Dict[str, Any], action: str, count: int = 1, interval: float = 0.2, duration: float = 1.0) -> Dict[str, Any]:
    if action not in {"on", "off", "pulse"}:
        raise DeviceError("继电器不支持该动作", device=device["name"], action=action, supported=["on", "off", "pulse"])

    gpio = load_gpio_backend()
    bcm = int(device["bcm"])
    setup_output(gpio, bcm)

    payload = base_payload(device, action)
    on_value = logical_to_level(device, True)
    off_value = logical_to_level(device, False)

    if action == "on":
        gpio.output(bcm, gpio.HIGH if on_value else gpio.LOW)
        payload.update({"state": "on", "value": on_value, "level": level_name(on_value)})
    elif action == "off":
        gpio.output(bcm, gpio.HIGH if off_value else gpio.LOW)
        payload.update({"state": "off", "value": off_value, "level": level_name(off_value)})
    elif action == "pulse":
        gpio.output(bcm, gpio.HIGH if on_value else gpio.LOW)
        time.sleep(duration)
        gpio.output(bcm, gpio.HIGH if off_value else gpio.LOW)
        payload.update({"state": "off", "duration_sec": duration, "value": off_value, "level": level_name(off_value)})

    return payload
