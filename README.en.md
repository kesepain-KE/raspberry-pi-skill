
## Dependencies

### Python Packages

```bash
pip3 install -r requirements.txt
```

| Package | Purpose | Required |
|:--------|:--------|:--------:|
| RPi.GPIO | GPIO pin control | Yes |

### System Tools (Pre-installed on Raspberry Pi OS)

| Command | Purpose |
|:--------|:--------|
| vcgencmd | CPU temp/freq/voltage (libraspberrypi-bin) |
| ip / df / free / cat | Network/disk/memory info |

### Hardware Permission

User must be in the `gpio` group to access `/dev/gpiomem` (default on Raspberry Pi OS).

### Optional

| Dependency | Purpose |
|:-----------|:--------|
| wiringpi (C lib + gpio CLI) | Reference only in SKILL.md WiringPi section, not used by scripts |

---
# raspberry-pi-skill

A Raspberry Pi hardware control skill pack for AI Agents running on the Pi. Covers GPIO control, system monitoring, and hardware reference.

## Compatible Models

All 40-pin Raspberry Pi models: Pi 1B+ / 2 / 3 / 3B+ / 4 / 5 / Zero W / Zero 2 W

## File Structure

```
raspberry-pi-skill/
├── SKILL.md                      # Skill descriptor (entry point for Agent)
├── README.md                     # Chinese documentation
├── README.en.md                  # This file
├── references/
│   ├── hardware.md               # Pi 1~5 + Zero full hardware specs
│   └── pinout.md                 # Complete 40-pin GPIO reference
└── scripts/
    ├── gpio_control.py           # GPIO control script
    └── pi_info.py                # System monitoring script
```

## Built-in Scripts

### gpio_control.py

GPIO pin control with read, write, PWM, buzzer, and conflict detection.

```bash
python3 scripts/gpio_control.py --list              # Pin mapping table
python3 scripts/gpio_control.py --status            # Occupied pins
python3 scripts/gpio_control.py --pin 17 --read     # Read pin state
python3 scripts/gpio_control.py --pin 17 --write 1  # Write HIGH
python3 scripts/gpio_control.py --pin 18 --pwm 1000 50  # PWM output
python3 scripts/gpio_control.py --pin 18 --beep 3   # Buzzer beep
```

### pi_info.py

One-command system info: CPU temp/freq/voltage, memory, disk, network.

```bash
python3 scripts/pi_info.py            # Human-readable dashboard
python3 scripts/pi_info.py --json     # JSON output
python3 scripts/pi_info.py --watch    # Live refresh (2s interval)
```

## Quick Start

1. Put this skill directory into your Agent's `skills/` folder
2. Install dependency on your Pi: `pip3 install RPi.GPIO`
   (For WiringPi C API: `sudo apt install wiringpi`)
3. Check system status: `python3 scripts/pi_info.py`
4. Start controlling GPIO

GPIO pinout at [references/pinout.md](references/pinout.md), hardware specs at [references/hardware.md](references/hardware.md).

## License

MIT
