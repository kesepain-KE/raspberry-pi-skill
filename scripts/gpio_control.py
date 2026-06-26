#!/usr/bin/env python3
"""
树莓派 GPIO 控制脚本（Agent 友好版）

特性:
  - 支持人类可读输出和 --json 结构化输出
  - 引脚占用从 config/pins.json 读取，不再写死在源码里
  - GPIO 后端懒加载，--list/--status 不依赖真实树莓派环境
  - 默认使用 RPi.GPIO 兼容 API：Pi 3/4 用 RPi.GPIO，Pi 5 建议用 rpi-lgpio
"""

from __future__ import annotations

import argparse
import json
import sys
import time
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

PIN_ROWS = [
    {"physical": 1, "bcm": None, "function": "3.3V", "status": "power", "note": ""},
    {"physical": 2, "bcm": None, "function": "5V", "status": "power", "note": ""},
    {"physical": 3, "bcm": 2, "function": "I2C SDA", "status": "free", "note": "I2C 默认未启用"},
    {"physical": 4, "bcm": None, "function": "5V", "status": "power", "note": ""},
    {"physical": 5, "bcm": 3, "function": "I2C SCL", "status": "free", "note": "I2C 默认未启用"},
    {"physical": 6, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 7, "bcm": 4, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 8, "bcm": 14, "function": "UART TX", "status": "free", "note": "UART 默认未启用"},
    {"physical": 9, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 10, "bcm": 15, "function": "UART RX", "status": "free", "note": "UART 默认未启用"},
    {"physical": 11, "bcm": 17, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 12, "bcm": 18, "function": "PWM0", "status": "free", "note": ""},
    {"physical": 13, "bcm": 27, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 14, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 15, "bcm": 22, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 16, "bcm": 23, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 17, "bcm": None, "function": "3.3V", "status": "power", "note": ""},
    {"physical": 18, "bcm": 24, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 19, "bcm": 10, "function": "SPI MOSI", "status": "free", "note": "SPI 默认未启用"},
    {"physical": 20, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 21, "bcm": 9, "function": "SPI MISO", "status": "free", "note": "SPI 默认未启用"},
    {"physical": 22, "bcm": 25, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 23, "bcm": 11, "function": "SPI SCLK", "status": "free", "note": "SPI 默认未启用"},
    {"physical": 24, "bcm": 8, "function": "SPI CE0", "status": "free", "note": "SPI 默认未启用"},
    {"physical": 25, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 26, "bcm": 7, "function": "SPI CE1", "status": "free", "note": "SPI 默认未启用"},
    {"physical": 27, "bcm": 0, "function": "ID EEPROM", "status": "reserved", "note": "系统保留"},
    {"physical": 28, "bcm": 1, "function": "ID EEPROM", "status": "reserved", "note": "系统保留"},
    {"physical": 29, "bcm": 5, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 30, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 31, "bcm": 6, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 32, "bcm": 12, "function": "PWM0", "status": "free", "note": ""},
    {"physical": 33, "bcm": 13, "function": "PWM1", "status": "free", "note": ""},
    {"physical": 34, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 35, "bcm": 19, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 36, "bcm": 16, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 37, "bcm": 26, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 38, "bcm": 20, "function": "GPIO", "status": "free", "note": ""},
    {"physical": 39, "bcm": None, "function": "GND", "status": "ground", "note": ""},
    {"physical": 40, "bcm": 21, "function": "GPIO", "status": "free", "note": ""},
]


def load_gpio_backend():
    global GPIO
    if GPIO is not None:
        return GPIO
    try:
        import RPi.GPIO as gpio  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "GPIO 后端不可用。Pi 3/4 请安装 RPi.GPIO；Pi 5 建议安装 rpi-lgpio 或使用 gpiozero/lgpio 后端。"
            f"原始错误: {exc}"
        ) from exc
    GPIO = gpio
    return GPIO


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


def normalize_entry(key: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    entry = dict(raw)
    bcm = entry.get("bcm")
    physical = entry.get("physical")

    if bcm is None and key.isdigit() and str(entry.get("type", "")).upper() == "BCM":
        bcm = int(key)
        entry["bcm"] = bcm

    if bcm is not None:
        entry["bcm"] = int(bcm)
        entry.setdefault("physical", BCM_TO_PHYSICAL.get(int(bcm)))
    elif physical is not None:
        entry["physical"] = int(physical)
    elif key.isdigit():
        entry["physical"] = int(key)

    entry.setdefault("type", "BCM" if entry.get("bcm") is not None else "POWER")
    entry.setdefault("device", "unknown")
    entry.setdefault("mode", "unknown")
    entry.setdefault("owner", "manual")
    entry.setdefault("notes", "")
    return entry


def load_registry(config_path: Path) -> List[Dict[str, Any]]:
    if not config_path.exists():
        return []

    with config_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    pins = data.get("pins", data)
    if not isinstance(pins, dict):
        raise ValueError("pins.json 中的 pins 必须是对象")

    entries: List[Dict[str, Any]] = []
    for key, raw in pins.items():
        if not isinstance(raw, dict):
            continue
        entries.append(normalize_entry(str(key), raw))
    return entries


def find_conflict(entries: List[Dict[str, Any]], bcm: int) -> Optional[Dict[str, Any]]:
    for entry in entries:
        if entry.get("bcm") == bcm:
            return entry
    return None


def conflict_warning(entry: Optional[Dict[str, Any]], bcm: int) -> Optional[str]:
    if not entry:
        return None
    phys = BCM_TO_PHYSICAL.get(bcm, "?")
    return f"BCM{bcm}（物理引脚{phys}）已登记为 {entry.get('device', 'unknown')} 使用"


def build_pin_rows(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = [dict(row) for row in PIN_ROWS]
    for entry in entries:
        for row in rows:
            bcm_match = entry.get("bcm") is not None and row.get("bcm") == entry.get("bcm")
            phy_match = entry.get("physical") is not None and row.get("physical") == entry.get("physical")
            if bcm_match or phy_match:
                row["status"] = "occupied"
                row["device"] = entry.get("device", "unknown")
                row["mode"] = entry.get("mode", "unknown")
                row["owner"] = entry.get("owner", "manual")
                row["note"] = entry.get("notes") or entry.get("device", "unknown")
                break
    return rows


def list_pins(entries: List[Dict[str, Any]], as_json: bool, config_path: Path) -> None:
    rows = build_pin_rows(entries)
    if as_json:
        emit_json({"ok": True, "action": "list", "config": str(config_path), "pins": rows})
        return

    icons = {
        "free": "○",
        "occupied": "●",
        "power": "⚡",
        "ground": "⊖",
        "reserved": "◆",
    }
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║           GPIO 引脚对照表                           ║")
    print("╠════╦════════╦════════╦═══════╦══════════════════════╣")
    print("║物理║  BCM   ║  功能  ║ 状态  ║  备注                ║")
    print("╠════╬════════╬════════╬═══════╬══════════════════════╣")
    for row in rows:
        phy = row["physical"]
        bcm = "--" if row["bcm"] is None else str(row["bcm"])
        func = row["function"]
        icon = icons.get(row["status"], "?")
        note = row.get("note", "")
        print(f"║ {phy:>2} ║ {bcm:>4} ║ {func:<7}║  {icon}  ║ {note:<22} ║")
    print("╚════╩════════╩════════╩═══════╩══════════════════════╝")
    print("  ○=空闲  ●=已登记占用  ⚡=电源  ⊖=GND  ◆=系统保留")
    print(f"  占用表: {config_path}")
    print()


def show_status(entries: List[Dict[str, Any]], as_json: bool, config_path: Path) -> None:
    if as_json:
        emit_json({"ok": True, "action": "status", "config": str(config_path), "count": len(entries), "pins": entries})
        return

    print()
    print("╔══════════════════════════════════════════╗")
    print("║         GPIO 登记占用状态                ║")
    print("╠══════╦════════╦══════╦═══════════════════╣")
    print("║ 物理 ║  BCM   ║ 类型 ║  用途             ║")
    print("╠══════╬════════╬══════╬═══════════════════╣")
    if entries:
        for info in entries:
            bcm_str = str(info.get("bcm")) if info.get("bcm") is not None else "--"
            phys = info.get("physical") or BCM_TO_PHYSICAL.get(info.get("bcm"), "?")
            pin_type = str(info.get("type", "--"))
            device = str(info.get("device", "unknown"))
            print(f"║ {str(phys):>4} ║ {bcm_str:>4} ║ {pin_type:>4} ║ {device:<17} ║")
    else:
        print("║   —   ║   —   ║  —   ║ 暂无登记记录      ║")
    print("╚══════╩════════╩══════╩═══════════════════╝")
    print(f"\n  已登记 {len(entries)} 个引脚")
    print(f"  提示: 编辑 {config_path} 可维护设备占用表")
    print()


def validate_bcm(bcm: int, as_json: bool) -> None:
    if bcm not in BCM_TO_PHYSICAL:
        fail(f"BCM{bcm} 不在 40-pin 树莓派 GPIO 对照表中", as_json, bcm=bcm)


def read_pin(bcm: int, entries: List[Dict[str, Any]], as_json: bool) -> None:
    validate_bcm(bcm, as_json)
    warning = conflict_warning(find_conflict(entries, bcm), bcm)
    gpio = load_gpio_backend()
    gpio.setmode(gpio.BCM)
    gpio.setup(bcm, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    value = int(gpio.input(bcm))
    gpio.cleanup(bcm)
    phys = BCM_TO_PHYSICAL.get(bcm)

    payload = {
        "ok": True,
        "action": "read",
        "bcm": bcm,
        "physical": phys,
        "value": value,
        "level": "HIGH" if value else "LOW",
        "warning": warning,
    }
    if as_json:
        emit_json(payload)
    else:
        if warning:
            print(f"警告: {warning}")
        print(f"BCM{bcm}（物理{phys}）= {'HIGH ⚡' if value else 'LOW ⊖'}")


def write_pin(bcm: int, value: int, entries: List[Dict[str, Any]], as_json: bool, keep_state: bool) -> None:
    validate_bcm(bcm, as_json)
    warning = conflict_warning(find_conflict(entries, bcm), bcm)
    gpio = load_gpio_backend()
    gpio.setmode(gpio.BCM)
    gpio.setup(bcm, gpio.OUT)
    gpio.output(bcm, gpio.HIGH if value else gpio.LOW)
    if not keep_state:
        gpio.cleanup(bcm)
    phys = BCM_TO_PHYSICAL.get(bcm)

    payload = {
        "ok": True,
        "action": "write",
        "bcm": bcm,
        "physical": phys,
        "value": value,
        "level": "HIGH" if value else "LOW",
        "cleanup": not keep_state,
        "warning": warning,
    }
    if as_json:
        emit_json(payload)
    else:
        if warning:
            print(f"警告: {warning}")
            print("   继续操作可能和登记设备冲突")
        print(f"BCM{bcm}（物理{phys}）→ {'HIGH ⚡' if value else 'LOW ⊖'}")
        if keep_state:
            print("   已跳过 cleanup，适合需要保持电平的场景")


def pwm_pin(bcm: int, freq: int, duty: int, duration: float, entries: List[Dict[str, Any]], as_json: bool) -> None:
    validate_bcm(bcm, as_json)
    if not 0 <= duty <= 100:
        fail("PWM 占空比必须在 0-100 之间", as_json, duty=duty)
    warning = conflict_warning(find_conflict(entries, bcm), bcm)
    gpio = load_gpio_backend()
    gpio.setmode(gpio.BCM)
    gpio.setup(bcm, gpio.OUT)
    pwm = gpio.PWM(bcm, freq)
    pwm.start(duty)
    if not as_json:
        if warning:
            print(f"警告: {warning}")
        print(f"BCM{bcm} PWM: {freq}Hz @ {duty}% → 持续 {duration}s ...")
    time.sleep(duration)
    pwm.stop()
    gpio.cleanup(bcm)
    payload = {
        "ok": True,
        "action": "pwm",
        "bcm": bcm,
        "physical": BCM_TO_PHYSICAL.get(bcm),
        "frequency_hz": freq,
        "duty_percent": duty,
        "duration_sec": duration,
        "warning": warning,
    }
    if as_json:
        emit_json(payload)
    else:
        print("   完成")


def beep(bcm: int, count: int, interval: float, entries: List[Dict[str, Any]], as_json: bool) -> None:
    validate_bcm(bcm, as_json)
    warning = conflict_warning(find_conflict(entries, bcm), bcm)
    gpio = load_gpio_backend()
    gpio.setmode(gpio.BCM)
    gpio.setup(bcm, gpio.OUT)
    for _ in range(count):
        gpio.output(bcm, gpio.HIGH)
        time.sleep(interval)
        gpio.output(bcm, gpio.LOW)
        time.sleep(interval)
    gpio.cleanup(bcm)
    payload = {
        "ok": True,
        "action": "beep",
        "bcm": bcm,
        "physical": BCM_TO_PHYSICAL.get(bcm),
        "count": count,
        "interval_sec": interval,
        "warning": warning,
    }
    if as_json:
        emit_json(payload)
    else:
        if warning:
            print(f"警告: {warning}")
        print(f"蜂鸣器响 {count} 次")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="树莓派 GPIO 控制（Agent 友好版）")
    parser.add_argument("--pin", type=int, help="BCM GPIO 编号")
    parser.add_argument("--read", action="store_true", help="读取引脚状态")
    parser.add_argument("--write", type=int, choices=[0, 1], help="写入 0(LOW) 或 1(HIGH)")
    parser.add_argument("--pwm", nargs=2, type=int, metavar=("FREQ", "DUTY"), help="PWM 输出: 频率Hz 占空比%")
    parser.add_argument("--beep", type=int, nargs="?", const=3, metavar="N", help="蜂鸣器响 N 次 (默认3)")
    parser.add_argument("--duration", type=float, default=3.0, help="PWM 持续时间，默认 3 秒")
    parser.add_argument("--interval", type=float, default=0.2, help="蜂鸣器间隔，默认 0.2 秒")
    parser.add_argument("--keep-state", action="store_true", help="写入后不 cleanup，适合保持电平状态")
    parser.add_argument("--list", action="store_true", help="打印完整引脚对照表")
    parser.add_argument("--status", action="store_true", help="查看登记占用状态")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="引脚登记表路径，默认 config/pins.json")
    parser.add_argument("--json", action="store_true", dest="as_json", help="输出 JSON，供 Agent/程序调用")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config_path = Path(args.config)

    try:
        entries = load_registry(config_path)
        if args.list:
            list_pins(entries, args.as_json, config_path)
        elif args.status:
            show_status(entries, args.as_json, config_path)
        elif args.pin is None:
            if args.as_json:
                emit_json({"ok": False, "error": "missing --pin or command", "hint": "try --list or --pin 17 --read"})
                raise SystemExit(1)
            parser.print_help()
            print("\n试试: python3 scripts/gpio_control.py --list")
        elif args.beep is not None:
            beep(args.pin, args.beep, args.interval, entries, args.as_json)
        elif args.read:
            read_pin(args.pin, entries, args.as_json)
        elif args.write is not None:
            write_pin(args.pin, args.write, entries, args.as_json, args.keep_state)
        elif args.pwm:
            freq, duty = args.pwm
            pwm_pin(args.pin, freq, duty, args.duration, entries, args.as_json)
        else:
            if args.as_json:
                emit_json({"ok": False, "error": "no action specified", "hint": "use --read, --write, --pwm, --beep, --list or --status"})
                raise SystemExit(1)
            parser.print_help()
    except SystemExit:
        raise
    except Exception as exc:
        fail(str(exc), args.as_json)


if __name__ == "__main__":
    main()
