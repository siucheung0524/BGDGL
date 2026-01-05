import requests
from datetime import datetime
import os

# 配置資訊
PODCAST_NAME = "Bad Girl 大過佬"
BASE_URL = "https://hkfm903.live/recordings/Bad%20Girl%E5%A4%A7%E9%81%8E%E4%BD%AC/"
RSS_FILE = "rss.xml"

def check_and_update():
    # 1. 取得今天日期 (格式: 20260105)
    today_str = datetime.now().strftime("%Y%m%d")
    # 建立目標網址
    file_name = f"{today_str}_1000_Bad_Girl%E5%A4%A7%E9%81%8E%E4%BD%AC.aac"
    target_url = BASE_URL + file_name
    
    # 2. 檢查網址是否有效 (HTTP 200)
    response = requests.head(target_url)
    if response.status_code != 200:
        print(f"今日節目 ({today_str}) 尚未上架，跳過更新。")
        return

    # 3. 讀取現有的 RSS 檔案
    if not os.path.exists(RSS_FILE):
        print("找不到 rss.xml，請先建立基礎模板。")
        return
        
    with open(RSS_FILE, "r", encoding="utf-8") as f:
        rss_content = f.read()

    # 4. 檢查是否已經收錄過這一集
    guid = f"bgog-{today_str}"
    if guid in rss_content:
        print(f"今日節目 ({today_str}) 已經在 RSS 中，無需重複更新。")
        return

    # 5. 構造新的 <item> 區塊
    new_item = f"""    <item>
      <title>{datetime.now().strftime("%Y-%m-%d")} Bad Girl 大過佬</title>
      <pubDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{target_url}" length="0" type="audio/aac" />
      <itunes:duration>02:00:00</itunes:duration>
    </item>
"""
    
    # 6. 插入到第一個 <item> 標籤之前（假設你已經有基礎結構）
    updated_content = rss_content.replace("    <item>", new_item + "    <item>", 1)

    with open(RSS_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"成功更新 RSS，已加入 {today_str} 的節目！")

if __name__ == "__main__":
    check_and_update()
