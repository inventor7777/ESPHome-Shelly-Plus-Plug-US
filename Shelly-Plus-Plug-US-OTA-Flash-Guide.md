# Shelly Plus Plug US: first ESPHome flash over OTA

This is the process used successfully on a Shelly Plus Plug US (`SNPL-00116US`, Gen 2, ESP32) that began on Shelly firmware 1.7.4. It installs an ESPHome application while retaining Shelly's original bootloader and partition table.

It relies on the stock updater accepting a Shelly-format ZIP whose `PlugUS.bin` has been replaced with an ESPHome application. Firmware behavior can change, so test on a spare plug with a serial recovery path available.

## What the wrapper does

Shelly's ZIP contains a manifest and six images. The wrapper preserves the stock bootloader, partition table, OTA data, and filesystem. It replaces only `PlugUS.bin`, updates that file's SHA-256 and size in `manifest.json`, then stores the result as an uncompressed ZIP.

The first ESPHome application must use Shelly's stock partition layout: two `0x190000` (1,638,400 byte) app slots at `0x10000` and `0x200000`. This is why a normal ESPHome app binary can fit, while an ESPHome `factory.bin` cannot be used for the initial upload.

## Prerequisites

- Confirm the device reports `model: "SNPL-00116US"` and `gen: 2`:

  ```sh
  curl -s http://PLUG_IP/rpc/Shelly.GetDeviceInfo
  ```

- An ESPHome configuration that uses the supplied stock partition CSV for the first build:

  ```yaml
  esp32:
    variant: ESP32
    flash_size: 4MB
    partitions: shelly-plug-us-stock.csv
    framework:
      type: esp-idf

  ota:
    - platform: esphome
      allow_partition_access: true
  ```

- An ESPHome **OTA application binary** (`firmware.ota.bin`), not `factory.bin`. It must be no larger than 1,638,400 bytes.
- Python 3, the official `PlugUS` 1.7.5 firmware ZIP, and `build-plugus-shelly-zip.py` in one directory.

The official package is checked by the script: its manifest must identify itself as `PlugUS` version `1.7.5`.

## Generate the ZIP

Build the initial ESPHome configuration in Builder, then download its OTA-format binary. Run:

```sh
python3 build-plugus-shelly-zip.py firmware.ota.bin PlugUS-ESPHome.zip
```

The script checks the ESP32 image magic byte, verifies the 1.638 MB slot limit, replaces only `PlugUS.bin`, and rewrites the manifest checksum and size.

## Flash it

1. Open the Shelly web interface.
2. Open the firmware update page and choose **Update from file**.
3. Upload `PlugUS-ESPHome.zip`.
4. Wait for upload completion and reboot. A successful update log ends with `Update succeeded, will reboot`.
5. Connect to the new ESPHome device through its configured Wi-Fi, API, web server, or serial logs.

On first boot, ESPHome runs from the preserved Shelly `app_0` slot at `0x10000`. The stock `otadata` may cause an `ota data invalid ... Assuming factory` message; that was expected in this setup and did not prevent ESPHome from booting.

## After the first boot

- Use normal ESPHome wireless installs for future application updates. ESPHome writes the alternate stock `app_1` slot and then alternates between the two slots.
- Builder's ESPHome bootloader update succeeded in this setup. It updated the bootloader while retaining the stock partition table.
- Do not include a replacement partition table or bootloader in the initial Shelly wrapper. A full partition-layout migration was not part of this procedure and needs serial recovery available.

## Files used here

- `build-plugus-shelly-zip.py` — generates the one-time Shelly-format wrapper.
- `shelly-plug-us-stock.csv` — stock 4 MB partition table used for the initial ESPHome build.
- `Shelly-Plus-Plug-US-1.7.5.zip` — the official package template used for this test.
