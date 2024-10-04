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

# ------------------------- (your existing code) -------------------------

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_sql_injection', methods=['POST'])
def handle_sql_injection():
    url = request.form['url']
    results = test_sql_injection(url)
    return render_template('results.html', results=results)

@app.route('/scan_ports', methods=['POST'])
def handle_scan_ports():
    target_ip = request.form['target_ip']
    port_range_input = request.form['port_range']
    if '-' in port_range_input:
        port_range = port_range_input.split('-')
        port_range = (int(port_range[0]), int(port_range[1]))
    else:
        port_range = (int(port_range_input), int(port_range_input))
    results = scan_ports(target_ip, port_range)
    return render_template('results.html', results=results)

@app.route('/ssh_brute_force', methods=['POST'])
def handle_ssh_brute_force():
    target_ip = request.form['target_ip']
    username = request.form['username']
    password_list = request.form['password_list'].split(',')
    results = ssh_brute_force(target_ip, username, password_list)
    return render_template('results.html', results=results)

@app.route('/dos_attack', methods=['POST'])
def handle_dos_attack():
    target_url = request.form['target_url']
    threads_count = int(request.form['threads_count'])
    request_limit = int(request.form['request_limit'])
    results = dos_attack(target_url, threads_count, request_limit)
    return render_template('results.html', results=results)

@app.route('/test_xss', methods=['POST'])
def handle_xss():
    url = request.form['url']
    results = test_xss(url)
    return render_template('results.html', results=results)

@app.route('/generate_report', methods=['POST'])
def handle_generate_report():
    results = request.form.getlist('results')
    report = generate_report(results)
    return send_file(report, attachment_filename='report.pdf', as_attachment=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
