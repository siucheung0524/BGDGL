import requests
from datetime import datetime, timedelta, timezone
import os
import urllib.parse

# --- 配置資訊 ---
PODCAST_NAME = "Bad Girl 大過佬"
RSS_FILE = "rss.xml"

def check_and_update():
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    print(f"[{PODCAST_NAME}] 檢查日期: {today_str}")

    # 模擬更完整的瀏覽器 Header
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'audio/mpeg,audio/*;q=0.9,application/ogg;q=0.7,audio/wav;q=0.6,*/*;q=0.5',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://hkfm903.live/'
    }

    found_url = None
    show_path = "Bad Girl大過佬"
    
    print(f"[{PODCAST_NAME}] 開始暴力搜尋 10:00 - 10:25...")

    for m in range(0, 26):
        time_str = f"10{m:02d}"
        for separator in [" ", "_"]:
            raw_filename = f"{today_str}_{time_str}_Bad{separator}Girl大過佬.aac"
            encoded_show = urllib.parse.quote(show_path)
            encoded_file = urllib.parse.quote(raw_filename)
            
            # 先用 HTTP 測試，因為網站本質是 HTTP，成功率較高
            test_url_http = f"http://hkfm903.live/recordings/{encoded_show}/{encoded_file}"
            
            try:
                # 關鍵：verify=False 忽略 SSL 憑證錯誤，避免握手失敗
                r = requests.get(test_url_http, headers=headers, timeout=10, stream=True, verify=False)
                
                # 偵錯：如果是 10:09，印出狀態碼
                if time_str == "1009":
                    print(f"DEBUG (1009): 嘗試 {test_url_http} -> 狀態碼: {r.status_code}")

                if r.status_code == 200:
                    print(f"✅ 找到檔案！ (HTTP 200)")
                    # 寫入 RSS 時改回 HTTPS，確保 Podcast App 接受
                    found_url = test_url_http.replace("http://", "https://")
                    break
            except Exception as e:
                if time_str == "1009":
                    print(f"DEBUG (1009) 出錯: {e}")
                continue
        if found_url: break

    if not found_url:
        print(f"[{PODCAST_NAME}] 依然找不到檔案。")
        return

    # 寫入 RSS
    if not os.path.exists(RSS_FILE): return
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    guid = f"bgog-{today_str}"
    if guid not in rss_content:
        pub_date_str = now_hk.strftime("%a, %d %b %Y 12:05:00 +0800")
        new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} Bad Girl 大過佬</title>
      <pubDate>{pub_date_str}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{found_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
        updated_content = rss_content.replace("    <item>", new_item + "    <item>", 1)
        with open(RSS_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"[{PODCAST_NAME}] 更新成功：{today_str}")

if __name__ == "__main__":
    check_and_update()
