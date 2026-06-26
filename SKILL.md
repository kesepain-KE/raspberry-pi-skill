---
name: raspberry-pi
description: 树莓派通用操作指南。覆盖 GPIO 引脚对接、RPi.GPIO 编程、I2C/SPI/UART 接口启用、PWM 控制、传感器/执行器接线、系统监控、引脚查询。当需要在树莓派上接外设、控制 GPIO、读写传感器、驱动蜂鸣器/LED/电机、查看系统状态或查询引脚定义时触发。适用于 Pi 3B/3B+/4B/5。
---

# 树莓派通用操作指南

## 内置工具脚本

技能目录下有两个一键脚本，优先使用：

### 系统监控 — `scripts/pi_info.py`

```bash
python3 scripts/pi_info.py            # 人类可读面板
python3 scripts/pi_info.py --json     # JSON 输出
python3 scripts/pi_info.py --watch    # 实时刷新（每 2 秒）
```

输出：CPU 温度/频率/电压/限频标志、内存、磁盘、网络状态。

### GPIO 控制 — `scripts/gpio_control.py`

```bash
python3 scripts/gpio_control.py --list              # 完整引脚对照表
python3 scripts/gpio_control.py --status            # 已用引脚
python3 scripts/gpio_control.py --pin 17 --read     # 读取引脚
python3 scripts/gpio_control.py --pin 17 --write 1  # 写高电平
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50  # PWM（频率 占空比）
python3 scripts/gpio_control.py --pin 18 --beep 3   # 蜂鸣器响 N 次
```

脚本内置冲突检测，`--status` 可查看当前已用引脚。

## 核心规则

1. **所有 GPIO 操作用 BCM 编号**（`GPIO.setmode(GPIO.BCM)`）
2. **用完后必须 `GPIO.cleanup()`**，避免引脚占用冲突
3. **建议将用户加入 `gpio` 组**以直接访问 `/dev/gpiomem`（无需 sudo）
4. **I2C、SPI、UART 默认未启用**，启用需改 `/boot/firmware/config.txt` 并重启
5. **操作完清理临时脚本**（`tmp/` 下的 .py）

## 操作流程

1. SSH 到树莓派（或本地终端）
2. 复制脚本到目标目录或用相对路径执行
3. 先 `python3 pi_info.py` 查看系统状态
4. 再 `python3 gpio_control.py --status` 查看引脚占用
5. 查引脚表确认可用引脚后操作

## 引脚参考

完整 40 引脚对照表详见 [`references/pinout.md`](references/pinout.md)。

### 推荐空闲引脚

| 类型 | BCM 引脚（物理引脚） |
|:----:|:-------------------:|
| GPIO | 17(11), 27(13), 22(15), 23(16), 24(18), 25(22), 5(29), 6(31) |
| PWM | 18(12), 12(32), 13(33) |
| GND | 引脚 9, 14, 20, 25, 30, 34, 39 |
| 5V | 引脚 2, 4 |
| 3.3V | 引脚 1, 17 |

### 已用引脚记录模板

建议维护表格记录已占用引脚：

| 物理引脚 | BCM | 类型 | 用途 |
|:-------:|:---:|:----:|:----:|
| （示例）12 | 18 | PWM0 | 蜂鸣器 |

用 `python3 gpio_control.py --status` 查看。

## RPi.GPIO 编程模板

### GPIO 输出（LED/继电器/蜂鸣器）

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.HIGH)   # 高电平
GPIO.output(17, GPIO.LOW)    # 低电平
GPIO.cleanup()
```

### PWM 输出

```python
p = GPIO.PWM(18, 1000)  # 频率 Hz
p.start(50)              # 占空比 0-100
p.ChangeFrequency(440)
p.ChangeDutyCycle(30)
p.stop()
```

### GPIO 输入（按钮/传感器）

```python
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
if GPIO.input(17) == GPIO.LOW:
    print("触发")
```

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

## WiringPi 操作参考

如果安装了 WiringPi：

### 命令行

```bash
gpio readall                    # 引脚对照表（wPi/BCM/物理）
gpio read 0                     # wPi 0（BCM 17）
gpio write 0 1                  # 写高电平
gpio mode 0 out                 # 设为输出
gpio pwm 1 500                  # wPi 1（BCM 18）PWM
```

### WiringPi 引脚速查

| wPi | BCM | 物理 | 功能 |
|:---:|:---:|:----:|:----:|
| 0 | 17 | 11 | GPIO |
| 1 | 18 | 12 | PWM0 |
| 2 | 27 | 13 | GPIO |
| 3 | 22 | 15 | GPIO |
| 4 | 23 | 16 | GPIO |
| 5 | 24 | 18 | GPIO |
| 6 | 25 | 22 | GPIO |
| 7 | 4 | 7 | GPIO |
| 8 | 2 | 3 | I2C SDA |
| 9 | 3 | 5 | I2C SCL |

### C 语言编程

```c
#include <wiringPi.h>
int main(void) {
    wiringPiSetupGpio();          // BCM 编号
    pinMode(17, OUTPUT);
    digitalWrite(17, HIGH);
    pinMode(18, PWM_OUTPUT);
    pwmWrite(18, 500);            // 占空比 0-1024
    return 0;
}
```

编译：`gcc -o myapp myapp.c -l wiringPi`

## 系统常用命令

```bash
vcgencmd measure_temp               # 温度
vcgencmd measure_clock arm          # CPU 频率
vcgencmd get_throttled              # 限频/低压标志
pinout                              # GPIO 引脚图
ip -br addr                         # 网络接口
df -h                               # 磁盘
free -h                             # 内存
```

## 硬件参数参考

详见 [`references/hardware.md`](references/hardware.md)。

各型号关键差异：

| 型号 | SoC | RAM | 最高频率 |
|:----|:----|:---:|:--------:|
| Pi 3B | BCM2837 (Cortex-A53) | 1GB | 1.2GHz |
| Pi 3B+ | BCM2837B0 (Cortex-A53) | 1GB | 1.4GHz |
| Pi 4B | BCM2711 (Cortex-A72) | 1-8GB | 1.8GHz |
| Pi 5 | BCM2712 (Cortex-A76) | 4-8GB | 2.4GHz |

## 注意事项

- 脚本依赖 `RPi.GPIO`：`pip3 install RPi.GPIO`
- 所有脚本默认 BCM 编号模式
- 接外设前确认引脚电压（3.3V vs 5V）
- 同一引脚不要同时被 RPi.GPIO 和 WiringPi 操作
