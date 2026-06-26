# 树莓派硬件参数参考

数据来源：Raspberry Pi 官方文档、Wikipedia。覆盖全系列型号。

## 各型号详细规格

### Pi 1 系列（2012-2014）

| 项目 | Model B (2012) | Model A (2013) | Model B+ (2014) |
|:----|:--------------|:--------------|:---------------|
| SoC | BCM2835 | BCM2835 | BCM2835 |
| CPU | ARM11 @700MHz 单核 32-bit | ARM11 @700MHz 单核 32-bit | ARM11 @700MHz 单核 32-bit |
| RAM | 256MB → 512MB (Rev 2) | 256MB | 512MB |
| GPU | VideoCore IV | VideoCore IV | VideoCore IV |
| GPIO | 26-pin | 26-pin | **40-pin** |
| USB | 2×USB 2.0 | 1×USB 2.0 | 4×USB 2.0 |
| 网络 | 100M ETH (USB) | 无 | 100M ETH (USB) |
| 无线 | 无 | 无 | 无 |
| 视频 | HDMI + RCA | HDMI + RCA | HDMI + 3.5mm AV |
| 存储 | SD卡 | SD卡 | **microSD卡** |
| 尺寸 | 85.6×56mm | 65×56mm | 85.6×56mm |
| 功耗 | ~3.5W | ~1.5W | ~3.0W |

### Pi 2 系列（2015-2016）

| 项目 | Pi 2 Model B v1.1 | Pi 2 Model B v1.2 |
|:----|:-----------------|:-----------------|
| SoC | BCM2836 | BCM2837 |
| CPU | Cortex-A7 @900MHz 4核 32-bit | Cortex-A53 @900MHz 4核 **64-bit** |
| RAM | 1GB LPDDR2 | 1GB LPDDR2 |
| GPU | VideoCore IV | VideoCore IV |
| GPIO | 40-pin | 40-pin |
| USB | 4×USB 2.0 | 4×USB 2.0 |
| 网络 | 100M ETH | 100M ETH |
| 无线 | 无 | 无 |
| 视频 | HDMI + 3.5mm AV | HDMI + 3.5mm AV |
| 存储 | microSD | microSD |
| 功耗 | ~4.0W | ~4.0W |

### Pi 3 系列（2016-2018）

| 项目 | Pi 3 Model B | Pi 3 Model B+ | Pi 3 Model A+ |
|:----|:------------|:-------------|:-------------|
| 发布 | 2016.02 | 2018.03 | 2018.11 |
| SoC | BCM2837 | BCM2837B0 | BCM2837B0 |
| CPU | Cortex-A53 @1.2GHz 4核 | Cortex-A53 @**1.4GHz** 4核 | Cortex-A53 @1.4GHz 4核 |
| RAM | 1GB LPDDR2 | 1GB LPDDR2 | **512MB** LPDDR2 |
| GPU | VideoCore IV | VideoCore IV | VideoCore IV |
| GPIO | 40-pin | 40-pin | 40-pin |
| USB | 4×USB 2.0 | 4×USB 2.0 | 1×USB 2.0 |
| 网络 | 100M ETH | **Gigabit ETH** (USB 2.0限) | 无 |
| 无线 | WiFi n + BT 4.1 | 双频WiFi ac + BT 4.2 + **PoE** | 双频WiFi ac + BT 4.2 |
| 视频 | HDMI + 3.5mm AV | HDMI + 3.5mm AV | HDMI + 3.5mm AV |
| 存储 | microSD + **USB boot** | microSD + USB boot + **网络启动** | microSD |
| 尺寸 | 85.6×56mm | 85.6×56mm | 65×56mm |
| 功耗 | ~5.0W | ~5.5W | ~3.5W |

### Pi 4 系列（2019-2020）

| 项目 | Pi 4 Model B | Pi 400（键盘一体机） |
|:----|:------------|:------------------|
| 发布 | 2019.06 | 2020.11 |
| SoC | BCM2711 | BCM2711 |
| CPU | Cortex-A72 @**1.5GHz** → 1.8GHz 4核 | Cortex-A72 @**1.8GHz** 4核 |
| RAM | **1/2/4/8GB** LPDDR4 | **4GB** LPDDR4 |
| GPU | **VideoCore VI** | VideoCore VI |
| GPIO | 40-pin | 40-pin（GPIO排针在背面） |
| USB | 2×USB 2.0 + **2×USB 3.0** | 2×USB 2.0 + 1×USB 3.0 |
| 网络 | **真Gigabit ETH** | Gigabit ETH |
| 无线 | 双频WiFi ac + BT 5.0 | 双频WiFi ac + BT 5.0 |
| 视频 | **2×microHDMI 双4K** | 2×microHDMI 双4K |
| 存储 | microSD + USB boot | microSD |
| USB-C PD | **5V/3A（USB-C）** | 5V/3A（USB-C） |
| 其他 | — | 集成键盘 + 散热片 |
| 功耗 | ~6.5W | ~8.0W |

### Pi 5 系列（2023-2024）

| 项目 | Pi 5 | Pi 500（键盘一体机） |
|:----|:----|:------------------|
| 发布 | 2023.10 | 2024.12 |
| SoC | BCM2712 | BCM2712 |
| CPU | Cortex-A76 @**2.4GHz** 4核 | Cortex-A76 @2.4GHz 4核 |
| RAM | **1/2/4/8/16GB** LPDDR4X | **8GB** LPDDR4X |
| GPU | **VideoCore VII** | VideoCore VII |
| GPIO | **40-pin**（兼容前代） | 40-pin（背面） |
| USB | 2×USB 2.0 + 2×USB 3.0 | 2×USB 2.0 + 1×USB 3.0 |
| 网络 | **真Gigabit ETH** | Gigabit ETH |
| 无线 | 双频WiFi **ac** + BT 5.0 | 双频WiFi ac + BT 5.0 |
| 视频 | **2×microHDMI 双4K@60fps** | 2×microHDMI 双4K@60fps |
| 存储 | microSD + **PCIe 2.0 x1** | microSD |
| USB-C PD | 5V/**5A**（USB-C，支持PD） | 5V/3A（USB-C） |
| 新特性 | **PCIe 接口**、**RTC**、**南桥 RP1**、**电源按钮** | 集成键盘 |
| 功耗 | ~7.5W（空闲）~12W（负载） | ~10W |

### Zero 系列（2015-2021）

| 项目 | Zero (2015) | Zero W (2017) | Zero 2 W (2021) |
|:----|:-----------|:-------------|:---------------|
| SoC | BCM2835 | BCM2835 | **BCM2837** |
| CPU | ARM11 @1GHz 单核 32-bit | ARM11 @1GHz 单核 32-bit | Cortex-A53 @1GHz **4核 64-bit** |
| RAM | 512MB | 512MB | 512MB |
| GPU | VideoCore IV | VideoCore IV | VideoCore IV |
| GPIO | 40-pin（未焊接） | 40-pin（未焊接） | 40-pin（未焊接） |
| USB | 1×micro USB OTG | 1×micro USB OTG | 1×micro USB OTG |
| 网络 | 无 | **WiFi n + BT 4.1** | **双频WiFi ac + BT 4.2** |
| 视频 | mini HDMI | mini HDMI | mini HDMI |
| 存储 | microSD | microSD | microSD |
| 尺寸 | 65×30mm | 65×30mm | 65×30mm |
| 功耗 | ~0.8W | ~0.8W | ~1.2W |

## GPIO 通用概览

| 项目 | Pi 1 (26-pin) | Pi 1 B+/2/3/4/5 (40-pin) | Zero 系列 |
|:----|:-------------|:------------------------|:---------|
| 引脚总数 | 26 | 40 | 40（未焊） |
| 可编程 GPIO | BCM 0-7（8个） | BCM 2-27（26个） | BCM 2-27（26个） |
| I2C | 默认启用 | 默认**未**启用 | 默认未启用 |
| SPI | 默认启用 | 默认**未**启用 | 默认未启用 |
| UART | 可用 | 默认未启用 | 默认未启用 |
| PWM | BCM 18 | BCM 12/13/18 | BCM 12/13/18 |
| Python 库 | RPi.GPIO | RPi.GPIO / gpiozero / lgpio | RPi.GPIO |

## 多代 GPIO 兼容性注意

1. **Pi 1 早期（26-pin）**与**40-pin** 型号的前 26 个物理引脚功能兼容
2. **Pi 5 的 GPIO** 通过南桥芯片 RP1 控制，不再直连 SoC，但软件接口完全兼容
3. **Zero 系列**的 GPIO 引脚默认未焊接，需自行焊接排针
4. **PWM 通道**在不同代之间可能有差异，建议用 `pinout` 命令确认

## 功率与供电

| 型号 | 官方电源要求 | 典型空闲功耗 | 典型负载功耗 |
|:----|:-----------|:-----------|:-----------|
| Pi 1 Model B | 5V/1A (micro USB) | ~2.0W | ~3.5W |
| Pi 2 Model B | 5V/2A (micro USB) | ~2.5W | ~4.0W |
| Pi 3 Model B | 5V/2.5A (micro USB) | ~3.0W | ~5.0W |
| Pi 3 Model B+ | 5V/2.5A (micro USB) | ~3.5W | ~5.5W |
| Pi 4 Model B | 5V/3A (USB-C) | ~3.5W | ~6.5W |
| Pi 5 | 5V/5A (USB-C, PD) | ~4.5W | ~12W |
| Zero | 5V/1A (micro USB) | ~0.5W | ~0.8W |
| Zero 2 W | 5V/1A (micro USB) | ~0.8W | ~1.2W |

## 常用系统命令

```bash
# 识别当前 Pi 型号
cat /proc/cpuinfo
cat /sys/firmware/devicetree/base/model

# 温度/频率/电压
vcgencmd measure_temp
vcgencmd measure_clock arm
vcgencmd measure_volts core
vcgencmd get_throttled

# GPIO 引脚图
pinout

# 网络
ip -br addr

# 外设
lsusb
lsmod

# 存储
df -h
lsblk

# 内存
free -h
```
