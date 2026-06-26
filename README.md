<div align="center">

<img src="logo.png" alt="raspberry-pi-skill logo" width="200">

# raspberry-pi-skill

树莓派智能体硬件操作技能包

<p>
  🇨🇳 中文 · <a href="README.en.md">🇬🇧 English</a>
</p>

给树莓派上运行的 AI Agent 使用的 GPIO 和硬件控制技能，覆盖设备语义控制、GPIO/PWM、蜂鸣器、引脚登记、系统监控与结构化 JSON 调用。

[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)

</div>

---

## 目录

- [项目定位](#项目定位)
- [适用型号](#适用型号)
- [文件结构](#文件结构)
- [依赖](#依赖)
- [安装](#安装)
- [快速开始](#快速开始)
- [内置脚本](#内置脚本)
- [设备注册表](#设备注册表)
- [引脚登记](#引脚登记)
- [Agent Schema](#agent-schema)
- [测试](#测试)
- [硬件参考](#硬件参考)
- [路线图](#路线图)
- [贡献](#贡献)
- [许可](#许可)

---

## 项目定位

`raspberry-pi-skill` 是面向 AI Agent 的树莓派硬件技能层。它不是完整物联网平台，而是为 `votx-agent` / `kemo-agent` 这类 Agent 提供可读、可执行、可结构化解析的硬件操作入口。

当前版本定位：

```text
Skill 描述 + CLI 脚本 + 设备语义层 + JSON 输出 + Schema + 测试 + 引脚/设备登记 + 硬件资料库
```

---

## 适用型号

所有 40-pin GPIO 的树莓派型号均可参考本项目的引脚资料，但 GPIO 运行后端有差异：

| 型号 | 处理器 | RAM | GPIO 后端建议 | 状态 |
|:----|:------|:---:|:-------------|:----:|
| Pi 1B+ | BCM2835 | 512 MB | RPi.GPIO | 可用 |
| Pi 2 / 2B | BCM2836/7 | 1 GB | RPi.GPIO | 可用 |
| Pi 3B / 3B+ | BCM2837 | 1 GB | RPi.GPIO | 推荐 |
| Pi 4B | BCM2711 | 1–8 GB | RPi.GPIO | 推荐 |
| Pi 5 | BCM2712 | 4–8 GB | rpi-lgpio / gpiozero / lgpio | 需切换后端 |
| Pi Zero W / Zero 2 W | BCM2835/2710 | 512 MB | RPi.GPIO | 可用 |

> Pi 5 的 GPIO 架构与旧型号不同，`RPi.GPIO` 原生模式不保证可用。Pi 5 请优先参考 [requirements-pi5.txt](requirements-pi5.txt)。
>
> Pi 1 早期 26-pin 型号不适用本项目的 40-pin 引脚表。

---

## 文件结构

```text
raspberry-pi-skill/
├── SKILL.md                        # 技能描述，Agent 入口读取
├── README.md                       # 中文文档
├── README.en.md                    # English documentation
├── logo.png                        # 项目 Logo
├── requirements.txt                # Pi 3/4 默认 Python 依赖
├── requirements-pi5.txt            # Pi 5 兼容依赖建议
├── requirements-dev.txt            # 测试依赖
├── devices/
│   ├── common.py                   # 设备注册、GPIO 懒加载、统一错误
│   ├── led.py                      # LED 语义动作
│   ├── buzzer.py                   # 蜂鸣器语义动作
│   ├── relay.py                    # 继电器语义动作，支持 active_low
│   └── button.py                   # 按钮读取
├── schemas/
│   ├── gpio_control.schema.json    # GPIO CLI 输入/输出协议
│   ├── pi_info.schema.json         # 系统信息 JSON 协议
│   └── device_control.schema.json  # 设备语义 CLI 协议
├── tests/
│   ├── test_gpio_control_cli.py    # GPIO CLI 最小回归测试
│   ├── test_pi_info_json.py        # 系统信息 JSON 结构测试
│   └── test_device_control_cli.py  # 设备语义层测试
├── config/
│   └── pins.example.json           # 引脚和设备登记示例
├── references/
│   ├── hardware.md                 # 全系列硬件参数对照表
│   └── pinout.md                   # 40-pin 完整引脚对照表
└── scripts/
    ├── device_control.py           # 设备语义控制脚本，推荐 Agent 优先使用
    ├── gpio_control.py             # GPIO 控制脚本，支持 JSON 输出
    └── pi_info.py                  # 系统状态监控脚本，支持 JSON 输出
```

`config/pins.json` 是本地运行时登记文件，已被 `.gitignore` 忽略。需要时从示例复制：

```bash
cp config/pins.example.json config/pins.json
```

---

## 依赖

### Python 包

Pi 3B / 3B+ / 4B 默认安装：

```bash
pip3 install -r requirements.txt
```

Pi 5 建议安装：

```bash
pip3 install -r requirements-pi5.txt
```

| 包 | 用途 | 适用场景 |
|:----|:----|:----|
| RPi.GPIO | GPIO 引脚读写控制 | Pi 1/2/3/4/Zero |
| rpi-lgpio | 提供 RPi.GPIO 兼容接口，底层使用 lgpio | Pi 5 推荐 |
| gpiozero | 高层 GPIO API，适合后续设备层 | Pi 5 / 通用 |

### 系统工具

Raspberry Pi OS 通常已预装：

| 命令 | 包 | 用途 |
|:----|:----|:----|
| `vcgencmd` | libraspberrypi-bin | CPU 温度 / 频率 / 电压 |
| `pinout` | raspberrypi-sys-mods | GPIO 引脚图 |
| `ip` / `df` / `free` | coreutils / iproute2 | 网络 / 磁盘 / 内存 |

### 硬件权限

用户需在 `gpio` 组才能访问 `/dev/gpiomem`。

```bash
groups
sudo usermod -aG gpio $USER
```

添加用户组后需要重新登录终端。

---

## 安装

推荐使用虚拟环境，避免 Raspberry Pi OS 新版的 `externally-managed-environment` 限制：

```bash
sudo apt update
sudo apt install -y python3-full python3-venv python3-pip libraspberrypi-bin python3-gpiozero

git clone https://github.com/kesepain-KE/raspberry-pi-skill.git
cd raspberry-pi-skill

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Pi 5 使用：

```bash
pip install -r requirements-pi5.txt
```

---

## 快速开始

### Agent 推荐：设备语义控制

```bash
cp config/pins.example.json config/pins.json

python3 scripts/device_control.py --list --json
python3 scripts/device_control.py --device bedroom_led --action on --json
python3 scripts/device_control.py --device bedroom_led --action blink --count 3 --interval 0.2 --json
python3 scripts/device_control.py --device buzzer --action beep --count 3 --json
python3 scripts/device_control.py --device relay_fan --action on --json
python3 scripts/device_control.py --device button_1 --action read --json
```

### 底层 GPIO 控制

```bash
python3 scripts/pi_info.py
python3 scripts/pi_info.py --json

python3 scripts/gpio_control.py --list
python3 scripts/gpio_control.py --status
python3 scripts/gpio_control.py --pin 17 --read
python3 scripts/gpio_control.py --pin 17 --write 1
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50
python3 scripts/gpio_control.py --pin 18 --beep 3
```

Agent 调 GPIO 层也应使用 JSON 输出：

```bash
python3 scripts/gpio_control.py --pin 17 --read --json
python3 scripts/gpio_control.py --pin 17 --write 1 --json
python3 scripts/gpio_control.py --status --json
```

---

## 内置脚本

### device_control.py

设备语义控制脚本。Agent 优先通过设备名和语义动作控制硬件，不必长期记 BCM 编号。

```bash
python3 scripts/device_control.py --list --json
python3 scripts/device_control.py --device bedroom_led --action on --json
python3 scripts/device_control.py --device bedroom_led --action off --json
python3 scripts/device_control.py --device bedroom_led --action blink --count 3 --interval 0.2 --json
python3 scripts/device_control.py --device buzzer --action beep --count 3 --json
python3 scripts/device_control.py --device relay_fan --action pulse --duration 1 --json
python3 scripts/device_control.py --device button_1 --action read --json
```

支持设备类型：

| 类型 | 动作 | 说明 |
|:----|:----|:----|
| led | on / off / toggle / blink | LED 输出 |
| buzzer | on / off / beep | 有源蜂鸣器输出 |
| relay | on / off / pulse | 继电器输出，支持低电平触发 |
| button | read | 按钮输入读取 |

继电器请正确设置 `active_high`。很多继电器模块是低电平触发，应配置为 `false`。

### gpio_control.py

GPIO 引脚控制，支持读取、写入、PWM 输出、蜂鸣器、引脚登记提示和 JSON 输出。

常用命令：

```bash
python3 scripts/gpio_control.py --list
python3 scripts/gpio_control.py --status
python3 scripts/gpio_control.py --pin 17 --read
python3 scripts/gpio_control.py --pin 17 --write 1
python3 scripts/gpio_control.py --pin 17 --write 1 --keep-state
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50 --duration 3
python3 scripts/gpio_control.py --pin 18 --beep 3 --interval 0.2
```

JSON 示例：

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

说明：

- 默认使用 BCM 编号。
- 默认操作后 cleanup，适合一次性测试。
- `--keep-state` 会跳过 cleanup，适合需要保持电平的场景。
- 引脚占用提示来自 `config/pins.json` 的登记记录，不是真正的系统级实时占用扫描。

### pi_info.py

系统信息一键采集，支持普通模式、JSON 输出、实时监控。

```bash
python3 scripts/pi_info.py
python3 scripts/pi_info.py --json
python3 scripts/pi_info.py --watch
```

输出内容：型号、系统、CPU 温度 / 频率 / 电压 / 限频标志、内存、磁盘、网络状态、GPIO 库版本。

---

## 设备注册表

`config/pins.json` 可以同时记录底层引脚占用和设备语义信息。设备层读取 `devices` 字段：

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

字段说明：

| 字段 | 说明 |
|:----|:----|
| type | led / buzzer / relay / button |
| bcm | BCM 引脚编号 |
| active_high | true 表示高电平触发，false 表示低电平触发 |
| pull | button 专用，up / down / none |
| description | 给 Agent 和用户看的说明 |

---

## 引脚登记

项目使用 `config/pins.json` 的 `pins` 字段记录用户实际接线，避免把占用信息写死在 Python 源码里。

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

查看登记：

```bash
python3 scripts/gpio_control.py --status
python3 scripts/gpio_control.py --status --json
```

---

## Agent Schema

项目提供 JSON Schema，帮助 Agent 理解 CLI 参数和 JSON 返回结构：

| 文件 | 内容 |
|:----|:----|
| [schemas/device_control.schema.json](schemas/device_control.schema.json) | `device_control.py` 的设备语义动作、参数、注册表和返回字段 |
| [schemas/gpio_control.schema.json](schemas/gpio_control.schema.json) | `gpio_control.py` 的动作、参数、CLI 映射、JSON 输出字段 |
| [schemas/pi_info.schema.json](schemas/pi_info.schema.json) | `pi_info.py` 的调用方式和系统信息 JSON 输出字段 |

Agent 推荐流程：

1. 先读取 `SKILL.md`
2. 再读取对应 `schemas/*.schema.json`
3. 优先使用 `scripts/device_control.py --json`
4. 解析返回中的 `ok`、`error`、`warning` 字段
5. 只有需要直接操作引脚时，再退到底层 `gpio_control.py`

---

## 测试

安装测试依赖：

```bash
pip install -r requirements-dev.txt
```

运行最小回归测试：

```bash
python -m py_compile scripts/gpio_control.py scripts/pi_info.py scripts/device_control.py devices/*.py
python -m pytest tests -q
```

当前测试覆盖：

- `gpio_control.py --list --json`
- `gpio_control.py --status --json`
- `gpio_control.py --pin 17 --json` 错误返回
- `gpio_control.py --pin 17 --read --json` 在有/无 GPIO 后端时的 JSON 行为
- `pi_info.py --json` 基础结构
- `device_control.py --list --json` 不依赖 GPIO
- 设备语义层缺少参数、未知设备、未知动作的 JSON 错误
- 无 GPIO 后端时的 JSON 错误
- fake GPIO 下的 LED、active_low 继电器、按钮读取行为

---

## 硬件参考

| 文件 | 内容 |
|:----|:----|
| [references/pinout.md](references/pinout.md) | 40-pin 完整引脚对照、PWM 通道、电源引脚 |
| [references/hardware.md](references/hardware.md) | Pi 1~5 + Zero 全系列 SoC / RAM / USB / 网络 / 功耗对照 |

---

## 路线图

- GPIO backend 抽象：RPi.GPIO / rpi-lgpio / gpiozero / lgpio
- 更丰富设备层：超声波、舵机、温湿度传感器
- 常驻 daemon：用于继电器、风扇、灯等需要保持状态的设备
- 设备状态持久化与远程硬件控制
- kemo-agent 感知层接入

---

## 贡献

欢迎提交 Issue 和 PR。大改动建议先开 Issue 讨论。

---

## 许可

项目基于 [MIT License](LICENSE) 开源。
