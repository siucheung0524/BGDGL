import subprocess
import re
from datetime import datetime, timedelta, timezone
import os
import urllib.parse

# --- 配置資訊 ---
PODCAST_NAME = "Bad Girl 大過佬"
RSS_FILE = "rss.xml"

def get_status_code(url):
    """使用系統 curl 指令獲取 HTTP 狀態碼"""
    try:
        # 模擬 Chrome 的真實 curl 請求
        cmd = [
            'curl', '-s', '-o', '/dev/null', '-I', '-w', '%{http_code}',
            '--connect-timeout', '5',
            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '-e', 'https://hkfm903.live/',
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "000"

def check_and_update():
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    print(f"[{PODCAST_NAME}] 檢查日期: {today_str}")

    found_url = None
    show_path = "Bad Girl大過佬"
    
    print(f"[{PODCAST_NAME}] 開始使用 curl 引擎搜尋 10:00 - 10:25...")

    for m in range(0, 26):
        time_str = f"10{m:02d}"
        # 同時測試空格版與底線版
        for separator in [" ", "_"]:
            raw_filename = f"{today_str}_{time_str}_Bad{separator}Girl大過佬.aac"
            encoded_show = urllib.parse.quote(show_path)
            encoded_file = urllib.parse.quote(raw_filename)
            test_url = f"https://hkfm903.live/recordings/{encoded_show}/{encoded_file}"
            
            code = get_status_code(test_url)
            
            if time_str == "1009":
                print(f"DEBUG (1009): {test_url} -> 狀態碼: {code}")

            if code == "200":
                print(f"✅ 成功命中！找到檔案。")
                found_url = test_url
                break
        if found_url: break

    if not found_url:
        print(f"[{PODCAST_NAME}] curl 依然回傳 403 或找不到檔案。")
        return

    # 更新 RSS 檔案
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
        print(f"[{PODCAST_NAME}] RSS 更新成功！")

if __name__ == "__main__":
    check_and_update()
