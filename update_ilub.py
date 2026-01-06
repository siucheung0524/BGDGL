import requests
import re
from datetime import datetime, timedelta, timezone
import os

# --- 配置資訊 ---
PODCAST_NAME = "聖艾粒LaLaLaLa"
SHOW_PAGE_URL = "https://hkfm903.live/?show=%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa"
RSS_FILE = "ilub.xml"
# ----------------

def check_and_update():
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    print(f"[{PODCAST_NAME}] 正在網頁上搜尋日期為 {today_str} 的檔案...")

    try:
        page_response = requests.get(SHOW_PAGE_URL, timeout=15)
        page_response.encoding = 'utf-8'
        
        # 搜尋包含今天日期的 .aac 連結
        pattern = rf'recordings/[^"]*{today_str}_[^"]*\.aac'
        match = re.search(pattern, page_response.text)
        
        if not match:
            print(f"[{PODCAST_NAME}] 網頁上尚未出現今日檔案。")
            return
            
        found_path = match.group(0)
        target_url = f"https://hkfm903.live/{found_path}"
        print(f"[{PODCAST_NAME}] 找到今日網址: {target_url}")

    except Exception as e:
        print(f"爬取網頁出錯: {e}")
        return

    if not os.path.exists(RSS_FILE):
        return
        
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    guid = f"ilub-{today_str}"
    if guid in rss_content:
        print(f"[{PODCAST_NAME}] 今日節目已存在。")
        return

    pub_date_str = now_hk.strftime("%a, %d %b %Y %H:%M:%S +0800")
    new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} 聖艾粒LaLaLaLa</title>
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
