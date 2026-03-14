#!/usr/bin/env python3
import os
import json
import random
import sys
import re

# --- 關鍵路徑配置 ---
BASE_DIR = "."
# 注入了語言信息的 HTML 完整路徑
CARD_HTML_PATH = os.path.join(BASE_DIR, "znsa.nintendo.com/super-mario-galaxy-movie/card/index.html")
# 卡片資源目錄（用於隨機選取 ID）
CARDS_ASSETS_DIR = os.path.join(BASE_DIR, "znsa.nintendo.com/super-mario-galaxy-movie-assets/cards/")
# 接口服務器根目錄
PROD_SERVER_DIR = os.path.join(BASE_DIR, "prod-server.de4taiqu.srv.nintendo.net")
# 001號卡片 ID (排除項)
DEFAULT_CARD_ID = "a210b829-d229-a7a4-9c20-0ca57cb6a4dc"

def get_current_language_from_html():
    """從 HTML 中提取當前注入的語言"""
    if not os.path.exists(CARD_HTML_PATH):
        return "en-US"
    try:
        with open(CARD_HTML_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'language:\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    except:
        pass
    return "en-US"

def clear_all_languages_draw():
    """遍歷所有語言目錄並清空抽卡 ID"""
    if not os.path.exists(PROD_SERVER_DIR):
        print(f"❌ 找不到目錄: {PROD_SERVER_DIR}")
        return

    # 獲取所有語言代碼目錄 (如 zh-TW, ja-JP, en-US)
    langs = [d for d in os.listdir(PROD_SERVER_DIR) if os.path.isdir(os.path.join(PROD_SERVER_DIR, d))]
    
    count = 0
    for lang in langs:
        data_file = os.path.join(PROD_SERVER_DIR, f"{lang}/smgm/cards")
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get("drawn_card_ids"):
                    data["drawn_card_ids"] = []
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"✅ 已清空語言 [{lang}] 的抽卡動畫數據")
                    count += 1
            except Exception as e:
                print(f"❌ 處理 {lang} 時出錯: {e}")
    
    if count == 0:
        print("ℹ️ 所有語言的抽卡數據原本就是空的，無需清理。")
    else:
        print(f"✨ 成功清理了 {count} 個語言環境的動畫標記。")

def update_single_draw(card_id):
    """僅更新當前 HTML 語言對應的卡片數據"""
    lang = get_current_language_from_html()
    data_file = os.path.join(PROD_SERVER_DIR, f"{lang}/smgm/cards")
    
    if not os.path.exists(data_file):
        print(f"❌ 錯誤：找不到當前語言 [{lang}] 的接口文件 {data_file}")
        return

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        data["drawn_card_ids"] = [card_id]

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"🎁 成功！已將新卡片 {card_id} 填入 [{lang}] 配置中。")
    except Exception as e:
        print(f"❌ 更新失敗: {e}")

def get_available_card_ids():
    """獲取可用的隨機 ID"""
    if not os.path.exists(CARDS_ASSETS_DIR):
        return []
    ids = [d for d in os.listdir(CARDS_ASSETS_DIR) if os.path.isdir(os.path.join(CARDS_ASSETS_DIR, d))]
    return [i for i in ids if i != DEFAULT_CARD_ID]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-r":
        # 執行全語言清理
        clear_all_languages_draw()
    else:
        # 隨機選取並寫入當前語言
        available_ids = get_available_card_ids()
        if available_ids:
            update_single_draw(random.choice(available_ids))
        else:
            print("⚠️ 沒找到可用的卡片文件夾。")
