# Rogue AP Tool

A modular, scalable, and customizable Python-based tool for creating rogue Access Points with captive portal functionality for cybersecurity testing and penetration testing purposes.

## ⚠️ Legal Disclaimer

**This tool is intended for educational purposes and authorized penetration testing only.** Using this tool on networks you do not own or without explicit permission is illegal and unethical. The authors are not responsible for any misuse of this software.

## 🔸 Features

- **Rogue Access Point Creation**: Uses `hostapd` to turn a Wi-Fi interface into a rogue AP
- **Captive Portal**: Forces connecting devices to a login page before internet access
- **Data Capture**: Logs user-submitted data (credentials, personal info) and device information
- **Device Detection**: Automatically detects Android/iOS devices and adapts portal appearance
- **Modular Architecture**: Plugin system for extending functionality
- **Multiple Logging Formats**: Supports JSON and SQLite logging
- **Webhook Integration**: Optional remote data transmission
- **Responsive Design**: Mobile-friendly captive portal interface
- **CLI Interface**: Command-line setup wizard and configuration options

## 🔸 Architecture

The tool consists of several modular components:

- **AP Control**: Manages wireless access point using `hostapd`
- **DNS Spoofing**: Uses `dnsmasq` for DHCP and DNS redirection
- **Firewall**: Configures `iptables` for HTTP traffic redirection
- **Captive Portal**: Flask-based web server for the login interface
- **Configuration**: YAML-based configuration system
- **Logging**: Structured data capture and storage

## 🔸 Requirements

### System Requirements
- Linux-based operating system (Ubuntu/Debian recommended)
- Wireless network interface capable of AP mode
- Root/sudo privileges for network configuration

### Software Dependencies
- Python 3.8+
- hostapd
- dnsmasq
- iptables

### Python Dependencies
See `requirements.txt` for the complete list.

## 🔸 Installation

1. **Clone or download the tool:**
   ```bash
   # If you have the source code
   cd rogue_ap_tool
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install hostapd dnsmasq iptables python3-pip
   ```

3. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Make the main script executable:**
   ```bash
   chmod +x main.py
   ```

## 🔸 Quick Start

### Basic Usage

1. **Run the interactive setup wizard:**
   ```bash
   sudo python3 main.py --setup
   ```

2. **Start the rogue AP with default settings:**
   ```bash
   sudo python3 main.py
   ```

3. **Start with custom parameters:**
   ```bash
   sudo python3 main.py --interface wlan0 --ssid "Free WiFi" --channel 6
   ```

### Command Line Options

```bash
usage: main.py [-h] [--config CONFIG] [--setup] [--interface INTERFACE] 
               [--ssid SSID] [--channel CHANNEL]

Rogue AP Tool - Captive Portal for Cybersecurity Testing

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Configuration file path (default: config/config.yaml)
  --setup, -s           Run interactive setup wizard
  --interface INTERFACE, -i INTERFACE
                        Wireless interface to use
  --ssid SSID           SSID for the rogue AP
  --channel CHANNEL     Channel for the rogue AP
```

## 🔸 Configuration

The tool uses a YAML configuration file (`config/config.yaml`) for customization. The configuration is automatically created with default values on first run.

### Configuration Sections

#### AP Settings
```yaml
ap_settings:
  ssid: 'Free Public WiFi'      # Access Point name
  channel: 6                    # WiFi channel (1-11)
  interface: 'wlan0'            # Wireless interface
```

#### Network Settings
```yaml
network_settings:
  local_ip: '10.0.0.1'          # IP address for the AP
  subnet_mask: '255.255.255.0'  # Subnet mask
```

#### Portal Settings
```yaml
portal_settings:
  port: 80                      # HTTP port for captive portal
  login_form_fields:            # Customizable form fields
    - name: 'username'
      label: 'Username'
      type: 'text'
    - name: 'password'
      label: 'Password'
      type: 'password'
  redirect_url_after_login: 'http://www.google.com'
```

#### Logging Settings
```yaml
logging_settings:
  enable_data_logging: true
  log_format: 'json'            # 'json' or 'sqlite'
  log_file: 'logs/captured_data.json'
```

#### Webhook Settings
```yaml
webhook_settings:
  enable_webhook: false
  webhook_url: ''               # URL to send captured data
```

#### Advanced Settings
```yaml
advanced_settings:
  enable_https_spoofing_attempts: false
  auto_shutdown: false
  plugin_paths: []              # Paths to custom plugins
```

## 🔸 Captured Data

The tool captures and logs the following information:

### Form Data
- All fields submitted through the captive portal
- Customizable based on configuration

### Device Information
- IP address
- MAC address (when available)
- User-Agent string
- Device type (Android, iOS, Windows, Mac, Linux)
- Browser information
- Operating system details
- Timestamp

### Log Formats

#### JSON Format
```json
[
  {
    "form_data": {
      "username": "user@example.com",
      "password": "password123"
    },
    "device_info": {
      "ip": "10.0.0.100",
      "mac_address": "aa:bb:cc:dd:ee:ff",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2025-01-01T12:00:00",
      "device_type": {
        "type": "android",
        "browser": "Chrome",
        "os": "Android"
      }
    }
  }
]
```

#### SQLite Format
Data is stored in a `captured_data` table with the following schema:
- `id`: Primary key
- `timestamp`: Capture timestamp
- `ip`: Client IP address
- `mac_address`: Client MAC address
- `user_agent`: Browser user agent
- `device_type`: Detected device type
- `form_data`: JSON string of form data

## 🔸 Customization

### Custom Form Fields

Modify the `portal_settings.login_form_fields` in the configuration file:

```yaml
portal_settings:
  login_form_fields:
    - name: 'email'
      label: 'Email Address'
      type: 'email'
    - name: 'phone'
      label: 'Phone Number'
      type: 'text'
    - name: 'company'
      label: 'Company'
      type: 'text'
```

### Custom Templates

The HTML template is located at `templates/login.html`. You can modify it to change the appearance of the captive portal. The template uses Jinja2 templating engine.

### Webhook Integration

Enable webhook functionality to send captured data to a remote server:

```yaml
webhook_settings:
  enable_webhook: true
  webhook_url: 'https://your-server.com/webhook'
```

The webhook will receive POST requests with JSON payload containing form data and device information.

## 🔸 Plugin System

The tool supports a plugin system for extending functionality. Plugins can be placed in the `plugins/` directory and configured in the `advanced_settings.plugin_paths` array.

### Plugin Structure

```python
class CustomPlugin:
    def __init__(self, config):
        self.config = config
    
    def on_user_login(self, form_data, device_info):
        # Custom logic when user submits login form
        pass
    
    def on_device_connect(self, device_info):
        # Custom logic when device connects to AP
        pass
```

## 🔸 Security Considerations

### For Penetration Testers

- Always obtain proper authorization before testing
- Document all activities for reporting
- Ensure data is handled securely and deleted after testing
- Follow responsible disclosure practices

### For Network Administrators

- Use this tool to test your organization's security awareness
- Monitor for rogue access points in your environment
- Implement proper wireless security policies
- Educate users about the risks of connecting to unknown networks

## 🔸 Troubleshooting

### Common Issues

#### Interface Not Supporting AP Mode
```bash
# Check if interface supports AP mode
iw list | grep -A 10 "Supported interface modes"
```

#### Permission Denied Errors
- Ensure you're running with sudo privileges
- Check that your user has access to network configuration

#### Hostapd Fails to Start
- Verify the wireless interface is not being used by NetworkManager
- Check that the interface supports the selected channel
- Ensure no other hostapd instances are running

#### DNS Resolution Issues
- Verify dnsmasq is running and configured correctly
- Check iptables rules are properly set
- Ensure the interface has the correct IP address

### Debug Mode

Run with debug output for troubleshooting:

```bash
sudo python3 main.py --config config/debug_config.yaml
```

## 🔸 File Structure

```
rogue_ap_tool/
├── main.py                     # Main entry point
├── config/
│   ├── config_manager.py       # Configuration management
│   └── config.yaml            # Configuration file
├── ap_control/
│   └── ap_control.py          # Access Point control
├── dns_spoofing/
│   └── dns_spoofing.py        # DNS spoofing functionality
├── firewall/
│   └── firewall.py            # Firewall/iptables management
├── captive_portal/
│   ├── captive_portal.py      # Portal base class
│   └── flask_app.py           # Flask web application
├── templates/
│   └── login.html             # Captive portal template
├── plugins/                   # Custom plugins directory
├── logs/                      # Log files directory
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔸 Contributing

Contributions are welcome! Please ensure that any contributions maintain the educational and ethical purpose of this tool.

### Development Guidelines

- Follow PEP 8 style guidelines
- Add appropriate documentation and comments
- Test thoroughly before submitting
- Ensure compatibility with the modular architecture

## 🔸 License

This project is provided for educational and authorized testing purposes only. Users are responsible for complying with all applicable laws and regulations.

## 🔸 Acknowledgments

- The cybersecurity community for tools and techniques
- Flask framework for the web interface
- Linux networking tools (hostapd, dnsmasq, iptables)

---

**Remember: Use this tool responsibly and only on networks you own or have explicit permission to test.**

