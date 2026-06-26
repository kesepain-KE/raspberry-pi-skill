<div align="center">

<img src="logo.png" alt="raspberry-pi-skill logo" width="200">

# raspberry-pi-skill

A Raspberry Pi hardware control skill pack for AI Agents

Covers GPIO pin control, PWM, sensor wiring, and system monitoring for Agents running on the Pi.

[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)

</div>

---

## Table of Contents

- [Compatible Models](#compatible-models)
- [File Structure](#file-structure)
- [Dependencies](#dependencies)
- [Quick Start](#quick-start)
- [Built-in Scripts](#built-in-scripts)
- [Hardware Reference](#hardware-reference)
- [Contributing](#contributing)
- [License](#license)

---

## Compatible Models

All models with **40-pin GPIO** header:

| Model | SoC | RAM |
|:------|:----|:---:|
| Pi 1B+ | BCM2835 | 512 MB |
| Pi 2 / 2B | BCM2836/7 | 1 GB |
| Pi 3B / 3B+ | BCM2837 | 1 GB |
| Pi 4B | BCM2711 | 1–8 GB |
| Pi 5 | BCM2712 | 4–8 GB |
| Pi Zero W / Zero 2 W | BCM2835/2710 | 512 MB |

> Early Pi 1 models (26-pin) are not compatible. Full hardware specs in `references/hardware.md`.

---

## File Structure

```
raspberry-pi-skill/
├── SKILL.md                        # Skill descriptor (Agent entry point)
├── README.md                       # Chinese documentation
├── README.en.md                    # This file
├── logo.png                        # Project logo
├── requirements.txt                # Python dependencies
├── references/
│   ├── hardware.md                 # Full hardware specs comparison
│   └── pinout.md                   # Complete 40-pin GPIO reference
└── scripts/
    ├── gpio_control.py             # GPIO control script
    └── pi_info.py                  # System monitoring script
```

---

## Dependencies

### Python Packages

```bash
pip3 install -r requirements.txt
```

| Package | Purpose | Required |
|:--------|:--------|:--------:|
| RPi.GPIO | GPIO pin control | Yes |

> Full list in [requirements.txt](requirements.txt).

### System Tools

Pre-installed on Raspberry Pi OS:

| Command | Package | Purpose |
|:--------|:--------|:--------|
| `vcgencmd` | libraspberrypi-bin | CPU temp / freq / voltage |
| `pinout` | raspberrypi-sys-mods | GPIO pinout diagram |
| `ip` / `df` / `free` | coreutils | Network / disk / memory |

### Hardware Permission

User must be in the `gpio` group to access `/dev/gpiomem` (default on Raspberry Pi OS).

```bash
groups                             # Check if in gpio group
sudo usermod -aG gpio $USER       # Add if missing (re-login required)
```

### Optional

| Dependency | Purpose |
|:-----------|:--------|
| wiringpi (C lib + `gpio` CLI) | Reference only in SKILL.md WiringPi section, not used by scripts |

---

## Quick Start

```bash
# 1. Copy skill to your Agent's skills/ directory
cp -r raspberry-pi-skill /path/to/agent/skills/raspberry-pi

# 2. Install Python dependency
pip3 install RPi.GPIO

# 3. Check system status
python3 scripts/pi_info.py

# 4. Start controlling GPIO
python3 scripts/gpio_control.py --list
python3 scripts/gpio_control.py --pin 17 --read
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50
```

---

## Built-in Scripts

### gpio_control.py

GPIO pin control with read, write, PWM, buzzer, and conflict detection.

```bash
python3 scripts/gpio_control.py --list              # Pin mapping table
python3 scripts/gpio_control.py --status            # Occupied pins
python3 scripts/gpio_control.py --pin 17 --read     # Read pin state
python3 scripts/gpio_control.py --pin 17 --write 1  # Write HIGH
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50  # PWM output
python3 scripts/gpio_control.py --pin 18 --beep 3   # Buzzer 3 beeps
```

> Built-in pin conflict detection warns when operating an occupied pin.

### pi_info.py

One-command system info with three output modes:

```bash
python3 scripts/pi_info.py            # Dashboard mode (human-readable)
python3 scripts/pi_info.py --json     # JSON output (for programmatic use)
python3 scripts/pi_info.py --watch    # Live refresh (2s interval, Ctrl+C to quit)
```

Output: CPU temp / freq / voltage / throttling, memory, disk, network, GPIO library version.

---

## Hardware Reference

See `references/` for detailed specs:

| File | Content |
|:----|:--------|
| [references/pinout.md](references/pinout.md) | Complete 40-pin mapping, PWM channels, power pins |
| [references/hardware.md](references/hardware.md) | Pi 1~5 + Zero SoC / RAM / USB / network / power comparison |

---

## Contributing

Issues and PRs are welcome! Open an issue for discussion before major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).
