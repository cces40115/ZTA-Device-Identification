import wmi
import subprocess
import re
from datetime import datetime
import requests
from getmac import get_mac_address  # type: ignore
import netifaces as ni  # type: ignore


# 初始化 WMI 物件，用於存取硬體資訊
c = wmi.WMI()

# 取得 BIOS 相關資訊
bios_info = c.Win32_BIOS()[0]
bios_manufacturer = bios_info.Manufacturer
bios_serial_number = bios_info.SerialNumber

# 取得 CPU 相關資訊
cpu_info = c.Win32_Processor()[0]
cpu_name = cpu_info.Name
cpu_id = cpu_info.ProcessorId.strip()
cpu_cores = cpu_info.NumberOfCores

# 取得磁碟相關資訊
disk_info = c.Win32_DiskDrive()[0]
disk_model = disk_info.Model
disk_size = round(int(disk_info.Size) / (1024**3))  # 將磁碟大小轉換為 GB
disk_partitions = disk_info.Partitions
disk_file_systems = []
for partition in c.Win32_DiskPartition():
    file_system = partition.Name
    if file_system != "Unknown":
        disk_file_systems.append(file_system)
disk_file_systems = disk_file_systems if disk_file_systems else None

# 取得記憶體相關資訊
memory_info = c.Win32_PhysicalMemory()
total_memory = round(sum(int(mem.Capacity) for mem in memory_info) / (1024**3))  # 計算總記憶體容量 (GB)
memory_speed = memory_info[0].Speed
memory_model = memory_info[0].PartNumber.strip() if memory_info else None  # 記憶體型號

# 取得作業系統相關資訊
os_info = c.Win32_OperatingSystem()[0]
os_name = os_info.Name.split('|')[0]
os_version = os_info.Version
os_build_number = os_info.BuildNumber

# 取得主機名稱
hostname = os_info.CSName

# 取得 Azure AD 或 Local AD Domain
result = subprocess.run(["dsregcmd", "/status"], capture_output=True, text=True)
tenant_match = re.search(r'TenantName\s*:\s*(.*)', result.stdout)
local_ad_match = re.search(r'DomainName\s*:\s*(\S+)', result.stdout)  # 抓取 Device State 中的 DomainName

azure_ad_domain = tenant_match.group(1).strip() if tenant_match else "Not Joined"
local_ad_domain = local_ad_match.group(1).strip() if local_ad_match else "Not Joined"

# 取得時區資訊
timezone = datetime.now().astimezone().strftime('%z')
timezone = f"UTC{timezone[:3]}:{timezone[3:]}"

# 取得裝置所在位置 (根據外部 IP 判斷)
try:
    response = requests.get("https://ipinfo.io")
    data = response.json()
    location = f"{data.get('city', 'Unknown City')}, {data.get('region', 'Unknown Region')}, {data.get('country', 'Unknown Country')}"
    current_ip = data.get('ip', 'Unknown IP')
except Exception as e:
    location = f"Error: {str(e)}"
    current_ip = "Unknown IP"

# 取得網路資訊 (IP、網路遮罩、網關)
def get_network_info(mac_address):
    network_info = {}
    try:
        # 取得所有網路介面
        interfaces = ni.interfaces()

        for interface in interfaces:
            addrs = ni.ifaddresses(interface)

            # 確認介面是否有 IPv4 地址
            if ni.AF_INET in addrs:
                ip_info = addrs[ni.AF_INET][0]
                ip_address = ip_info.get('addr', 'Unknown')
                netmask = ip_info.get('netmask', 'Unknown')

                # 確認是否為指定的 MAC 地址
                if ni.AF_LINK in addrs:
                    interface_mac = addrs[ni.AF_LINK][0].get('addr', 'Unknown')
                    if interface_mac == mac_address:
                        gateways = ni.gateways()
                        gateway = gateways[ni.AF_INET][0][0] if ni.AF_INET in gateways else 'Unknown'

                        network_info = {
                            'IP': ip_address,
                            'Netmask': netmask,
                            'Gateway': gateway,
                            'MAC address': mac_address
                        }
                        break
        if not network_info:
            network_info = {
                'IP': 'Unknown',
                'Netmask': 'Unknown',
                'Gateway': 'Unknown',
                'MAC address': 'Unknown',
                'Error': 'No matching interface found'
            }
    except Exception as e:
        network_info = {
            'IP': 'Unknown',
            'Netmask': 'Unknown',
            'Gateway': 'Unknown',
            'MAC address': 'Unknown',
            'Error': f"Error: {str(e)}"
        }
    return network_info

# 取得 PC 裝置的 MAC 地址
pc_mac_address = get_mac_address()

# 取得網路資訊
network_data = get_network_info(pc_mac_address)

# 取得藍芽 MAC 地址
def get_bluetooth_mac_address():
    try:
        result = subprocess.run(["wmic", "path", "Win32_NetworkAdapterConfiguration", "get", "Description,MACAddress"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if "Bluetooth" in line:
                mac_address = line.split()[-1].strip()
                return mac_address
        return "Unknown"
    except Exception as e:
        return f"Error: {str(e)}"

bluetooth_mac_address = get_bluetooth_mac_address()

# 準備輸出結果
output = f"""
BIOS Info:
Manufacturer: {bios_manufacturer}
SerialNumber: {bios_serial_number}

CPU Info:
Name: {cpu_name}
ProcessorId: {cpu_id}
NumberOfCores: {cpu_cores}

Disk Info:
Model: {disk_model}
Size: {disk_size} GB
Partitions: {disk_partitions}
FileSystems: {disk_file_systems if disk_file_systems else 'None'}

Memory Info:
TotalSize: {total_memory} GB
MemoryModel: {memory_model}
MemorySpeed: {memory_speed} MHz

OS Info:
OSName: {os_name}
Version: {os_version}
BuildNumber: {os_build_number}

Network Info:
HostName: {hostname}
AzureADDomain: {azure_ad_domain}
LocalADDomain: {local_ad_domain}
Location: {location}
CurrentIP: {current_ip}
IP: {network_data['IP']}
Netmask: {network_data['Netmask']}
Gateway: {network_data['Gateway']}
MAC address: {network_data['MAC address']}
Bluetooth MAC address: {bluetooth_mac_address}
"""

print(output.strip())
input("Press Enter to exit...")

