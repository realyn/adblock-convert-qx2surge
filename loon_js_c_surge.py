import os
import requests
from urllib.parse import urlparse
import re

def fetch_js_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch content from {url}")
        return None

def extract_metadata(js_content):
    metadata = {}
    pattern = r'/\*[\s\S]*?\*/'
    comment_block = re.search(pattern, js_content)
    if comment_block:
        lines = comment_block.group().split('\n')
        for line in lines[1:-1]:  # Skip the first and last lines
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    return metadata

def extract_rules(js_content):
    rules = []
    pattern = r'DOMAIN(?:-SUFFIX)?,\s*([^,]+),\s*REJECT'
    matches = re.findall(pattern, js_content)
    for match in matches:
        rules.append(f"DOMAIN{'-SUFFIX' if '.com' in match else ''}, {match}, REJECT")
    return rules

def extract_url_rewrites(js_content):
    rewrites = []
    pattern = r'\$done\(\{ url: \$request\.url\.replace\(/(.+?)/, "(.+?)"\) \}\);'
    matches = re.findall(pattern, js_content)
    for match in matches:
        rewrites.append(f"{match[0]} {match[1]} 302")
    return rewrites

def extract_scripts(js_content, js_url):
    scripts = []
    pattern = r'\/\*\*.+?\*\/\n.*?function\s+(\w+)'
    matches = re.findall(pattern, js_content, re.DOTALL)
    for match in matches:
        scripts.append(f"{match} = type=http-response,pattern=^https?://.*$,requires-body=1,max-size=0,script-path={js_url}")
    return scripts

def convert_to_sgmodule(js_content, js_filename, js_url):
    metadata = extract_metadata(js_content)
    base_filename = os.path.splitext(js_filename)[0]
    
    sgmodule_content = f'''#!name={metadata.get('name', base_filename)}
#!desc={metadata.get('desc', f'Converted from {js_filename}')}
'''
    
    for key, value in metadata.items():
        if key not in ['name', 'desc']:
            sgmodule_content += f'#!{key}={value}\n'
    
    rules = extract_rules(js_content)
    url_rewrites = extract_url_rewrites(js_content)
    scripts = extract_scripts(js_content, js_url)
    
    if rules:
        sgmodule_content += '\n[Rule]\n'
        sgmodule_content += '# 移除广告下发请求\n'
        sgmodule_content += 'AND, ((URL-REGEX, ^http:\/\/amdc\.m\.taobao\.com\/amdc\/mobileDispatch), (USER-AGENT, AMapiPhone*)), REJECT\n'
        sgmodule_content += '\n'.join(rules) + '\n'
    
    if url_rewrites:
        sgmodule_content += '\n[URL Rewrite]\n'
        sgmodule_content += '\n'.join(url_rewrites) + '\n'
    
    if scripts:
        sgmodule_content += '\n[Script]\n'
        sgmodule_content += '\n'.join(scripts) + '\n'
    
    sgmodule_content += '''
[MITM]
hostname = %APPEND% *
'''
    
    return sgmodule_content

def save_sgmodule(content, filename):
    os.makedirs('loon_js_c_surge', exist_ok=True)
    with open(os.path.join('loon_js_c_surge', filename), 'w') as f:
        f.write(content)

def process_js_file(js_url):
    js_content = fetch_js_content(js_url)
    if js_content:
        js_filename = os.path.basename(urlparse(js_url).path)
        sgmodule_content = convert_to_sgmodule(js_content, js_filename, js_url)
        sgmodule_filename = js_filename.replace('.js', '.sgmodule')
        save_sgmodule(sgmodule_content, sgmodule_filename)
        print(f"Converted {js_filename} to {sgmodule_filename}")

def main():
    js_urls = [
        "https://raw.githubusercontent.com/luestr/ProxyResource/refs/heads/main/Resource/Script/Weibo/Weibo_remove_ads.js",
        "https://github.com/luestr/ProxyResource/raw/refs/heads/main/Resource/Script/Amap/Amap_remove_ads.js"
    ]
    
    for url in js_urls:
        process_js_file(url)

if __name__ == "__main__":
    main()
