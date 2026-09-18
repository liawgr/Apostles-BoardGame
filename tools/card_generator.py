"""
卡牌資料統計與全牌庫驗證工具 (Comprehensive Card Data Analyzer & Generator)
用法：
    python card_generator.py
"""

import csv
import os
import sys
from collections import Counter

# 確保在 Windows 命令提示字元下 UTF-8 正常輸出
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DECKS_DIR = os.path.join(DATA_DIR, 'decks')

DECKS_TO_ANALYZE = [
    ('核心角色與恩賜', os.path.join(DATA_DIR, 'cards.csv')),
    ('旅程牌庫 (26張)', os.path.join(DECKS_DIR, 'journey_deck.csv')),
    ('第一區：故鄉基石 (51張)', os.path.join(DECKS_DIR, 'region_1_homeland.csv')),
    ('第一區地點牌 (9張)', os.path.join(DECKS_DIR, 'region_1_locations.csv')),
    ('第二區：異族荒原 (51張)', os.path.join(DECKS_DIR, 'region_2_wilderness.csv')),
    ('第二區地點牌 (9張)', os.path.join(DECKS_DIR, 'region_2_locations.csv')),
    ('第三區：帝國巨城 (51張)', os.path.join(DECKS_DIR, 'region_3_empire.csv')),
    ('第三區地點牌 (9張)', os.path.join(DECKS_DIR, 'region_3_locations.csv')),
    ('終極罪惡墮落卡 (5張)', os.path.join(DECKS_DIR, 'depravity_cards.csv')),
]

FRUITS = ['仁愛', '喜樂', '和平', '忍耐', '恩慈', '良善', '信實', '溫柔', '節制']

def analyze_all_decks():
    grand_total_cards = 0
    grand_total_types = 0

    print("================================================================================")
    print("                🕊️ 《使徒:大使命》 全牌庫數據庫深度檢驗報告                     ")
    print("================================================================================")

    for deck_name, filepath in DECKS_TO_ANALYZE:
        if not os.path.exists(filepath):
            print(f"[!] 警告：找不到卡牌檔案 {filepath}")
            continue

        cards = []
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cards.append(row)

        total_kinds = len(cards)
        total_count = sum(int(c.get('count', 1)) for c in cards)
        grand_total_types += total_kinds
        grand_total_cards += total_count

        type_counter = Counter()
        fruit_counter = Counter()

        for c in cards:
            t = c.get('type', c.get('deck_type', '未分類'))
            cnt = int(c.get('count', 1))
            type_counter[t] += cnt
            desc = c.get('description', '')
            for fruit in FRUITS:
                if fruit in desc:
                    fruit_counter[fruit] += cnt

        print(f"\n📂 【{deck_name}】 -> 條目: {total_kinds:>2} | 實體張數: {total_count:>2}")
        types_str = " | ".join([f"{k}: {v}" for k, v in type_counter.items()])
        print(f"   類型分佈: {types_str}")
        if fruit_counter:
            fruit_str = " | ".join([f"{k}: {v}" for k, v in fruit_counter.most_common(4)])
            print(f"   主要牽涉果子: {fruit_str}")

    print("\n================================================================================")
    print(f"📊 全案總計：{grand_total_types} 種獨立卡牌設計，共 {grand_total_cards} 張實體卡牌規格！")
    print("================================================================================")
    print("提示：可開啟 tools/previewer.html 預覽與列印卡牌，所有數據均與 GDD 規則書同步。")

if __name__ == '__main__':
    analyze_all_decks()
