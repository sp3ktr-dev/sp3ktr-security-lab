import os
import platform
import socket
import uuid
import subprocess

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

def analyze_system(ip, os_info, listening_ports):
    findings = []

    # Check if private IP
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
        findings.append("Private network detected (likely internal system)")

    # OS detection
    if "Linux" in os_info:
        findings.append("Linux system identified")
    elif "Windows" in os_info:
        findings.append("Windows system identified")

    # Service-based observations
    if "tcp 22" in listening_ports:
        findings.append("SSH service detected (remote administration possible)")

    if "tcp 53" in listening_ports or "udp 53" in listening_ports:
        findings.append("DNS service detected")

    if "udp 68" in listening_ports:
        findings.append("DHCP client activity detected")

    if len(listening_ports) >= 3 and listening_ports != ["None detected"]:
        findings.append("Multiple network services exposed")

    findings.append("Potential lateral movement candidate")

    return findings

def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def get_defualt_gateway():
    output = run_command(["ip", "route"])
    for line in output.splitlines():
        if line.startswith("default via"):
            parts = line.split()
            return parts[2]
    return "Unavailable"

def get_subnet_info():
    output = run_command(["ip", "-4", "addr", "show"])
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("inet ") and "127.0.0.1" not in line:
            parts = line.split()
            return parts[1]
    return "Unavailable"

def get_dns_servers():
    servers = []

    try:
        with open("/etc/resolv.conf", "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    parts = line.split()
                    if len(parts) > 1:
                        servers.append(parts[1])
    except Exception:
        return ["Unavailable"]

    # If Ubuntu/systemd stub resolver is in use, get real upstream DNS
    if "127.0.0.53" in servers:
        output = run_command(["resolvectl", "status"])
        real_servers = []

        for line in output.splitlines():
            line = line.strip()

            if line.startswith("DNS Servers:"):
                dns_value = line.split(":", 1)[1].strip()
                if dns_value and dns_value not in real_servers:
                    real_servers.append(dns_value)

            elif line.startswith("Current DNS Server:"):
                dns_value = line.split(":", 1)[1].strip()
                if dns_value and dns_value not in real_servers:
                    real_servers.append(dns_value)

        return real_servers if real_servers else ["127.0.0.53"]

    # Remove duplicates while preserving order
    unique_servers = []
    for server in servers:
        if server not in unique_servers:
            unique_servers.append(server)

    return unique_servers if unique_servers else ["Unavailable"]

def get_listening_ports():
    output = run_command(["ss", "-tuln"])
    ports = set()

    for line in output.splitlines():
        line = line.strip()

        if not line or line.startswith("Netid"):
            continue

        parts = line.split()

        if len(parts) < 5:
            continue

        protocol = parts[0]
        local_address = parts[4]

        if ":" in local_address:
            port = local_address.rsplit(":", 1)[-1]
            ports.add((protocol, port))

    if not ports:
        return ["None detected"]

    sorted_ports = sorted(ports, key=lambda x: (x[0], int(x[1]) if x[1].isdigit() else x[1]))
    return [f"{protocol} {port}" for protocol, port in sorted_ports]

# -- Main ---
def main():
    print("=== Sp3ktr Security Lab - System Enumerator v1 ===")

    hostname = get_hostname()
    user = get_current_user()
    os_info = get_os_info()
    arch = get_architecture()
    ip = get_local_ip()
    mac = get_mac_address()
    dns_servers = get_dns_servers()
    listening_ports = get_listening_ports()

    print(f"Hostname     : {hostname}")
    print(f"Current User : {user}")
    print(f"OS Info      : {os_info}")
    print(f"Architecture : {arch}")
    print(f"Local IP     : {ip}")
    print(f"Default GW   : {get_defualt_gateway()}")
    print(f"Subnet/CIDR  : {get_subnet_info()}")
    print(f"MAC Address  : {mac}")
    print(f"DNS Servers  : {', '.join(dns_servers)}")

    print("\n[+] Listening Ports")
    for port in listening_ports:
        print(f"- {port}")

    print("\n[+] Attacker Perspective")
    findings = analyze_system(ip, os_info, listening_ports)

    for f in findings:
        print(f"- {f}")

if __name__ == "__main__":
    main() 
