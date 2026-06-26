
## 依赖

### Python 包

```bash
pip3 install -r requirements.txt
```

| 包 | 用途 | 必需 |
|:----|:----|:----:|
| RPi.GPIO | GPIO 引脚读写 | 是 |

### 系统工具（Raspberry Pi OS 预装）

| 命令 | 用途 |
|:----|:----|
| vcgencmd | CPU 温度/频率/电压（libraspberrypi-bin） |
| ip / df / free / cat | 网络/磁盘/内存信息 |

### 硬件权限

用户需在 `gpio` 组以访问 `/dev/gpiomem`（Raspberry Pi OS 默认已添加）。

### 可选

| 依赖 | 用途 |
|:----|:----|
| wiringpi (C 库 + gpio 命令行) | SKILL.md WiringPi 章节参考用，脚本不依赖 |

---
# raspberry-pi-skill

树莓派智能体硬件操作技能包。给树莓派上运行的 AI Agent 用的 GPIO 和硬件控制技能。

## 适用型号

所有 40-pin 树莓派型号：Pi 1B+ / 2 / 3 / 3B+ / 4 / 5 / Zero W / Zero 2 W

## 文件结构

```
raspberry-pi-skill/
├── SKILL.md                      # 技能主描述（Agent 读取入口）
├── README.md                     # 本文件（中文）
├── README.en.md                  # English version
├── references/
│   ├── hardware.md               # Pi 1~5 + Zero 全系列硬件参数对照
│   └── pinout.md                 # 40-pin 完整引脚对照表
└── scripts/
    ├── gpio_control.py           # GPIO 控制脚本
    └── pi_info.py                # 系统状态监控脚本
```

## 内置脚本

### gpio_control.py

GPIO 引脚控制，支持读取、写入、PWM、蜂鸣器、引脚冲突检测。

```bash
python3 scripts/gpio_control.py --list              # 引脚对照表
python3 scripts/gpio_control.py --status            # 已用引脚
python3 scripts/gpio_control.py --pin 17 --read     # 读取引脚
python3 scripts/gpio_control.py --pin 17 --write 1  # 写高电平
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50  # PWM
python3 scripts/gpio_control.py --pin 18 --beep 3   # 蜂鸣器
```

### pi_info.py

系统状态一键采集，CPU 温度/频率/电压、内存、磁盘、网络。

```bash
python3 scripts/pi_info.py            # 人类可读面板
python3 scripts/pi_info.py --json     # JSON 输出
python3 scripts/pi_info.py --watch    # 实时刷新
```

## 快速开始

1. 将本技能目录放入 Agent 的 `skills/` 下
2. 在树莓派上安装依赖：`pip3 install RPi.GPIO`
   （如需 WiringPi C API：`sudo apt install wiringpi`）
3. 查看系统状态：`python3 scripts/pi_info.py`
4. 开始操作 GPIO

GPIO 引脚图详见 [references/pinout.md](references/pinout.md)，硬件参数详见 [references/hardware.md](references/hardware.md)。

## License

MIT
