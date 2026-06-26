<div align="center">

<img src="logo.png" alt="raspberry-pi-skill logo" width="180">

# raspberry-pi-skill

A Raspberry Pi hardware skill pack for general-purpose AI Agents

<p>
  🇬🇧 English · <a href="README.md">🇨🇳 中文</a>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)

</div>

> Current version line: v0.3 Device Semantic Skill

## Introduction

`raspberry-pi-skill` is a Raspberry Pi hardware skill pack for general-purpose AI Agents. It splits hardware capabilities into four layers:

- `SKILL.md` helps an Agent understand the capability
- `schemas/*.schema.json` define parameters and return values
- `scripts/*.py` provide stable CLI tools and JSON output
- `references/` and `config/` provide hardware references and pin registry files

It is not an IoT platform, background service, automation system, remote bridge, or integration layer for any specific Agent framework.

## Core Features

- Semantic device control for LED, buzzer, relay, and button
- GPIO, PWM, read/write control
- `pi_info.py` for system status collection
- JSON output for reliable Agent parsing
- Device registry and pin registry
- 40-pin mapping and hardware reference tables
- Basic regression test coverage

## Compatibility

All Raspberry Pi models with a 40-pin GPIO header can use the project as a reference. Recommended runtime backends are listed below:

| Model | SoC | RAM | Recommended GPIO backend | Status |
|:--|:--|:--:|:--|:--:|
| Pi 1B+ | BCM2835 | 512 MB | RPi.GPIO | Works |
| Pi 2 / 2B | BCM2836/7 | 1 GB | RPi.GPIO | Works |
| Pi 3B / 3B+ | BCM2837 | 1 GB | RPi.GPIO | Recommended |
| Pi 4B | BCM2711 | 1–8 GB | RPi.GPIO | Recommended |
| Pi 5 | BCM2712 | 4–8 GB | rpi-lgpio / gpiozero / lgpio | Backend switch required |
| Pi Zero W / Zero 2 W | BCM2835/2710 | 512 MB | RPi.GPIO | Works |

> Raspberry Pi 5 changed the GPIO stack. Native `RPi.GPIO` mode is not guaranteed to work. For Pi 5, prefer [requirements-pi5.txt](requirements-pi5.txt).
>
> Early 26-pin Pi 1 boards are not covered by the 40-pin pinout table.

## File Structure

```text
raspberry-pi-skill/
├── SKILL.md                        # Skill entry point for Agents
├── README.md                       # Chinese documentation
├── README.en.md                    # English documentation
├── logo.png                        # Project logo
├── requirements.txt                # Default dependencies for Pi 3 / Pi 4
├── requirements-pi5.txt            # Pi 5 compatibility deps
├── requirements-dev.txt            # Test dependencies
├── config/
│   └── pins.example.json           # Example pin and device registry
├── devices/
│   ├── common.py                   # Device registry, lazy GPIO loading, unified errors
│   ├── led.py                      # LED semantic actions
│   ├── buzzer.py                   # Buzzer semantic actions
│   ├── relay.py                    # Relay semantic actions with active_low support
│   └── button.py                   # Button input reading
├── references/
│   ├── hardware.md                 # Hardware comparison table
│   └── pinout.md                   # Complete 40-pin mapping
├── schemas/
│   ├── gpio_control.schema.json    # GPIO CLI protocol
│   ├── pi_info.schema.json         # System info JSON protocol
│   └── device_control.schema.json  # Semantic device CLI protocol
├── scripts/
│   ├── device_control.py           # Semantic device control script
│   ├── gpio_control.py             # GPIO control script
│   └── pi_info.py                  # System info script
└── tests/
    ├── test_gpio_control_cli.py    # GPIO CLI regression tests
    ├── test_pi_info_json.py        # System info JSON tests
    └── test_device_control_cli.py  # Semantic device layer tests
```

`config/pins.json` is a local runtime file and is not committed to Git by default. Create it from the example when needed:

```bash
cp config/pins.example.json config/pins.json
```

## Dependencies

### Python Packages

Default install for Pi 3B, 3B+, and 4B:

```bash
pip3 install -r requirements.txt
```

Recommended install for Pi 5:

```bash
pip3 install -r requirements-pi5.txt
```

| Package | Purpose | Scenario |
|:--|:--|:--|
| RPi.GPIO | GPIO pin read/write control | Pi 1 / 2 / 3 / 4 / Zero |
| rpi-lgpio | RPi.GPIO-compatible interface backed by lgpio | Pi 5 recommended |
| gpiozero | High-level GPIO API for future device layers | Pi 5 or general use |

### System Tools

Raspberry Pi OS usually includes these tools:

| Command | Package | Purpose |
|:--|:--|:--|
| `vcgencmd` | libraspberrypi-bin | CPU temperature, frequency, and voltage |
| `pinout` | raspberrypi-sys-mods | GPIO pinout diagram |
| `ip`, `df`, `free` | coreutils, iproute2 | Network, disk, and memory |

### Hardware Permission

The user must be in the `gpio` group to access `/dev/gpiomem`:

```bash
groups
sudo usermod -aG gpio $USER
```

Re-login is required after changing groups.

## Installation

A virtual environment is recommended to avoid the Raspberry Pi OS `externally-managed-environment` restriction:

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

## Quick Start

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

## Recommended Flow for Agents

1. Read `SKILL.md` first
2. Read the matching `schemas/*.schema.json`
3. Prefer `scripts/device_control.py --json`
4. Use `scripts/gpio_control.py --json` only when direct pin control is needed
5. Use `scripts/pi_info.py --json` for system status
6. Always inspect `ok` first, then handle `error` and `warning`

## Script Reference

### device_control.py

Semantic device control script. Agents control hardware by device name and semantic action instead of memorizing BCM pin numbers.

```bash
python3 scripts/device_control.py --list --json
python3 scripts/device_control.py --device bedroom_led --action on --json
python3 scripts/device_control.py --device bedroom_led --action off --json
python3 scripts/device_control.py --device bedroom_led --action blink --count 3 --interval 0.2 --json
python3 scripts/device_control.py --device buzzer --action beep --count 3 --json
python3 scripts/device_control.py --device relay_fan --action pulse --duration 1 --json
python3 scripts/device_control.py --device button_1 --action read --json
```

Supported device types:

| Type | Actions | Description |
|:--|:--|:--|
| led | on / off / toggle / blink | LED output |
| buzzer | on / off / beep | Active buzzer output |
| relay | on / off / pulse | Relay output with active-low support |
| button | read | Button input reading |

Set `active_high` carefully for relays. Many relay modules are active-low.

### gpio_control.py

GPIO pin control with read, write, PWM output, buzzer beep, pin registry hints, and JSON output.

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

- BCM numbering is used by default
- Cleanup runs after operations by default, which is suitable for one-shot tests
- `--keep-state` skips cleanup, which is useful when a pin must hold its level
- Pin conflict hints come from `config/pins.json`; they are registry hints, not real-time system-level scans

### pi_info.py

One-command system information collection with human-readable, JSON, and watch modes.

```bash
python3 scripts/pi_info.py
python3 scripts/pi_info.py --json
python3 scripts/pi_info.py --watch
```

Output includes model, OS, CPU temperature, frequency, voltage, throttling flags, memory, disk, network status, and GPIO library version.

## Configuration

`config/pins.example.json` provides two local registry types:

- `devices`: semantic device registry
- `pins`: actual wiring registry

Common fields:

| Field | Description |
|:--|:--|
| `type` | Device type, supports `led`, `buzzer`, `relay`, `button` |
| `bcm` | BCM pin number |
| `physical` | Physical pin number |
| `active_high` | Output polarity, especially important for relays |
| `pull` | Button input pull-up, pull-down, or none |
| `description` | Human-readable note for Agents and users |

`config/pins.json` is only for local runtime use and wiring notes, and is not committed by default.

## Testing

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the minimal regression suite:

```bash
python -m py_compile scripts/gpio_control.py scripts/pi_info.py scripts/device_control.py devices/*.py
python -m pytest tests -q
```

Current test coverage:

- `gpio_control.py --list --json`
- `gpio_control.py --status --json`
- Error output for `gpio_control.py --pin 17 --json`
- JSON behavior for `gpio_control.py --pin 17 --read --json` with or without GPIO backend
- Basic structure for `pi_info.py --json`
- `device_control.py --list --json` behavior without GPIO backend
- Missing-argument, unknown-device, and unknown-action errors for the semantic layer
- LED, active-low relay, and button behavior under fake GPIO

## Hardware Reference

| File | Content |
|:--|:--|
| [references/pinout.md](references/pinout.md) | Complete 40-pin mapping, PWM channels, power pins |
| [references/hardware.md](references/hardware.md) | SoC, RAM, USB, network, and power comparison for Pi 1 to Pi 5 and Zero |

## Project Scope

This project only provides a general-purpose hardware skill pack and does not expand into a platform. The following are out of scope:

- daemon
- state persistence
- systemd service
- MQTT
- Web API
- remote control
- rule engine
- automation tasks
- specific Agent framework adapters

## Contributing

Issues and PRs are welcome. Please open an issue before major changes.

## License

This project is licensed under the [MIT License](LICENSE).
