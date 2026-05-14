import os
import telebot
import time

print("🚀 Bot starting...")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("NO TOKEN")
    exit()

bot = telebot.TeleBot(TOKEN)


def parse_time(t):
    try:
        if t.endswith("m"):
            return int(t[:-1]) * 60
        if t.endswith("h"):
            return int(t[:-1]) * 3600
        if t.endswith("d"):
            return int(t[:-1]) * 86400
    except:
        return None


@bot.message_handler(func=lambda m: m.text and m.text.startswith("мут"))
def mute(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "reply на пользователя")

    sec = parse_time(m.text.split()[1])
    if not sec:
        return bot.reply_to(m, "ошибка времени")

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    try:
        bot.restrict_chat_member(cid, uid, can_send_messages=False)
        bot.reply_to(m, "🔇 мут")

        time.sleep(sec)

        bot.restrict_chat_member(cid, uid, can_send_messages=True)

    except Exception as e:
        print("mute error:", e)


@bot.message_handler(func=lambda m: m.text and m.text.startswith("бан"))
def ban(m):
    if not m.reply_to_message:
        return bot.reply_to(m, "reply на пользователя")

    sec = parse_time(m.text.split()[1])
    if not sec:
        return bot.reply_to(m, "ошибка времени")

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    try:
        bot.kick_chat_member(cid, uid)
        bot.reply_to(m, "🚫 бан")

        time.sleep(sec)

        bot.unban_chat_member(cid, uid)

    except Exception as e:
        print("ban error:", e)


@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "бот работает ✅")


bot.infinity_polling(skip_pending=True)
