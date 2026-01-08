import requests
import re
from datetime import datetime, timedelta, timezone
import os

# --- 配置資訊 ---
PODCAST_NAME = "Bad Girl 大過佬"
SHOW_PAGE_URL = "https://hkfm903.live/?show=Bad%20Girl%E5%A4%A7%E9%81%8E%E4%BD%AC"
RSS_FILE = "rss.xml"
# ----------------

def check_and_update():
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    print(f"[{PODCAST_NAME}] 開始檢查日期: {today_str}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        # 1. 爬取網頁（嘗試尋找 http 或 https 連結）
        page_response = requests.get(SHOW_PAGE_URL, headers=headers, timeout=15)
        page_response.encoding = 'utf-8'
        # 搜尋任何包含日期和 aac 的字串
        pattern = rf'recordings/[^"\'\s>]*{today_str}_[^"\'\s>]*\.aac'
        raw_links = re.findall(pattern, page_response.text)
        
        valid_links = []
        for link in raw_links:
            target_url = f"https://hkfm903.live/{link.lstrip('/')}".replace("https://hkfm903.live/https://", "https://")
            target_url = target_url.replace("http://", "https://")
            valid_links.append(target_url)

        # 2. 強力猜測模式 (10:00-10:20)
        if not valid_links:
            print(f"[{PODCAST_NAME}] 網頁沒看到連結，開始暴力嘗試 10:00-10:20...")
            # 根據你提供的成功網址：.../20260108_1009_Bad_Girl大過佬.aac
            # 注意：資料夾是 Bad%20Girl，但檔名是 Bad_Girl
            for m in range(0, 21):
                min_str = f"{m:02d}"
                test_url = f"https://hkfm903.live/recordings/Bad%20Girl%E5%A4%A7%E9%81%8E%E4%BD%AC/{today_str}_10{min_str}_Bad_Girl%E5%A4%A7%E9%81%8E%E4%BD%AC.aac"
                
                try:
                    # 改用 GET + stream 確保能穿透伺服器檢測
                    r = requests.get(test_url, headers=headers, timeout=5, stream=True)
                    if r.status_code == 200:
                        print(f"成功命中！ -> {test_url}")
                        valid_links = [test_url]
                        break
                except: continue

        if not valid_links:
            print(f"[{PODCAST_NAME}] 依然找不到今日檔案，請確認網址格式是否改變。")
            return

    except Exception as e:
        print(f"執行錯誤: {e}")
        return

    # 3. 更新 RSS 檔案
    if not os.path.exists(RSS_FILE): return
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    target_url = valid_links[0]
    guid = f"bgog-{today_str}"
    
    if guid not in rss_content:
        pub_date_str = now_hk.strftime("%a, %d %b %Y 12:05:00 +0800")
        new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} Bad Girl 大過佬</title>
      <pubDate>{pub_date_str}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{target_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
        rss_content = rss_content.replace("    <item>", new_item + "    <item>", 1)
        with open(RSS_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"[{PODCAST_NAME}] 更新完成！已加入 {today_str}。")
    else:
        print(f"[{PODCAST_NAME}] 集數已存在。")

if __name__ == "__main__":
    check_and_update()
