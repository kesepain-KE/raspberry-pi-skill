<div align="center">

<img src="logo.png" alt="raspberry-pi-skill logo" width="180">

# raspberry-pi-skill

面向通用 AI Agent 的树莓派硬件技能包

<p>
  🇨🇳 中文 · <a href="README.en.md">🇬🇧 English</a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)

</div>

> 当前版本线：v0.3 Device Semantic Skill

## 简介

`raspberry-pi-skill` 是一个面向通用 AI Agent 的树莓派硬件技能包。它把硬件能力拆成四层：

- `SKILL.md` 让 Agent 读懂能力
- `schemas/*.schema.json` 说明参数和返回值
- `scripts/*.py` 提供稳定 CLI 和 JSON 输出
- `references/` 与 `config/` 提供硬件参考和引脚登记

它不是 IoT 平台、后台服务、自动化系统、远程桥接，也不绑定任何特定智能体框架。

## 核心能力

- 设备语义控制：LED、蜂鸣器、继电器、按钮
- GPIO、PWM、读写控制
- `pi_info.py` 系统状态采集
- JSON 输出，方便 Agent 稳定解析
- 设备注册表和引脚登记表
- 40-pin 引脚和硬件参数参考
- 基础测试覆盖

## 适用范围

所有带 40-pin GPIO 排针的树莓派型号都可以参考本项目。运行后端建议如下：

| 型号 | SoC | RAM | 推荐 GPIO 后端 | 状态 |
|:--|:--|:--:|:--|:--:|
| Pi 1B+ | BCM2835 | 512 MB | RPi.GPIO | 可用 |
| Pi 2 / 2B | BCM2836/7 | 1 GB | RPi.GPIO | 可用 |
| Pi 3B / 3B+ | BCM2837 | 1 GB | RPi.GPIO | 推荐 |
| Pi 4B | BCM2711 | 1–8 GB | RPi.GPIO | 推荐 |
| Pi 5 | BCM2712 | 4–8 GB | rpi-lgpio / gpiozero / lgpio | 需切换后端 |
| Pi Zero W / Zero 2 W | BCM2835/2710 | 512 MB | RPi.GPIO | 可用 |

> Pi 5 的 GPIO 架构和旧型号不同，`RPi.GPIO` 原生模式不保证可用。Pi 5 请优先使用 [requirements-pi5.txt](requirements-pi5.txt)。
>
> 早期 26-pin 的 Pi 1 不适用本项目的 40-pin 引脚表。

## 目录结构

```text
raspberry-pi-skill/
├── SKILL.md                        # 技能入口，Agent 先读这里
├── README.md                       # 中文说明
├── README.en.md                    # English 说明
├── logo.png                        # 项目 Logo
├── requirements.txt                # Pi 3 / Pi 4 默认依赖
├── requirements-pi5.txt            # Pi 5 兼容依赖
├── requirements-dev.txt            # 测试依赖
├── config/
│   └── pins.example.json           # 引脚和设备登记示例
├── devices/
│   ├── common.py                   # 设备注册、GPIO 懒加载、统一错误
│   ├── led.py                      # LED 语义动作
│   ├── buzzer.py                   # 蜂鸣器语义动作
│   ├── relay.py                    # 继电器语义动作，支持 active_low
│   └── button.py                   # 按钮读取
├── references/
│   ├── hardware.md                 # 硬件参数对照
│   └── pinout.md                   # 40-pin 引脚对照
├── schemas/
│   ├── gpio_control.schema.json    # GPIO CLI 协议
│   ├── pi_info.schema.json         # 系统信息 JSON 协议
│   └── device_control.schema.json  # 设备语义 CLI 协议
├── scripts/
│   ├── device_control.py           # 设备语义控制脚本
│   ├── gpio_control.py             # GPIO 控制脚本
│   └── pi_info.py                  # 系统信息脚本
└── tests/
    ├── test_gpio_control_cli.py    # GPIO CLI 回归测试
    ├── test_pi_info_json.py        # 系统信息 JSON 测试
    └── test_device_control_cli.py  # 设备语义层测试
```

`config/pins.json` 是本地运行时文件，默认不提交到 Git。需要时从示例复制：

```bash
cp config/pins.example.json config/pins.json
```

## 依赖

### Python 包

Pi 3B、3B+、4B 默认安装：

```bash
pip3 install -r requirements.txt
```

Pi 5 建议安装：

```bash
pip3 install -r requirements-pi5.txt
```

| 包 | 用途 | 适用场景 |
|:--|:--|:--|
| RPi.GPIO | GPIO 引脚读写控制 | Pi 1 / 2 / 3 / 4 / Zero |
| rpi-lgpio | 提供 RPi.GPIO 兼容接口，底层使用 lgpio | Pi 5 推荐 |
| gpiozero | 高层 GPIO API，适合后续设备层 | Pi 5 或通用场景 |

### 系统工具

Raspberry Pi OS 通常已预装：

| 命令 | 包 | 用途 |
|:--|:--|:--|
| `vcgencmd` | libraspberrypi-bin | CPU 温度、频率、电压 |
| `pinout` | raspberrypi-sys-mods | GPIO 引脚图 |
| `ip`、`df`、`free` | coreutils、iproute2 | 网络、磁盘、内存 |

### 硬件权限

用户需要在 `gpio` 组中才能访问 `/dev/gpiomem`：

```bash
groups
sudo usermod -aG gpio $USER
```

改完组后需要重新登录终端。

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

## 快速开始

```bash
cp config/pins.example.json config/pins.json

python3 scripts/device_control.py --list --json
python3 scripts/device_control.py --device bedroom_led --action on --json
python3 scripts/device_control.py --device buzzer --action beep --count 3 --json
python3 scripts/device_control.py --device relay_fan --action pulse --duration 1 --json
python3 scripts/device_control.py --device button_1 --action read --json

python3 scripts/gpio_control.py --status --json
python3 scripts/gpio_control.py --pin 17 --read --json
python3 scripts/pi_info.py --json
```

## 给 Agent 的推荐流程

1. 先读 `SKILL.md`
2. 再读对应的 `schemas/*.schema.json`
3. 优先使用 `scripts/device_control.py --json`
4. 直接操作引脚时再用 `scripts/gpio_control.py --json`
5. 系统状态用 `scripts/pi_info.py --json`
6. 统一先看返回里的 `ok`，再处理 `error` 和 `warning`

## 脚本说明

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
|:--|:--|:--|
| led | on / off / toggle / blink | LED 输出 |
| buzzer | on / off / beep | 有源蜂鸣器输出 |
| relay | on / off / pulse | 继电器输出，支持 active_low |
| button | read | 按钮输入读取 |

继电器请正确设置 `active_high`，很多继电器模块是低电平触发。

### gpio_control.py

GPIO 引脚控制，支持读取、写入、PWM 输出、蜂鸣器、引脚登记提示和 JSON 输出。

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

- 默认使用 BCM 编号
- 默认操作后会 cleanup，适合一次性测试
- `--keep-state` 会跳过 cleanup，适合需要保持电平的场景
- 引脚占用提示来自 `config/pins.json` 的登记记录，不是真正的系统级实时占用扫描

### pi_info.py

系统信息一键采集，支持普通模式、JSON 输出、实时监控。

```bash
python3 scripts/pi_info.py
python3 scripts/pi_info.py --json
python3 scripts/pi_info.py --watch
```

输出内容包括型号、系统、CPU 温度、频率、电压、限频标志、内存、磁盘、网络状态和 GPIO 库版本。

## 配置

`config/pins.example.json` 提供了两类本地登记：

- `devices`：设备语义注册表
- `pins`：实际接线登记表

常用字段：

| 字段 | 说明 |
|:--|:--|
| `type` | 设备类型，支持 `led`、`buzzer`、`relay`、`button` |
| `bcm` | BCM 引脚编号 |
| `physical` | 物理引脚编号 |
| `active_high` | 输出极性，继电器尤其重要 |
| `pull` | 按钮输入上拉、下拉或无 |
| `description` | 给 Agent 和用户看的说明 |

`config/pins.json` 只用于本地运行和接线记录，默认不提交。

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
- `gpio_control.py --pin 17 --json` 的错误返回
- `gpio_control.py --pin 17 --read --json` 在有无 GPIO 后端时的 JSON 行为
- `pi_info.py --json` 的基础结构
- `device_control.py --list --json` 在无 GPIO 后端时的行为
- 设备语义层的缺参、未知设备、未知动作错误
- fake GPIO 下的 LED、active_low 继电器和按钮读取行为

## 硬件参考

| 文件 | 内容 |
|:--|:--|
| [references/pinout.md](references/pinout.md) | 40-pin 完整引脚对照、PWM 通道、电源引脚 |
| [references/hardware.md](references/hardware.md) | Pi 1 到 Pi 5 与 Zero 的 SoC、RAM、USB、网络、功耗对照 |

## 项目边界

本项目只做通用硬件技能包，不向平台化扩展。以下内容不纳入边界：

- daemon
- 状态持久化
- systemd 服务
- MQTT
- Web API
- 远程控制
- 规则引擎
- 自动化任务
- 特定 Agent 框架适配

## 贡献

欢迎提交 Issue 和 PR。大改动建议先开 Issue 讨论。

## 许可

项目基于 [MIT License](LICENSE) 开源。
