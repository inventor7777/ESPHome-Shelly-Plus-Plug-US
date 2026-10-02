# Shelly Plus Plug US: hardware and stock-firmware notes

Device examined: **Shelly Plus Plug US**, model `SNPL-00116US` (`PlugUS` app), Gen 2, 4 MB ESP32. Stock firmware examined in Ghidra: **1.7.5** (`20260311-095849/1.7.5-g9979d16`). Live stock configuration was read from a separate Plug US on 1.7.4.

## Hardware map

| Function | ESP32 GPIO | Notes |
|---|---:|---|
| Relay | 32 | Confirmed on the converted plug. |
| Button | 4 | Active-low with pull-up; confirmed by physical operation. |
| Red LED | 26 | Active-low; confirmed by test. |
| Blue LED | 33 | Active-low; confirmed by test. |
| BL0937 CF | 27 | Confirmed from the stock firmware driver. |
| BL0937 CF1 | 14 | Confirmed from the stock firmware driver. |
| BL0937 SEL | 12 | Confirmed from the stock firmware driver; low/high selects the CF1 measurement mode. |
| NTC thermistor ADC | 34 | Confirmed from the stock firmware temperature-sensor constructor. |

The Plug US is a full dual-core **ESP32**, not an ESP32-Solo. The tested chip identifies as revision 3.1.

## NTC circuit and stock conversion

Stock firmware configures the NTC measurement as:

| Property | Value |
|---|---|
| Divider supply | 3.3 V |
| Fixed resistor | 10 kOhm |
| Thermistor nominal resistance | 10 kOhm at 25 C |
| Beta | B3950 |
| Divider arrangement | NTC is downstream, between the ADC node and ground |
| ADC attenuation | Dynamic; it begins at ESP-IDF legacy 11 dB and changes range as needed |

`attenuation: auto` is the closest ESPHome equivalent. Ambient validation was encouraging: after two hours unpowered, stock and ESPHome both initially reported 27 C. Their warm-up readings still need side-by-side characterization before relying on a cutoff.

## Metering behavior

The plug uses a **BL0937**. Ghidra recovered the driver wiring above and showed that the stock application polls it every second, alternates CF1's voltage/current selection each poll, and therefore refreshes each of voltage and current about every two seconds. CF provides active-power pulses continuously.

Stock fallback coefficients embedded in the driver are `0.16882`, `0.011316`, and `1.774957`; production calibration is device-specific, so these are useful reverse-engineering evidence, not portable ESPHome calibration values.

The converted plug's initial ESPHome meter reading was 132.6 V while a multimeter read 119.65 V. It therefore requires calibration against trusted voltage, current, and load-power references before using protection thresholds based on those readings.

## Stock protections

On the untouched stock Plug US, `Switch.GetConfig?id=0` returned:

| Protection | Stock setting | Meaning |
|---|---:|---|
| Overcurrent | 16.0 A | Configurable current cutoff. |
| Overvoltage | 280 V | Configurable voltage cutoff. |
| Overpower | 4,480 W | Configurable power cutoff. |
| Overheating | 95 C | Firmware safety cutoff; not exposed as a Gen2 RPC configuration item. |

The electrical defaults are permissive: 4,480 W equals 280 V × 16 A. Do not copy them blindly into ESPHome for a US 15 A outlet. The 95 C temperature value is Shelly's documented thermal shutdown threshold; use it only after the NTC mapping is characterized.

## Flash layout and OTA state

The original Shelly partition table has two 1,638,400-byte OTA app slots:

| Partition | Address | Size |
|---|---:|---:|
| `nvs` | `0x9000` | `0x4000` |
| `otadata` | `0xD000` | `0x2000` |
| `app_0` | `0x10000` | `0x190000` |
| `fs_0` | `0x1A0000` | `0x60000` |
| `app_1` | `0x200000` | `0x190000` |
| `fs_1` | `0x390000` | `0x60000` |
| `aux` | `0x3F0000` | `0xC000` |
| `shelly` | `0x3FC000` | `0x4000` |

ESPHome first booted at `app_0`; a normal ESPHome OTA then successfully booted from `app_1`. The bootloader was subsequently updated over ESPHome OTA to **ESP-IDF v5.5.5**. The existing layout already supports normal dual-slot ESPHome OTA. A standard ESPHome table migration is optional and may reset NVS-backed values such as the lifetime-energy counter.

## Limits of this record

The pin map and NTC topology are firmware-confirmed. Meter calibration and thermal response are not universal constants: validate them per plug or against good reference instruments before treating their readings as safety controls.
