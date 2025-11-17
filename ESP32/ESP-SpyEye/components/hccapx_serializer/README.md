# 📦 ESP32 Component: HCCAPX Serializer

<p align="center">
  <img src="https://img.shields.io/badge/Module-ESP--IDF%20Component-blueviolet?style=for-the-badge" alt="ESP-IDF Component">
  <img src="https://img.shields.io/badge/Language-C-00599C?style=for-the-badge" alt="Language: C">
  <img src="https://img.shields.io/badge/Dependency-frame__analyzer-orange?style=for-the-badge" alt="Dependency: frame_analyzer">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#---architectural-overview-the-hashcat-converter">Architectural Overview (The Hashcat Converter)</a></li>
    <li><a href="#--%EF%B8%8F-core-functionality-the-handshake-state-machine">Core Functionality (The Handshake State Machine)</a></li>
    <li><a href="#--%EF%B8%8F-key-file-analysis">Key File Analysis</a></li>
    <li><a href="#--%EF%B8%8F-public-api--dependencies">Public API & Dependencies</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Overview (The Hashcat Converter)
</h2>

This component, **`hccapx_serializer`**, is one of the most critical components in the ESP32 firmware for offensive operations. Its function is not to capture, but to **process and format**.

It is purpose-built to convert the raw EAPOL frames (identified by the `frame_analyzer`) into the **`.hccapx` binary format**. This format is the industry-standard for the powerful password cracking tool, **Hashcat** (specifically for Mode 16800 - WPA-PBKDF2).

This component effectively functions as a real-time **state machine**. It collects the distinct pieces of the WPA 4-Way Handshake (M1, M2, M3, M4) as they arrive from the sniffer. Once it has collected a valid pair (e.g., M1+M2 or M2+M3), it assembles them into a single, static `hccapx_t` struct, ready to be downloaded by the user via the standalone web server.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Functionality (The Handshake State Machine)
</h2>

The component's logic is designed to build a valid `hccapx` struct over time as packets are received.

1.  **Initialization**:
    * Before an attack, `hccapx_serializer_init()` is called by `attack_handshake.c`.
    * This function sets the correct file signature (`0x58504348`), version (`4`), and stores the target's `ESSID`. Crucially, it resets the handshake state by setting `hccapx.message_pair = 255` (indicating no valid pair yet).

2.  **Frame Ingestion**:
    * For every EAPOL frame captured by `frame_analyzer`, the `attack_handshake.c` module calls `hccapx_serializer_add_frame()`, passing in the parsed data frame.

3.  **Stateful Parsing (`_add_frame`)**:
    * The function first determines the frame's direction (AP-to-STA or STA-to-AP) by analyzing the MAC addresses (`addr1`, `addr2`, `addr3`).
    * **AP Message (M1/M3)**: If the frame is from the AP, it checks if the MIC is all-zero. If yes, it's **M1** (`ap_message_m1`); it stores the `mac_ap` and `nonce_ap`. If the MIC is not zero, it's **M3** (`ap_message_m3`).
    * **STA Message (M2/M4)**: If the frame is from the STA, it checks the `key_nonce`. If it's not zero, it's **M2** (`sta_message_m2`); it stores `mac_sta`, `nonce_sta`, and the raw `eapol` frame data. If the nonce is zero, it's **M4** (`sta_message_m4`).
    * **Message Pair Logic**: The component intelligently updates the `message_pair` flag based on the combination of messages it has seen (e.g., M1 + M2 = `0`, M1 + M4 = `1`, etc.), prioritizing the most useful pairs for cracking.

4.  **Data Retrieval**:
    * At any time, the `webserver` or another module can call `hccapx_serializer_get()`.
    * This function checks if a valid pair has been captured (`message_pair != 255`). If not, it returns `NULL`. If it has, it returns a pointer to the complete, static `hccapx` struct.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ Key File Analysis
</h2>

* **`hccapx_serializer.c`**:
    Contains the core state machine logic. It implements the `ap_message` and `sta_message` handlers that parse and store the handshake components as they arrive.
* **`interface/hccapx_serializer.h`**:
    This is the most important file for data structure. It defines the `__attribute__((__packed__)) struct hccapx_t`, which perfectly mirrors the binary layout required by Hashcat (signature, version, MACs, nonces, EAPOL data, etc.).
* **`CMakeLists.txt`**:
    Declares this component and its critical dependency: `PRIV_REQUIRES frame_analyzer`. This means it *must* have access to the headers and functions of `frame_analyzer` to function.

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Public API & Dependencies
</h2>

### Public Functions
* `void hccapx_serializer_init(const uint8_t *ssid, unsigned size)`
    * Resets the state machine and initializes a new, empty `hccapx` struct for a new target.
* `void hccapx_serializer_add_frame(data_frame_t *frame)`
    * The main ingestion function. Feeds a new EAPOL frame into the state machine.
* `hccapx_t *hccapx_serializer_get()`
    * Returns a pointer to the completed `hccapx_t` struct if a valid handshake has been captured, otherwise returns `NULL`.

### Dependencies
* **`frame_analyzer`**: This component is entirely dependent on `frame_analyzer` to provide it with parsed `data_frame_t` and `eapol_packet_t` structures.
