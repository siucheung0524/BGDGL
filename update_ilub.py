import requests
import re
from datetime import datetime, timedelta, timezone
import os

# --- 配置資訊 ---
PODCAST_NAME = "聖艾粒LaLaLaLa"
# 節目存檔頁面 (含 URL 編碼)
SHOW_PAGE_URL = "https://hkfm903.live/?show=%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa"
RSS_FILE = "ilub.xml"
# ----------------

def check_and_update():
    # 1. 設定香港時區 (UTC+8)
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    print(f"[{PODCAST_NAME}] 開始檢查日期: {today_str}")

    try:
        # 模擬瀏覽器標頭
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 2. 爬取網頁內容
        page_response = requests.get(SHOW_PAGE_URL, headers=headers, timeout=15)
        page_response.encoding = 'utf-8'
        html_content = page_response.text

        # 搜尋包含今天日期且以 .aac 結尾的連結 (處理 http 或相對路徑)
        pattern = rf'/[^"\'\s>]*{today_str}_[^"\'\s>]*\.aac|http[^"\'\s>]*{today_str}_[^"\'\s>]*\.aac'
        raw_links = re.findall(pattern, html_content)
        
        valid_links = []
        for link in raw_links:
            # 強制轉換為 https 完整連結
            if link.startswith('http'):
                target_url = link.replace("http://", "https://")
            else:
                target_url = f"https://hkfm903.live{link}"
            valid_links.append(target_url)

        # 3. 進入「強力猜測模式」 (17:00 - 17:15)
        if not valid_links:
            print(f"[{PODCAST_NAME}] 網頁未見連結，開始暴力嘗試 17:00-17:15 區間...")
            for m in range(0, 16):
                minute_str = f"{m:02d}"
                # 拼接聖艾粒的檔案格式
                test_url = f"https://hkfm903.live/recordings/%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa/{today_str}_17{minute_str}_%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa.aac"
                try:
                    # 使用 stream=True 進行輕量化連線測試
                    r = requests.get(test_url, headers=headers, timeout=5, stream=True)
                    if r.status_code == 200:
                        print(f"成功找到隱藏網址: {test_url}")
                        valid_links = [test_url]
                        break
                except: continue

        if not valid_links:
            print(f"[{PODCAST_NAME}] 依然找不到今日檔案。")
            return

    except Exception as e:
        print(f"執行出錯: {e}")
        return

    # 4. 更新 RSS 檔案
    if not os.path.exists(RSS_FILE): return
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    target_url = valid_links[0]
    guid = f"ilub-{today_str}"
    
    if guid not in rss_content:
        print(f"正在將新集數寫入 {RSS_FILE}: {today_str}")
        # 設定發布時間為當晚 19:05
        pub_date_str = now_hk.strftime("%a, %d %b %Y 19:05:00 +0800")
        
        new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} 聖艾粒LaLaLaLa</title>
      <pubDate>{pub_date_str}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{target_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
        # 在第一個 <item> 標籤之前插入新內容
        rss_content = rss_content.replace("    <item>", new_item + "    <item>", 1)
        
        with open(RSS_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"[{PODCAST_NAME}] RSS 更新成功！")
    else:
        print(f"[{PODCAST_NAME}] 該日期集數已存在。")

if __name__ == "__main__":
    check_and_update()
