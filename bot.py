import os
import telebot
import time
import threading

print("🚀 Bot starting...")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(TOKEN)


# --- время ---
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


# --- разбан ---
def unban(chat_id, user_id, sec):
    time.sleep(sec)
    try:
        bot.unban_chat_member(chat_id, user_id)
    except:
        pass


# --- размут ---
def unmute(chat_id, user_id, sec):
    time.sleep(sec)
    try:
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
    except:
        pass


# --- БАН ---
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("бан"))
def ban(m):
    if not m.reply_to_message:
        bot.reply_to(m, "Ответь на сообщение пользователя")
        return

    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m, "Формат: бан 10m / 1h / 1d")
        return

    sec = parse_time(args[1])
    if not sec:
        bot.reply_to(m, "Неверное время")
        return

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    bot.kick_chat_member(cid, uid)
    bot.reply_to(m, f"🚫 Бан на {args[1]}")

    threading.Thread(target=unban, args=(cid, uid, sec)).start()


# --- МУТ ---
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("мут"))
def mute(m):
    if not m.reply_to_message:
        bot.reply_to(m, "Ответь на сообщение пользователя")
        return

    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m, "Формат: мут 10m / 1h / 1d")
        return

    sec = parse_time(args[1])
    if not sec:
        bot.reply_to(m, "Неверное время")
        return

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    bot.restrict_chat_member(cid, uid, can_send_messages=False)
    bot.reply_to(m, f"🔇 Мут на {args[1]}")

    threading.Thread(target=unmute, args=(cid, uid, sec)).start()


# --- старт ---
@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "бот работает ✅")

print("🤖 polling started")

bot.infinity_polling(skip_pending=True)