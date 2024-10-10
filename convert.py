import requests
import re
import os

def convert_to_surge(qx_content):
    surge_content = "#!name=Weibo AdBlock for Surge\n#!desc=Converted from QX Weibo AdBlock Rules\n\n"
    
    sections = {
        "[URL Rewrite]": [],
        "[Map Local]": [],
        "[Script]": [],
        "[MITM]": []
    }
    
    current_section = None
    
    for line in qx_content.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue
        if line in sections:
            current_section = line
            continue
        if not line or not current_section:
            continue
        
        if current_section == "[URL Rewrite]":
            if "reject" in line:
                parts = line.split()
                sections[current_section].append(f"{parts[0]} - reject")
        elif current_section == "[Map Local]":
            if "data=" in line:
                sections[current_section].append(line)
        elif current_section == "[Script]":
            if "type=http-response" not in line:
                line = line.replace("script-response-body", "type=http-response,requires-body=1,max-size=0,script-path=")
            sections[current_section].append(line)
        elif current_section == "[MITM]":
            if line.startswith("hostname"):
                sections[current_section].append(line.replace("hostname = ", "hostname = %APPEND% "))

    for section, content in sections.items():
        if content:
            surge_content += f"{section}\n" + "\n".join(content) + "\n\n"
    
    print(f"Generated Surge content:\n{surge_content}")
    return surge_content

# 获取原始QX配置
qx_url = "https://raw.githubusercontent.com/ddgksf2013/Rewrite/master/AdBlock/Weibo.conf"
response = requests.get(qx_url)
qx_content = response.text

print(f"Fetched QX content (first 100 characters):\n{qx_content[:100]}...")

# 转换
surge_content = convert_to_surge(qx_content)

# 写入Surge模块
output_file = 'Weibo_AdBlock.sgmodule'
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(surge_content)
    print(f"Successfully wrote to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
except Exception as e:
    print(f"Error writing to file: {e}")

print("Conversion completed.")
