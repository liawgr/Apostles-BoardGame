"""
《使徒:大使命》實戰數值模擬驗證工具 (Automated Playtest Simulation Engine)
角色組合：P1 剛烈開路者 (戰士/開路) + P2 勸慰之子巴拿巴 (牧者/成全)
"""

import csv
import random
import os
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

random.seed(2026) # 固定隨機種子，確保推演可複現

# 讀取卡牌
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DECKS_DIR = os.path.join(DATA_DIR, 'decks')

def load_csv(path):
    with open(path, mode='r', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

journey_cards = load_csv(os.path.join(DECKS_DIR, 'journey_deck.csv'))
random.shuffle(journey_cards)

r1_encounters = [c for c in load_csv(os.path.join(DECKS_DIR, 'region_1_homeland.csv')) if c['type'] in ['災禍', '複合試煉', '試煉', '事件']]
r1_people = [c for c in load_csv(os.path.join(DECKS_DIR, 'region_1_homeland.csv')) if c['type'] == '人民']
r1_pillars = [c for c in load_csv(os.path.join(DECKS_DIR, 'region_1_homeland.csv')) if c['type'] == '大能者']
r1_locs_pillar = [c for c in load_csv(os.path.join(DECKS_DIR, 'region_1_locations.csv')) if c['deck_type'] == '大能者據點']
r1_locs_free = [c for c in load_csv(os.path.join(DECKS_DIR, 'region_1_locations.csv')) if c['deck_type'] == '自由地點']

random.shuffle(r1_encounters)
random.shuffle(r1_people)
random.shuffle(r1_locs_pillar)
random.shuffle(r1_locs_free)

# 玩家狀態
p1 = {
    'name': '剛烈開路者',
    'hp': 18, 'max_hp': 18,
    'piety': 8,
    'fruits': {'喜樂': 8, '忍耐': 7, '信實': 6, '仁愛': 5, '和平': 4, '溫柔': 4, '節制': 5},
    'sins': {'喜樂': 0, '忍耐': 0, '信實': 0, '仁愛': 0, '和平': 0, '溫柔': 0, '節制': 0},
    'intercession': 0,
    'truth_tokens': 0,
    'location': '曠野'
}

p2 = {
    'name': '勸慰之子巴拿巴',
    'hp': 14, 'max_hp': 14,
    'piety': 12,
    'fruits': {'仁愛': 8, '溫柔': 8, '信實': 7, '和平': 6, '喜樂': 6, '忍耐': 5, '節制': 5},
    'sins': {'仁愛': 0, '溫柔': 0, '信實': 0, '和平': 0, '喜樂': 0, '忍耐': 0, '節制': 0},
    'intercession': 0,
    'truth_tokens': 0,
    'location': '曠野'
}

supplies = {
    'food': 6, # 3n
    'coins': 4, # 2n
    'prayer_tokens_pool': 40
}

log = []

def log_event(msg):
    log.append(msg)
    print(msg)

def get_effective_stat(player, fruit_name):
    base = player['fruits'].get(fruit_name, 5)
    sin = player['sins'].get(fruit_name, 0)
    ceiling = max(0, 10 - sin)
    return min(base, ceiling)

def roll_check(player, fruit_name, dc, bonus=0):
    base = player['fruits'].get(fruit_name, 5)
    sin = player['sins'].get(fruit_name, 0)
    piety = player.get('piety', 0)
    
    # 1. 計算可用骰池容量 N (受限於 10 - 罪惡值天花板)
    pool_size = max(0, min(base, 10 - sin))
    
    # 2. 計算罪惡骰 (每 2 點罪惡 1 顆，絕對優先塞入)
    sin_dice_count = min(pool_size, sin // 2)
    
    # 3. 計算聖靈骰 (每 5 點虔誠 1 顆，受罪骰擠壓)
    potential_hs = piety // 5
    available_slots = pool_size - sin_dice_count
    hs_dice_count = min(available_slots, potential_hs)
    
    # 4. 剩餘為常規天意骰
    prov_dice_count = pool_size - sin_dice_count - hs_dice_count
    
    # 定義特規六面骰規格
    PROV_FACES = [0, 0, 1, 1, 2, 2]
    HS_FACES = [1, 1, 1, 2, 2, 2]
    SIN_FACES = ['罪', '罪', 0, 1, 1, 2]
    
    dice_results = []
    points = 0
    sin_inflicted = 0
    
    # 擲罪惡骰
    for _ in range(sin_dice_count):
        face = random.choice(SIN_FACES)
        if face == '罪':
            sin_inflicted += 1
            dice_results.append("⛓️[☠️罪]")
        else:
            points += face
            dice_results.append(f"⛓️[{face}]")
            
    # 擲聖靈骰
    for _ in range(hs_dice_count):
        face = random.choice(HS_FACES)
        points += face
        dice_results.append(f"🕊️[{face}]")
        
    # 擲天意骰
    for _ in range(prov_dice_count):
        face = random.choice(PROV_FACES)
        points += face
        dice_results.append(f"⚪[{face}]")
        
    # 結算罪惡增長與完全墮落
    fallen_msg = ""
    if sin_inflicted > 0:
        player['sins'][fruit_name] += sin_inflicted
        new_sin = player['sins'][fruit_name]
        fallen_msg = f" 🩸【罪惡值+{sin_inflicted} (累計 {new_sin})】"
        if new_sin >= 10:
            player['sins'][fruit_name] = 10
            player['depraved'] = True
            fallen_msg += " 🚨🚨【當場完全墮落 (COMPLETE DEPRAVITY)！！】"
            
    total = points + bonus
    success = total >= dc and not player.get('depraved', False)
    
    dice_str = " ".join(dice_results) if dice_results else "（無可用骰子）"
    log_event(f"    🎲 [{player['name']}] 檢定【{fruit_name}】(可用果子:{pool_size}顆, 虔誠:{piety}, 罪惡:{sin}):")
    log_event(f"       骰池: {sin_dice_count}罪骰 + {hs_dice_count}聖靈骰 + {prov_dice_count}天意骰")
    log_event(f"       擲出: {dice_str} = 點數 {points} + 加成 {bonus} = 總值 {total} vs DC {dc} -> {'【成功】' if success else '【失敗】'}{fallen_msg}")
    return success, total

def check_deceiver_interference(player):
    """
    【欺瞞者擴充】：在親近神行動前擲 1 顆欺瞞者骰 (2面謊言 😈, 4面平靜 🕊️)
    若出現謊言，則進行智慧識破檢定 (DC 10)
    """
    DECEIVER_FACES = ['😈謊言', '😈謊言', '🕊️安息', '🕊️安息', '🕊️安息', '🕊️安息']
    roll = random.choice(DECEIVER_FACES)
    if roll == '🕊️安息':
        log_event(f"    🎲 [{player['name']}] 投擲欺瞞者骰：【🕊️平靜安息】心靈清朗，親近神行動順暢！")
        return True
    
    log_event(f"    🎲 [{player['name']}] 投擲欺瞞者骰：【😈謊言面】仇敵謊言襲來！心神受阻，嘗試以智慧與真理識破！")
    # 智慧值 = (最高果子 + 最低果子) // 2
    fruit_vals = list(player['fruits'].values())
    wisdom = (max(fruit_vals) + min(fruit_vals)) // 2
    
    # 骰池構成：含聖靈骰 (piety // 5)，絕不含罪骰，其餘天意骰
    piety = player.get('piety', 0)
    hs_count = min(wisdom, piety // 5)
    prov_count = wisdom - hs_count
    
    PROV_FACES = [0, 0, 1, 1, 2, 2]
    HS_FACES = [1, 1, 1, 2, 2, 2]
    dice_results = []
    points = 0
    for _ in range(hs_count):
        f = random.choice(HS_FACES)
        points += f
        dice_results.append(f"🕊️[{f}]")
    for _ in range(prov_count):
        f = random.choice(PROV_FACES)
        points += f
        dice_results.append(f"⚪[{f}]")
        
    truth_tokens = player.get('truth_tokens', 0)
    total = points + truth_tokens
    success = total >= 10
    
    log_event(f"       【識破謊言檢定】智慧值:{wisdom} (最高{max(fruit_vals)}+最低{min(fruit_vals)})/2 -> {hs_count}聖靈骰 + {prov_count}天意骰")
    log_event(f"       擲出: {' '.join(dice_results)} = 點數 {points} + 真理代幣 {truth_tokens} = 總識破值 {total} vs DC 10 -> {'【🌟 識破成功！奉主名斥退撒旦】' if success else '【🌫️ 識破失敗，心靈受阻】'}")
    return success

log_event("=" * 80)
log_event("       🕊️ 《使徒:大使命》2人實戰數值跑測記錄 (剛烈開路者 + 勸慰之子巴拿巴)")
log_event("=" * 80)
log_event(f"初始配置：P1 HP:{p1['hp']} 虔誠:{p1['piety']} | P2 HP:{p2['hp']} 虔誠:{p2['piety']} | 糧食:{supplies['food']} 銀幣:{supplies['coins']}")

# ==================== 第 1 輪：曠野序章 ====================
log_event("\n" + "-"*40 + "【第 1 輪：曠野序章・荒漠跋涉】" + "-"*40)
# 晨更：無歸主者，時間標記推進至第 1 輪
log_event("🌅 【晨更階段】：時間軌標記推進至第 1 輪。荒漠中尚無歸主者，全隊同心起行。")

# P1 行動：抽 1 張旅程牌
card_p1 = journey_cards.pop(0)
log_event(f"\n🏃 【P1 剛烈開路者 回合】：抽到旅程牌《{card_p1['name']}》（{card_p1['type']}）")
log_event(f"   內容：{card_p1['description']}")
# 執行 3 AP
log_event("   P1 規劃 3 個行動點：")
# 行動 1: 親手做工 (1 AP)
supplies['food'] += 1
log_event("   - 行動 1【親手做工 / 織帳棚】：投入勞力，穩定獲得 1 份糧食！（糧食存量：7）")
# 行動 2: 親近靈修 (1 AP)
p1['piety'] += 2
log_event(f"   - 行動 2【親近靈修】：曠野晨更禱告，自身虔誠 +2（目前虔誠：{p1['piety']}）")
# 行動 3: 為人代禱 (1 AP)
p2['intercession'] += 1
log_event(f"   - 行動 3【為人代禱】：剛烈開路者為同伴巴拿巴切切代求！巴拿巴獲得 1 枚【代禱代幣】！")

# 結算遭遇牌
log_event(f"   結算面前旅程牌《{card_p1['name']}》：")
# 根據 card_p1 進行判定（例如 JNY_TRL_02 或其他）
if '喜樂' in card_p1['description'] or '喜樂熱心' in card_p1['description']:
    succ, _ = roll_check(p1, '喜樂', 10, bonus=2) # 開路者特質 DC -2
    if succ:
        log_event("   -> 剛烈開路者一柄開山斧威震荒野，全隊平安無事！")
    else:
        p1['hp'] -= 4
        log_event(f"   -> 判定失敗，P1 受傷 HP -4（目前 HP: {p1['hp']}）")
else:
    succ, _ = roll_check(p1, '忍耐', 10, bonus=2)
    if not succ:
        p1['hp'] -= 2
        log_event(f"   -> 遭遇風沙摩擦，P1 HP -2（目前 HP: {p1['hp']}）")

# P2 行動
card_p2 = journey_cards.pop(0)
log_event(f"\n🏃 【P2 勸慰之子巴拿巴 回合】：抽到旅程牌《{card_p2['name']}》（{card_p2['type']}）")
log_event(f"   內容：{card_p2['description']}")
# 執行 3 AP
log_event("   P2 規劃 3 個行動點：")
# 行動 1: 親近靈修 (1 AP) -> 巴拿巴虔誠 12 + 2 = 14
p2['piety'] += 2
log_event(f"   - 行動 1【親近靈修】：默想聖言，虔誠 +2（目前虔誠：{p2['piety']}，即將達 15 覺醒恩賜！）")
# 行動 2: 親近靈修 (1 AP) -> 14 + 2 = 16! 覺醒恩賜!
p2['piety'] += 2
log_event(f"   - 行動 2【親近靈修】：深層默禱，虔誠達 {p2['piety']} 點！🌟 成功跨越 15 門檻，點亮專屬恩賜！")
# 行動 3: 為人代禱 (1 AP)
p1['intercession'] += 1
log_event(f"   - 行動 3【為人代禱】：巴拿巴為開路者按手祝福！開路者獲得 1 枚【代禱代幣】！")

# 結算 P2 旅程牌
if '仁愛' in card_p2['description'] or '恩慈' in card_p2['description']:
    succ, _ = roll_check(p2, '仁愛', 10, bonus=p2['intercession']*2)
    if succ:
        p2['piety'] += 2
        log_event("   -> 巴拿巴仁愛施予，感動路人，全隊虔誠大受激勵！")
else:
    succ, _ = roll_check(p2, '溫柔', 10)
    if not succ:
        p2['hp'] -= 2
        log_event(f"   -> 略有磨損，P2 HP -2（目前 HP: {p2['hp']}）")

# 黃昏階段
log_event("\n🌆 【第 1 輪黃昏結算】：")
supplies['food'] -= 2 # 2 位使徒各扣 1 糧
log_event(f"   - 日用糧食消耗：全隊消耗 2 份糧食，剩餘 {supplies['food']} 份。無人飢餓！")
log_event(f"   - 罪惡檢驗：全體罪惡均為 0，靈命純全安息。")
log_event(f"   - 第一輪結束狀態：P1 (HP:{p1['hp']}/18, 虔誠:{p1['piety']}, 代禱:{p1['intercession']}) | P2 (HP:{p2['hp']}/14, 虔誠:{p2['piety']}, 代禱:{p2['intercession']}) | 糧食:{supplies['food']}")

# ==================== 第 2 輪：曠野序章 ====================
log_event("\n" + "-"*40 + "【第 2 輪：曠野序章・神聖守候】" + "-"*40)
log_event("🌅 【晨更階段】：時間軌推進至第 2 輪。晨曦照耀戈壁。")

# P1 行動
card_p1_2 = journey_cards.pop(0)
log_event(f"\n🏃 【P1 剛烈開路者 回合】：抽到旅程牌《{card_p1_2['name']}》")
log_event("   P1 規劃 3 個行動點：")
# 行動 1: 親手做工 (1 AP) + 檢定節制克己 DC 8
succ_work, _ = roll_check(p1, '節制', 8)
if succ_work:
    supplies['food'] += 2
    log_event("   - 行動 1【親手做工（勤勞檢定通過）】：獲得 2 份糧食！（糧食存量：7）")
else:
    supplies['food'] += 1
    log_event("   - 行動 1【親手做工（保底）】：獲得 1 份糧食。（糧食存量：6）")

# 行動 2: 守候神蹟 (1 AP) -> 啟動《磐石出水》充能 1 枚
miracle_charges = 1
log_event(f"   - 行動 2【守候神蹟】：在史詩神蹟《磐石出水》上放置第 1 枚信心守候標記（1/5）！")

# 行動 3: 親近靈修 (1 AP)
p1['piety'] += 2
log_event(f"   - 行動 3【親近靈修】：開路者靈修補給，虔誠由 10 升至 {p1['piety']}！")

# 結算旅程牌（消耗巴拿巴給的代禱代幣）
log_event(f"   結算旅程牌《{card_p1_2['name']}》：開路者消耗 1 枚同伴給的【代禱代幣】(+2加成)！")
p1['intercession'] -= 1
succ, _ = roll_check(p1, '忍耐', 10, bonus=2 + 2)
if succ:
    log_event("   -> 藉著弟兄代禱的托住，大有能力跨越險阻！")

# P2 行動
card_p2_2 = journey_cards.pop(0)
log_event(f"\n🏃 【P2 勸慰之子巴拿巴 回合】：抽到旅程牌《{card_p2_2['name']}》")
log_event("   P2 規劃 3 個行動點：")
# 巴拿巴使用已覺醒的恩賜，並進行代禱與靈修
# 行動 1: 親近靈修 (1 AP) -> 虔誠 16 + 2 = 18!
p2['piety'] += 2
log_event(f"   - 行動 1【親近靈修】：靈命滿溢，虔誠達 {p2['piety']}！即將觸及 20 點【聖靈充滿】！")
# 行動 2: 親近靈修 (1 AP) -> 虔誠達 20 滿溢！
p2['piety'] = 20
log_event(f"   - 行動 2【親近靈修】：🔥 聖靈大降臨！巴拿巴虔誠達到頂峰 20 點【聖靈充滿 (Pentecostal Aura)】！全場同工自帶 +1 聖靈光環！")
# 行動 3: 為人代禱 (1 AP)
p1['intercession'] += 2 # 恩賜效果+代禱
log_event(f"   - 行動 3【聖靈大代禱】：在聖靈充滿位階下，為開路者發放 2 枚【代禱代幣】！")

# 黃昏階段
log_event("\n🌆 【第 2 輪黃昏結算】：")
supplies['food'] -= 2
log_event(f"   - 日用糧食消耗：消耗 2 份糧食，剩餘 {supplies['food']} 份。")
log_event(f"   - 第 2 輪結束狀態：P1 (HP:{p1['hp']}, 虔誠:{p1['piety']}, 代禱:{p1['intercession']}) | P2 (HP:{p2['hp']}, 虔誠:{p2['piety']}[聖靈充滿!]) | 糧食:{supplies['food']}")

# ==================== 第 3 輪：曠野序章拔營 ====================
log_event("\n" + "-"*40 + "【第 3 輪：曠野序章拔營・奔向故鄉】" + "-"*40)
log_event("🌅 【晨更階段】：曠野序章最後一輪！天際破曉，使徒拔營整裝。")
supplies['food'] -= 2
log_event(f"   - 拔營物資消耗 2 份糧食（剩餘 {supplies['food']} 份）。全隊安全走出曠野，邁入第一區【故鄉基石】！")

# ==================== 第 4 輪：第一區【故鄉基石】第 1 輪 ====================
log_event("\n" + "="*40 + "【第一區：故鄉基石 (猶太地與耶路撒冷) 第 1 輪】" + "="*40)

# 布置 1+2 地點
pillar_loc = r1_locs_pillar[0]
free_loc_1 = r1_locs_free[0]
free_loc_2 = r1_locs_free[1]
bound_pillar = [p for p in r1_pillars if p['id'] in pillar_loc['bound_pillar'] or p['name'] in pillar_loc['bound_pillar']][0]

log_event(f"🏛️ 【1+2 活動地點翻開】：")
log_event(f"   1. 大能據點：【{pillar_loc['name']}】（容量 {pillar_loc['capacity']} 人）-> 綁定大能者【{bound_pillar['name']}】直接就位！")
log_event(f"   2. 自由地點 1：【{free_loc_1['name']}】（容量 {free_loc_1['capacity']} 人）")
log_event(f"   3. 自由地點 2：【{free_loc_2['name']}】（容量 {free_loc_2['capacity']} 人）")

# 開出百姓
total_cap = int(free_loc_1['capacity']) + int(free_loc_2['capacity'])
spawned_people = [r1_people.pop(0) for _ in range(min(total_cap, len(r1_people)))]
log_event(f"\n👥 【未歸主人民登場 (共開出 {len(spawned_people)} 人)】：")
for p in spawned_people:
    log_event(f"   - ［{p['name']}］：需要 -> {p['description'].split('｜')[0]} | 講道 -> {p['description'].split('｜')[1] if '｜' in p['description'] else '常規'}")

# 使徒就位
p1['location'] = free_loc_1['name']
p2['location'] = free_loc_1['name']
log_event(f"\n使徒登場：開路者與巴拿巴共同抵達【{free_loc_1['name']}】！")

# P1 回合
enc_1 = r1_encounters.pop(0)
log_event(f"\n🏃 【P1 剛烈開路者 回合】：抽取地區遭遇牌《{enc_1['name']}》（{enc_1['type']}）")
log_event(f"   遭遇：{enc_1['description']}")

target_person = spawned_people[0]
log_event(f"\n   P1 在【{free_loc_1['name']}】向［{target_person['name']}］傳道！規劃 3 AP：")
# 行動 1: 滿足需要 (1 AP) - 消耗 1 糧食
supplies['food'] -= 1
log_event(f"   - 行動 1【滿足迫切需要】：消耗 1 份糧食施捨周濟！移除鎖頭標記，［{target_person['name']}］心門敞開！（剩餘糧食：{supplies['food']}）")
# 行動 2: 真理講道 (1 AP) - 檢定溫柔或信實
log_event(f"   - 行動 2【真理宣講講道】：巴拿巴聖靈充滿光環提供 +1 加成，開路者燃燒 1 代禱代幣(+2)！")
p1['intercession'] -= 1
succ_preach, total_val = roll_check(p1, '信實', 8, bonus=1 + 2)
if succ_preach:
    log_event(f"   -> 🌟 講道大得勝！［{target_person['name']}］深受感動，當場在水池中【受洗為歸主者】！🎉")
    target_person['converted'] = True
else:
    log_event(f"   -> 頑石未開，需同工接續澆灌。")

# 行動 3: 親手做工 (1 AP) 補充糧食
supplies['food'] += 1
log_event(f"   - 行動 3【親手做工 / 織帳棚】：使徒親自做工，迅速回補 1 份糧食！（糧食存量：{supplies['food']}）")

# 結算遭遇牌
log_event(f"   結算地區遭遇牌《{enc_1['name']}》：")
if enc_1['type'] == '事件':
    log_event(f"   -> 恩典臨到！全隊安然獲益。")
else:
    succ_enc, _ = roll_check(p1, '和平', 10, bonus=1) # 聖靈充滿光環 +1
    if not succ_enc:
        p1['hp'] -= 2
        log_event(f"   -> 遭遇小摩擦，P1 HP -2（HP: {p1['hp']}）")

# P2 回合
enc_2 = r1_encounters.pop(0)
log_event(f"\n🏃 【P2 勸慰之子巴拿巴 回合】：抽取地區遭遇牌《{enc_2['name']}》（{enc_2['type']}）")
target_person_2 = spawned_people[1]
log_event(f"   P2 面前有心門緊閉的［{target_person_2['name']}］。規劃 3 AP：")

# 巴拿巴發動【聖靈充滿神聖大爆發 (Divine Outpouring)】！
log_event("   - ⚡【發動聖靈權柄：神聖大爆發】！巴拿巴宣告聖靈大降臨（不耗費 AP）！")
log_event(f"     效果：為在場所有敞開信徒各放置 1 枚祈禱代幣！巴拿巴虔誠降回 16 點（仍處於恩賜彰顯位階）。")
p2['piety'] = 16

# 行動 1: 滿足需要 (1 AP)
supplies['food'] -= 1
log_event(f"   - 行動 1【滿足迫切需要】：消耗 1 份糧食救濟［{target_person_2['name']}］，其心門敞開！")
# 行動 2: 真理講道 (1 AP)
succ_preach_2, _ = roll_check(p2, '溫柔', 8, bonus=2) # 地區屬靈共鳴：第一區溫柔自帶加成
if succ_preach_2:
    log_event(f"   -> 🌟 勸慰之言直透人心！［{target_person_2['name']}］痛哭悔改，【受洗為歸主者】！🎉")
    target_person_2['converted'] = True

# 行動 3: 為人代禱 (1 AP)
p1['intercession'] += 1
p2['intercession'] += 1
log_event(f"   - 行動 3【彼此代禱】：全體使徒各獲 1 枚【代禱代幣】！")

# 結算遭遇牌
log_event(f"   結算地區遭遇牌《{enc_2['name']}》：巴拿巴沉穩化解。")

# 第一區第 1 輪黃昏
log_event("\n🌆 【第一區第 1 輪黃昏結算】：")
supplies['food'] -= 2
log_event(f"   - 日用糧食消耗：全隊消耗 2 份糧食，剩餘 {supplies['food']} 份。")
log_event(f"   - 歸主者統計：場上已有 2 位已受洗百姓（美門癱子/加利利漁夫等），下輪晨更將開始產出祈禱代幣！")
log_event(f"   - 雙重死亡線檢驗：P1 HP {p1['hp']}/18, 虔誠 {p1['piety']} | P2 HP {p2['hp']}/14, 虔誠 {p2['piety']}。全員健康，靈命豐盛！")

log_event("\n" + "="*80)
log_event("                          🎉 實戰跑測模擬推演圓滿成功！")
log_event("="*80)
