import os
import json
import requests
from datetime import datetime

# 从 GitHub Secrets 获取环境变量
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"发送失败: {e}")

def check_birthdays():
    # 读取生日数据
    if not os.path.exists("birthdays.json"):
        print("未找到 birthdays.json")
        return

    with open("birthdays.json", "r", encoding="utf-8") as f:
        birthdays = json.load(f)
    
    # 获取今日日期 (MM-dd)
    today = datetime.now().strftime("%m-%d")
    
    for person in birthdays:
        if person["date"] == today:
            msg = f"🎂 *生日提醒*\n\n今天是 **{person['name']}** 的生日！别忘了送上祝福！"
            send_tg_message(msg)

if __name__ == "__main__":
    check_birthdays()
