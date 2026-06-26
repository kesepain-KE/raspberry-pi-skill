---
name: raspberry-pi
description: 树莓派 AI Agent 硬件技能包。覆盖设备语义控制、GPIO 引脚读写、PWM、蜂鸣器、继电器、按钮、引脚/设备登记、系统状态采集、40-pin 引脚查询、I2C/SPI/UART 启用参考。优先用于 Pi 3B/3B+/4B/Zero；Pi 5 需使用 rpi-lgpio/gpiozero/lgpio 后端，不保证原生 RPi.GPIO 可用。
---

# 树莓派 AI Agent 硬件技能包

## 定位

这是给树莓派上运行的 AI Agent 使用的硬件技能层。当前版本提供：

- 设备语义控制：LED、蜂鸣器、继电器、按钮
- GPIO/PWM/蜂鸣器基础控制
- 系统状态采集
- JSON 结构化输出
- 设备注册表和引脚登记表
- 40-pin 引脚和硬件参数参考

它不是完整 IoT 平台，也不是成熟硬件控制框架。优先把它当作 Agent 的硬件执行入口。

## 兼容性规则

- Pi 3B / 3B+ / 4B / Zero：默认使用 `RPi.GPIO`
- Pi 5：原生 `RPi.GPIO` 不保证可用，建议安装 `requirements-pi5.txt` 中的 `rpi-lgpio` / `gpiozero`
- 所有 GPIO 操作默认使用 BCM 编号
- 接线前必须核对电压：GPIO 是 3.3V 逻辑，不可直接输入 5V 信号
- 继电器必须确认 `active_high`，很多继电器模块是低电平触发

## 推荐调用顺序

Agent 优先走设备语义层：

```bash
python3 scripts/device_control.py --list --json
python3 scripts/device_control.py --device bedroom_led --action on --json
python3 scripts/device_control.py --device buzzer --action beep --count 3 --json
python3 scripts/device_control.py --device relay_fan --action off --json
python3 scripts/device_control.py --device button_1 --action read --json
```

只有需要直接操作 BCM 引脚时，才退到底层 GPIO：

```bash
python3 scripts/gpio_control.py --pin 17 --read --json
python3 scripts/gpio_control.py --pin 17 --write 1 --json
python3 scripts/gpio_control.py --status --json
```

系统状态采集：

```bash
python3 scripts/pi_info.py --json
```

## 内置工具脚本

### 设备语义控制 — `scripts/device_control.py`

```bash
python3 scripts/device_control.py --list
python3 scripts/device_control.py --device bedroom_led --action on
python3 scripts/device_control.py --device bedroom_led --action off
python3 scripts/device_control.py --device bedroom_led --action blink --count 3 --interval 0.2
python3 scripts/device_control.py --device buzzer --action beep --count 3 --interval 0.2
python3 scripts/device_control.py --device relay_fan --action pulse --duration 1
python3 scripts/device_control.py --device button_1 --action read
```

Agent 调用时优先加 `--json`。

支持设备类型：

| 类型 | 动作 | 说明 |
|:----|:----|:----|
| led | on / off / toggle / blink | LED 输出 |
| buzzer | on / off / beep | 有源蜂鸣器输出 |
| relay | on / off / pulse | 继电器输出，支持 active_low |
| button | read | 按钮输入读取 |

`device_control.py` 的 JSON 返回示例：

```json
{
  "ok": true,
  "device": "relay_fan",
  "type": "relay",
  "action": "on",
  "bcm": 23,
  "physical": 16,
  "active_high": false,
  "state": "on",
  "value": 0,
  "level": "LOW"
}
```

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
```

## Agent Schema

执行脚本前，Agent 可以读取以下协议文件来确认参数和返回结构：

```text
schemas/device_control.schema.json
schemas/gpio_control.schema.json
schemas/pi_info.schema.json
```

调用约定：

- 设备语义控制优先使用 `python3 scripts/device_control.py ... --json`
- GPIO 控制使用 `python3 scripts/gpio_control.py ... --json`
- 系统信息使用 `python3 scripts/pi_info.py --json`
- JSON 返回统一先看 `ok`
- `ok=false` 时读取 `error` 和 `hint`
- `warning` 不代表失败，但表示引脚登记冲突或潜在风险

## 设备注册表

设备语义层读取 `config/pins.json` 的 `devices` 字段。

示例：

```json
{
  "devices": {
    "bedroom_led": {
      "type": "led",
      "bcm": 17,
      "active_high": true,
      "description": "卧室 LED"
    },
    "buzzer": {
      "type": "buzzer",
      "bcm": 18,
      "active_high": true,
      "description": "有源蜂鸣器"
    },
    "relay_fan": {
      "type": "relay",
      "bcm": 23,
      "active_high": false,
      "description": "低电平触发风扇继电器"
    },
    "button_1": {
      "type": "button",
      "bcm": 24,
      "pull": "up",
      "description": "按钮输入"
    }
  }
}
```

字段要点：

- `type`: `led` / `buzzer` / `relay` / `button`
- `bcm`: BCM 引脚编号
- `active_high`: 输出设备触发电平，继电器尤其要确认
- `pull`: 按钮输入上拉/下拉，支持 `up` / `down` / `none`

## 引脚登记表

引脚占用信息不写在 Python 源码里，而是放在本地文件：

```text
config/pins.json
```

该文件默认不提交到 Git。创建方式：

```bash
cp config/pins.example.json config/pins.json
```

注意：这是手动登记表，用于提醒 Agent 和用户避免接线冲突，不是真正的系统级实时占用扫描。

## 操作流程

1. 先查看系统状态：`python3 scripts/pi_info.py --json`
2. 查看设备表：`python3 scripts/device_control.py --list --json`
3. 优先用设备语义动作控制硬件
4. 需要直接操作引脚时，查看引脚表：`python3 scripts/gpio_control.py --list`
5. 查看登记占用：`python3 scripts/gpio_control.py --status --json`
6. 确认 BCM 编号、物理引脚和电平触发逻辑
7. 执行读取、写入、PWM 或蜂鸣器操作
8. 需要持续保持电平时才使用 `--keep-state`

## cleanup 策略

- 默认会在单次 GPIO 操作后 cleanup，适合测试、读取、短时 PWM、蜂鸣器
- `device_control.py` 当前不主动 cleanup，适合 LED/继电器等语义设备保持状态
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

详见 [`references/hardware.md`](references/hardware.md)。

## 测试和维护

```bash
python -m py_compile scripts/gpio_control.py scripts/pi_info.py scripts/device_control.py devices/*.py
python -m pytest tests -q
```

维护要求：文档、Schema、CLI、测试必须同步更新。

## 后续建议

- 增加 GPIO backend 抽象：RPi.GPIO / rpi-lgpio / gpiozero / lgpio
- 增加更多设备层：超声波、舵机、DHT 传感器
- 增加常驻 daemon，支持需要保持状态的设备
- 增加设备状态持久化、远程硬件控制和 kemo-agent 接入
