import subprocess
import os
import time

class APControl:
    def __init__(self, interface, ssid, channel):
        self.interface = interface
        self.ssid = ssid
        self.channel = channel
        self.hostapd_conf_path = f"/tmp/hostapd_{self.interface}.conf"

    def _generate_hostapd_conf(self):
        config_content = f"""
interface={self.interface}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel={self.channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
        with open(self.hostapd_conf_path, "w") as f:
            f.write(config_content)

    def start_ap(self):
        print(f"[*] Starting AP on interface {self.interface} with SSID {self.ssid} on channel {self.channel}")
        self._generate_hostapd_conf()
        try:
            subprocess.run(["sudo", "ifconfig", self.interface, "up"], check=True)
            
            subprocess.run(["sudo", "iwconfig", self.interface, "mode", "Master"], check=True)

            self.hostapd_process = subprocess.Popen(["sudo", "hostapd", self.hostapd_conf_path])
            print("[+] Hostapd started successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Error starting hostapd: {e}")
            return False

    def stop_ap(self):
        print("[*] Stopping hostapd...")
        if hasattr(self, 'hostapd_process') and self.hostapd_process.poll() is None:
            self.hostapd_process.terminate()
            self.hostapd_process.wait()
            print("[+] Hostapd stopped.")
        else:
            print("[-] Hostapd not running or already stopped.")

        if os.path.exists(self.hostapd_conf_path):
            os.remove(self.hostapd_conf_path)

if __name__ == '__main__':

    ap_controller = APControl(interface="wlan0", ssid="FreeWiFi", channel="6")
    ap_controller.start_ap()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ap_controller.stop_ap()


