# 🤝 Contributing to SpyEye

<p align="center">
  <img src="https://img.shields.io/badge/Status-Contributions%20Welcome!-brightgreen?style=flat-square" alt="Contributions Welcome!">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License: MIT">
</p>

First off, thank you for considering contributing to SpyEye! This project is driven by the community, and every contribution helps make it a more powerful and stable tool for security researchers.

This document provides guidelines for contributing, whether it's through reporting a bug, suggesting a new feature, or submitting code.

## 📜 Code of Conduct

Before contributing, please take a minute to read our **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**. We enforce this code strictly to ensure that the SpyEye community remains a professional, welcoming, and inclusive environment for everyone.

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#-suggesting-enhancements-or-new-features">How Can I Contribute?</a></li>
    <li><a href="#--%EF%B8%8F-setting-up-your-development-environment">Setting Up Your Development Environment</a></li>
    <li><a href="#--pull-request-pr-workflow-">Pull Request (PR) Workflow</a></li>
    <li><a href="#-%EF%B8%8F-coding-style-guides-">Coding Style Guides</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 How Can I Contribute?
</h2>

### 🐞 Reporting Bugs

If you find a bug, please **open a new Issue** on our GitHub repository. A good bug report is essential for us to fix it. Please include:

* **A clear, descriptive title:** e.g., "Crash when selecting interface in [CONFIG] menu."
* **Your Environment:** What OS (e.g., Kali Linux 2024.1), Python version (e.g., 3.10), and ESP-IDF version are you using?
* **Steps to Reproduce:** Provide a clear, step-by-step guide on how to trigger the bug.
* **Expected Behavior:** What did you expect to happen?
* **Actual Behavior:** What happened instead? (Include full terminal output, logs, or screenshots).

### ✨ Suggesting Enhancements or New Features

We'd love to hear your ideas! Please **open a new Issue** and use the "Feature Request" template (if available).

* **Describe the feature:** What should it do? Why is it needed?
* **Pitch the solution:** How do you imagine it working?
* **Provide context:** How does this fit into the existing SpyEye architecture (e.g., is this a C2 feature, an ESP32 attack, or a new Captive Portal template)?

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Setting Up Your Development Environment
</h2>

SpyEye has a hybrid architecture, so you may need to set up one or both parts depending on what you're contributing to.

### 1. Python C2 (Host) Setup

This is for working on the main `main.py`, the `cli.py`, `flask_app.py`, or other Python modules.

```bash
git clone [https://github.com/YOUR-USERNAME/SpyEye.git](https://github.com/YOUR-USERNAME/SpyEye.git)
cd SpyEye

python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt
```
You will also need the core Linux dependencies installed, as mentioned in the main README.md (hostapd, dnsmasq, iptables).

### 2.ESP32 Probe (Firmware) Setup
This is for working on the C-based firmware in the ESP32/ESP-SpyEye directory.

This is critical: This project is built using `ESP-IDF v4.4` Using other versions may result in build errors.

```bash
# 1. Navigate to the firmware directory
cd SpyEye/ESP32/ESP-SpyEye

# 2. Set up the ESP-IDF v4.4 toolchain
# (Follow the official Espressif documentation for your OS)
# ...
# 
# 3. Once installed, activate the IDF environment
source /path/to/esp-idf-v4.4/export.sh

idf.py build
```
---
<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;"> 🚀 Pull Request (PR) Workflow </h2>

Ready to submit your code? Follow these steps to ensure a smooth review process.

* Fork the Repository: Create your own copy of Delta-Sec/SpyEye.
* Create a Feature Branch: Branch off main to keep your changes isolated.

```bash
git checkout -b feature/my-awesome-feature
```

* Commit Your Changes: Make your changes and write clear, descriptive commit messages.

```bash
git commit -m "feat(esp32): Add new parser for X frame"
git commit -m "fix(c2): Resolve crash in config menu"
```

* Push to Your Branch:
```bash
git push origin feature/my-awesome-feature
```
* Open a Pull Request (PR):

  * Go to the main SpyEye repository and click "New Pull Request".

  * Provide a clear title and a detailed description of your changes.

  * Explain what you changed and why.

  * If you are fixing an existing issue, link it (e.g., "Closes #123").

--- 
<h2 style="color: #FF5722; border-bottom: 2px solid #FF5722; padding-bottom: 10px;"> ✍️ Coding Style Guides </h2>

To maintain consistency in the codebase, we adhere to the following styles:

* Python: We follow PEP 8. Please run a linter (like flake8) over your code before submitting.

* C (ESP-IDF): We follow the official Espressif IDF C Code Style.

By contributing to SpyEye, you agree that your contributions will be licensed under its [MIT License](https://github.com/Delta-Sec/SpyEye/?tab=MIT-1-ov-file).
