#!/usr/bin/env python3
"""
树莓派 GPIO 控制脚本（通用版）
用法:
  python3 gpio_control.py --list              # 引脚对照表
  python3 gpio_control.py --pin 17 --read     # 读取引脚
  python3 gpio_control.py --pin 17 --write 1  # 写高电平
  python3 gpio_control.py --pin 18 --pwm 1000 50  # PWM (频率 占空比)
  python3 gpio_control.py --pin 18 --beep 3   # 蜂鸣器快速响 N 次
  python3 gpio_control.py --status            # 查看已用引脚
"""

import argparse
import sys
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("需要 RPi.GPIO: pip3 install RPi.GPIO")
    sys.exit(1)

# ============================================================
# 已用引脚记录 — 请根据实际接线修改
# 格式: { BCM编号: {"type": "类型", "device": "设备名"} }
# 电源引脚（5V/GND/3.3V）不占用 BCM，type=5V/GND/3.3V，bcm=None
# ============================================================
OCCUPIED = {
    # 示例：
    # 4:  {"type": "5V",  "device": "散热风扇 VCC", "bcm": None},
    # 6:  {"type": "GND", "device": "散热风扇 GND", "bcm": None},
    # 18: {"type": "BCM", "device": "蜂鸣器 IO",    "bcm": 18},
}

BCM_TO_PHYSICAL = {
    2: 3, 3: 5, 4: 7, 14: 8, 15: 10, 17: 11,
    18: 12, 27: 13, 22: 15, 23: 16, 24: 18, 25: 22,
    5: 29, 6: 31, 12: 32, 13: 33, 19: 35, 16: 36,
    26: 37, 20: 38, 21: 40,
}


def check_conflict(pin):
    """检查引脚是否已被占用"""
    if pin in OCCUPIED:
        o = OCCUPIED[pin]
        phys = BCM_TO_PHYSICAL.get(pin, "?")
        print(f"警告: BCM{pin}（物理引脚{phys}）已被 [{o['device']}] 占用！")
        return True
    return False


def list_pins():
    """打印完整引脚对照表"""
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║           GPIO 引脚对照表                           ║")
    print("╠════╦════════╦════════╦═══════╦══════════════════════╣")
    print("║物理║  BCM   ║  功能  ║ 状态  ║  备注                ║")
    print("╠════╬════════╬════════╬═══════╬══════════════════════╣")

    rows = [
        (1,  "--", "3.3V",    "⚡", ""),
        (2,  "--", "5V",      "⚡", ""),
        (3,  "2", "I2C SDA",  "○", "I2C 默认未启用"),
        (4,  "--", "5V",      "⚡", ""),
        (5,  "3", "I2C SCL",  "○", "I2C 默认未启用"),
        (6,  "--", "GND",     "⊖", ""),
        (7,  "4", "GPIO",     "○", ""),
        (8,  "14","UART TX",  "○", "UART 默认未启用"),
        (9,  "--", "GND",     "⊖", ""),
        (10, "15","UART RX",  "○", "UART 默认未启用"),
        (11, "17","GPIO",     "○", ""),
        (12, "18","PWM0",     "○", ""),
        (13, "27","GPIO",     "○", ""),
        (14, "--", "GND",     "⊖", ""),
        (15, "22","GPIO",     "○", ""),
        (16, "23","GPIO",     "○", ""),
        (17, "--", "3.3V",    "⚡", ""),
        (18, "24","GPIO",     "○", ""),
        (19, "10","SPI MOSI", "○", "SPI 默认未启用"),
        (20, "--", "GND",     "⊖", ""),
        (21, "9", "SPI MISO", "○", "SPI 默认未启用"),
        (22, "25","GPIO",     "○", ""),
        (23, "11","SPI SCLK", "○", "SPI 默认未启用"),
        (24, "8", "SPI CE0",  "○", "SPI 默认未启用"),
        (25, "--", "GND",     "⊖", ""),
        (26, "7", "SPI CE1",  "○", "SPI 默认未启用"),
        (27, "0", "ID EEPROM","◆", "系统保留"),
        (28, "1", "ID EEPROM","◆", "系统保留"),
        (29, "5", "GPIO",     "○", ""),
        (30, "--", "GND",     "⊖", ""),
        (31, "6", "GPIO",     "○", ""),
        (32, "12","PWM0",     "○", ""),
        (33, "13","PWM1",     "○", ""),
        (34, "--", "GND",     "⊖", ""),
        (35, "19","GPIO",     "○", ""),
        (36, "16","GPIO",     "○", ""),
        (37, "26","GPIO",     "○", ""),
        (38, "20","GPIO",     "○", ""),
        (39, "--", "GND",     "⊖", ""),
        (40, "21","GPIO",     "○", ""),
    ]

    # 标记已占用引脚
    for pin, info in OCCUPIED.items():
        for i, (phy, bcm, func, icon, note) in enumerate(rows):
            if info["bcm"] is not None and bcm == str(info["bcm"]):
                rows[i] = (phy, bcm, func, "●", note or info["device"])
            elif info["bcm"] is None and phy == pin:
                rows[i] = (phy, bcm, func, "●", info["device"])

    for phy, bcm, func, icon, note in rows:
        print(f"║ {phy:>2} ║ {bcm:>4} ║ {func:<7}║  {icon}  ║ {note:<22} ║")

    print("╚════╩════════╩════════╩═══════╩══════════════════════╝")
    print("  ○=空闲  ●=已占用  ⚡=电源  ⊖=GND  ◆=系统保留")
    print()


def read_pin(bcm):
    check_conflict(bcm)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    val = GPIO.input(bcm)
    phys = BCM_TO_PHYSICAL.get(bcm, "?")
    GPIO.cleanup()
    print(f"BCM{bcm}（物理{phys}）= {'HIGH ⚡' if val else 'LOW ⊖'}")
    return val


def write_pin(bcm, value):
    if check_conflict(bcm):
        print("   坚持操作，可能冲突！")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm, GPIO.OUT)
    GPIO.output(bcm, GPIO.HIGH if value else GPIO.LOW)
    phys = BCM_TO_PHYSICAL.get(bcm, "?")
    print(f"BCM{bcm}（物理{phys}）→ {'HIGH ⚡' if value else 'LOW ⊖'}")
    GPIO.cleanup()


def pwm_pin(bcm, freq, duty, duration=3):
    if check_conflict(bcm):
        print("   坚持操作，可能冲突！")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm, GPIO.OUT)
    p = GPIO.PWM(bcm, freq)
    p.start(duty)
    print(f"BCM{bcm} PWM: {freq}Hz @ {duty}% → 持续 {duration}s ...")
    time.sleep(duration)
    p.stop()
    GPIO.cleanup()
    print("   完成")


def beep(bcm, count=3, interval=0.2):
    """蜂鸣器快速提示音"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcm, GPIO.OUT)
    for i in range(count):
        GPIO.output(bcm, GPIO.HIGH)
        time.sleep(interval)
        GPIO.output(bcm, GPIO.LOW)
        time.sleep(interval)
    GPIO.cleanup()
    print(f"蜂鸣器响 {count} 次")


def show_status():
    print()
    print("╔══════════════════════════════════════════╗")
    print("║         GPIO 占用状态                    ║")
    print("╠══════╦════════╦══════╦═══════════════════╣")
    print("║ 物理 ║  BCM   ║ 类型 ║  用途             ║")
    print("╠══════╬════════╬══════╬═══════════════════╣")
    if OCCUPIED:
        for pin, info in OCCUPIED.items():
            bcm_str = str(info["bcm"]) if info["bcm"] else "--"
            phys = BCM_TO_PHYSICAL.get(info["bcm"], pin) if info["bcm"] is not None else pin
            print(f"║ {phys:>4} ║ {bcm_str:>4} ║ {info['type']:>4} ║ {info['device']:<17} ║")
    else:
        print("║   —   ║   —   ║  —   ║ 暂无占用记录      ║")
    print("╚══════╩════════╩══════╩═══════════════════╝")
    print(f"\n  已用 {len(OCCUPIED)} 个引脚，剩余 {40 - len(OCCUPIED)} 个空闲")
    print("  提示: 编辑脚本顶部 OCCUPIED 字典可记录已用引脚")
    print()


def main():
    parser = argparse.ArgumentParser(description="树莓派 GPIO 控制（通用版）")
    parser.add_argument("--pin", type=int, help="BCM GPIO 编号")
    parser.add_argument("--read", action="store_true", help="读取引脚状态")
    parser.add_argument("--write", type=int, choices=[0, 1], help="写入 0(LOW) 或 1(HIGH)")
    parser.add_argument("--pwm", nargs=2, type=int, metavar=("FREQ", "DUTY"), help="PWM 输出: 频率Hz 占空比%")
    parser.add_argument("--beep", type=int, nargs="?", const=3, metavar="N", help="蜂鸣器响 N 次 (默认3)")
    parser.add_argument("--list", action="store_true", help="打印完整引脚对照表")
    parser.add_argument("--status", action="store_true", help="查看已用引脚状态")

    args = parser.parse_args()

    if args.list:
        list_pins()
    elif args.status:
        show_status()
    elif args.pin is None:
        parser.print_help()
        print("\n试试: python3 gpio_control.py --list")
    elif args.beep is not None:
        beep(args.pin, args.beep)
    elif args.read:
        read_pin(args.pin)
    elif args.write is not None:
        write_pin(args.pin, args.write)
    elif args.pwm:
        freq, duty = args.pwm
        pwm_pin(args.pin, freq, duty)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
