import json
import datetime
from zhdate import ZhDate
import requests

# ====================== 配置项（GitHub Secrets 中读取） ======================
TELEGRAM_BOT_TOKEN = ""  # 会从环境变量读取
TELEGRAM_CHAT_ID = ""    # 会从环境变量读取

def load_birthdays():
    """加载生日列表"""
    with open("birthdays.json", "r", encoding="utf-8") as f:
        return json.load(f)

def parse_birthday(birthday_str):
    """解析 YYYYMMDD 格式为 年-月-日"""
    year = int(birthday_str[:4])
    month = int(birthday_str[4:6])
    day = int(birthday_str[6:8])
    return year, month, day

def get_days_diff(birth_month, birth_day, is_lunar):
    """计算距离生日的天数（忽略年份）"""
    today = datetime.date.today()
    
    if is_lunar:
        # 农历转公历
        birth_date = ZhDate(today.year, birth_month, birth_day).to_datetime().date()
    else:
        # 公历直接构造
        birth_date = datetime.date(today.year, birth_month, birth_day)

    # 如果生日已过，算明年
    if birth_date < today:
        if is_lunar:
            birth_date = ZhDate(today.year + 1, birth_month, birth_day).to_datetime().date()
        else:
            birth_date = datetime.date(today.year + 1, birth_month, birth_day)

    return (birth_date - today).days

def send_telegram_message(message):
    """发送消息到 Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=data)

def main():
    # 从环境变量读取配置
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    import os
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    birthdays = load_birthdays()
    reminder_list = []

    for user in birthdays:
        name = user["name"]
        birthday = user["birthday"]
        b_type = user["type"]
        year, month, day = parse_birthday(birthday)
        
        # 计算距离生日天数
        days_diff = get_days_diff(month, day, is_lunar=(b_type == "lunar"))
        
        # 提前3天 ~ 当天提醒（0=当天，1=提前1天，2=提前2天，3=提前3天）
        if 0 <= days_diff <= 3:
            type_text = "农历" if b_type == "lunar" else "公历"
            if days_diff == 0:
                reminder_list.append(f"🎉 **{name}** 今天({type_text})生日啦！")
            else:
                reminder_list.append(f"📅 **{name}** 还有 {days_diff} 天过{type_text}生日！")

    # 有需要提醒的就发送消息
    if reminder_list:
        final_msg = "🎂 生日提醒\n\n" + "\n".join(reminder_list)
        send_telegram_message(final_msg)
        print("已发送提醒：", final_msg)
    else:
        print("今日无生日提醒")

if __name__ == "__main__":
    main()
