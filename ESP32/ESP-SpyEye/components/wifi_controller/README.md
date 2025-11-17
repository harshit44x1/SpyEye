# 📡 ESP32 Component: Wi-Fi Controller (HAL)

<p align="center">
  <img src="https://img.shields.io/badge/Module-ESP--IDF%20Component-blueviolet?style=for-the-badge" alt="ESP-IDF Component">
  <img src="https://img.shields.io/badge/Language-C-00599C?style=for-the-badge" alt="Language: C">
  <img src="https://img.shields.io/badge/Role-Hardware%20Abstraction%20Layer%20(HAL)-E27063?style=for-the-badge" alt="Role: HAL">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#---architectural-overview-the-radio-hal">Architectural Overview (The Radio HAL)</a></li>
    <li><a href="#--%EF%B8%8F-core-functionality-sub-module-deep-dive">Core Functionality (Sub-Module Deep Dive)</a></li>
    <li><a href="#--%EF%B8%8F-key-file-analysis">Key File Analysis</a></li>
    <li><a href="#--%EF%B8%8F-public-api--dependencies">Public API & Dependencies</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Overview (The Radio HAL)
</h2>

The **`wifi_controller`** is the foundational Hardware Abstraction Layer (HAL) for all 802.11 radio operations within the SpyEye ESP32 firmware. It is arguably the most critical component, as it provides the low-level functions that all other attack and management components depend on.

Its core design principle is to abstract the complexity of the Espressif Wi-Fi drivers into a simple, task-oriented API. It initializes the ESP32 radio in **`WIFI_MODE_APSTA`**, allowing the device to simultaneously act as an Access Point (for the Management UI or Rogue AP) and a Station (for connecting to a target).

This component is responsible for four primary duties:
1.  **AP Management**: Starting and stopping Access Points (both Management and Rogue).
2.  **STA Management**: Connecting to target networks (e.g., for PMKID attacks).
3.  **Scanning**: Discovering nearby networks.
4.  **Sniffing**: Capturing raw 802.11 frames from the air.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Functionality (Sub-Module Deep Dive)
</h2>

The component is internally divided into three logical units, which are compiled together as defined in `CMakeLists.txt`.

### 1. `wifi_controller.c` (Core Radio Control)
This file manages the state of the Wi-Fi interfaces.
* **AP/STA Mode**: Initializes the `esp_netif` in `APSTA` mode, creating both a default AP and STA interface.
* **Management AP**: `wifictl_mgmt_ap_start()` is a high-level function that starts the standalone "SpyEye AP". It pulls its configuration (SSID, Password, Channel) directly from the `Kconfig` settings. It also starts a DHCP server with a static IP (`192.168.33.1`) for the web interface.
* **Rogue AP / MAC Spoofing**: Provides `wifictl_set_ap_mac()` and `wifictl_restore_ap_mac()`. These are critical for the "Rogue AP" attack method, allowing the ESP32 to clone the BSSID of a target network.
* **Station Control**: `wifictl_sta_connect_to_ap()` allows the ESP32 to act as a client and connect to a target AP, which is the core mechanism of the PMKID attack.

### 2. `ap_scanner.c` (Network Discovery)
This file implements the scanning functionality required by both the C2 and the Standalone Web UI.
* **`wifictl_scan_nearby_aps()`**: This function initiates an active 802.11 scan and stores the results in a static `wifictl_ap_records_t` array.
* **`wifictl_get_ap_records()` / `wifictl_get_ap_record()`**: These are getter functions that allow other components (like `webserver` or `main`) to retrieve the list of scanned APs to present to the user.

### 3. `sniffer.c` (Raw Packet Capture)
This file manages the promiscuous mode and the flow of raw packets.
* **`wifictl_sniffer_start()`**: This is the core capture function. It enables promiscuous mode on the Wi-Fi radio, sets it to a specific channel, and registers the `frame_handler` as the primary callback.
* **`frame_handler()`**: This function is executed for **every single 802.11 frame** captured by the radio. It's a critical piece of the architecture. Instead of processing the frame itself, it immediately filters it by type (Data, Mgmt, Ctrl) and publishes it to the ESP-IDF event system under the `SNIFFER_EVENTS` base.
* **Decoupling**: This event-based design is highly efficient. It decouples raw packet capture (this component's job) from packet analysis (the `frame_analyzer`'s job), preventing the sniffer callback from blocking.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ Key File Analysis
</h2>

* **`Kconfig`**:
    This is the component's configuration file. It allows the developer to set the Management AP's SSID, Password, Channel, and Max Connections via `idf.py menuconfig`.
* **`interface/wifi_controller.h`**:
    The main header file that aggregates all public functions from `ap_scanner.h`, `sniffer.h`, and `wifi_controller.c` into a single, clean API for other components to include.
* **`sniffer.h`**:
    Defines the `SNIFFER_EVENTS` event base and its event IDs (`SNIFFER_EVENT_CAPTURED_DATA`, etc.), which `frame_analyzer` subscribes to.

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Public API & Dependencies
</h2>

### Public Functions (Partial List)
* `void wifictl_mgmt_ap_start()`: Starts the standalone Management Access Point.
* `void wifictl_scan_nearby_aps()`: Initiates a new 802.11 network scan.
* `const wifictl_ap_records_t *wifictl_get_ap_records()`: Gets the results from the last scan.
* `void wifictl_sniffer_start(uint8_t channel)`: Puts the radio in promiscuous (monitor) mode on a specific channel.
* `void wifictl_sniffer_stop()`: Stops promiscuous mode.
* `void wifictl_sta_connect_to_ap(...)`: Connects the ESP32 to a target AP.
* `void wifictl_sta_disconnect()`: Disconnects from the target AP.
* `void wifictl_set_ap_mac(const uint8_t *mac_ap)`: Spoofs the ESP32's AP MAC address.
* `void wifictl_restore_ap_mac()`: Restores the original MAC address.

### Events Published
* `SNIFFER_EVENT_CAPTURED_DATA`: Published for every 802.11 Data frame captured.
* `SNIFFER_EVENT_CAPTURED_MGMT`: Published for every 802.11 Management frame captured.
* `SNIFFER_EVENT_CAPTURED_CTRL`: Published for every 802.11 Control frame captured.

### Dependencies
* This component is foundational and has no other custom component dependencies. It relies directly on the ESP-IDF `esp_wifi`, `esp_netif`, and `esp_event` libraries.
