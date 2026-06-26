#!/usr/bin/env python3
"""
Device semantic control CLI for raspberry-pi-skill.

This layer lets an Agent control named devices instead of raw BCM pins.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from devices.common import DEFAULT_CONFIG, DeviceError, emit_json, fail, load_device_registry

DEVICE_MODULES = {
    "led": "devices.led",
    "buzzer": "devices.buzzer",
    "relay": "devices.relay",
    "button": "devices.button",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="树莓派设备语义控制脚本")
    parser.add_argument("--list", action="store_true", help="列出已注册设备")
    parser.add_argument("--device", help="设备注册名，如 bedroom_led / buzzer / relay_fan")
    parser.add_argument("--action", help="语义动作，如 on / off / blink / beep / pulse / read")
    parser.add_argument("--count", type=int, default=3, help="重复次数，默认 3")
    parser.add_argument("--interval", type=float, default=0.2, help="闪烁/蜂鸣间隔秒数，默认 0.2")
    parser.add_argument("--duration", type=float, default=1.0, help="pulse 持续秒数，默认 1.0")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="设备注册表路径，默认 config/pins.json")
    parser.add_argument("--json", action="store_true", help="输出 JSON，推荐 Agent 使用")
    return parser


def run_device(device: Dict[str, Any], action: str, count: int, interval: float, duration: float) -> Dict[str, Any]:
    module_path = DEVICE_MODULES.get(device["type"])
    if not module_path:
        raise DeviceError("设备类型没有可用模块", device=device["name"], type=device["type"])
    module = importlib.import_module(module_path)
    return module.run(device, action, count=count, interval=interval, duration=duration)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        registry = load_device_registry(args.config)

        if args.list:
            payload = {
                "ok": True,
                "action": "list",
                "config": str(args.config),
                "devices": registry.list_devices(),
            }
            if args.json:
                emit_json(payload)
            else:
                for device in payload["devices"]:
                    print(
                        f"{device['name']}: {device['type']} BCM{device['bcm']} "
                        f"physical={device.get('physical')} {device.get('description', '')}"
                    )
            return

        if not args.device:
            fail("缺少 --device。使用 --list 查看可用设备。", args.json, hint="python3 scripts/device_control.py --list --json")
        if not args.action:
            fail("缺少 --action。", args.json, device=args.device)

        device = registry.get(args.device)
        payload = run_device(device, args.action, args.count, args.interval, args.duration)
        if args.json:
            emit_json(payload)
        else:
            print(f"OK: {payload['device']} {payload['action']}")
    except DeviceError as exc:
        fail(exc.message, args.json, **exc.extra)
    except Exception as exc:
        fail(f"未预期错误: {exc}", args.json)


if __name__ == "__main__":
    main()
