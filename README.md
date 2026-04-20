# Telegram 生日自动提醒
基于 GitHub Actions 自动运行，支持公历/农历生日，提前3天+当天提醒

## 使用方法
1. 修改 `birthdays.json` 添加生日信息
2. 在 GitHub 仓库 Settings -> Secrets and variables -> Actions 中添加两个密钥：
   - `TELEGRAM_BOT_TOKEN`: 你的机器人 Token
   - `TELEGRAM_CHAT_ID`: 接收提醒的聊天 ID
3. 自动每天 8 点检查并提醒

## 生日格式
统一格式：YYYYMMDD
type：solar=公历，lunar=农历
