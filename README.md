# ESPHome Shelly Plus Plug US

OTA conversion for the **Shelly Plus Plug US** (`SNPL-00116US`). It installs ESPHome through the stock Shelly web interface, then supports normal ESPHome updates.

## Quick start

1. In the ESPHome Builder configuration directory, download and place these two files together
   - `shelly-plus-plug-us-builder.yaml`
   - `shelly-plug-us-stock.csv`
2. Download `Shelly-Plus-Plug-US-ESPHome-OTA.zip` to anywhere on your computer from this repository.
3. Open your stock Plug US web interface, choose **Update from file**, and upload that ZIP. It takes a pretty long time to upload (1-2 minutes). If you wish to keep track of progress, you can set a syslog server in the Shelly UI.
4. Wait for the plug to reboot. Join its Wi-Fi hotspot, **shelly-plus-plug-us**, then open the Captive Portal and enter your home Wi-Fi details. The hotspot has no password. You can also provision Wi-Fi through Bluetooth Improv.
5. Open the YAML in Builder. Leave its hostname as `shelly-plus-plug-us` until Builder has connected to the plug for the first time. It should show as Online. Click Install, and then click Builder's **Update bootloader** action. **DO NOT interrupt power while the bootloader updates.** If you do not update the bootloader, it will not be able to be OTA updated via ESPHome (it will just revert back to the previous app image after upload).
6. Use normal wireless installs from Builder for future firmware updates. Change the hostname before deploying a second plug. You can do so easily by changing the friendly name in the YAML, and then using the Update Hostname action from the Builder homepage.

The initial OTA ZIP replaces only Shelly's `PlugUS.bin` application image. The first install keeps Shelly's original bootloader, partition table, and other flash contents. The bootloader update and future flashes are separate ESPHome OTA actions which finish the conversion

After this, it becomes a normal ESPHome device, albeit with a Shelly partition table. It may be possible to upload a new partition table OTA, but I have not tried to do so yet.

**NOTE:** Shelly's stock OS checks the firmware after upload to see if it is official. If it is not, the plug permanently and irreversibly burns eFuse BLOCK3 to indicate custom firmware and void your warranty.

## Added features

Compared with the stock user interface, the ESPHome package exposes these controls and diagnostics directly in Home Assistant:

- Persistent lifetime energy, relay on-time, relay-cycle, and button-press counters.
- Peak power, current, voltage, internal temperature, and minimum-voltage records.
- Apparent power and power factor.
- Configurable overcurrent, overvoltage, undervoltage, overpower, and overtemperature limits, with trip counters, last-trip reason, and optional automatic recovery.
- Configurable power-on behavior, auto-off timer, button lock, and blue LED brightness for on and standby states.
- Reset buttons for statistics, protection history, extrema, and lifetime energy.

## What is included

- `Shelly-Plus-Plug-US-ESPHome-OTA.zip`: ready to upload through the stock Shelly web interface.
- `shelly-plus-plug-us-builder.yaml`: Builder configuration with Captive Portal, BLE Improv, and partition-table access.
- `shelly-plus-plug-us-package.yaml`: hardware map and device behavior imported by the Builder YAML.
- `shelly-plug-us-stock.csv`: the original Shelly partition table. Keep this beside the Builder YAML.

The bootstrap image contains no home Wi-Fi credentials. Captive Portal and Improv save the credentials you enter on the plug.

## Build your own custom release ZIP (optional)

For a custom ESPHome image, build `shelly-plus-plug-us-builder.yaml`, download `firmware.ota.bin`, place the official Shelly `PlugUS` 1.7.5 ZIP beside `build-plugus-shelly-zip.py`, then run:

```sh
python3 build-plugus-shelly-zip.py firmware.ota.bin Shelly-Plus-Plug-US-ESPHome-OTA.zip
```

The app image must fit Shelly's existing 1,638,400-byte OTA slot. While you could compile any custom ESPHome firmware for it in this step, it at least needs to have partition access, otherwise you will never be able to update it OTA.

## Notes

- This project supports **only** the Plus Plug US model `SNPL-00116US`.
- Metering and temperature values need validation against trusted reference instruments before using them as safety limits. The default calibrations worked on my Plug USes, but there is likely some variation between batches.
- [Hardware and stock-firmware notes](Shelly-Plus-Plug-US-Hardware-and-Stock-Firmware-Notes.md) and the [detailed flash guide](Shelly-Plus-Plug-US-OTA-Flash-Guide.md) contain the technical records if you are interested.
- The README and YAML was mostly written by me, partly by AI.
- The investigation documents are written by AI, since it is more knowledgable about Ghidra and reversing firmware than me.
