import requests
import re
import os
import logging
from urllib.parse import urlparse

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_loon_plugin(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch plugin from {url}: {e}")
        return None

def convert_to_surge(loon_content):
    if not loon_content:
        return None
    
    try:
        # 移除 #!loon_version 行
        surge_content = re.sub(r'#!loon_version.*\n', '', loon_content)
        
        # 移除 #!system 和 #!system_version 行
        surge_content = re.sub(r'#!system.*\n', '', surge_content)
        surge_content = re.sub(r'#!system_version.*\n', '', surge_content)
        
        # 保留其他注释和元数据，但不添加额外的 #
        surge_content = re.sub(r'(#!.*\n)', r'\1', surge_content)
        
        # 转换 [Rewrite] 为 [URL Rewrite] 和 [Map Local]
        rewrite_section = re.search(r'\[Rewrite\](.*?)\[', surge_content, re.DOTALL)
        if rewrite_section:
            rewrite_content = rewrite_section.group(1)
            url_rewrite = []
            map_local = []
            for line in rewrite_content.strip().split('\n'):
                if 'reject-dict' in line:
                    map_local.append(line.replace('reject-dict', 'data="{}"\ndata-type=text'))
                else:
                    url_rewrite.append(line)
            
            surge_content = surge_content.replace('[Rewrite]', '[URL Rewrite]\n' + '\n'.join(url_rewrite) + '\n\n[Map Local]\n' + '\n'.join(map_local))
        
        # 转换脚本部分
        surge_content = re.sub(r'http-response (.*) script-path = (.*), requires-body = true, tag = (.*)',
                               r'\3 = type=http-response, pattern=\1, requires-body=true, script-path=\2',
                               surge_content)
        
        # 修改 MITM 部分
        surge_content = surge_content.replace('[MitM]', '[MITM]')
        
        return surge_content
    except Exception as e:
        logging.error(f"Error during conversion: {e}")
        return None

def process_url(url):
    logging.info(f"Processing URL: {url}")
    loon_content = fetch_loon_plugin(url)
    if not loon_content:
        logging.warning(f"Skipping {url} due to fetch failure")
        return

    surge_content = convert_to_surge(loon_content)
    if not surge_content:
        logging.warning(f"Skipping {url} due to conversion failure")
        return
    
    # 从 URL 中提取文件名
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    file_name = file_name.replace('.plugin', '.sgmodule')
    
    # 使用绝对路径创建输出目录
    output_dir = os.path.join(os.getcwd(), 'loon_c_surge')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 保存文件
    output_path = os.path.join(output_dir, file_name)
    try:
        with open(output_path, 'w') as f:
            f.write(surge_content)
        logging.info(f"Converted {file_name} and saved to {output_path}")
    except IOError as e:
        logging.error(f"Failed to save file {output_path}: {e}")

def main():
    urls = [
        "https://raw.githubusercontent.com/luestr/ProxyResource/main/Tool/Loon/Plugin/Amap_remove_ads.plugin",
        "https://raw.githubusercontent.com/luestr/ProxyResource/main/Tool/Loon/Plugin/ColorfulClouds_remove_ads.plugin",
        "https://raw.githubusercontent.com/luestr/ProxyResource/main/Tool/Loon/Plugin/Weibo_remove_ads.plugin",
        "https://raw.githubusercontent.com/luestr/ProxyResource/main/Tool/Loon/Plugin/DiDi_remove_ads.plugin"
    ]
    
    for url in urls:
        process_url(url)

if __name__ == "__main__":
    main()
