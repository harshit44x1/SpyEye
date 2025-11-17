class ExamplePlugin:
    def __init__(self, config):
        self.config = config
        self.name = "Example Plugin"
        print(f"[*] {self.name} initialized")

    def on_user_login(self, form_data, device_info):

        print(f"[{self.name}] User login detected:")
        print(f"  - IP: {device_info.get('ip', 'unknown')}")
        print(f"  - Device: {device_info.get('device_type', {}).get('type', 'unknown')}")
        print(f"  - Form data: {form_data}")

    def on_device_connect(self, device_info):

        print(f"[{self.name}] Device connected:")
        print(f"  - IP: {device_info.get('ip', 'unknown')}")
        print(f"  - MAC: {device_info.get('mac_address', 'unknown')}")

    def on_portal_request(self, request_info):

        print(f"[{self.name}] Portal request: {request_info.get('path', '/')}")


def get_plugin_class():
    return ExamplePlugin

