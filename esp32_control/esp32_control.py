import serial
import time
import sys
import os
from rich.console import Console

console = Console()

class ESP32Controller:

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None

    def connect(self):

        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            console.print(f"[bold green]Connected to ESP32 on {self.port}[/bold green]")
            return True
        except serial.SerialException as e:
            console.print(f"[bold red]Error connecting to ESP32 on {self.port}: {e}[/bold red]")
            self.serial_conn = None
            return False

    def disconnect(self):

        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            console.print(f"[bold yellow]Disconnected from ESP32 on {self.port}[/bold yellow]")
            self.serial_conn = None

    def send_command(self, command):

        if not self.serial_conn or not self.serial_conn.is_open:
            console.print("[bold red]Error: ESP32 not connected.[/bold red]")
            return "ERROR: Not connected"

        try:
            command_bytes = (command.strip() + '\n').encode('utf-8')
            self.serial_conn.write(command_bytes)
            

            response = ""
            start_time = time.time()
            while (time.time() - start_time) < self.timeout * 5: 
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    response += line + "\n"
                else:
                    
                    if (time.time() - start_time) > self.timeout:
                        break
            
            return response.strip()

        except Exception as e:
            console.print(f"[bold red]Error sending command to ESP32: {e}[/bold red]")
            self.disconnect()
            return f"ERROR: {e}"

    def get_status(self):
        
        return self.send_command("STATUS")

    
    def start_scan(self):
        return self.send_command("SCAN")

    def start_deauth(self, target_mac, ap_mac, count=0):
        return self.send_command(f"DEAUTH {target_mac} {ap_mac} {count}")

    
    
if __name__ == '__main__':

    controller = ESP32Controller(port='/dev/ttyUSB0')
    if controller.connect():
        print("Status:", controller.get_status())

        controller.disconnect()
    else:
        print("Failed to connect.")
