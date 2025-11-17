# 👁️ SpyEye: Advanced Network Reconnaissance and Attack Platform

<!-- 
    ====================================================================================================
    PROMINENT HEADER IMAGE PLACEHOLDER
    The user will replace this with a high-resolution, professional header image.
    ====================================================================================================
-->
<p align="center">
  <img src="[YOUR_HIGH_RESOLUTION_HEADER_IMAGE_URL_HERE]" alt="SpyEye Platform Header Image" width="100%">
  <br>
  <h1 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
    SpyEye: The Enterprise-Grade Network Security Assessment Framework
  </h1>
</p>

<!-- 
    ====================================================================================================
    PROFESSIONAL BADGES
    Adding badges for a professional, at-a-glance status view.
    ====================================================================================================
-->
<p align="center">
  <img src="https://img.shields.io/badge/Status-Active%20Development-brightgreen" alt="Status: Active Development">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Framework-Flask-black" alt="Framework: Flask">
  <img src="https://img.shields.io/badge/CLI-Rich-orange" alt="CLI: Rich">
  <img src="https://img.shields.io/badge/Hardware-ESP32%20Supported-red" alt="Hardware: ESP32 Supported">
</p>

## 🛡️ Strategic Overview

The **SpyEye** platform is a sophisticated, modular, and highly extensible framework designed for comprehensive network security assessments, penetration testing, and advanced rogue device emulation. It is engineered to provide security professionals with an unparalleled toolset for simulating real-world threat scenarios, including rogue Access Point deployment, credential harvesting via captive portals, and DNS manipulation.

Built with a focus on stability, performance, and enterprise integration, SpyEye features a robust command-line interface (CLI) powered by `rich` for an enhanced user experience and a modular architecture that supports rapid development of new attack vectors and plugins.

---

<h2 style="color: #FF6B6B; border-bottom: 2px solid #FF6B6B; padding-bottom: 10px;">
  🌟 Core Capabilities and Feature Matrix
</h2>

SpyEye is built on a foundation of modularity and high-fidelity attack simulation, offering a suite of capabilities essential for modern security auditing.

| Feature Category | Core Capability | Technical Implementation | Enterprise Value Proposition |
| :--- | :--- | :--- | :--- |
| **Rogue AP Emulation** | **Access Point Control (`ap_control`)** | Python-based management of wireless adapters for creating and controlling malicious Wi-Fi networks. | Simulates real-world "Evil Twin" attacks to test network resilience and user awareness. |
| **Credential Harvesting** | **Captive Portal Deployment (`captive_portal`)** | Flask-based web application serving customizable, high-fidelity login pages (`templates`). | Assesses the vulnerability of network users to phishing and credential harvesting over Wi-Fi. |
| **Traffic Redirection** | **DNS Spoofing (`dns_spoofing`)** | Intercepts and redirects DNS queries to malicious or controlled IP addresses. | Tests the effectiveness of network monitoring and intrusion detection systems against man-in-the-middle attacks. |
| **Hardware Integration** | **ESP32 Control (`esp32_control`)** | Serial communication (`pyserial`) for commanding and receiving data from an embedded ESP32 device. | Enables low-level, hardware-accelerated attacks and physical layer manipulation. |
| **Extensibility** | **Plugin Architecture (`plugins`)** | A dedicated directory for extending functionality with custom attack modules and scripts. | Future-proofs the platform and allows security teams to integrate proprietary or custom-developed tools. |
| **System Management** | **Configuration Management (`config`)** | YAML-based configuration (`pyyaml`) for persistent, easy-to-manage settings. | Ensures repeatable, consistent testing environments and simplifies deployment across multiple systems. |
| **User Experience** | **Rich Command-Line Interface (`cli.py`)** | Utilizes the `rich` library for beautiful, informative, and interactive console output. | Reduces the learning curve and increases operational efficiency for security analysts. |

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Installation and Deployment
</h2>

### Prerequisites

SpyEye requires a Python 3 environment and specific hardware for full functionality.

#### 💻 Software Requirements

The following Python packages are required and are managed via `requirements.txt`:

| Package | Version | Purpose |
| :--- | :--- | :--- |
| `flask` | `>=2.3.0` | Web framework for serving the Captive Portal. |
| `requests` | `>=2.31.0` | HTTP library for making network requests. |
| `pyyaml` | `>=6.0` | Configuration file parsing and management. |
| `user-agents` | `>=2.2.0` | User-Agent string parsing for enhanced logging and targeting. |
| `inquirerpy` | (Latest) | Provides an interactive and user-friendly command-line prompt. |
| `rich` | `>=13.7.0` | Enables a beautiful, colorized, and structured command-line interface. |
| `pyserial` | (Latest) | Facilitates serial communication with the ESP32 hardware module. |

#### ⚙️ Hardware Requirements (Mandatory for Full Functionality)

For advanced wireless attack vectors, the following hardware components are **mandatory**:

*   **Wireless Adapters:** Two (2) compatible external wireless adapters are required for simultaneous AP creation and monitoring/packet injection.
    *   *Recommended Models:* **TL-WN722N** / **TL-WN725N** (or similar chipsets supporting monitor mode and packet injection).
*   **Embedded Device:** One (1) **ESP32** microcontroller unit.
    *   *Purpose:* Used for low-level wireless control, deauthentication attacks, and other hardware-accelerated functions.
*   **Driver Support:** A compatible driver is necessary to enable **packet injection** capabilities on the chosen wireless adapters.
    *   *Note:* Please replace `[DRIVER_REPO_NAME]` with the actual driver repository name.
    ```
    Driver for Packet Injection: [DRIVER_REPO_NAME]
    ```

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Delta-Sec/SpyEye.git
    cd SpyEye
    ```

2.  **Create a Virtual Environment (Best Practice):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # .\venv\Scripts\activate  # On Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Hardware Setup:**
    *   Ensure your wireless adapters are connected and the necessary packet injection drivers are installed and configured.
    *   Flash the required firmware onto your ESP32 device (firmware details are located in the `ESP32/` directory).

---

<h2 style="color: #00BCD4; border-bottom: 2px solid #00BCD4; padding-bottom: 10px;">
  🚀 Usage and Operational Workflow
</h2>

The SpyEye platform is executed via the main Python script, which launches the interactive, `rich`-powered CLI.

### Launching the Platform

```bash
python3 main.py
```

Upon execution, the system will perform an initial setup check, load the configuration from `config/config.yaml`, and present the main menu.

### Core Operational Modules

The platform is divided into several operational modules, each accessible from the main menu:

1.  **AP Control:** Manage the creation, configuration, and teardown of rogue Access Points.
2.  **Captive Portal:** Deploy and monitor the Flask-based web server for credential harvesting.
3.  **DNS Spoofing:** Configure and activate DNS redirection rules for targeted hosts.
4.  **ESP32 Controller:** Establish and manage the serial connection to the ESP32 device for hardware-level commands.
5.  **Firewall Management:** Configure temporary network rules to isolate targets or manage traffic flow during an assessment.

### Configuration Management

All persistent settings are managed through the `config/config.yaml` file. This includes network interface names, default SSIDs, DNS redirection targets, and ESP32 serial port settings.

```yaml
# Example config/config.yaml snippet
network:
  interface_ap: wlan0mon  # Interface for Access Point
  interface_monitor: wlan1mon # Interface for monitoring/injection
  default_ssid: "Free_Public_WiFi"
dns_spoofing:
  enabled: true
  targets:
    - host: "google.com"
      ip: "192.168.1.100"
esp32:
  serial_port: "/dev/ttyUSB0"
  baud_rate: 115200
```

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  🏗️ Architectural Deep Dive
</h2>

SpyEye employs a clean, layered architecture to ensure stability, maintainability, and high extensibility.

### 1. Presentation Layer (CLI)

*   **`cli.py`:** Handles all user interaction, menu navigation, and input validation using `inquirerpy`.
*   **`rich`:** Provides the visual styling, colorization, and structured output for a professional user experience.

### 2. Core Logic Layer (RogueAPTool)

*   **`main.py`:** Contains the `RogueAPTool` class, which acts as the central orchestrator. It initializes all sub-modules and manages the application lifecycle.
*   **`shared.py`:** Contains utility functions, shared constants, and the `rich` console instance used across all modules.

### 3. Module Layer (Attack Vectors)

This layer comprises the specialized directories, each containing the logic for a specific attack or control mechanism:

*   **`ap_control/`:** Logic for managing the host AP interface.
*   **`captive_portal/`:** Flask application setup and template rendering (`templates/`).
*   **`dns_spoofing/`:** Implementation of the DNS redirection service.
*   **`esp32_control/`:** Serial communication and command mapping for the ESP32.
*   **`firewall/`:** System-level network rule management.
*   **`plugins/`:** Reserved for future and custom extensions.

### 4. Data Layer

*   **`config/`:** Stores the `config.yaml` file for persistent settings.
*   **`templates/`:** HTML/CSS/JS files used by the captive portal for high-fidelity page emulation.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🤝 Contribution and Support
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

This project is licensed under the **MIT License** - see the `LICENSE` file for details.

---
*Developed by Delta-Sec | Engineered for Precision and Performance*
