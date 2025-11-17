# 🧠 ESP32 Component: Frame Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Module-ESP--IDF%20Component-blueviolet?style=for-the-badge" alt="ESP-IDF Component">
  <img src="https://img.shields.io/badge/Language-C-00599C?style=for-the-badge" alt="Language: C">
  <img src="https://img.shields.io/badge/Dependency-wifi_controller-orange?style=for-the-badge" alt="Dependency: wifi_controller">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#-architectural-overview-the-probes-brain">Architectural Overview (The Probe's Brain)</a></li>
    <li><a href="#-core-functionality-real-time-parsing-workflow">Core Functionality (Real-time Parsing Workflow)</a></li>
    <li><a href="#-key-file-analysis">Key File Analysis</a></li>
    <li><a href="#-public-api--dependencies">Public API & Dependencies</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Overview (The Probe's Brain)
</h2>

The **`frame_analyzer`** is the core packet processing engine of the SpyEye ESP32 firmware. It acts as the intelligent layer sitting directly on top of the `wifi_controller` (which provides the raw sniffing capabilities).

This component's sole responsibility is to receive a stream of raw 802.11 data frames, parse them in real-time, and identify high-value packets (specifically **EAPOL frames**) related to WPA handshakes and PMKID exchanges.

When a relevant packet is identified, this component does *not* handle the attack logic itself. Instead, it publishes a new, high-level event (e.g., `DATA_FRAME_EVENT_PMKID`) that the main attack logic (like `attack_pmkid.c` or `attack_handshake.c`) can subscribe to.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Functionality (Real-time Parsing Workflow)
</h2>

The logic is event-driven and highly efficient, designed to minimize processing time in the promiscuous mode callback.

1.  **Initialization**: An attack module (e.g., `attack_handshake.c`) calls `frame_analyzer_capture_start()`, providing a `search_type_t` (either `SEARCH_HANDSHAKE` or `SEARCH_PMKID`) and the target BSSID.
2.  **Event Registration**: The component registers its own handler, `data_frame_handler`, to listen for `SNIFFER_EVENT_CAPTURED_DATA` events published by the `wifi_controller`.
3.  **Frame Filtering**: When a raw data frame is received, it is first passed to `is_frame_bssid_matching()`. Frames not matching the target BSSID are immediately discarded.
4.  **EAPOL Parsing**:
    * If the BSSID matches, `parse_eapol_packet()` is called. This function navigates the 802.11 Data Frame headers (including QoS headers), finds the LLC/SNAP header, and checks for the EAPOL EtherType (`0x888e`).
    * If successful, `parse_eapol_key_packet()` is called to verify it's an EAPOL-Key frame (Type 3).
5.  **Event Publishing**:
    * **If `search_type == SEARCH_HANDSHAKE`**: The component immediately publishes a `DATA_FRAME_EVENT_EAPOLKEY_FRAME` event, passing the raw frame up to the `attack_handshake.c` module.
    * **If `search_type == SEARCH_PMKID`**: The component proceeds to `parse_pmkid()`. This function iterates through the Key-Data fields of the EAPOL-Key packet, searching for a field with the correct OUI (`0x00fac00`) and Data Type (`4` for PMKID KDE). If a valid PMKID is found, it publishes a `DATA_FRAME_EVENT_PMKID` event.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ Key File Analysis
</h2>

* **`frame_analyzer.c`**:
    Contains the main event handler `data_frame_handler` and the public API functions (`_start`, `_stop`). It acts as the orchestrator for the parser.
* **`frame_analyzer_parser.c`**:
    The core parsing logic. This file contains the low-level functions responsible for navigating the packet structures to find and validate EAPOL and PMKID data.
* **`interface/frame_analyzer.h`**:
    Defines the public API and the `FRAME_ANALYZER_EVENTS` event base, which other components use to subscribe to this component's findings.
* **`interface/frame_analyzer_types.h`**:
    This is one of the most critical files. It defines the C `struct`s that map directly to 802.11, EAPOL, and Key-Data packet formats (e.g., `data_frame_mac_header_t`, `eapol_key_packet_t`, `key_data_field_t`). This allows the parser to cast raw packet buffers into meaningful, accessible data structures.

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Public API & Dependencies
</h2>

### Public Functions
* `void frame_analyzer_capture_start(search_type_t search_type, const uint8_t *bssid)`
    * Registers the data handler to start analyzing packets for a specific target.
* `void frame_analyzer_capture_stop()`
    * Unregisters the data handler to stop analysis.

### Events Subscribed To
* `SNIFFER_EVENT_CAPTURED_DATA` (from `wifi_controller`)

### Events Published
* `DATA_FRAME_EVENT_EAPOLKEY_FRAME`: Fired when any EAPOL-Key frame from the target BSSID is found.
* `DATA_FRAME_EVENT_PMKID`: Fired *only* when a valid PMKID is found within an EAPOL-Key frame.

### Dependencies
* As defined in `CMakeLists.txt`, this component requires `wifi_controller` to be active, as it provides the raw data packets.
