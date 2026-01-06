import requests
from datetime import datetime, timedelta, timezone
import os

# --- 配置資訊 ---
PODCAST_NAME = "聖艾粒LaLaLaLa"
# 使用 URL 編碼的中文字元路徑
BASE_URL = "https://hkfm903.live/recordings/%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa/"
RSS_FILE = "ilub.xml"
# ----------------

def check_and_update():
    # 強制使用香港時區 (UTC+8)
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    # 建立目標網址 (17:00 節目)
    file_name = f"{today_str}_1700_%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa.aac"
    target_url = BASE_URL + file_name
    
    # 1. 檢查網址是否有效
    try:
        response = requests.head(target_url, timeout=10)
        if response.status_code != 200:
            print(f"[{PODCAST_NAME}] 今日 ({today_str}) 檔案尚未上架。")
            return
    except Exception as e:
        print(f"檢查失敗: {e}")
        return

    # 2. 讀取現有 RSS
    if not os.path.exists(RSS_FILE):
        print(f"錯誤: 找不到 {RSS_FILE}")
        return
        
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    # 3. 檢查 GUID 防止重複
    guid = f"ilub-{today_str}"
    if guid in rss_content:
        print(f"[{PODCAST_NAME}] 今日節目已存在，跳過。")
        return

    # 4. 建立新 Item
    pub_date_str = now_hk.strftime("%a, %d %b %Y %H:%M:%S +0800")
    
    new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} 聖艾粒LaLaLaLa</title>
      <pubDate>{pub_date_str}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{target_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
    
    # 5. 插入到第一個 <item> 標籤之前
    updated_content = rss_content.replace("    <item>", new_item + "    <item>", 1)

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"[{PODCAST_NAME}] 成功更新 {RSS_FILE}！")

if __name__ == "__main__":
    check_and_update()
