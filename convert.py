import requests
import os

def convert_to_surge(qx_content):
    surge_content = "#!name=Weibo AdBlock for Surge\n#!desc=Converted from QX Weibo AdBlock Rules\n\n"
    
    sections = {
        "URL Rewrite": [],
        "Map Local": [],
        "Script": [],
        "MITM": []
    }
    
    current_section = None
    
    for line in qx_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('#'):
            continue
        
        if line.startswith('hostname = '):
            sections["MITM"].append(line.replace("hostname = ", "hostname = %APPEND% "))
            continue
        
        if "reject" in line:
            parts = line.split()
            if len(parts) >= 2:
                sections["URL Rewrite"].append(f"{parts[0]} - reject")
        elif "data=" in line:
            sections["Map Local"].append(line)
        elif "script-response-body" in line or "script-request-body" in line:
            parts = line.split()
            if len(parts) >= 4:
                script_type = "http-response" if "script-response-body" in line else "http-request"
                sections["Script"].append(f"{parts[3].split('=')[1]} = type={script_type},pattern={parts[0]},requires-body=1,max-size=0,script-path={parts[3].split('=')[1]}")
    
    for section, content in sections.items():
        if content:
            surge_content += f"[{section}]\n" + "\n".join(content) + "\n\n"
    
    return surge_content

# 获取原始QX配置
qx_url = "https://raw.githubusercontent.com/ddgksf2013/Rewrite/master/AdBlock/Weibo.conf"
print(f"Fetching QX content from URL: {qx_url}")
response = requests.get(qx_url)
qx_content = response.text

print(f"Fetched QX content (first 500 characters):\n{qx_content[:500]}...")
print(f"Total length of fetched content: {len(qx_content)} characters")

# 转换
print("Starting conversion to Surge format...")
surge_content = convert_to_surge(qx_content)

print(f"Generated Surge content (first 500 characters):\n{surge_content[:500]}...")
print(f"Total length of generated Surge content: {len(surge_content)} characters")

# 写入Surge模块
output_file = 'Weibo_AdBlock.sgmodule'
print(f"Attempting to write content to file: {output_file}")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(surge_content)
    print(f"Successfully wrote to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
    
    # 读取文件内容进行验证
    with open(output_file, 'r', encoding='utf-8') as f:
        file_content = f.read()
    print(f"Verification - File content (first 500 characters):\n{file_content[:500]}...")
    print(f"Verification - Total length of file content: {len(file_content)} characters")
except Exception as e:
    print(f"Error handling file: {e}")

print("Conversion and file writing process completed.")
