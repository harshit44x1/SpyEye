import subprocess

class Firewall:
    def __init__(self, config_manager):
        
        self.config = config_manager
        self.interface = self.config.get('ap_settings.interface', 'wlan0')
        self.local_ip = self.config.get('network_settings.local_ip', '10.0.0.1')
        self.http_port = self.config.get('portal_settings.port', 80)
        self.internet_interface = self.config.get('network_settings.internet_interface', 'eth0')


    def setup_redirection(self):
        print(f"[*] Setting up iptables rules for HTTP redirection to {self.local_ip}:{self.http_port}")
        
        try:
           
            self.restore_firewall()

          
            print("[*] Setting default policies to DROP (quarantine mode)")
           
            subprocess.run(["sudo", "iptables", "-P", "FORWARD", "DROP"], check=True)
         
            subprocess.run(["sudo", "iptables", "-P", "INPUT", "DROP"], check=True)
            subprocess.run(["sudo", "iptables", "-P", "OUTPUT", "ACCEPT"], check=True)


        
            print("[*] Setting up INPUT chain rules for DHCP, DNS, and HTTP")
          
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-m", "conntrack", "--ctstate", "ESTABLISHED,RELATED", "-j", "ACCEPT"], check=True)
            
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-i", "lo", "-j", "ACCEPT"], check=True)
          
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-i", self.interface, "-p", "udp", "--dport", "67", "-j", "ACCEPT"], check=True)
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-i", self.interface, "-p", "udp", "--dport", "68", "-j", "ACCEPT"], check=True)
          
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-i", self.interface, "-p", "udp", "--dport", "53", "-j", "ACCEPT"], check=True)
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-i", self.interface, "-p", "tcp", "--dport", "53", "-j", "ACCEPT"], check=True)
           
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-i", self.interface, "-p", "tcp", "--dport", str(self.http_port), "-j", "ACCEPT"], check=True)


          
            print("[*] Setting up FORWARD chain rules")
         
            subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-i", self.internet_interface, "-o", self.interface, "-m", "state", "--state", "ESTABLISHED,RELATED", "-j", "ACCEPT"], check=True)
            
           
            subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-i", self.interface, "-o", self.internet_interface, "-p", "udp", "--dport", "53", "-j", "ACCEPT"], check=True)
            subprocess.run(["sudo", "iptables", "-A", "FORWARD", "-i", self.interface, "-o", self.internet_interface, "-p", "tcp", "--dport", "53", "-j", "ACCEPT"], check=True)


          
            print("[*] Setting up NAT rules")
         
            subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "PREROUTING", "-i", self.interface, "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", f"{self.local_ip}:{self.http_port}"], check=True)
            
         
            
       
            subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", self.internet_interface, "-j", "MASQUERADE"], check=True)

            print("[+] Iptables rules set up successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Error setting up iptables rules: {e}")
            return False

    def authenticate_user(self, ip_address):

        print(f"[*] Authenticating user: {ip_address} in firewall")
        try:
           
            subprocess.run(["sudo", "iptables", "-t", "nat", "-I", "PREROUTING", "1", "-s", ip_address, "-j", "ACCEPT"], check=True)
            
         
            subprocess.run(["sudo", "iptables", "-I", "FORWARD", "1", "-s", ip_address, "-j", "ACCEPT"], check=True)

            print(f"[+] User {ip_address} authenticated and granted internet access.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Error authenticating user {ip_address}: {e}")
            return False

    def restore_firewall(self):
        print("[*] Restoring iptables to default state...")
        try:
          
            subprocess.run(["sudo", "iptables", "-F"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "iptables", "-X"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "iptables", "-t", "nat", "-F"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "iptables", "-t", "nat", "-X"], check=True, stderr=subprocess.DEVNULL)
            
          
            subprocess.run(["sudo", "iptables", "-P", "INPUT", "ACCEPT"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "iptables", "-P", "FORWARD", "ACCEPT"], check=True, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "iptables", "-P", "OUTPUT", "ACCEPT"], check=True, stderr=subprocess.DEVNULL)
            
            print("[+] Iptables restored.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Error restoring iptables: {e}")
            return False

if __name__ == '__main__':
    print("This script is not meant to be run directly. Run main.py instead.")
