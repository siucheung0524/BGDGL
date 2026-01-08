import subprocess
import os
from datetime import datetime, timedelta, timezone

# --- 配置資訊 ---
PODCAST_NAME = "聖艾粒LaLaLaLa"
RSS_FILE = "ilub.xml"

def get_status_code(url):
    try:
        cmd = ['curl', '-s', '-o', '/dev/null', '-I', '-w', '%{http_code}', '--connect-timeout', '5', '-A', 'Mozilla/5.0', url]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except: return "000"

def check_and_update():
    hk_tz = timezone(timedelta(hours=8))
    now_hk = datetime.now(hk_tz)
    today_str = now_hk.strftime("%Y%m%d")
    
    # 限制執行時間：只有在 19:00 後才開始「暴力偵測」，避免誤抓舊檔案
    if int(now_hk.strftime("%H%M")) < 1900:
        print(f"[{PODCAST_NAME}] 現在時間尚早，稍後再試。")
        return

    found_url = None
    # 掃描 17:00 到 17:15
    for m in range(0, 16):
        time_str = f"17{m:02d}"
        test_url = f"https://hkfm903.live/recordings/%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa/{today_str}_{time_str}_%E8%81%96%E8%89%BE%E7%B2%92LaLaLaLa.aac"
        
        code = get_status_code(test_url)
        if code in ["200", "206", "403"]:
            print(f"🎯 成功定位今日檔案網址: {test_url} (狀態碼: {code})")
            found_url = test_url
            break

    if found_url:
        if os.path.exists(RSS_FILE):
            with open(RSS_FILE, "r", encoding="utf-8") as f: content = f.read()
            guid = f"ilub-{today_str}"
            if guid not in content:
                pub_date = now_hk.strftime("%a, %d %b %Y 19:10:00 +0800")
                new_item = f"""    <item>
      <title>{now_hk.strftime("%Y-%m-%d")} 聖艾粒LaLaLaLa</title>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{found_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
                with open(RSS_FILE, "w", encoding="utf-8") as f:
                    f.write(content.replace("    <item>", new_item + "    <item>", 1))
                print(f"✅ RSS 已更新！")
    else:
        print("目前尚未發現今日檔案。")

if __name__ == "__main__":
    check_and_update()
