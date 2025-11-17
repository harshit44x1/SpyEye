import re
import os
import sys
from art import text2art
from InquirerPy import prompt
from InquirerPy.base.control import Choice
from shared import console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.columns import Columns


TOOL_NAME = "SpyEye"
TOOL_VERSION = "2.3.0"
TOOL_DESCRIPTION = "By Delta-Security"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(subtitle_text=None):
    clear_screen()
    
    logo_art = text2art("Spy Eye", font="roman")
    
    title = Text(f"  {TOOL_NAME}  ", style="bold white on red")
    version = Text(f"v{TOOL_VERSION}", style="bold red")

    logo_renderable = Align.center(
        Text(logo_art , style="#FF5700") +
        Text(f"\n{TOOL_DESCRIPTION}", justify="center", style="blue")
    )
    
   
  
    dev_table = Table(show_header=False, box=None, padding=(0, 1))
    dev_table.add_row("[bold]Team[/bold]:", "Delta-Security")
    dev_table.add_row("[bold]GitHub[/bold]:", "[link=https://github.com/delta-sec]github.com/Delta-Sec[/link]")
    dev_table.add_row("[bold]Status[/bold]:", "[green]Operational[/green]")
  
    
    dev_panel = Panel(
        dev_table,
        title="[bold white]About[/bold white]",
        border_style="blue",
        padding=(1, 2),
        width=40  
    )

    
    layout = Columns([
        logo_renderable,
        dev_panel
    ], expand=True, align="center")
    
   
    final_subtitle = Text(subtitle_text, style="bold yellow") if subtitle_text else version
    header_panel = Panel(
        layout,
        title=title,
        subtitle=final_subtitle,
        border_style="red",
        padding=(1, 2),
        title_align="center",
        subtitle_align="right"
    )
    console.print(header_panel)
    
  

def main_menu():

    display_header()
    
    questions = [
        {
            "type": "list",
            "message": "Select the desired action:",
            "choices": [
                Choice(value="start", name="🚀 [START] Start Rogue Access Point Attack"),
                Choice(value="config", name="⚙️ [CONFIG] Tool Configuration"),
                Choice(value="esp32_control", name="💻 [ESP32] ESP32 Control"),
                Choice(value="exit", name="🚪 [EXIT] Exit and Cleanup"),
            ],
            "default": "start",
            "name": "action",
            "mandatory": True,
            "instruction": "Use arrow keys to select",
        }
    ]
    
    try:
        console.print() 
        result = prompt(questions)
        if not result:
             return "exit"
        return result.get("action", "exit")
    except KeyboardInterrupt:
        return "exit"

def interactive_setup(config_manager, ap_tool):

    
    clear_screen()
    console.print(Panel("[bold yellow]Tool Configuration Wizard[/bold yellow]", border_style="yellow", expand=False, title_align="center"))
    

    try:
        all_interfaces = ap_tool._get_all_interfaces()
        wireless_interfaces = ap_tool._get_wireless_interfaces()
    except Exception as e:
        console.print(Panel(f"[bold red]Error fetching interfaces: {e}[/bold red]", border_style="red"))
        return False

    if not wireless_interfaces:
        console.print(Panel("[bold red]No wireless interfaces found! Cannot proceed.[/bold red]", border_style="red"))
        return False


    ap_interface_q = [
        {
            "type": "list",
            "message": "Select Access Point Interface (for Wi-Fi broadcast):",
            "choices": [Choice(i, name=i) for i in wireless_interfaces],
            "default": config_manager.get('ap_settings.interface', wireless_interfaces[0]),
            "name": "ap_interface",
            "mandatory": True,
        }
    ]
    ap_interface_result = prompt(ap_interface_q)
    if not ap_interface_result:
        return False
    ap_interface = ap_interface_result.get("ap_interface")

    internet_interface_q = [
        {
            "type": "list",
            "message": "Select Internet Interface (for Internet access/forwarding):",
            "choices": [Choice(i, name=i) for i in all_interfaces],
            "default": config_manager.get('network_settings.internet_interface', 'eth0'),
            "name": "internet_interface",
            "mandatory": True,
        }
    ]
    internet_interface_result = prompt(internet_interface_q)
    if not internet_interface_result:
        return False
    internet_interface = internet_interface_result.get("internet_interface")

    ssid_q = [
        {
            "type": "input",
            "message": "Enter Network Name (SSID):",
            "default": config_manager.get('ap_settings.ssid', 'Free Public WiFi'),
            "name": "ssid",
            "mandatory": True,
        }
    ]
    ssid_result = prompt(ssid_q)
    if not ssid_result:
        return False
    ssid = ssid_result.get("ssid")

    channel_q = [
        {
            "type": "input",
            "message": "Enter Channel (1-14):",
            "default": str(config_manager.get('ap_settings.channel', 6)),
            "name": "channel",
            "validate": lambda c: c.isdigit() and 1 <= int(c) <= 14,
            "filter": lambda c: int(c) if c.isdigit() else 6,
            "mandatory": True,
        }
    ]
    channel_result = prompt(channel_q)
    if not channel_result:
        return False
    channel = channel_result.get("channel")
    
    console.print(Panel(
        f"To prevent conflicts, the interface [bold cyan]{ap_interface}[/bold cyan] must be made unmanaged by NetworkManager.",
        title="[bold red]NetworkManager Configuration[/bold red]",
        border_style="red",
        expand=False
    ))
    
    nm_config_q = [
        {
            "type": "confirm",
            "message": "Do you want to configure NetworkManager automatically now?",
            "default": True,
            "name": "configure_nm",
        }
    ]
    nm_config_result = prompt(nm_config_q)
    if not nm_config_result:
        return False
    configure_nm = nm_config_result.get("configure_nm")
    
    if configure_nm:
        ap_tool._configure_network_manager(ap_interface)

    config_manager.set('ap_settings.interface', ap_interface)
    config_manager.set('network_settings.internet_interface', internet_interface)
    config_manager.set('ap_settings.ssid', ssid)
    config_manager.set('ap_settings.channel', channel)
    
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_row("Access Point Interface:", f"[cyan]{ap_interface}[/cyan]")
    summary_table.add_row("Internet Interface:", f"[cyan]{internet_interface}[/cyan]")
    summary_table.add_row("Network Name (SSID):", f"[cyan]{ssid}[/cyan]")
    summary_table.add_row("Channel:", f"[cyan]{channel}[/cyan]")

    console.print(Panel(
        summary_table,
        title="[bold green]Settings saved successfully![/bold green]",
        border_style="green",
        expand=False
    ))
    
    console.input("\nPress Enter to return to the main menu...")

    return True
    
def esp32_menu(controller):

    while True:
            status_text = '[bold green]Connected[/bold green]' if controller.serial_conn and controller.serial_conn.is_open else '[bold red]Disconnected[/bold red]'
            display_header(f"ESP32 Control - Status: {status_text}")
            
            choices = [
                Choice("Connect", name="[bold green]Connect[/bold green] - Connect to ESP32"),
                Choice("Disconnect", name="[bold red]Disconnect[/bold red] - Disconnect from ESP32"),
                Choice("Status", name="[bold yellow]Status[/bold yellow] - Get ESP32 Status"),
                Choice("Scan", name="[bold cyan]Scan[/bold cyan] - Start Wi-Fi Scan"),
                Choice("Deauth", name="[bold red]Deauth[/bold red] - Start Deauthentication Attack"),
                Choice("Back", name="[bold blue]Back[/bold blue] - Return to Main Menu"),
            ]
    
            questions = [
                {
                    "type": "list",
                    "message": "Select an ESP32 operation:",
                    "choices": choices,
                    "name": "esp32_choice",
                }
            ]
            
            result = prompt(questions)
            choice = result.get("esp32_choice") if result else "Back"
    
            if choice == "Connect":
                port_q = [
                    {
                        "type": "input",
                        "message": "Enter Serial Port (e.g., /dev/ttyUSB0):",
                        "name": "port",
                        "default": controller.port,
                    }
                ]
                port_result = prompt(port_q)
                if port_result:
                    controller.port = port_result.get("port")
                    controller.connect()
                
            elif choice == "Disconnect":
                controller.disconnect()
                
            elif choice == "Status":
                console.print(Panel(controller.get_status(), title="[bold yellow]ESP32 Status[/bold yellow]", border_style="yellow"))
                input("Press Enter to continue...")
                
            elif choice == "Scan":
                console.print(Panel(controller.start_scan(), title="[bold cyan]Wi-Fi Scan Results[/bold cyan]", border_style="cyan"))
                input("Press Enter to continue...")
    
            elif choice == "Deauth":
                
                mac_regex = r"^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$"
                
                def is_valid_mac(text):
                	return re.match(mac_regex, text, re.IGNORECASE) is not None
                
                invalid_mac_msg = "Invalid format. Please use XX:XX:XX:XX:XX:XX"
                
                deauth_q = [
                    {"type": "input", "message": "Target MAC (Client):", "name": "target_mac"},
                    {"type": "input", "message": "AP MAC (Router):", "name": "ap_mac"},
                    {"type": "input", "message": "Count (0 for infinite):", "name": "count", "default": "0"},
                ]
                deauth_result = prompt(deauth_q)
                if deauth_result:
                    target = deauth_result.get("target_mac")
                    ap = deauth_result.get("ap_mac")
                    count = deauth_result.get("count")
                    console.print(Panel(controller.start_deauth(target, ap, count), title="[bold red]Deauth Attack Status[/bold red]", border_style="red"))
                    input("Press Enter to continue...")
                
            elif choice == "Back":
                break
    
    if __name__ == '__main__':
        display_header()
        action = main_menu()
        console.print(f"\n[bold]Selected action:[/bold] {action}")
