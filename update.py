#!/usr/bin/env python3
import os
import re

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

def update_mii_data(root_dir):
    cfg = get_mii_config()
    
    print(f"🔄 正在同步最新配置:")
    print(f"   - 语言: {cfg['language']}")
    print(f"   - 昵称: {cfg['nickName']}")
    print(f"   - 生日: {cfg['birthday']}")

    # 定义正则模式，捕获前缀、旧值和后缀
    patterns = {
        "language": re.compile(r'(language:\s*")([^"]+)(")'),
        "nickName": re.compile(r'(nickName:\s*")([^"]+)(")'),
        "birthday": re.compile(r'(birthday:\s*")([^"]+)(")')
    }

    for subdir, _, files in os.walk(root_dir):
        # 排除不必要的目录
        if any(x in subdir for x in ['.git', '__pycache__', 'mii_images']):
            continue

        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(subdir, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 仅处理包含模拟器脚本的文件
                    if 'id="nintendo-emulator-v43"' in content:
                        new_content = content
                        
                        # 使用 lambda 替换函数，彻底避免 \1 引用冲突
                        new_content = patterns["language"].sub(lambda m: f'{m.group(1)}{cfg["language"]}{m.group(3)}', new_content)
                        new_content = patterns["nickName"].sub(lambda m: f'{m.group(1)}{cfg["nickName"]}{m.group(3)}', new_content)
                        new_content = patterns["birthday"].sub(lambda m: f'{m.group(1)}{cfg["birthday"]}{m.group(3)}', new_content)

                        if new_content != content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"✅ 已成功同步: {file_path}")
                except Exception as e:
                    print(f"❌ 错误 {file}: {e}")

if __name__ == "__main__":
    update_mii_data(".")
    print("\n✨ 处理完成！")
