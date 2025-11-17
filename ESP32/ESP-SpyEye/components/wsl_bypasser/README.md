# 💉 ESP32 Component: WSL Bypasser (Raw 802.11 Frame Injector)

<p align="center">
  <img src="https://img.shields.io/badge/Module-ESP--IDF%20Component-blueviolet?style=for-the-badge" alt="ESP-IDF Component">
  <img src="https://img.shields.io/badge/Language-C-00599C?style=for-the-badge" alt="Language: C">
  <img src="https://img.shields.io/badge/Role-Low%20Level%20Utility-E27063?style=for-the-badge" alt="Role: Low Level Utility">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#---architectural-overview-the-injection-engine">Architectural Overview (The Injection Engine)</a></li>
    <li><a href="#--%EF%B8%8F-core-functionality-the-sanity-check-bypass">Core Functionality (The Sanity Check Bypass)</a></li>
    <li><a href="#--%EF%B8%8F-key-file-analysis">Key File Analysis</a></li>
    <li><a href="#--%EF%B8%8F-public-api--dependencies">Public API & Dependencies</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Overview (The Injection Engine)
</h2>

The **`wsl_bypasser`** component is a low-level utility that provides the core **raw 802.11 packet injection** capability for the SpyEye firmware. While the name might be misleading (it is not related to Windows Subsystem for Linux), its function is critical: it "bypasses" the standard, high-level ESP-IDF Wi-Fi functions to inject custom-crafted frames.

This component is the "weapon" that is directly used by `attack_method.c` to perform deauthentication (DoS) attacks.

It achieves this by using the unofficial, low-level ESP-IDF function `esp_wifi_80211_tx()`, which allows for sending arbitrary raw buffers directly to the Wi-Fi radio. This is a powerful but non-standard method that is essential for offensive operations.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Functionality (The Sanity Check Bypass)
</h2>

The component's operation is simple and direct, focusing on constructing and transmitting deauthentication frames.

1.  **Raw Frame Template**:
    * The file `wsl_bypasser.c` defines a static `uint8_t` array named `deauth_frame_default[]`.
    * This is a pre-compiled, valid 802.11 deauthentication frame. The destination MAC is set to broadcast (`ff:ff:ff:ff:ff:ff`), while the Source MAC (Addr2) and BSSID (Addr3) are left as placeholders.

2.  **Frame Crafting (`wsl_bypasser_send_deauth_frame`)**:
    * This is the high-level function used by the attack modules.
    * It takes a `wifi_ap_record_t` struct (the target AP) as an argument.
    * It copies the `deauth_frame_default` template into a new buffer.
    * It then uses `memcpy` to inject the target AP's BSSID into the correct offsets in the frame header: the Source MAC (offset 10) and the BSSID (offset 16).

3.  **Raw Injection (`wsl_bypasser_send_raw_frame`)**:
    * This is the core injection function. It takes the crafted frame and its size.
    * It calls `esp_wifi_80211_tx(WIFI_IF_AP, frame_buffer, size, false)`, which transmits the raw frame buffer over the air using the AP interface.

4.  **The "Bypass"**:
    * The ESP-IDF normally has sanity checks (like `ieee80211_raw_frame_sanity_check`) to prevent this type of injection.
    * This component provides its own stub version of this function that simply returns `0` (OK).
    * The `CMakeLists.txt` file includes the linker flag `-Wl,-zmuldefs`. This flag tells the linker to "allow multiple definitions" of a function, ensuring that this component's "bypass" function is used instead of the original one from the ESP-IDF libraries.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ Key File Analysis
</h2>

* **`wsl_bypasser.c`**:
    * Implements the core logic, including the deauth frame template and the call to `esp_wifi_80211_tx`.
* **`interface/wsl_bypasser.h`**:
    * Defines the simple, two-function public API used by other components (`main/attack_method.c`).
* **`CMakeLists.txt`**:
    * Contains the critical `-Wl,-zmuldefs` linker flag, which is the key that enables this component's "bypass" of standard ESP-IDF protections against raw frame injection.

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Public API & Dependencies
</h2>

### Public Functions
* `void wsl_bypasser_send_raw_frame(const uint8_t *frame_buffer, int size)`
    * Transmits any arbitrary buffer as a raw 802.11 frame.
* `void wsl_bypasser_send_deauth_frame(const wifi_ap_record_t *ap_record)`
    * A helper function that crafts and sends a broadcast deauthentication frame spoofing the target AP's BSSID.

### Dependencies
* **None**. This is a self-contained, low-level utility component that relies only on base ESP-IDF libraries (like `esp_wifi`).
