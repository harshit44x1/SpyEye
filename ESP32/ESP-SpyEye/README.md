# 👁️ SpyEye: ESP32 Attack Probe Firmware

<p align="center">
  <img src="https://img.shields.io/badge/MCU-ESP32-9724a3?style=for-the-badge" alt="MCU: ESP32">
  <img src="https://img.shields.io/badge/Framework-ESP--IDF%20v4.4-E27063?style=for-the-badge" alt="ESP-IDF v4.4">
  <img src="https://img.shields.io/badge/Language-C-00599C?style=for-the-badge" alt="Language: C">
  <img src="https://img.shields.io/badge/Status-Firmware%20Stable-brightgreen?style=for-the-badge" alt="Status: Firmware Stable">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#about-this-firmware">About This Firmware</a></li>
    <li><a href="#firmware-architecture-component-deep-dive">Firmware Architecture (Component Deep Dive)</a></li>
    <li><a href="#core-features-of-the-esp32-probe">Core Features of the ESP32 Probe</a></li>
    <li><a href="#build-and-flash-instructions">Build and Flash Instructions</a></li>
    <li><a href="#operating-modes">Operating Modes</a></li>
    <li><a href="#configuration">Configuration</a></li>
  </ol>
</details>

---

## About This Firmware

This directory (`ESP32/ESP-SpyEye`) contains the complete ESP-IDF project for the **SpyEye Attack Probe**. This firmware turns a standard ESP32 microcontroller into a powerful, hardware-accelerated weapon for Wi-Fi security assessments.

This firmware is the "Probe" half of the SpyEye Hybrid Framework. It is designed to be controlled by the Python C2 host (`main.py`) via a serial (UART) connection, but it can also function as a **fully independent, standalone tool** controlled via its own Wi-Fi Management AP and web interface.

## Firmware Architecture: Component Deep Dive

The firmware is built on a modular, component-based architecture using ESP-IDF. Here is a breakdown of the key components and their roles:

### 1. `main` (Core Application Logic)
This is the heart of the firmware, responsible for initializing all other components and managing the primary attack state machine.
* **`main.c`**: Initializes the UART serial command task, the Wi-Fi Management AP, the core attack state machine (`attack_init`), and the standalone web server (`webserver_run`).
* **`attack.c`**: Manages the global attack status (`READY`, `RUNNING`, `FINISHED`, `TIMEOUT`) and handles event-based attack requests from both UART and the web server.
* **Attack Implementations**: Contains the high-level logic for each attack type:
    * `attack_pmkid.c`: Handles the PMKID capture process, including starting the sniffer, connecting to the target, and handling the "PMKID captured" event.
    * `attack_handshake.c`: Manages the 4-way handshake capture, registers the EAPOL frame handler, and initiates deauthentication methods.
    * `attack_dos.c`: Initiates Denial of Service attacks by calling the appropriate methods from `attack_method.c`.
* **`attack_method.c`**: Implements the *actual* attack vectors, such as the deauthentication broadcast loop (`attack_method_broadcast`) and the AP cloning logic (`attack_method_rogueap`).

### 2. `wifi_controller` (Component)
This is the hardware abstraction layer (HAL) for all Wi-Fi functions.
* `wifi_controller.c`: Manages the ESP32's Wi-Fi state (AP, STA) and provides functions to start/stop the Management AP (`wifictl_mgmt_ap_start`) or connect to a target (`wifictl_sta_connect_to_ap`).
* `ap_scanner.c`: Implements the 802.11 scanning functionality (`wifictl_scan_nearby_aps`) to find nearby networks.
* `sniffer.c`: Controls the Wi-Fi promiscuous mode (`wifictl_sniffer_start`), captures 802.11 frames, and filters them by type (Data, Mgmt, Ctrl).

### 3. `frame_analyzer` (Component)
The "brain" of the probe. This component inspects captured frames in real-time.
* `frame_analyzer.c`: Registers a handler for captured data and passes relevant frames to the parser.
* `frame_analyzer_parser.c`: The core parsing engine. It checks BSSIDs, digs into data frames, extracts EAPOL packets (`parse_eapol_packet`), and specifically hunts for PMKIDs within Key-Data fields (`parse_pmkid`).

### 4. `pcap_serializer` & `hccapx_serializer` (Components)
These components are critical for professional output. They convert raw captured data into industry-standard formats.
* `pcap_serializer.c`: Generates a valid `.pcap` file header and appends captured frames with their correct timestamps, allowing the entire capture to be downloaded and analyzed in Wireshark.
* `hccapx_serializer.c`: A stateful parser that specifically extracts the necessary components of a 4-way handshake (MACs, Nonces, EAPOL frames) and formats them into a `.hccapx` structure, ready for direct use with Hashcat for password cracking.

### 5. `webserver` (Component)
This component provides the full standalone functionality.
* `webserver.c`: Runs a lightweight HTTP server on the Management AP. It defines all API endpoints, such as `/ap-list` (triggers a scan), `/run-attack` (receives attack config), `/status` (provides real-time status), and the crucial `/capture.pcap` and `/capture.hccapx` endpoints for downloading attack results.
* `utils/index.html`: A rich, single-page-application (SPA) written in HTML/JS that serves as the graphical front-end for the standalone mode. It is compressed with `gzip` and embedded directly into the firmware binary as `page_index.h`.

### 6. `wsl_bypasser` (Component)
A low-level utility for raw frame injection.
* `wsl_bypasser.c`: Provides the function `wsl_bypasser_send_deauth_frame`, which constructs and sends raw 802.11 deauthentication frames using `esp_wifi_80211_tx`. This allows for direct, low-level packet injection without relying on higher-level APIs.

---

## Core Features of the ESP32 Probe

* **Dual Control Modes:** Can be controlled via serial (UART) by the Python C2 or as a standalone device via its Wi-Fi web interface.
* **Hardware-Accelerated Attacks:**
    * WPA/WPA2 PMKID Capture
    * WPA/WPA2 4-Way Handshake Capture
    * Broadcast & Targeted Deauthentication (DoS)
* **Real-time 802.11 Sniffing:** Captures and analyzes 802.11 data frames in promiscuous mode.
* **On-Chip Packet Parsing:** Intelligently parses EAPOL frames to identify handshakes and PMKIDs.
* **Standardized Attack Output:** Serializes captures into **.pcap** (for Wireshark) and **.hccapx** (for Hashcat) formats.
* **Standalone Web UI:** A rich web interface for scanning, configuring, and launching attacks, and downloading results directly from the device.
* **Configurable Management AP:** Launches its own password-protected Wi-Fi network for secure, standalone management.

---

## Build and Flash Instructions

### Prerequisites

* A working installation of the **Espressif IoT Development Framework (ESP-IDF)**.
* This firmware is built and tested against **ESP-IDF v4.4**. Using other versions may require code modifications.

### 1. Configure the Firmware
Before building, you can configure the Management AP settings (SSID, Password, Channel).

1.  Navigate to the firmware directory:
    ```bash
    cd ESP32/ESP-SpyEye
    ```
2.  Open the ESP-IDF configuration menu:
    ```bash
    idf.py menuconfig
    ```
3.  Navigate to `Component config` -> `Wi-Fi Controller` -> `Management AP`.
4.  Set your desired `Management AP SSID`, `Password`, and `Channel`.
5.  Save and exit.

### 2. Build and Flash
Connect your ESP32 board via USB and run the following commands, replacing `/dev/ttyUSB0` with your device's serial port.

```bash
# Clean the previous build (optional, but recommended)
idf.py fullclean

# Build the firmware
idf.py build

# Flash the firmware to the ESP32
idf.py -p /dev/ttyUSB0 flash

# Monitor the serial output (optional)
idf.py -p /dev/ttyUSB0 monitor

```
---

## Operating Modes

### Mode 1: C2 Controlled (via UART)
This is the primary mode of operation when used with the main SpyEye framework.

1.  Connect the flashed ESP32 to the host machine via USB.
2.  Run the main Python script: `sudo python3 main.py`.
3.  From the CLI, select **[ESP32 Control]** and connect to the correct serial port (e.g., `/dev/ttyUSB0`).
4.  The Python C2 will now send commands (like `STATUS`, `SCAN`, `DEAUTH`) directly to the ESP32's `serial_command_task`.

### Mode 2: Standalone Mode (via Web Interface)
The probe can be used as a completely independent, "headless" attack tool.

1.  Power on the flashed ESP32 (e.g., via a USB power bank).
2.  On your phone or laptop, scan for Wi-Fi networks.
3.  Connect to the **Management AP** (SSID and Password are set via `menuconfig`, default is `SpyEye AP` / `delta-sec-spyeye`).
4.  Open a web browser and navigate to the server's IP: **`http://192.168.33.1`**.
5.  You can now use the web interface to scan, configure, launch attacks, and download `.pcap` / `.hccapx` results directly.

## Configuration
All primary firmware settings (Wi-Fi channels, passwords, AP settings) are configured using the ESP-IDF Kconfig system.

* **Primary Configuration:** `idf.py menuconfig` -> `Component config` -> `Wi-Fi Controller`.
* **Other Settings:** `sdkconfig.defaults` provides project-wide build defaults, such as disabling Wi-Fi NVS to save flash space.
