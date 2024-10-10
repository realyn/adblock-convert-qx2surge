import requests
import os

# 配置直接在脚本中定义
CONFIG = {
    "conversions": [
        {
            "input_url": "https://raw.githubusercontent.com/ddgksf2013/Rewrite/master/AdBlock/Weibo.conf",
            "output_file": "Weibo_AdBlock.sgmodule",
            "name": "Weibo AdBlock for Surge",
            "desc": "Converted from QX Weibo AdBlock Rules"
        },
        {
            "input_url": "https://raw.githubusercontent.com/ddgksf2013/Rewrite/master/AdBlock/Ximalaya.conf",
            "output_file": "Ximalaya_AdBlock.sgmodule",
            "name": "Ximalaya AdBlock for Surge",
            "desc": "Converted from QX Ximalaya AdBlock Rules"
        }
    ]
}

def convert_to_surge(qx_content, name, desc, input_url):
    surge_content = f"#!name={name}\n"
    surge_content += f"#!desc={desc}\n"
    surge_content += f"# Surge Module Source: https://github.com/realyn/weibo-adblock-surge\n"
    surge_content += f"# Original QX Config Source: {input_url}\n\n"
    
    sections = {
        "URL Rewrite": [],
        "Map Local": [],
        "Script": [],
        "MITM": []
    }
    
    current_section = None
    
    for line in qx_content.split('\n'):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        
        if stripped_line.startswith('hostname = '):
            sections["MITM"].append(stripped_line.replace("hostname = ", "hostname = %APPEND% "))
            continue
        
        if stripped_line.startswith('#'):
            # 保存注释，但不立即添加到任何部分
            last_comment = stripped_line
            continue
        
        if "reject" in stripped_line:
            parts = stripped_line.split()
            if len(parts) >= 2:
                sections["URL Rewrite"].extend([last_comment, f"{parts[0]} - reject"])
        elif "data=" in stripped_line:
            sections["Map Local"].extend([last_comment, stripped_line])
        elif "script-response-body" in stripped_line or "script-request-body" in stripped_line:
            parts = stripped_line.split()
            if len(parts) >= 4:
                script_type = "http-response" if "script-response-body" in stripped_line else "http-request"
                pattern = parts[0]
                script_path = parts[-1]
                script_name = os.path.basename(script_path).split('.')[0]
                sections["Script"].extend([last_comment, f"{script_name} = type={script_type},pattern={pattern},requires-body=1,max-size=0,script-path={script_path}"])
        
        last_comment = ""  # 重置注释，因为它已经被使用了
    
    for section, content in sections.items():
        if content:
            surge_content += f"[{section}]\n" + "\n".join(content) + "\n\n"
    
    return surge_content

def process_file(input_url, output_file, name, desc):
    print(f"Fetching QX content from URL: {input_url}")
    response = requests.get(input_url)
    qx_content = response.text

    print(f"Fetched QX content (first 500 characters):\n{qx_content[:500]}...")
    print(f"Total length of fetched content: {len(qx_content)} characters")

    print("Starting conversion to Surge format...")
    surge_content = convert_to_surge(qx_content, name, desc, input_url)

    print(f"Generated Surge content (first 500 characters):\n{surge_content[:500]}...")
    print(f"Total length of generated Surge content: {len(surge_content)} characters")

    print(f"Attempting to write content to file: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(surge_content)
        print(f"Successfully wrote to {output_file}")
        print(f"File size: {os.path.getsize(output_file)} bytes")
    except Exception as e:
        print(f"Error handling file: {e}")
    
    # 添加调试信息
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir()}")

def main():
    for conversion in CONFIG['conversions']:
        process_file(conversion['input_url'], conversion['output_file'], conversion['name'], conversion['desc'])

if __name__ == "__main__":
    main()
