<div align="center">

# raspberry-pi-skill

A Raspberry Pi hardware control skill pack for AI Agents

Covers GPIO pin control, PWM, sensor wiring, and system monitoring for Agents running on the Pi.

[![GitHub](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![RPi.GPIO](https://img.shields.io/badge/dep-RPi.GPIO-blue)](requirements.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange)](https://github.com/kesepain-KE/raspberry-pi-skill/pulls)

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

Pi 1B+ / 2 / 3 / 3B+ / 4 / 5 / Zero W / Zero 2 W

> Early Pi 1 models (26-pin) are not compatible. Hardware reference covers Pi 1 ~ 5 and Zero series.

---

## File Structure

```
raspberry-pi-skill/
├── SKILL.md                        # Skill descriptor (Agent entry point)
├── README.md                       # Chinese documentation
├── README.en.md                    # This file
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
groups                          # Check if in gpio group
sudo usermod -aG gpio $USER    # Add if missing (re-login required)
```

### Optional

| Dependency | Purpose |
|:-----------|:--------|
| wiringpi (C lib + gpio CLI) | Reference only in SKILL.md WiringPi section, not used by scripts |

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
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50  # PWM
python3 scripts/gpio_control.py --pin 18 --beep 3   # Buzzer 3 beeps
```

Built-in **pin conflict detection** warns when operating an occupied pin.

### pi_info.py

One-command system info with human-readable, JSON, and live monitoring modes.

```bash
python3 scripts/pi_info.py            # Dashboard mode
python3 scripts/pi_info.py --json     # JSON output
python3 scripts/pi_info.py --watch    # Live refresh (2s, Ctrl+C to quit)
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

MIT
