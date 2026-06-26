<div align="center">

# raspberry-pi-skill

树莓派智能体硬件操作技能包

给树莓派上运行的 AI Agent 使用的 GPIO 和硬件控制技能，覆盖引脚读写、PWM、传感器接线、系统监控。

[![GitHub](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange)](https://github.com/kesepain-KE/raspberry-pi-skill/pulls)

</div>

---

## 目录

- [适用型号](#适用型号)
- [文件结构](#文件结构)
- [依赖](#依赖)
- [快速开始](#快速开始)
- [内置脚本](#内置脚本)
- [硬件参考](#硬件参考)
- [贡献](#贡献)
- [许可](#许可)

---

## 适用型号

所有 **40-pin GPIO** 的树莓派型号：

Pi 1B+ / 2 / 3 / 3B+ / 4 / 5 / Zero W / Zero 2 W

> Pi 1 早期 26-pin 型号不适用。硬件参数表覆盖 Pi 1 ~ 5 + Zero 全系列。

---

## 文件结构

```
raspberry-pi-skill/
├── SKILL.md                        # 技能描述（Agent 入口读取）
├── README.md                       # 本文件
├── README.en.md                    # English version
├── requirements.txt                # Python 依赖
├── references/
│   ├── hardware.md                 # 全系列硬件参数对照表
│   └── pinout.md                   # 40-pin 完整引脚对照表
└── scripts/
    ├── gpio_control.py             # GPIO 控制脚本
    └── pi_info.py                  # 系统状态监控脚本
```

---

## 依赖

### Python 包

```bash
pip3 install -r requirements.txt
```

| 包 | 用途 | 必需 |
|:----|:----|:----:|
| RPi.GPIO | GPIO 引脚读写控制 | 是 |

### 系统工具

Raspberry Pi OS 预装，无需额外安装：

| 命令 | 包 | 用途 |
|:----|:----|:----|
| `vcgencmd` | libraspberrypi-bin | CPU 温度 / 频率 / 电压 |
| `pinout` | raspberrypi-sys-mods | GPIO 引脚图 |
| `ip` / `df` / `free` | coreutils | 网络 / 磁盘 / 内存 |

### 硬件权限

用户需在 `gpio` 组以访问 `/dev/gpiomem`（Raspberry Pi OS 默认已添加）。

```bash
groups           # 确认是否在 gpio 组
sudo usermod -aG gpio $USER   # 若不在则添加（需重登录）
```

### 可选

| 依赖 | 用途 |
|:----|:----|
| wiringpi（C 库 + gpio 命令） | SKILL.md WiringPi 章节参考，脚本不依赖 |

---

## 快速开始

```bash
# 1. 将本技能放入 Agent 的 skills/ 目录
cp -r raspberry-pi-skill /path/to/agent/skills/raspberry-pi

# 2. 安装 Python 依赖
pip3 install RPi.GPIO

# 3. 查看系统状态
python3 scripts/pi_info.py

# 4. 开始操作 GPIO
python3 scripts/gpio_control.py --list
python3 scripts/gpio_control.py --pin 17 --read
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50
```

---

## 内置脚本

### gpio_control.py

GPIO 引脚控制，支持读取、写入、PWM 输出、蜂鸣器、引脚冲突检测。

```bash
python3 scripts/gpio_control.py --list              # 引脚对照表
python3 scripts/gpio_control.py --status            # 已用引脚
python3 scripts/gpio_control.py --pin 17 --read     # 读取高/低电平
python3 scripts/gpio_control.py --pin 17 --write 1  # 写高电平
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50  # PWM
python3 scripts/gpio_control.py --pin 18 --beep 3   # 蜂鸣器响 3 次
```

脚本内置 **引脚占用检测**，操作已被占用的引脚时会自动警告。

### pi_info.py

系统信息一键采集，支持普通模式、JSON 输出、实时监控。

```bash
python3 scripts/pi_info.py            # 面板模式
python3 scripts/pi_info.py --json     # JSON 输出（供其他程序调用）
python3 scripts/pi_info.py --watch    # 每 2 秒刷新（Ctrl+C 退出）
```

输出内容：CPU 温度 / 频率 / 电压 / 限频标志、内存、磁盘、网络状态、GPIO 库版本。

---

## 硬件参考

详细参数见 `references/` 目录：

| 文件 | 内容 |
|:----|:----|
| [references/pinout.md](references/pinout.md) | 40-pin 完整引脚对照、PWM 通道、电源引脚 |
| [references/hardware.md](references/hardware.md) | Pi 1~5 + Zero 全系列 SoC / RAM / USB / 网络 / 功耗对照 |

---

## 贡献

欢迎提交 Issue 和 PR！建议请直接开 Issue 讨论。

---

## 许可

MIT License
