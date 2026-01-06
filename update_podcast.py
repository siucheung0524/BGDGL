import requests
import re
from datetime import datetime, timedelta, timezone
import os

# --- 配置資訊 ---
PODCAST_NAME = "Bad Girl 大過佬"
# 節目存檔的網頁
SHOW_PAGE_URL = "https://hkfm903.live/?show=Bad%20Girl%E5%A4%A7%E9%81%8E%E4%BD%AC"
RSS_FILE = "rss.xml"
# ----------------

def check_and_update():
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    print(f"[{PODCAST_NAME}] 正在網頁上搜尋日期為 {today_str} 的檔案...")

    try:
        # 1. 抓取網頁內容
        page_response = requests.get(SHOW_PAGE_URL, timeout=15)
        page_response.encoding = 'utf-8' # 確保中文不亂碼
        
        # 2. 使用正則表達式尋找今天的 .aac 連結
        # 尋找格式如：recordings/.../20260106_xxxx_Bad_Girl...aac
        pattern = rf'recordings/[^"]*{today_str}_[^"]*\.aac'
        match = re.search(pattern, page_response.text)
        
        if not match:
            print(f"[{PODCAST_NAME}] 在網頁上找不到今日 ({today_str}) 的檔案連結。")
            return
            
        # 取得完整網址
        found_path = match.group(0)
        target_url = f"https://hkfm903.live/{found_path}"
        print(f"[{PODCAST_NAME}] 找到今日網址: {target_url}")

    except Exception as e:
        print(f"爬取網頁出錯: {e}")
        return

    # 3. 讀取現有 RSS 並檢查 GUID
    if not os.path.exists(RSS_FILE):
        return
        
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    guid = f"bgog-{today_str}"
    if guid in rss_content:
        print(f"[{PODCAST_NAME}] 今日節目已存在，跳過更新。")
        return

    # 4. 插入新 Item
    pub_date_str = now_hk.strftime("%a, %d %b %Y %H:%M:%S +0800")
    new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} Bad Girl 大過佬</title>
      <pubDate>{pub_date_str}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{target_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
    updated_content = rss_content.replace("    <item>", new_item + "    <item>", 1)

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"[{PODCAST_NAME}] 成功更新 RSS！")

if __name__ == "__main__":
    check_and_update()
