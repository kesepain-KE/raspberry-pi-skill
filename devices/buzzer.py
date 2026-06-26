from __future__ import annotations

import time
from typing import Any, Dict

from .common import DeviceError, base_payload, level_name, load_gpio_backend, logical_to_level, setup_output


def run(device: Dict[str, Any], action: str, count: int = 3, interval: float = 0.2, duration: float = 1.0) -> Dict[str, Any]:
    if action not in {"on", "off", "beep"}:
        raise DeviceError("蜂鸣器不支持该动作", device=device["name"], action=action, supported=["on", "off", "beep"])

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
    elif action == "beep":
        for _ in range(count):
            gpio.output(bcm, gpio.HIGH if on_value else gpio.LOW)
            time.sleep(interval)
            gpio.output(bcm, gpio.HIGH if off_value else gpio.LOW)
            time.sleep(interval)
        payload.update({"state": "off", "count": count, "interval_sec": interval, "value": off_value, "level": level_name(off_value)})

    return payload
