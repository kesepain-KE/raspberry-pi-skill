---
name: raspberry-pi
description: 树莓派 AI Agent 硬件技能包。覆盖 GPIO 引脚读写、PWM、蜂鸣器、引脚登记、系统状态采集、40-pin 引脚查询、I2C/SPI/UART 启用参考。优先用于 Pi 3B/3B+/4B/Zero；Pi 5 需使用 rpi-lgpio/gpiozero/lgpio 后端，不保证原生 RPi.GPIO 可用。
---

# 树莓派 AI Agent 硬件技能包

## 定位

这是给树莓派上运行的 AI Agent 使用的硬件技能层。当前版本提供：

- GPIO/PWM/蜂鸣器基础控制
- 系统状态采集
- JSON 结构化输出
- 引脚登记表
- 40-pin 引脚和硬件参数参考

它不是完整 IoT 平台，也不是成熟硬件控制框架。优先把它当作 Agent 的硬件执行入口。

## 兼容性规则

- Pi 3B / 3B+ / 4B / Zero：默认使用 `RPi.GPIO`
- Pi 5：原生 `RPi.GPIO` 不保证可用，建议安装 `requirements-pi5.txt` 中的 `rpi-lgpio` / `gpiozero`
- 所有 GPIO 操作默认使用 BCM 编号
- 接线前必须核对电压：GPIO 是 3.3V 逻辑，不可直接输入 5V 信号

## 内置工具脚本

### 系统监控 — `scripts/pi_info.py`

```bash
python3 scripts/pi_info.py            # 人类可读面板
python3 scripts/pi_info.py --json     # JSON 输出
python3 scripts/pi_info.py --watch    # 实时刷新（每 2 秒）
```

输出：型号、系统、CPU 温度/频率/电压/限频标志、内存、磁盘、网络状态、GPIO 库版本。

### GPIO 控制 — `scripts/gpio_control.py`

```bash
python3 scripts/gpio_control.py --list
python3 scripts/gpio_control.py --status
python3 scripts/gpio_control.py --pin 17 --read
python3 scripts/gpio_control.py --pin 17 --write 1
python3 scripts/gpio_control.py --pin 17 --write 1 --keep-state
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50 --duration 3
python3 scripts/gpio_control.py --pin 18 --beep 3 --interval 0.2
```

Agent 调用时优先加 `--json`：

```bash
python3 scripts/gpio_control.py --pin 17 --read --json
python3 scripts/gpio_control.py --pin 17 --write 1 --json
python3 scripts/gpio_control.py --status --json
python3 scripts/pi_info.py --json
```

`gpio_control.py` 的 JSON 返回示例：

```json
{
  "ok": true,
  "action": "write",
  "bcm": 17,
  "physical": 11,
  "value": 1,
  "level": "HIGH",
  "cleanup": true,
  "warning": null
}
```

## Agent Schema

执行脚本前，Agent 可以读取以下协议文件来确认参数和返回结构：

```text
schemas/gpio_control.schema.json
schemas/pi_info.schema.json
```

调用约定：

- GPIO 控制优先使用 `python3 scripts/gpio_control.py ... --json`
- 系统信息优先使用 `python3 scripts/pi_info.py --json`
- JSON 返回统一先看 `ok`
- `ok=false` 时读取 `error` 和 `hint`
- `warning` 不代表失败，但表示引脚登记冲突或潜在风险

## 引脚登记表

引脚占用信息不写在 Python 源码里，而是放在本地文件：

```text
config/pins.json
```

该文件默认不提交到 Git。创建方式：

```bash
cp config/pins.example.json config/pins.json
```

示例：

```json
{
  "pins": {
    "18": {
      "type": "BCM",
      "bcm": 18,
      "physical": 12,
      "device": "buzzer",
      "mode": "PWM/output",
      "owner": "raspberry-pi-skill",
      "notes": "蜂鸣器 IO"
    }
  }
}
```

注意：这是手动登记表，用于提醒 Agent 和用户避免接线冲突，不是真正的系统级实时占用扫描。

## 操作流程

1. 先查看系统状态：`python3 scripts/pi_info.py --json`
2. 查看引脚表：`python3 scripts/gpio_control.py --list`
3. 查看登记占用：`python3 scripts/gpio_control.py --status --json`
4. 确认 BCM 编号和物理引脚
5. 执行读取、写入、PWM 或蜂鸣器操作
6. 需要持续保持电平时才使用 `--keep-state`

## cleanup 策略

- 默认会在单次 GPIO 操作后 cleanup，适合测试、读取、短时 PWM、蜂鸣器
- `--keep-state` 会跳过 cleanup，适合继电器、风扇、灯等需要保持电平的场景
- 长期稳定控制建议后续使用常驻 daemon，不建议一直用一次性 CLI 维持状态

## 引脚参考

完整 40 引脚对照表详见 [`references/pinout.md`](references/pinout.md)。

推荐空闲引脚：

| 类型 | BCM 引脚（物理引脚） |
|:----:|:-------------------:|
| GPIO | 17(11), 27(13), 22(15), 23(16), 24(18), 25(22), 5(29), 6(31) |
| PWM | 18(12), 12(32), 13(33) |
| GND | 引脚 9, 14, 20, 25, 30, 34, 39 |
| 5V | 引脚 2, 4 |
| 3.3V | 引脚 1, 17 |

## 启用额外接口

编辑 `/boot/firmware/config.txt`：

```bash
dtparam=i2c_arm=on      # I2C
dtparam=spi=on          # SPI
enable_uart=1           # UART
sudo reboot
```

检查是否已启用：

```bash
ls /dev/i2c* /dev/spi* /dev/ttyAMA0 /dev/ttyS0 2>/dev/null
lsmod | grep -E "i2c|spi|uart"
```

## RPi.GPIO 编程模板

### GPIO 输出

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)
GPIO.output(17, GPIO.LOW)
GPIO.cleanup()
```

### PWM 输出

```python
p = GPIO.PWM(18, 1000)
p.start(50)
p.ChangeFrequency(440)
p.ChangeDutyCycle(30)
p.stop()
GPIO.cleanup()
```

### GPIO 输入

```python
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
if GPIO.input(17) == GPIO.LOW:
    print("触发")
```

## WiringPi 操作参考

WiringPi 只作为参考，不是脚本依赖。

```bash
gpio readall
gpio read 0
gpio write 0 1
gpio mode 0 out
gpio pwm 1 500
```

## 系统常用命令

```bash
vcgencmd measure_temp
vcgencmd measure_clock arm
vcgencmd get_throttled
pinout
ip -br addr
df -h
free -h
```

## 硬件参数参考
- 增加 JSON Schema 和自动测试后，优先保持文档、Schema、CLI 三者同步

详见 [`references/hardware.md`](references/hardware.md)。

## 后续建议

- 增加 GPIO backend 抽象：RPi.GPIO / rpi-lgpio / gpiozero / lgpio
- 增加设备层：LED、蜂鸣器、继电器、按钮、超声波、舵机、DHT 传感器
- 增加常驻 daemon，支持需要保持状态的设备
- 增加错误码、模拟测试和 Agent tool schema
