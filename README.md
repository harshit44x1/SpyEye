# 👁️  SpyEye: Hybrid Network Attack Framework

<img width="1280" height="442" alt="SpyEye_git_c" src="https://github.com/user-attachments/assets/e84b8df6-19d6-44e2-a74c-b5b6e57f2509" />

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square" alt="Status: Active Development">
  <img src="https://img.shields.io/badge/Python-3.10-blueviolet?style=flat-square" alt="Python 3.10">
  <img src="https://img.shields.io/badge/Framework-Flask%20%7C%20ESP--IDF-orange?style=flat-square" alt="Frameworks">
  <img src="https://img.shields.io/badge/Interface-Rich%20CLI-blue?style=flat-square" alt="Interface: Rich CLI">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <br>
  <img src="https://img.shields.io/badge/Author-Delta--Security-red?style=flat-square" alt="Author Delta-Security">
</p>

---

<details>
<summary><strong>Table of Contents</strong></summary>
<ol>
<li><a href="#--%EF%B8%8F-legal-disclaimer-use-responsibly">Legal Disclaimer</a></li>
<li><a href="#--architectural-philosophy-the-hybrid-advantage">Architectural Philosophy</a></li>
<li><a href="#--%EF%B8%8F-core-attack-vectors-feature-deep-dive">Core Attack Vectors</a></li>
<li><a href="#--%EF%B8%8F-core-attack-vectors-feature-deep-dive">Architectural Deep Dive</a></li>
<li><a href="#--%EF%B8%8F-core-attack-vectors-feature-deep-dive">Requirements & Deployment</a></li>
<li><a href="#---contribution-and-community">Contribution & Community</a></li>
<li><a href="#%EF%B8%8F-license">License</a></li>
</ol>
</details>

<h2 style="color: #FF0000; border-bottom: 2px solid #FF0000; padding-bottom: 10px;">
  ⚠️ Legal Disclaimer: Use Responsibly
</h2>

> This tool is intended **strictly for educational purposes and authorized security assessments only**. All code and functionalities are provided "as-is" without any warranty. The author (`Delta-Security`) is not responsible for any malicious use, damage, or illegal activities conducted with this framework. By using this software, you agree to do so in compliance with all applicable laws and with explicit, documented permission from any target network owners. **DO NOT USE THIS TOOL ON NETWORKS YOU DO NOT OWN OR HAVE EXPLICIT PERMISSION TO TEST.**

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Philosophy: The Hybrid Advantage
</h2>

**SpyEye** is not merely a collection of scripts; it is a meticulously engineered **Hybrid Network Attack Framework** designed to simulate the most advanced threat vectors in Wi-Fi security. The core innovation lies in its **decoupled architecture**, which separates the high-level command-and-control (C2) infrastructure from the low-level, hardware-accelerated attack execution.

### The Decoupled Model

1.  **The Python C2 (Host):** This component, running on a Linux host, handles the complex, resource-intensive tasks of network orchestration, victim traffic manipulation, and data logging. It is the brain of the operation, managing the Rogue AP, DNS/DHCP services, and the Captive Portal.
2.  **The ESP32 Probe (Attacker):** This dedicated microcontroller acts as the specialized "weapon." It is responsible for all time-critical, frame-level 802.11 operations (like Deauthentication and PMKID capture). By offloading these tasks to dedicated hardware, SpyEye achieves unparalleled stability and precision in its attacks, bypassing the limitations of host-OS-based packet injection.

This hybrid approach allows for **complex, multi-vector attack scenarios** that are both stable and highly effective, making SpyEye an indispensable tool for red teams and security researchers.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Attack Vectors: Feature Deep Dive
</h2>

The modular structure of SpyEye is built around specialized directories, each representing a critical component of the attack chain.

### 1. Rogue AP Management (`ap_control/`)

This module is the foundation of the social engineering attack. It is responsible for creating a convincing "Evil Twin" or a malicious open network to lure targets.

*   **Mechanism:** Leverages system calls to **`hostapd`** and low-level network interface manipulation to bring up a virtual access point.
*   **Key Features:**
    *   **Interface Configuration:** Dynamically sets up the necessary network interfaces (e.g., `wlan0mon`) and assigns IP addresses.
    *   **SSID Cloaking:** Supports broadcasting SSIDs that mimic legitimate networks for targeted attacks.
    *   **DHCP/DNS Integration:** Works seamlessly with `dnsmasq` (managed by the C2) to provide a functional network environment for connected victims.

### 2. Credential Harvesting (`captive_portal/` and `templates/`)

The captive portal is the payload delivery system, designed for high-fidelity credential harvesting.

*   **Mechanism:** Implemented as a robust **`Flask`** web application, it serves highly realistic, themeable login pages from the **`templates/`** directory.
*   **Key Features:**
    *   **High-Fidelity Emulation:** Includes pre-built templates for high-value targets (e.g., major web services, university portals) to maximize victim trust.
    *   **Data Logging:** Securely logs captured credentials, along with critical device metadata (User-Agent, MAC, IP), to a structured format (`logs/captured_data.json`) for post-exploitation analysis.
    *   **User-Agent Analysis:** Utilizes the `user-agents` library to parse and log device types, aiding in targeted follow-up attacks.

### 3. Traffic Interception and Redirection (`dns_spoofing/` and `firewall/`)

This is the core of the Man-in-the-Middle (MITM) capability, ensuring victims are isolated and their traffic is manipulated.

*   **Mechanism:**
    *   **`firewall/`:** Dynamically configures **`iptables`** rules to quarantine connected clients, forcing all DNS and HTTP traffic through the C2. This ensures the victim cannot bypass the captive portal.
    *   **`dns_spoofing/`:** The DNS redirection service intercepts queries and returns a controlled IP address (the C2's IP) for specified domains, effectively redirecting the victim to the captive portal.
*   **Key Features:**
    *   **Transparent Redirection:** The victim is seamlessly redirected without any visible certificate warnings or errors (for HTTP traffic).
    *   **Targeted Spoofing:** Configuration allows for specific domain targeting, ensuring only high-value traffic is manipulated.

### 4. Hardware-Accelerated Attacks (`esp32_control/`)

The C2 communicates with the ESP32 Probe via the **`pyserial`** library, sending low-level commands to execute hardware-timed 802.11 attacks.

*   **Mechanism:** The `esp32_control` module acts as the stable **`pyserial` bridge**, translating high-level C2 commands (e.g., `INITIATE_DEAUTH`) into serial instructions for the ESP32 firmware.
*   **Key Features:**
    *   **PMKID Capture:** Executes a fast, efficient attack to capture PMKIDs from WPA/WPA2-PSK networks, a critical step for offline password cracking.
    *   **Forced Re-authentication:** Launches targeted or broadcast Deauthentication attacks to force clients to disconnect and re-authenticate, enabling WPA 4-Way Handshake capture.
    *   **Industry-Standard Output:** The ESP32 firmware serializes captured data into **HCCAPX** (for Hashcat) and standard **PCAP** files (for Wireshark), streamlining the post-capture workflow.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ Architectural Deep Dive and Data Flow
</h2>

The following table and diagram illustrate the complex interaction between the C2 and the Probe, highlighting the separation of duties.

| Component | Technology Stack | Primary Responsibility | Data Ingestion/Output |
| :--- | :--- | :--- | :--- |
| **Python C2 (Host)** | Python 3.10, Flask, Rich, PyYAML | Orchestration, Traffic Manipulation, Data Presentation, High-Level Logic. | Reads: `config.yaml`. Writes: `logs/captured_data.json`. |
| **ESP32 Probe (Attacker)** | ESP-IDF, C, 802.11 Stack | Low-Level Packet Injection, Frame Analysis, Hardware-Timed Attacks. | Reads: Serial Commands (from C2). Writes: Serial Data (Handshakes, Status). |
| **Network Infrastructure** | hostapd, dnsmasq, iptables | Rogue AP creation, DHCP/DNS services, Firewalling, Victim Isolation. | System-level configuration and traffic routing. |

### Architectural Diagram: C2-Probe Relationship

```
                         +-----------------------+
                         |    Victim / Target    |
                         +-----------------------+
                               ^     |
                              /       \ 802.11 (Deauth, PMKID, Handshake)
                             /         \
+-------------------------+ / \ +--------------------------+
|    Python C2 Host       | / v |    ESP32 Attack Probe    |
|   (Linux Machine)       | /   |        (Hardware)        |
|=========================|/    |==========================|
| - Rogue AP (hostapd)    |<---------------------->| - 802.11 Sniffer          |
| - DHCP/DNS (dnsmasq)    | \ (Captive Portal) | - Frame Analyzer (EAPOL)  |
| - Firewall (iptables)   |  \                 | - PMKID / Handshake Atk   |
| - Captive Portal (Flask)|   \                | - Deauth / DoS Attack     |
| - C2 CLI (Rich/Python)  |    \ (UART Control) | - HCCAPX/PCAP Serialization |
+-------------------------+ <=================> +--------------------------+
                          | (Serial Commands) | (Handshake Data)
                          v
                +-------------------------+
                |   Attacker / Operator   |
                +-------------------------+
```

---
<details>
<summary><strong>🛠️ Requirements and Deployment Guide (Click to Expand)</strong></summary>

### Hardware Requirements (Mandatory for Full Functionality)

The framework's power is unlocked with the correct hardware configuration.

*   **ESP32 Probe:**
    *   1x **ESP32 Development Board** (e.g., ESP32-WROOM-32).
*   **Host C2 Machine:**
    *   1x **Linux Host** (Kali, Parrot OS recommended) with `sudo` / root privileges.
    *   2x **USB Wi-Fi Adapters**:
    *   *   **Adapter 1 (Rogue AP):** Must support **AP mode** and `hostapd`.
        * **Adapter 2 (Internet Uplink):** Any standard Wi-Fi adapter (or Ethernet port) to provide an internet connection to the C2 host. This is used by `iptables` (NAT/Masquerade) to give internet access to authenticated victims.
        * **All Monitoring/Injection tasks are offloaded to the ESP32 Probe,** removing the need for expensive, specialized adapters on the host machine.
    *   *Recommended Models:* **TL-WN722N** / **TL-WN725N** (or similar chipsets with compatible drivers).
*   **Driver Support:**
    *   The primary requirement for the C2 host is a driver compatible with `hostapd` (AP mode).
    ```
    Driver for Packet Injection: https://github.com/aircrack-ng/rtl8188eus
    ```

### Software Requirements

#### Host (Python C2)

1.  **Operating System:** Debian-based Linux (Kali, Parrot, Ubuntu) is strongly recommended.
2.  **Core Linux Dependencies:** `hostapd`, `dnsmasq`, `iptables`.
3.  **Python 3.8+** and `pip`.
4.  **Python Dependencies (from `requirements.txt`):**
    ```
    flask>=2.3.0
    requests>=2.31.0
    pyyaml>=6.0
    user-agents>=2.2.0
    inquirerpy
    rich>=13.7.0
    pyserial
    ```

#### Probe (ESP32)

1.  **Espressif IDF (ESP-IDF):** Requires a working installation of the Espressif IoT Development Framework. **(This project is built and verified against ESP-IDF v4.4)**.

### Installation Workflow: Step-by-Step

#### Step 1: Clone the Repository
```bash
git clone https://github.com/Delta-Sec/SpyEye.git
cd SpyEye
```

#### Step 2: Install Host Dependencies
This step ensures the C2 has all the necessary system and Python libraries to manage the network infrastructure.

```bash
sudo apt update
sudo apt install -y hostapd dnsmasq iptables

pip3 install -r requirements.txt
```

#### Step 3: Build and Flash the ESP32 Probe
The ESP32 firmware must be compiled and flashed before the C2 can communicate with it.

1.  Navigate to the ESP32 firmware directory:
    ```bash
    cd ESP32/ESP-SpyEye
    ```
2.  Build and flash the firmware using the ESP-IDF toolchain. Replace `/dev/ttyUSB0` with your ESP32's port:
    ```bash
    idf.py build
    idf.py -p /dev/ttyUSB0 flash
    ```

#### Step 4: Launch the SpyEye C2
With the hardware connected and the software installed, the framework is ready for launch.

1.  **Connect Hardware:** Plug in the flashed ESP32 probe (via USB) and your two USB Wi-Fi adapters.
2.  **Launch:** The framework requires root privileges to manipulate network interfaces and firewall rules.
    ```bash
    sudo python3 main.py
    ```
3.  **Interactive CLI:** Follow the `rich`-powered interactive menu:
    *   **[CONFIG]:** Run the configuration wizard to select your Rogue AP interface and Monitoring interface.
    *   **[ESP32 Control]:** Connect to the ESP32 by selecting its serial port (e.g., `/dev/ttyUSB0`).
    *   **[START]:** Launch the full Hybrid Attack Chain (Rogue AP + Captive Portal + ESP32 Attacks).
</details>
---

<h2 style="color: #00BCD4; border-bottom: 2px solid #00BCD4; padding-bottom: 10px;">
  🤝 Contribution and Community
</h2>

We welcome contributions from security researchers and developers to enhance the SpyEye platform.

### Reporting Issues

Please use the GitHub Issues tracker to report any bugs, suggest new features, or ask for support.

### Contributing Code

1.  Fork the repository.
2.  Create a new feature branch (`git checkout -b feature/new-module`).
3.  Commit your changes (`git commit -m 'feat: Add new module for X'`).
4.  Push to the branch (`git push origin feature/new-module`).
5.  Open a Pull Request with a detailed description of your changes.

## ⚖️ License

This project is licensed under the **MIT License** - see the [`LICENSE`](https://github.com/Delta-Sec/SpyEye/tree/main?tab=MIT-1-ov-file) file for details.

---
*Developed by Delta-Sec | Engineered for Precision and Performance*
*GitHub: [github.com/Delta-Sec](https://github.com/Delta-Sec)*
