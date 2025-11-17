# 📼 ESP32 Component: PCAP Serializer

<p align="center">
  <img src="https://img.shields.io/badge/Module-ESP--IDF%20Component-blueviolet?style=for-the-badge" alt="ESP-IDF Component">
  <img src="https://img.shields.io/badge/Language-C-00599C?style=for-the-badge" alt="Language: C">
  <img src="https://img.shields.io/badge/Standard-PCAP-007ACC?style=for-the-badge" alt="Standard: PCAP">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#---architectural-overview-the-wireshark-converter">Architectural Overview (The Wireshark Converter)</a></li>
    <li><a href="#--%EF%B8%8F-core-functionality-dynamic-in-memory-buffer">Core Functionality (Dynamic In-Memory Buffer)</a></li>
    <li><a href="#--%EF%B8%8F-key-file-analysis">Key File Analysis</a></li>
    <li><a href="#--%EF%B8%8F-public-api--dependencies">Public API & Dependencies</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Overview (The Wireshark Converter)
</h2>

The **`pcap_serializer`** is a self-contained utility component designed for one purpose: to create industry-standard Packet Capture (`.pcap`) files compatible with analysis tools like **Wireshark**, `tcpdump`, and `tshark`.

While the `hccapx_serializer` extracts *only* the data needed for password cracking, this component captures the **full 802.11 frames** associated with an attack (like all EAPOL handshake messages). This allows the operator to perform deep packet inspection and offline analysis of the capture, which is essential for advanced debugging and verification of the attack's success.

This component dynamically builds a complete, valid `.pcap` file in the ESP32's RAM, which is then served by the `webserver` component via the `/capture.pcap` endpoint.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Functionality (Dynamic In-Memory Buffer)
</h2>

The component works by constructing the `.pcap` file in a single, dynamically growing memory buffer.

1.  **Initialization (`pcap_serializer_init`)**:
    * This function is called at the beginning of an attack (e.g., by `attack_handshake_start`).
    * It allocates an initial memory buffer (`pcap_buffer`) just large enough to hold the `pcap_global_header_t` struct.
    * It populates this header with the correct **PCAP Magic Number (`0xa1b2c3d4`)** and, most importantly, sets the `network` type to **`LINKTYPE_IEEE802_11 (105)`**. This tells tools like Wireshark to parse these packets as 802.11 Wi-Fi frames.

2.  **Frame Appending (`pcap_serializer_append_frame`)**:
    * This function is called for every raw packet (e.g., each EAPOL frame) that needs to be saved.
    * It first creates a `pcap_record_header_t` struct, populating it with the packet's timestamp (`ts_sec`, `ts_usec`) and length (`incl_len`, `orig_len`).
    * It performs a **`realloc`** on the main `pcap_buffer` to expand it by the exact size of the new header *plus* the new packet data.
    * Finally, it `memcpy`s the new header and the packet data into the newly allocated space at the end of the buffer.

3.  **Data Retrieval (`pcap_serializer_get_buffer`, `_get_size`)**:
    * These are simple getter functions that allow other components (like the `webserver`) to get a direct pointer to the `pcap_buffer` in memory and its total `pcap_size`.

4.  **Cleanup (`pcap_serializer_deinit`)**:
    * Frees the entire `pcap_buffer` from memory, allowing a new capture session to begin.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ Key File Analysis
</h2>

* **`pcap_serializer.c`**:
    * Contains the full implementation of the dynamic memory buffer logic, including `init`, `append`, and `deinit` functions.
* **`interface/pcap_serializer.h`**:
    * Defines the public API functions for other components to use.
    * Critically, it defines the C `struct`s `pcap_global_header_t` and `pcap_record_header_t`, which map directly to the binary specification of the PCAP file format.
* **`CMakeLists.txt`**:
    * A simple component registration. Note that it has **no `PRIV_REQUIRES` dependencies**, indicating it is a fully self-contained utility component.

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Public API & Dependencies
</h2>

### Public Functions
* `uint8_t *pcap_serializer_init()`: Initializes the buffer with the global header and returns a pointer to it.
* `void pcap_serializer_append_frame(const uint8_t *buffer, unsigned size, unsigned ts_usec)`: Appends a new raw frame to the in-memory PCAP file.
* `void pcap_serializer_deinit()`: Frees the memory buffer.
* `unsigned pcap_serializer_get_size()`: Returns the current total size of the PCAP file in bytes.
* `uint8_t *pcap_serializer_get_buffer()`: Returns a direct pointer to the start of the PCAP data in memory.

### Dependencies
* **None**. This is a self-contained utility.
