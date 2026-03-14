#!/usr/bin/env python3
import json
import os
import requests
import argparse
from urllib.parse import urlparse
import sys

def load_tokens():
    """從同路徑下的 har.token 讀取配置"""
    configs = {'COOKIE': '', 'BEARER': '', 'UA': 'com.nintendo.znsa/3.0.0 (Android 13)'}
    token_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'har.token')
    
    if not os.path.exists(token_path):
        print(f"⚠️  警告：找不到 {token_path}，將使用空值執行。")
        return configs

    with open(token_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if ':' in line:
                key, value = line.split(':', 1)
                configs[key.strip().upper()] = value.strip()
    return configs

def download_from_har(har_path, output_dir, force_update=False):
    tokens = load_tokens()
    
    if not os.path.exists(har_path):
        print(f"❌ 错误：找不到文件 {har_path}")
        return

    print(f"📖 正在解析 HAR: {har_path}")
    try:
        with open(har_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")
        return

    entries = har_data.get('log', {}).get('entries', [])
    session = requests.Session()
    
    # 允许的域名
    allowed_keywords = ['nintendo.com', 'nintendo.net', 'storage.googleapis.com']
    download_count = 0
    skip_count = 0

    for entry in entries:
        request_data = entry.get('request', {})
        url = request_data.get('url', '')
        method = request_data.get('method', '')

        if method != 'GET' or not any(kw in url for kw in allowed_keywords):
            continue

        # 1. 提取 HAR 原始 Headers
        headers = {h['name'].lower(): h['value'] for h in request_data.get('headers', [])}
        for pseudo in [':authority', ':method', ':path', ':scheme']:
            headers.pop(pseudo, None)

        # 2. 基礎 UA 設定
        headers['user-agent'] = tokens['UA']

        # 3. 智能 Header 注入邏輯
        if 'nintendo.net' in url:
            # API 域名：需要 Cookie + Bearer
            headers.pop('cookie', None)
            if tokens['BEARER']:
                bearer = tokens['BEARER']
                headers['authorization'] = bearer if bearer.startswith('Bearer ') else f'Bearer {bearer}'
            headers['application-version'] = '3.0.0'
            headers['operating-system'] = 'android'
        elif 'nintendo.com' in url:
            # 靜態資源域名：只需要 Cookie，禁用 Authorization
            if tokens['COOKIE']: headers['cookie'] = tokens['COOKIE']
            headers.pop('authorization', None)
        else:
            # Google Storage 或其他：移除敏感資訊，避免 Google 403
            headers.pop('cookie', None)
            headers.pop('authorization', None)
            headers.pop('x-requested-with', None)

        # 4. 路径处理
        parsed_url = urlparse(url)
        relative_path = parsed_url.path.lstrip('/')
        if not relative_path or url.endswith('/'):
            relative_path = os.path.join(relative_path, 'index.html')

        local_path = os.path.join(output_dir, parsed_url.netloc, relative_path)
        etag_path = local_path + ".etag"

        # 5. 增量檢查 (ETag + Size)
        should_download = True
        if os.path.exists(local_path) and not force_update:
            try:
                head_res = session.head(url, headers=headers, timeout=5)
                if head_res.status_code == 200:
                    remote_size = int(head_res.headers.get('Content-Length', 0))
                    remote_etag = head_res.headers.get('ETag', '').strip('"')
                    
                    local_size = os.path.getsize(local_path)
                    local_etag = ""
                    if os.path.exists(etag_path):
                        with open(etag_path, 'r') as f: local_etag = f.read().strip()

                    if (remote_etag and remote_etag == local_etag) or (not remote_etag and remote_size == local_size):
                        should_download = False
                        skip_count += 1
                        continue
            except: pass

        # 6. 執行下載
        if should_download:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            try:
                print(f"📥 正在下载: {url}")
                r = session.get(url, headers=headers, timeout=15)
                if r.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(r.content)
                    if 'ETag' in r.headers:
                        with open(etag_path, 'w') as f: f.write(r.headers['ETag'].strip('"'))
                    download_count += 1
                else:
                    print(f"❌ 请求失败 ({r.status_code}): {url}")
            except Exception as e:
                print(f"🔥 网络错误: {url} -> {e}")

    print(f"\n✨ 任务完成！下载/更新: {download_count}, 跳过: {skip_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nintendo HAR Advanced Downloader")
    parser.add_argument("har_file", help="Path to the .har file")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    parser.add_argument("-f", "--force", action="store_true", help="Force re-download")
    
    args = parser.parse_args()
    download_from_har(args.har_file, args.output, args.force)
