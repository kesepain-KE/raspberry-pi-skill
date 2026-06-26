#!/usr/bin/env python3
"""
树莓派系统信息一键采集（通用版）
用法:
  python3 pi_info.py             # 人类可读格式
  python3 pi_info.py --json      # JSON 格式
  python3 pi_info.py --watch     # 每2秒刷新（CTRL+C 退出）
"""

import json
import os
import subprocess
import sys
import time


def run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return f"<error: {e}>"


def get_cpu():
    temp = run("vcgencmd measure_temp 2>/dev/null")
    temp = temp.replace("temp=", "").replace("'C", "°C") if "temp=" in temp else "N/A"

    freq = run("vcgencmd measure_clock arm 2>/dev/null")
    freq = f"{int(freq.split('=')[1]) / 1e6:.0f} MHz" if "=" in freq else "N/A"

    volt = run("vcgencmd measure_volts core 2>/dev/null")
    volt = volt.split("=")[1] if "=" in volt else "N/A"

    throttled = run("vcgencmd get_throttled 2>/dev/null")
    throttled = throttled.split("=")[1] if "=" in throttled else "N/A"

    load = run("cat /proc/loadavg").split()[:3]
    load_str = " / ".join(load) if load else "N/A"

    return {
        "temperature": temp,
        "frequency": freq,
        "voltage": volt,
        "throttled": throttled,
        "load_avg": load_str,
    }


def get_memory():
    m = run("free -h | grep Mem")
    parts = m.split() if m else []
    if len(parts) >= 3:
        return {
            "total": parts[1],
            "used": parts[2],
            "free": parts[3],
            "available": parts[6] if len(parts) > 6 else "N/A",
        }
    return {}


def get_disk():
    result = {}
    # 系统盘
    d = run("df -h / | tail -1")
    parts = d.split() if d else []
    if len(parts) >= 5:
        result["系统盘"] = {"size": parts[1], "used": parts[2], "avail": parts[3], "use%": parts[4]}
    # USB 挂载点（如果存在）
    usb = run("df -h /mnt/usb 2>/dev/null | tail -1")
    if usb and "Filesystem" not in usb:
        parts = usb.split()
        if len(parts) >= 5:
            result["USB"] = {"size": parts[1], "used": parts[2], "avail": parts[3], "use%": parts[4]}
    return result


def get_network():
    info = {}
    for iface in ["eth0", "wlan0"]:
        ip = run(f"ip -4 addr show {iface} 2>/dev/null | grep inet | awk '{{print $2}}'")
        state = run(f"cat /sys/class/net/{iface}/operstate 2>/dev/null")
        info[iface] = {"ip": ip or "无", "state": state or "down"}
    return info


def get_system():
    return {
        "hostname": run("hostname"),
        "kernel": run("uname -r"),
        "arch": run("uname -m"),
        "os": run("cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'"),
        "uptime": run("uptime -p"),
    }


def get_gpio_info():
    lib = run("python3 -c 'import RPi.GPIO; print(RPi.GPIO.VERSION)' 2>/dev/null")
    return {"library": f"RPi.GPIO {lib}" if lib else "未安装"}


def print_human(info):
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
║ 主机: {s['hostname']:<12}  系统: {s['os']:<20} ║
║ 内核: {s['kernel']:<20}  架构: {s['arch']:<7} ║
║ 运行: {s['uptime']:<37} ║
╠══════════════════════════════════════════╣
║  CPU
║    温度: {c['temperature']:<10} 频率: {c['frequency']:<13}
║    电压: {c['voltage']:<10} 负载: {c['load_avg']:<13}
║    限频标志: {c['throttled']:<29}
╠══════════════════════════════════════════╣
║  内存
║    总计: {m.get('total','N/A'):<8} 已用: {m.get('used','N/A'):<8} 可用: {m.get('available','N/A'):<8} ║""")
    for label, dd in d.items():
        print(f"║  存储 {label}: {dd['size']}  已用 {dd['used']} ({dd['use%']})  剩余 {dd['avail']}")
    print(f"""╠══════════════════════════════════════════╣
║  网络""")
    for iface, info in n.items():
        print(f"║    {iface}: {info['ip']:<18} [{info['state']}]")
    print(f"""╠══════════════════════════════════════════╣
║  GPIO: {g['library']:<34} ║
╚══════════════════════════════════════════╝""")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--watch", action="store_true", help="每 2 秒刷新")
    args = parser.parse_args()

    def collect():
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system": get_system(),
            "cpu": get_cpu(),
            "memory": get_memory(),
            "disk": get_disk(),
            "network": get_network(),
            "gpio": get_gpio_info(),
        }

    if args.watch:
        try:
            while True:
                os.system("clear")
                info = collect()
                print_human(info)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n退出监控")
    elif args.json:
        print(json.dumps(collect(), indent=2, ensure_ascii=False))
    else:
        print_human(collect())
