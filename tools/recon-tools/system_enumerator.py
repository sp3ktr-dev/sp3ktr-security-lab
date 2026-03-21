import os
import platform
import socket
import uuid

def get_hostname():
    return socket.gethostname()

def get_current_user():
    try:
        return os.getlogin()
    except OSError:
        return os.environ.get("USER") or os.environ.get("USERNAME") or "Unknown"

def get_os_info():
    try:
        return platform.platform()
    except Exception:
        return "Unavailable"

def get_architecture():
    return platform.machine()

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "Unavailable"

def get_mac_address():
    try:
        mac = uuid.getnode()
        mac_hex = f"{mac:012X}"
        return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2))
    except Exception:
        return "Unavailable"

def analyze_system(ip, os_info):
    findings = []

    # Check if private IP
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        findings.append("Private network detected (likely internal system)")

    # OS detection
    if "Linux" in os_info:
        findings.append("Linux system identified")
    elif "Windows" in os_info:
        findings.append("Windows system identified")

    # Basic attack surface thought
    findings.append("Potential lateral movement candidate")

    return findings

def main():
    print("=== Sp3ktr Security Lab - System Enumerator v1 ===")

    hostname = get_hostname()
    user = get_current_user()
    os_info = get_os_info()
    arch = get_architecture()
    ip = get_local_ip()
    mac = get_mac_address()

    print(f"Hostname     : {hostname}")
    print(f"Current User : {user}")
    print(f"OS Info      : {os_info}")
    print(f"Architecture : {arch}")
    print(f"Local IP     : {ip}")
    print(f"MAC Address  : {mac}")

    print("\n[+] Attacker Perspective")
    findings = analyze_system(ip, os_info)

    for f in findings:
        print(f"- {f}")

if __name__ == "__main__":
    main() 
