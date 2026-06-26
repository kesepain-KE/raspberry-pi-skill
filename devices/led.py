from __future__ import annotations

import time
from typing import Any, Dict

from .common import DeviceError, base_payload, level_name, load_gpio_backend, logical_to_level, setup_output


def run(device: Dict[str, Any], action: str, count: int = 3, interval: float = 0.2, duration: float = 1.0) -> Dict[str, Any]:
    if action not in {"on", "off", "toggle", "blink"}:
        raise DeviceError("LED 不支持该动作", device=device["name"], action=action, supported=["on", "off", "toggle", "blink"])

    gpio = load_gpio_backend()
    bcm = int(device["bcm"])
    setup_output(gpio, bcm)

    payload = base_payload(device, action)

    if action == "on":
        value = logical_to_level(device, True)
        gpio.output(bcm, gpio.HIGH if value else gpio.LOW)
        payload.update({"state": "on", "value": value, "level": level_name(value)})
    elif action == "off":
        value = logical_to_level(device, False)
        gpio.output(bcm, gpio.HIGH if value else gpio.LOW)
        payload.update({"state": "off", "value": value, "level": level_name(value)})
    elif action == "toggle":
        current = int(gpio.input(bcm))
        value = 0 if current else 1
        gpio.output(bcm, gpio.HIGH if value else gpio.LOW)
        logical_on = bool(value) if device.get("active_high", True) else not bool(value)
        payload.update({"state": "on" if logical_on else "off", "value": value, "level": level_name(value), "previous_value": current})
    elif action == "blink":
        on_value = logical_to_level(device, True)
        off_value = logical_to_level(device, False)
        for _ in range(count):
            gpio.output(bcm, gpio.HIGH if on_value else gpio.LOW)
            time.sleep(interval)
            gpio.output(bcm, gpio.HIGH if off_value else gpio.LOW)
            time.sleep(interval)
        payload.update({"state": "off", "count": count, "interval_sec": interval, "value": off_value, "level": level_name(off_value)})

    return payload
