import requests
import re

def fetch_loon_plugin(url):
    response = requests.get(url)
    return response.text

def convert_to_surge(loon_content):
    # 移除 Loon 特定的头部信息
    surge_content = re.sub(r'#!.*\n', '', loon_content)
    
    # 转换脚本部分
    surge_content = re.sub(r'(.+) = type=http-response, pattern=(.+), script-path=(.+)',
                           r'\1 = type=http-response, pattern=\2, script-path=\3, requires-body=true',
                           surge_content)
    
    # 添加 MITM 的 %APPEND%
    surge_content = surge_content.replace('hostname =', 'hostname = %APPEND%')
    
    # 这里可以添加更多转换规则
    
    return surge_content

def main():
    loon_url = "https://raw.githubusercontent.com/luestr/ProxyResource/main/Tool/Loon/Plugin/Weibo_remove_ads.plugin"
    loon_content = fetch_loon_plugin(loon_url)
    surge_content = convert_to_surge(loon_content)
    
    with open('weibo_Adblock_from_loon.sgmodule', 'w') as f:
        f.write(surge_content)

if __name__ == "__main__":
    main()
