---
name: "\U0001F41E Bug Report"
about: Create a report to help us improve SpyEye
title: ''
labels: bug
assignees: AyhamAsfoor

---

**Thank you for helping improve SpyEye! To help us fix this bug, please provide the following details.**

### 1. Clear Bug Description
(A clear and concise description of what the bug is. Example: "The C2 crashes with a 'SerialException' when selecting 'Connect' from the ESP32 menu, even if the device is plugged in.")

### 2. Steps to Reproduce
(Please provide a clear, step-by-step guide on how to trigger the bug. This is the most important part!)

1.  Run `sudo python3 main.py`.
2.  Go to '⚙️ [CONFIG]' and configure interfaces...
3.  Go to '💻 [ESP32] ESP32 Control'...
4.  Select 'Connect'...
5.  **BUG:** The application crashes here.

### 3. Expected Behavior
(A clear description of what you expected to happen.)

* I expected the app to successfully connect to the ESP32 on `/dev/ttyUSB0` and show a "[bold green]Connected[/bold green]" status.

### 4. Actual Behavior (The Bug)
(A description of what actually happened. **Please paste all terminal output, error messages, and logs here.** Use a code block for clarity.)

### 5. Your Development Environment
(This is critical for us to debug. Please fill out all relevant fields.)

* **Operating System:** (e.g., Kali Linux 2024.2, Parrot OS 5.3)
* **Python Version:** (e.g., Python 3.10.1)
* **ESP-IDF Version:** (Run `idf.py --version`. e.g., ESP-IDF v4.4)
* **SpyEye Version:** (e.g., v2.3.0 or the latest `main` branch)
* **Hardware:**
    * **ESP32 Board:** (e.g., ESP32-WROOM-32)
    * **Adapter 1 (Rogue AP):** (e.g., TL-WN722N v1)
    * **Adapter 2 (Uplink):** (e.g., Built-in Intel Wi-Fi)

### 6. Additional Context
(Add any other context about the problem here. For example: "This only happens on my laptop, but it works on my Raspberry Pi," or "This started happening after I re-flashed the ESP32.")
