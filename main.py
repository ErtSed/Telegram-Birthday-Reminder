import json
import os
import datetime
import requests
from borax.calendars.lunardate import LunarDate

def get_valid_lunar_date(year, month, day):
    """
    获取有效的农历日期。处理农历大小月问题，如果某个月没有30号，则取29号。
    """
    try:
        return LunarDate(year, month, day)
    except ValueError:
        return LunarDate(year, month, day - 1)

def send_telegram_message(token, chat_id, text):
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram 消息发送成功！")
    except Exception as e:
        print(f"Telegram 消息发送失败: {e}")

def main():
    # 1. 获取环境变量（在 Github Actions 的 Secrets 中配置）
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("未找到 Telegram Token 或 Chat ID，请检查环境变量配置。")
        return

    # 2. 读取生日配置文件
    try:
        with open("birthdays.json", "r", encoding="utf-8") as f:
            birthdays = json.load(f)
    except Exception as e:
        print(f"读取 birthdays.json 失败: {e}")
        return

    today_solar = datetime.date.today()
    messages = []

    # 3. 遍历计算每个人的生日
    for person in birthdays:
        name = person.get("name")
        date_str = person.get("date")  # 格式 YYYYMMDD
        b_type = person.get("type")    # solar (公历) 或 lunar (农历)

        if not name or not date_str or not b_type:
            continue

        birth_year = int(date_str[0:4])
        birth_month = int(date_str[4:6])
        birth_day = int(date_str[6:8])

        if b_type == "solar":
            # 公历计算逻辑
            try:
                this_year_bday = datetime.date(today_solar.year, birth_month, birth_day)
            except ValueError:
                # 处理闰年2月29日生日，非闰年视作3月1日
                this_year_bday = datetime.date(today_solar.year, 3, 1)

            if this_year_bday < today_solar:
                # 今年的生日已经过了，计算明年的
                try:
                    next_bday = datetime.date(today_solar.year + 1, birth_month, birth_day)
                except ValueError:
                    next_bday = datetime.date(today_solar.year + 1, 3, 1)
            else:
                next_bday = this_year_bday
            
            age = next_bday.year - birth_year
            date_display = f"公历 {birth_month}月{birth_day}日"

        elif b_type == "lunar":
            # 农历计算逻辑
            today_lunar = LunarDate.from_solar_date(today_solar.year, today_solar.month, today_solar.day)
            
            # 推算今年的农历生日对应的公历日期
            this_year_lunar_bday = get_valid_lunar_date(today_lunar.year, birth_month, birth_day)
            this_year_solar_bday = this_year_lunar_bday.to_solar_date()

            if this_year_solar_bday < today_solar:
                # 今年的农历生日已经过了，计算明年的
                next_lunar_bday = get_valid_lunar_date(today_lunar.year + 1, birth_month, birth_day)
                next_bday = next_lunar_bday.to_solar_date()
            else:
                next_bday = this_year_solar_bday
            
            age = next_bday.year - birth_year
            date_display = f"农历 {this_year_lunar_bday.cn_month}月{this_year_lunar_bday.cn_day}"
            
        else:
            continue

        # 计算距离下次生日还有多少天
        days_left = (next_bday - today_solar).days

        # 4. 判断是否在提醒范围内（提前3天至当天）
        if 0 <= days_left <= 3:
            if days_left == 0:
                msg = f"🎂 <b>{name}</b> 的生日就是今天啦！（{date_display}，{age}岁）\n快去送上祝福吧！"
            else:
                msg = f"⏳ 距离 <b>{name}</b> 的生日还有 <b>{days_left}</b> 天！（{date_display}，即将 {age} 岁）"
            messages.append(msg)

    # 5. 汇总并发送提醒
    if messages:
        final_text = "🎉 <b>生日提醒</b> 🎉\n\n" + "\n\n".join(messages) + "\n\n<i>—— 你的专属提醒小助手 DiWinter</i>"
        send_telegram_message(token, chat_id, final_text)
    else:
        print("今天没有需要提醒的生日。")

if __name__ == "__main__":
    main()
