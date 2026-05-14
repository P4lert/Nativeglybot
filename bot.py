import os
import telebot
import time
import threading

print("🚀 Bot starting...")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN is missing")
    exit()

bot = telebot.TeleBot(TOKEN)


# ---------- TIME PARSER ----------
def parse_time(text):
    try:
        if text.endswith("m"):
            return int(text[:-1]) * 60
        if text.endswith("h"):
            return int(text[:-1]) * 3600
        if text.endswith("d"):
            return int(text[:-1]) * 86400
    except:
        return None


# ---------- UNMUTE ----------
def unmute(chat_id, user_id, seconds):
    time.sleep(seconds)
    try:
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
    except Exception as e:
        print("Unmute error:", e)


# ---------- UNBAN ----------
def unban(chat_id, user_id, seconds):
    time.sleep(seconds)
    try:
        bot.unban_chat_member(chat_id, user_id)
    except Exception as e:
        print("Unban error:", e)


# ---------- MUTE ----------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("мут"))
def mute(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "Ответь на пользователя")

    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "Формат: мут 10m / 1h / 1d")

    seconds = parse_time(parts[1])
    if not seconds:
        return bot.reply_to(message, "Неверное время")

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id

    bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
    bot.reply_to(message, f"🔇 мут на {parts[1]}")

    threading.Thread(target=unmute, args=(chat_id, user_id, seconds)).start()


# ---------- BAN ----------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("бан"))
def ban(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "Ответь на пользователя")

    parts = message.text.split()
    if len(parts) < 2:
        return bot.reply_to(message, "Формат: бан 10m / 1h / 1d")

    seconds = parse_time(parts[1])
    if not seconds:
        return bot.reply_to(message, "Неверное время")

    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id

    bot.kick_chat_member(chat_id, user_id)
    bot.reply_to(message, f"🚫 бан на {parts[1]}")

    threading.Thread(target=unban, args=(chat_id, user_id, seconds)).start()


# ---------- START ----------
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "бот работает ✅")


print("🤖 polling started")

bot.infinity_polling(skip_pending=True)
