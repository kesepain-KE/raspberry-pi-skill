#!/usr/bin/env python3
"""
树莓派系统信息一键采集（通用版）
用法:
  python3 pi_info.py             # 人类可读格式
  python3 pi_info.py --json      # JSON 格式
  python3 pi_info.py --watch     # 每2秒刷新（CTRL+C 退出）
"""

import argparse
import json
import os
import subprocess
import time
from typing import List, Optional


def run(args: List[str], timeout: int = 5, default: str = "") -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return (result.stdout.strip() or result.stderr.strip() or default).strip()
    except Exception as exc:
        return f"<error: {exc}>"


def read_text(path: str, default: str = "") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return default


def first_existing(paths: List[str]) -> Optional[str]:
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def get_pi_model() -> str:
    model = read_text("/proc/device-tree/model") or read_text("/sys/firmware/devicetree/base/model")
    return model.replace("\x00", "").strip() or "N/A"


def get_os_pretty_name() -> str:
    content = read_text("/etc/os-release")
    for line in content.splitlines():
        if line.startswith("PRETTY_NAME="):
            return line.split("=", 1)[1].strip().strip('"')
    return "N/A"


def get_cpu() -> dict:
    temp = run(["vcgencmd", "measure_temp"])
    temp = temp.replace("temp=", "").replace("'C", "°C") if "temp=" in temp else "N/A"

    freq = run(["vcgencmd", "measure_clock", "arm"])
    try:
        freq = f"{int(freq.split('=')[1]) / 1e6:.0f} MHz" if "=" in freq else "N/A"
    except Exception:
        freq = "N/A"

    volt = run(["vcgencmd", "measure_volts", "core"])
    volt = volt.split("=", 1)[1] if "=" in volt else "N/A"

    throttled = run(["vcgencmd", "get_throttled"])
    throttled = throttled.split("=", 1)[1] if "=" in throttled else "N/A"

    load = read_text("/proc/loadavg").split()[:3]
    load_str = " / ".join(load) if load else "N/A"

    return {
        "temperature": temp,
        "frequency": freq,
        "voltage": volt,
        "throttled": throttled,
        "load_avg": load_str,
    }


def get_memory() -> dict:
    meminfo = read_text("/proc/meminfo")
    values = {}
    for line in meminfo.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key] = value.strip()
    return {
        "total": values.get("MemTotal", "N/A"),
        "free": values.get("MemFree", "N/A"),
        "available": values.get("MemAvailable", "N/A"),
        "swap_total": values.get("SwapTotal", "N/A"),
        "swap_free": values.get("SwapFree", "N/A"),
    }


def parse_df(path: str) -> dict:
    output = run(["df", "-h", path])
    lines = [line for line in output.splitlines() if line.strip()]
    if len(lines) < 2:
        return {}
    parts = lines[-1].split()
    if len(parts) >= 6:
        return {"filesystem": parts[0], "size": parts[1], "used": parts[2], "avail": parts[3], "use%": parts[4], "mount": parts[5]}
    return {}


def get_disk() -> dict:
    result = {}
    system_disk = parse_df("/")
    if system_disk:
        result["system"] = system_disk
    usb_path = first_existing(["/mnt/usb", "/media"])
    if usb_path:
        usb_disk = parse_df(usb_path)
        if usb_disk:
            result["external"] = usb_disk
    return result


def get_network() -> dict:
    info = {}
    for iface in ["eth0", "wlan0"]:
        state = read_text(f"/sys/class/net/{iface}/operstate", "down")
        ip_output = run(["ip", "-4", "-o", "addr", "show", iface])
        ip_addr = "无"
        parts = ip_output.split()
        if "inet" in parts:
            idx = parts.index("inet")
            if idx + 1 < len(parts):
                ip_addr = parts[idx + 1]
        info[iface] = {"ip": ip_addr, "state": state or "down"}
    return info


def get_system() -> dict:
    return {
        "hostname": run(["hostname"]),
        "model": get_pi_model(),
        "kernel": run(["uname", "-r"]),
        "arch": run(["uname", "-m"]),
        "os": get_os_pretty_name(),
        "uptime": run(["uptime", "-p"]),
    }


def get_gpio_info() -> dict:
    candidates = [
        ["python3", "-c", "import RPi.GPIO; print(RPi.GPIO.VERSION)"],
        ["python", "-c", "import RPi.GPIO; print(RPi.GPIO.VERSION)"],
    ]
    lib = ""
    for command in candidates:
        lib = run(command)
        error_markers = ["<error:", "Traceback", "ModuleNotFoundError", "ImportError", "No module"]
        if lib and not any(marker in lib for marker in error_markers):
            break
    else:
        lib = ""
    return {"library": f"RPi.GPIO {lib}" if lib else "未安装"}


def print_human(info: dict) -> None:
    c = info["cpu"]
    m = info["memory"]
    s = info["system"]
    n = info["network"]
    g = info["gpio"]
    d = info["disk"]

    print(f"""
╔══════════════════════════════════════════╗
║     树莓派系统状态                       ║
╠══════════════════════════════════════════╣
║ 主机: {s['hostname']:<12} 架构: {s['arch']:<12} ║
║ 型号: {s['model']:<37} ║
║ 系统: {s['os']:<37} ║
║ 内核: {s['kernel']:<37} ║
║ 运行: {s['uptime']:<37} ║
╠══════════════════════════════════════════╣
║  CPU
║    温度: {c['temperature']:<10} 频率: {c['frequency']:<13}
║    电压: {c['voltage']:<10} 负载: {c['load_avg']:<13}
║    限频标志: {c['throttled']:<29}
╠══════════════════════════════════════════╣
║  内存
║    总计: {m.get('total','N/A'):<12} 可用: {m.get('available','N/A'):<12} ║""")
    for label, dd in d.items():
        print(f"║  存储 {label}: {dd['size']}  已用 {dd['used']} ({dd['use%']})  剩余 {dd['avail']}")
    print("╠══════════════════════════════════════════╣")
    print("║  网络")
    for iface, net in n.items():
        print(f"║    {iface}: {net['ip']:<18} [{net['state']}]")
    print(f"""╠══════════════════════════════════════════╣
║  GPIO: {g['library']:<34} ║
╚══════════════════════════════════════════╝""")


def collect() -> dict:
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "system": get_system(),
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disk": get_disk(),
        "network": get_network(),
        "gpio": get_gpio_info(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="树莓派系统信息一键采集")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--watch", action="store_true", help="每 2 秒刷新")
    args = parser.parse_args()

    if args.watch:
        try:
            while True:
                os.system("clear")
                print_human(collect())
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n退出监控")
    elif args.json:
        print(json.dumps(collect(), indent=2, ensure_ascii=False))
    else:
        print_human(collect())


if __name__ == "__main__":
    main()
