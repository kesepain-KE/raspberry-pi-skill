# 树莓派 40 引脚完整对照表

适用所有 40-pin 树莓派（Pi 3B/3B+/4B/5/Zero W 等）。

## 引脚布局图

```
                  ┌────────────────────────┐
 3.3V (DC) →  1 ● ● 2  ← 5V (DC)
 I2C1 SDA  →  3 ● ● 4  ← 5V (DC)
 I2C1 SCL  →  5 ● ● 6  ← GND
  BCM 4    →  7 ● ● 8  ← BCM 14 (UART TX)
  GND      →  9 ● ● 10 ← BCM 15 (UART RX)
  BCM 17   → 11 ● ● 12 ← BCM 18 (PWM0)
  BCM 27   → 13 ● ● 14 ← GND
  BCM 22   → 15 ● ● 16 ← BCM 23
  3.3V     → 17 ● ● 18 ← BCM 24
 SPI MOSI  → 19 ● ● 20 ← GND
 SPI MISO  → 21 ● ● 22 ← BCM 25
 SPI SCLK  → 23 ● ● 24 ← BCM 8  (SPI CE0)
  GND      → 25 ● ● 26 ← BCM 7  (SPI CE1)
 ID EEPROM → 27 ● ● 28 ← ID EEPROM
  BCM 5    → 29 ● ● 30 ← GND
  BCM 6    → 31 ● ● 32 ← BCM 12 (PWM0)
 PWM1      → 33 ● ● 34 ← GND
 SPI MISO  → 35 ● ● 36 ← BCM 16
  BCM 26   → 37 ● ● 38 ← BCM 20 (SPI MOSI)
  GND      → 39 ● ● 40 ← BCM 21 (SPI SCLK)
                  └────────────────────────┘
```

## 引脚详细表

| 物理引脚 | BCM GPIO | 默认功能 | 特殊功能 | 备注 |
|:-------:|:--------:|:--------:|:--------:|:-----|
| 1 | — | 3.3V DC | 电源（50mA max） | |
| 2 | — | 5V DC | 电源 | |
| 3 | BCM 2 | I2C1 SDA | GPIO | I2C 默认未启用 |
| 4 | — | 5V DC | 电源 | |
| 5 | BCM 3 | I2C1 SCL | GPIO | I2C 默认未启用 |
| 6 | — | GND | 地 | |
| 7 | BCM 4 | GPIO | GPCLK0 | |
| 8 | BCM 14 | UART TX | GPIO | UART 默认未启用 |
| 9 | — | GND | 地 | |
| 10 | BCM 15 | UART RX | GPIO | UART 默认未启用 |
| 11 | BCM 17 | GPIO | | |
| 12 | BCM 18 | GPIO | **PWM0** | |
| 13 | BCM 27 | GPIO | | |
| 14 | — | GND | 地 | |
| 15 | BCM 22 | GPIO | | |
| 16 | BCM 23 | GPIO | | |
| 17 | — | 3.3V DC | 电源（50mA max） | |
| 18 | BCM 24 | GPIO | | |
| 19 | BCM 10 | SPI MOSI | GPIO | SPI 默认未启用 |
| 20 | — | GND | 地 | |
| 21 | BCM 9 | SPI MISO | GPIO | SPI 默认未启用 |
| 22 | BCM 25 | GPIO | | |
| 23 | BCM 11 | SPI SCLK | GPIO | SPI 默认未启用 |
| 24 | BCM 8 | SPI CE0 | GPIO | SPI 默认未启用 |
| 25 | — | GND | 地 | |
| 26 | BCM 7 | SPI CE1 | GPIO | SPI 默认未启用 |
| 27 | BCM 0 | ID EEPROM | — | 系统保留 |
| 28 | BCM 1 | ID EEPROM | — | 系统保留 |
| 29 | BCM 5 | GPIO | | |
| 30 | — | GND | 地 | |
| 31 | BCM 6 | GPIO | | |
| 32 | BCM 12 | GPIO | **PWM0** | |
| 33 | BCM 13 | GPIO | **PWM1** | |
| 34 | — | GND | 地 | |
| 35 | BCM 19 | GPIO | SPI MISO | SPI 默认未启用 |
| 36 | BCM 16 | GPIO | | |
| 37 | BCM 26 | GPIO | | |
| 38 | BCM 20 | GPIO | SPI MOSI | SPI 默认未启用 |
| 39 | — | GND | 地 | |
| 40 | BCM 21 | GPIO | SPI SCLK | SPI 默认未启用 |

## PWM 引脚

| BCM | 物理引脚 | PWM 通道 | 备注 |
|:---:|:-------:|:--------:|:----:|
| 18 | 12 | PWM0 | 通用 |
| 12 | 32 | PWM0 | |
| 13 | 33 | PWM1 | |

> 注意：Pi 5 的 PWM 引脚分配有变化，建议用 `pinout` 命令确认。

## 电源引脚

| 物理引脚 | 电压 | 最大电流 |
|:-------:|:----:|:--------:|
| 1, 17 | 3.3V | 50mA |
| 2, 4 | 5V | 取决于电源适配器 |

## 编号体系

| 编号体系 | 说明 |
|:---------|:-----|
| 物理引脚 | 1-40，按位置排列 |
| BCM GPIO | Broadcom SoC 编号，编程推荐使用 |
| wPi | WiringPi 编号 |
