#!/usr/bin/env python3
import os
import re
import random
import string

def get_mii_config():
    """读取外部 mii.config 文件"""
    config = {"nickName": "Mii", "birthday": "1900-01-01","language": "ja-JP"}
    config_path = "mii.config"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=', 1)
                    config[k] = v
    return config

def generate_random_id():
    """生成随机的 Nintendo Account ID"""
    return ''.join(random.choices(string.hexdigits.lower(), k=16))

def get_v43_script(config):
    """生成 V43 模拟器脚本字符串"""
    random_id = generate_random_id()
    return f"""
<script id="nintendo-emulator-v43">
(function() {{
    const MOCK_DATA = {{
        nintendoAccount: {{
            nintendoAccountId: "{random_id}",
            nickName: "{config['nickName']}",
            country: "JP",
            birthday: "{config['birthday']}",
            iconUrl: window.location.origin + "/mii_images/me.png"
        }}
    }};
    const _rawPostMessage = window.postMessage;
    window.addEventListener('message', function(event) {{
        if (event.data && typeof event.data === 'string' && event.data.includes('"success":')) return;
        let req;
        try {{ req = JSON.parse(event.data); }} catch(e) {{ return; }}
        const rid = req.requestId;
        if (!rid) return;
        const sendResponse = (payload) => {{
            _rawPostMessage.call(window, JSON.stringify({{ requestId: rid, success: payload }}), window.location.origin);
        }};
        if (req.method === "getInitialData") {{
            sendResponse({{
                token: "MOCK_TOKEN_" + Math.floor(Math.random()*1000),
                localizeInfo: {{ language: "{config['language']}", country: "JP" }},
                serverTime: Math.floor(Date.now() / 1000),
                platformInfo: {{ applicationVersion: "3.0.0", operatingSystem: "android" }}
            }});
        }} else if (req.method === "getNintendoAccount") {{
            sendResponse(MOCK_DATA);
        }}
    }}, true);
    const bridge = {{ postMessage: function(msg) {{ _rawPostMessage.call(window, msg, window.location.origin); }} }};
    window.aquavast = bridge;
    if (!window.webkit) window.webkit = {{ messageHandlers: {{}} }};
    window.webkit.messageHandlers.aquavast = bridge;
    const _fetch = window.fetch;
    window.fetch = function(url, options) {{
        if (options && (options.method === 'PUT' || options.method === 'POST')) {{
            return Promise.resolve(new Response(JSON.stringify({{status:"ok"}}), {{ status: 200, headers: {{'Content-Type': 'application/json'}} }}));
        }}
        return _fetch.apply(this, arguments);
    }};
}})();
</script>
"""

def process_files(root_dir):
    mii_cfg = get_mii_config()
    v43_html_snippet = get_v43_script(mii_cfg)

    url_replacements = [
        ("https://cdn-mii.accounts.nintendo.com", "/cdn-mii.accounts.nintendo.com"),
        ("https://events.nintendo.com", "/events.nintendo.com"),
        ("https://ncl-gcd-araragi-live.firebaseapp.com", "/ncl-gcd-araragi-live.firebaseapp.com"),
        ("https://prod-server.de4taiqu.srv.nintendo.net", "/prod-server.de4taiqu.srv.nintendo.net"),
        ("https://prod-web-sdk-znsa.de4taiqu.srv.nintendo.net", "/prod-web-sdk-znsa.de4taiqu.srv.nintendo.net"),
        ("https://prod-webview-znsa.de4taiqu.srv.nintendo.net", "/prod-webview-znsa.de4taiqu.srv.nintendo.net"),
        ("https://prod-znsa.de4taiqu.srv.nintendo.net", "/prod-znsa.de4taiqu.srv.nintendo.net"),
        ("https://storage.googleapis.com", "/storage.googleapis.com"),
        ("https://znsa.nintendo.com", "/znsa.nintendo.com")
    ]

    for subdir, _, files in os.walk(root_dir):
        if any(x in subdir for x in ['.git', '__pycache__', 'mii_images']): continue

        for file in files:
            file_path = os.path.join(subdir, file)
            _, ext = os.path.splitext(file)
            
            if ext.lower() in {'.html', '.js', '.css', '.json'} or ext == "":
                try:
                    with open(file_path, 'rb') as f:
                        chunk = f.read(1024)
                        if b'\x00' in chunk: continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    new_content = content
                    modified = False

                    # 1. 域名替换
                    for old_url, new_url in url_replacements:
                        if old_url in new_content:
                            new_content = new_content.replace(old_url, new_url)
                            modified = True

                    # 2. HTML 注入 (仅限 .html)
                    if ext.lower() == '.html':
                        if '<head>' in new_content and 'nintendo-emulator-v43' not in new_content:
                            new_content = new_content.replace('<head>', f'<head>{v43_html_snippet}')
                            modified = True
                            print(f"💉 已注入模拟器脚本: {file}")

                    if modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"✅ 已处理文件: {file}")

                except Exception as e:
                    print(f"❌ 错误 {file}: {e}")

if __name__ == "__main__":
    process_files(".")
    print("\n✨ 本地化与脚本注入完成！")
