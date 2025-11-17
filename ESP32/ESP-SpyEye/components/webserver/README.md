# 🌐 ESP32 Component: Standalone Web Server

<p align="center">
  <img src="https://img.shields.io/badge/Module-ESP--IDF%20Component-blueviolet?style=for-the-badge" alt="ESP-IDF Component">
  <img src="https://img.shields.io/badge/Language-C%20%7C%20HTML%20%7C%20JS-00599C?style=for-the-badge" alt="Language: C/HTML/JS">
  <img src="https://img.shields.io/badge/Dependency-esp__http__server-E27063?style=for-the-badge" alt="Dependency: esp_http_server">
</p>

---

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#---architectural-overview-the-standalone-controller">Architectural Overview (The Standalone Controller)</a></li>
    <li><a href="#--%EF%B8%8F-core-functionality-the-web-api-endpoints">Core Functionality (The Web API Endpoints)</a></li>
    <li><a href="#--%EF%B8%8F-the-web-ui-indexhtml-as-a-c-header">The Web UI (index.html as a C Header)</a></li>
    <li><a href="#--%EF%B8%8F-public-api--dependencies">Public API & Dependencies</a></li>
  </ol>
</details>

---

<h2 style="color: #007ACC; border-bottom: 2px solid #007ACC; padding-bottom: 10px;">
  💡 Architectural Overview (The Standalone Controller)
</h2>

The **`webserver`** component is what provides the "Standalone Mode" (Mode 2) for the SpyEye Attack Probe. It runs a lightweight, multithreaded HTTP server (`esp_http_server`) that activates when the ESP32 boots.

This server runs on the **SpyEye AP** (the Management AP, default IP `192.168.33.1`). Its purpose is to serve a rich, single-page-application (SPA) web interface and provide a simple REST API for controlling the probe's functions (scan, attack, download) directly from a browser, without needing the Python C2.

This component acts as a high-level frontend that translates HTTP requests into the firmware's internal event system.

---

<h2 style="color: #FFC107; border-bottom: 2px solid #FFC107; padding-bottom: 10px;">
  ⚙️ Core Functionality (The Web API Endpoints)
</h2>

The `webserver.c` file defines all the API endpoints that the web interface (`index.html`) calls.

* **`GET /`**
    * **Handler**: `uri_root_get_handler`
    * **Action**: Serves the main web interface. It responds with `Content-Encoding: gzip` and sends the `page_index` byte array from `pages/page_index.h`.

* **`GET /ap-list`**
    * **Handler**: `uri_ap_list_get_handler`
    * **Action**: Triggers a Wi-Fi scan by calling `wifictl_scan_nearby_aps()`. It then serializes the list of found APs (`ssid`, `bssid`, `rssi`) into a custom 40-byte binary chunk format and sends the full list back to the browser.

* **`POST /run-attack`**
    * **Handler**: `uri_run_attack_post_handler`
    * **Action**: This is the endpoint that starts an attack. The browser sends a small binary payload matching the `attack_request_t` struct (ap_id, type, method, timeout). The server receives this and immediately publishes a `WEBSERVER_EVENT_ATTACK_REQUEST` event, passing the struct to any listening components (like `attack.c`).

* **`GET /status`**
    * **Handler**: `uri_status_get_handler`
    * **Action**: The endpoint used by the UI to poll for real-time attack status. It calls `attack_get_status()` from the `main` component. It sends back the 4-byte `attack_status_t` struct, and if the attack is `FINISHED` or `TIMEOUT`, it appends the full result content (like the PMKID) to the response body.

* **`HEAD /reset`**
    * **Handler**: `uri_reset_head_handler`
    * **Action**: Called when the "New Attack" button is pressed. It publishes a `WEBSERVER_EVENT_ATTACK_RESET` event, telling the `main` component to free all attack-related memory and return to the `READY` state.

* **`GET /capture.pcap`**
    * **Handler**: `uri_capture_pcap_get_handler`
    * **Action**: Provides the download link for PCAP files. It calls `pcap_serializer_get_buffer()` and `pcap_serializer_get_size()` and sends the complete in-memory PCAP file directly to the user's browser.

* **`GET /capture.hccapx`**
    * **Handler**: `uri_capture_hccapx_get_handler`
    * **Action**: Provides the download link for Hashcat files. It calls `hccapx_serializer_get()` and sends the complete `hccapx_t` struct directly to the user's browser.

---

<h2 style="color: #9C27B0; border-bottom: 2px solid #9C27B0; padding-bottom: 10px;">
  🏛️ The Web UI (index.html as a C Header)
</h2>

This component uses a clever build process to embed the entire web interface into the firmware binary, saving flash space and simplifying deployment.

1.  **Source (`utils/index.html`)**: This is the human-readable HTML, CSS, and JavaScript source code for the web interface. The JavaScript in this file is responsible for making all the API calls described above (e.g., `getStatus()`, `runAttack()`, `refreshAps()`).
2.  **Build Script (`utils/convert_html_to_header_file.sh`)**: This shell script is **not** run by the ESP32. It is a utility for the developer. It first compresses `index.html` using `gzip`, then uses `xxd` to convert the gzipped binary file into a C header file (a large `unsigned char[]` array).
3.  **Output (`pages/page_index.h`)**: This is the auto-generated C header file. It is the *only* file from the UI that is actually compiled into the firmware. The `webserver.c` includes this file and serves this byte array at the root (`/`) endpoint.

---

<h2 style="color: #4CAF50; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
  🛠️ Public API & Dependencies
</h2>

### Public Functions
* `void webserver_run()`: The only public function. It initializes and starts the HTTP server.

### Events Published
* `WEBSERVER_EVENT_ATTACK_REQUEST`: Fired when the user starts an attack from the web UI.
* `WEBSERVER_EVENT_ATTACK_RESET`: Fired when the user resets the attack state from the web UI.

### Dependencies
As defined in `CMakeLists.txt`, this component is high-level and relies on many other components to function:
* **`hccapx_serializer`**: To get the captured handshake data.
* **`pcap_serializer`**: To get the captured PCAP data.
* **`esp_http_server`**: The underlying Espressif HTTP server library.
* **`wifi_controller`**: To trigger Wi-Fi scans.
* **`main`**: To access the attack state functions (`attack_get_status`, etc.).
