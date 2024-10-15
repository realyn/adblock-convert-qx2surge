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

def convert_to_sgmodule(js_content, js_filename, js_url):
    # Extract metadata from the first comment block
    metadata_match = re.search(r'/\*([\s\S]*?)\*/', js_content)
    metadata = metadata_match.group(1) if metadata_match else ''
    
    # Start building the sgmodule content
    sgmodule_content = f'''#!name={js_filename.replace('.js', '')}
#!desc=Converted from {js_filename}
{metadata.strip()}

[Script]
{js_filename.replace('.js', '')} = type=http-response,pattern=^https?://.*$,requires-body=1,max-size=0,script-path={js_url}

[MITM]
hostname = %APPEND% *
'''

    # Extract URL Rewrite rules
    url_rewrite_rules = re.findall(r'(\^https?://.*?) url (reject-dict|reject-array|reject-200|reject-img|reject|request-body|response-body|echo-response|script-response-body|script-request-header|script-request-body|script-response-header|script-echo-response|script-analyze-echo-response).*', js_content)
    
    if url_rewrite_rules:
        sgmodule_content += '\n[URL Rewrite]\n'
        for rule in url_rewrite_rules:
            sgmodule_content += f'{rule[0]} - {rule[1]}\n'

    # Extract Map Local rules
    map_local_rules = re.findall(r'(\^https?://.*?) data="(.*?)"', js_content)
    
    if map_local_rules:
        sgmodule_content += '\n[Map Local]\n'
        for rule in map_local_rules:
            sgmodule_content += f'{rule[0]} data="{rule[1]}"\n'

    # Extract General rules
    general_rules = re.findall(r'(URL-REGEX|DOMAIN|DOMAIN-SUFFIX|DOMAIN-KEYWORD|IP-CIDR|IP-CIDR6|GEOIP|USER-AGENT|URL-REGEX|IP-ASN),.*', js_content)
    
    if general_rules:
        sgmodule_content += '\n[Rule]\n'
        for rule in general_rules:
            sgmodule_content += f'{rule}\n'

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
