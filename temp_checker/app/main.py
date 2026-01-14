# for iframe in homarr

from flask import Flask
import os
import time
import requests
from dotenv import load_dotenv
import subprocess
from datetime import datetime, timedelta

app = Flask(__name__)

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
CHAT_ID =  os.getenv('CHAT_ID')

WORKER_IP =  os.getenv('WORKER_IP')
MASTER_IP =  os.getenv('MASTER_IP')
PORT =  os.getenv('PORT')

def get_cpu_temperature(ip, port):
    try:
        result = subprocess.run(
            f"curl -s http://{ip}:{port}/temp", 
            shell=True, capture_output=True, text=True
        )
        temp_str = result.stdout.strip()
        if temp_str:
            return int(temp_str) / 1000
        return None
    except:
        return None

def send_telegram_api(message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def index():
    """main page with temperature"""
    temp = get_cpu_temperature(WORKER_IP, PORT)
    temp_master = get_cpu_temperature(MASTER_IP, PORT)

    print(temp)
    print(temp_master)
    
    if temp >= 70.0:
        message = f"ALERT! Temperature on worker = {temp:.1f}!!!"
        send_telegram_api(message)
        print(message)

    if temp_master >= 70.0:
        message = f"ALERT! Temperature on master = {temp_master:.1f}!!!"
        send_telegram_api(message)
        print(message)
    
    if temp and temp_master is not None:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CPU Temperature</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="5">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #121212;
                    margin: 0;
                    padding: 0;
                }}
                .temp-container {{
                    background: linear-gradient(145deg, #1e1e1e, #2a2a2a);
                    padding: 45px 35px;
                    border-radius: 0 0 16px 0;
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5),
                                0 0 0 1px rgba(255, 255, 255, 0.05);
                    text-align: center;
                    max-width: 250px;
                    width: 90%;
                    position: fixed;
                    top: 0;
                    left: 0;
                }}
                .temp-value {{
                    font-size: 42px;
                    font-weight: 700;
                    color: #ffffff;
                    letter-spacing: -0.5px;
                    margin: 10px 0 5px 0;
                    text-shadow: 0 2px 10px rgba(0, 200, 255, 0.3);
                }}
                .temp-unit {{
                    font-size: 24px;
                    color: #64b5f6;
                    font-weight: 500;
                }}
                .timestamp {{
                    color: #b0b0b0;
                    margin-top: 12px;
                    font-size: 14px;
                    letter-spacing: 0.5px;
                }}
                h1 {{
                    margin: 0;
                    font-size: 18px;
                    color: #e0e0e0;
                    font-weight: 500;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                }}
                .cpu-label {{
                    color: #64b5f6;
                    font-weight: 600;
                }}
                .subtext {{
                    color: #888;
                    font-size: 11px;
                    margin-top: 15px;
                    letter-spacing: 0.5px;
                }}
            </style>
        </head>
        <body>
            <div class="temp-container">
                <h1><span class="cpu-label">CPU WORKER</span> Temperature</h1>
                <div class="temp-value">{temp:.1f}<span class="temp-unit">°C</span></div>

                <h1><span class="cpu-label">CPU MASTER</span> Temperature</h1>
                <div class="temp-value">{temp_master:.1f}<span class="temp-unit">°C</span></div>
                <div class="timestamp">{(datetime.now() + timedelta(hours=3)).strftime('%H:%M:%S')}</div>
            </div>
        </body>
        </html>
        """
        return html
    else:
        return "<h1>failed to get CPU temperature</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8013, debug=False)
