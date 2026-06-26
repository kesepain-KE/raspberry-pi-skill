<div align="center">

<img src="logo.png" alt="raspberry-pi-skill logo" width="200">

# raspberry-pi-skill

A Raspberry Pi hardware control skill pack for AI Agents

<p>
  🇬🇧 English · <a href="README.md">🇨🇳 中文</a>
</p>

GPIO, PWM, buzzer control, pin registry, system monitoring, and JSON-friendly calls for Agents running on Raspberry Pi.

[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)

</div>

---

## Table of Contents

- [Project Scope](#project-scope)
- [Compatible Models](#compatible-models)
- [File Structure](#file-structure)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Built-in Scripts](#built-in-scripts)
- [Pin Registry](#pin-registry)
- [Hardware Reference](#hardware-reference)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Project Scope

`raspberry-pi-skill` is a Raspberry Pi hardware skill layer for AI Agents. It is not a full IoT platform; it provides readable, executable, and structured hardware operation entries for Agent systems such as `votx-agent` and `kemo-agent`.

Current scope:

```text
Skill descriptor + CLI scripts + JSON output + pin registry + hardware references
```

---

## Compatible Models

All Raspberry Pi models with a **40-pin GPIO** header can use the pin references, but runtime GPIO backends differ by board:

| Model | SoC | RAM | Recommended GPIO backend | Status |
|:------|:----|:---:|:-------------------------|:------:|
| Pi 1B+ | BCM2835 | 512 MB | RPi.GPIO | Works |
| Pi 2 / 2B | BCM2836/7 | 1 GB | RPi.GPIO | Works |
| Pi 3B / 3B+ | BCM2837 | 1 GB | RPi.GPIO | Recommended |
| Pi 4B | BCM2711 | 1–8 GB | RPi.GPIO | Recommended |
| Pi 5 | BCM2712 | 4–8 GB | rpi-lgpio / gpiozero / lgpio | Backend switch required |
| Pi Zero W / Zero 2 W | BCM2835/2710 | 512 MB | RPi.GPIO | Works |

> Raspberry Pi 5 changed the GPIO stack. Native `RPi.GPIO` mode is not guaranteed to work. For Pi 5, prefer [requirements-pi5.txt](requirements-pi5.txt).
>
> Early 26-pin Pi 1 boards are not covered by the 40-pin pinout table.

---

## File Structure

```text
raspberry-pi-skill/
├── SKILL.md                        # Skill descriptor, Agent entry point
├── README.md                       # Chinese documentation
├── README.en.md                    # This file
├── logo.png                        # Project logo
├── requirements.txt                # Default Python deps for Pi 3/4
├── requirements-pi5.txt            # Pi 5 compatibility deps
├── config/
│   └── pins.example.json           # Example pin registry
├── references/
│   ├── hardware.md                 # Hardware specs comparison
│   └── pinout.md                   # Complete 40-pin GPIO reference
└── scripts/
    ├── gpio_control.py             # GPIO control with JSON output
    └── pi_info.py                  # System monitoring with JSON output
```

`config/pins.json` is a local runtime registry and is ignored by `.gitignore`. Create it from the example when needed:

```bash
cp config/pins.example.json config/pins.json
```

---

## Dependencies

### Python Packages

Default install for Pi 3B / 3B+ / 4B:

```bash
pip3 install -r requirements.txt
```

Recommended install for Pi 5:

```bash
pip3 install -r requirements-pi5.txt
```

| Package | Purpose | Scenario |
|:--------|:--------|:---------|
| RPi.GPIO | GPIO pin control | Pi 1/2/3/4/Zero |
| rpi-lgpio | RPi.GPIO-compatible interface backed by lgpio | Pi 5 recommended |
| gpiozero | High-level GPIO API for future device layer | Pi 5 / general |

### System Tools

Usually pre-installed on Raspberry Pi OS:

| Command | Package | Purpose |
|:--------|:--------|:--------|
| `vcgencmd` | libraspberrypi-bin | CPU temp / freq / voltage |
| `pinout` | raspberrypi-sys-mods | GPIO pinout diagram |
| `ip` / `df` / `free` | coreutils / iproute2 | Network / disk / memory |

### Hardware Permission

User must be in the `gpio` group to access `/dev/gpiomem`.

```bash
groups
sudo usermod -aG gpio $USER
```

Re-login is required after changing groups.

---

## Installation

A virtual environment is recommended to avoid Raspberry Pi OS `externally-managed-environment` restrictions:

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

For Pi 5:

```bash
pip install -r requirements-pi5.txt
```

---

## Quick Start

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

For Agents, use JSON output:

```bash
python3 scripts/gpio_control.py --pin 17 --read --json
python3 scripts/gpio_control.py --pin 17 --write 1 --json
python3 scripts/gpio_control.py --status --json
```

---

## Built-in Scripts

### gpio_control.py

GPIO control with read, write, PWM output, buzzer beep, pin registry warning, and JSON output.

Common commands:

```bash
python3 scripts/gpio_control.py --list
python3 scripts/gpio_control.py --status
python3 scripts/gpio_control.py --pin 17 --read
python3 scripts/gpio_control.py --pin 17 --write 1
python3 scripts/gpio_control.py --pin 17 --write 1 --keep-state
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50 --duration 3
python3 scripts/gpio_control.py --pin 18 --beep 3 --interval 0.2
```

JSON example:

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

Notes:

- BCM numbering is used by default.
- Cleanup is enabled after operations by default, suitable for one-shot tests.
- `--keep-state` skips cleanup, useful when a pin needs to keep its level.
- Pin conflict warnings come from `config/pins.json`; they are registry hints, not real-time system-level pin scans.

### pi_info.py

One-command system information collection with human-readable, JSON, and watch modes.

```bash
python3 scripts/pi_info.py
python3 scripts/pi_info.py --json
python3 scripts/pi_info.py --watch
```

Output: model, OS, CPU temp / freq / voltage / throttling, memory, disk, network, GPIO library version.

---

## Pin Registry

The project uses `config/pins.json` to record actual wiring, instead of hard-coding occupied pins in Python source.

Create local registry:

```bash
cp config/pins.example.json config/pins.json
```

Example:

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
      "notes": "buzzer IO"
    }
  }
}
```

View registry:

```bash
python3 scripts/gpio_control.py --status
python3 scripts/gpio_control.py --status --json
```

---

## Hardware Reference

| File | Content |
|:----|:--------|
| [references/pinout.md](references/pinout.md) | Complete 40-pin mapping, PWM channels, power pins |
| [references/hardware.md](references/hardware.md) | Pi 1~5 + Zero SoC / RAM / USB / network / power comparison |

---

## Roadmap

- GPIO backend abstraction: RPi.GPIO / rpi-lgpio / gpiozero / lgpio
- Device layer: LED, buzzer, relay, button, ultrasonic, servo, DHT sensor
- Long-running daemon for devices that must hold state, such as relays, fans, and lights
- More complete error codes and tests

---

## Contributing

Issues and PRs are welcome. Please open an issue before major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).
