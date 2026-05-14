import os
import telebot
import time
import threading
import random

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN not found")
    exit()

bot = telebot.TeleBot(TOKEN)

print("🚀 Nativegly ONLINE")


# ----------------- РОЛИ -----------------
roles = {}
warns = {}
users = {}


def get_level(user_id):
    return roles.get(user_id, 1)


def is_owner(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status == "creator"
    except:
        return False


def can_mod(user_id, chat_id):
    return get_level(user_id) >= 3 or is_owner(chat_id, user_id)


# ----------------- TIME -----------------
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


def min_mute(sec):
    return max(sec, 300)  # минимум 5 минут


def min_ban(sec):
    return max(sec, 86400)  # минимум 1 день


# ----------------- USER TRACKER -----------------
@bot.message_handler(func=lambda m: True)
def tracker(m):
    users[m.from_user.id] = m.from_user.first_name


# ----------------- ПРОБУЖДЕНИЕ -----------------
@bot.message_handler(content_types=["new_chat_members"])
def wake(m):
    for u in m.new_chat_members:
        if u.id == bot.get_me().id:

            if is_owner(m.chat.id, m.from_user.id):
                roles[m.from_user.id] = 5

            bot.send_message(
                m.chat.id,
                "⚜️ Я, Nativegly, пробуждён.\n"
                "Система модерации активирована.\n"
                "Этот чат принят под наблюдение."
            )

            print("✅ Activated in:", m.chat.id)


# ----------------- UNMUTE -----------------
def unmute(chat_id, user_id, sec):
    time.sleep(sec)

    try:
        bot.restrict_chat_member(
            chat_id,
            user_id,
            can_send_messages=True
        )

        print("🔊 User unmuted")

    except Exception as e:
        print("UNMUTE ERROR:", e)


# ----------------- UNBAN -----------------
def unban(chat_id, user_id, sec):
    time.sleep(sec)

    try:
        bot.unban_chat_member(chat_id, user_id)

        print("🔓 User unbanned")

    except Exception as e:
        print("UNBAN ERROR:", e)


# ----------------- МУТ -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("мут"))
def mute(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    parts = m.text.split()

    if len(parts) < 2:
        return bot.reply_to(m, "пример: мут 10m")

    sec = parse_time(parts[1])

    if not sec:
        return bot.reply_to(m, "❌ ошибка времени")

    sec = min_mute(sec)

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    if can_mod(uid, cid) or is_owner(cid, uid):
        return bot.reply_to(m, "❌ нельзя мутить администрацию")

    try:
        bot.restrict_chat_member(
            cid,
            uid,
            can_send_messages=False
        )

        bot.reply_to(m, f"🔇 пользователь замучен на {parts[1]}")

        threading.Thread(
            target=unmute,
            args=(cid, uid, sec)
        ).start()

    except Exception as e:
        bot.reply_to(m, f"ERROR: {e}")


# ----------------- РАЗМУТ -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("размут"))
def unmute_cmd(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    try:
        bot.restrict_chat_member(
            cid,
            uid,
            can_send_messages=True
        )

        bot.reply_to(m, "🔊 пользователь размучен")

    except Exception as e:
        bot.reply_to(m, f"ERROR: {e}")


# ----------------- БАН -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("бан"))
def ban(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    parts = m.text.split()

    if len(parts) < 2:
        return bot.reply_to(m, "пример: бан 1d")

    sec = parse_time(parts[1])

    if not sec:
        return bot.reply_to(m, "❌ ошибка времени")

    sec = min_ban(sec)

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    if can_mod(uid, cid) or is_owner(cid, uid):
        return bot.reply_to(m, "❌ нельзя банить администрацию")

    try:
        bot.kick_chat_member(cid, uid)

        bot.reply_to(m, f"🚫 пользователь забанен на {parts[1]}")

        threading.Thread(
            target=unban,
            args=(cid, uid, sec)
        ).start()

    except Exception as e:
        bot.reply_to(m, f"ERROR: {e}")


# ----------------- ВАРН -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("варн"))
def warn(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    uid = m.reply_to_message.from_user.id

    warns[uid] = warns.get(uid, 0) + 1

    bot.reply_to(
        m,
        f"⚠️ предупреждение {warns[uid]}/3"
    )


# ----------------- ШАНС -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("шанс"))
def chance(m):

    chance_value = random.randint(0, 100)

    bot.reply_to(
        m,
        f"🎲 вероятность: {chance_value}%"
    )


# ----------------- STAT -----------------
@bot.message_handler(commands=["stat"])
def stat(m):

    text = "📊 СТАТИСТИКА:\n\n"

    for uid, name in users.items():

        lvl = roles.get(uid, 1)

        text += f"{name} — уровень {lvl}\n"

    bot.reply_to(m, text)


# ----------------- START -----------------
@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "⚜️ Nativegly online")


# ----------------- START BOT -----------------
bot.infinity_polling(skip_pending=True) import os
import telebot
import time
import threading
import random

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN not found")
    exit()

bot = telebot.TeleBot(TOKEN)

print("🚀 Nativegly ONLINE")


# ----------------- РОЛИ -----------------
roles = {}
warns = {}
users = {}


def get_level(user_id):
    return roles.get(user_id, 1)


def is_owner(chat_id, user_id):
    try:
        m = bot.get_chat_member(chat_id, user_id)
        return m.status == "creator"
    except:
        return False


def can_mod(user_id, chat_id):
    return get_level(user_id) >= 3 or is_owner(chat_id, user_id)


# ----------------- TIME -----------------
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


def min_mute(sec):
    return max(sec, 300)  # минимум 5 минут


def min_ban(sec):
    return max(sec, 86400)  # минимум 1 день


# ----------------- USER TRACKER -----------------
@bot.message_handler(func=lambda m: True)
def tracker(m):
    users[m.from_user.id] = m.from_user.first_name


# ----------------- ПРОБУЖДЕНИЕ -----------------
@bot.message_handler(content_types=["new_chat_members"])
def wake(m):
    for u in m.new_chat_members:
        if u.id == bot.get_me().id:

            if is_owner(m.chat.id, m.from_user.id):
                roles[m.from_user.id] = 5

            bot.send_message(
                m.chat.id,
                "⚜️ Я, Nativegly, пробуждён.\n"
                "Система модерации активирована.\n"
                "Этот чат принят под наблюдение."
            )

            print("✅ Activated in:", m.chat.id)


# ----------------- UNMUTE -----------------
def unmute(chat_id, user_id, sec):
    time.sleep(sec)

    try:
        bot.restrict_chat_member(
            chat_id,
            user_id,
            can_send_messages=True
        )

        print("🔊 User unmuted")

    except Exception as e:
        print("UNMUTE ERROR:", e)


# ----------------- UNBAN -----------------
def unban(chat_id, user_id, sec):
    time.sleep(sec)

    try:
        bot.unban_chat_member(chat_id, user_id)

        print("🔓 User unbanned")

    except Exception as e:
        print("UNBAN ERROR:", e)


# ----------------- МУТ -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("мут"))
def mute(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    parts = m.text.split()

    if len(parts) < 2:
        return bot.reply_to(m, "пример: мут 10m")

    sec = parse_time(parts[1])

    if not sec:
        return bot.reply_to(m, "❌ ошибка времени")

    sec = min_mute(sec)

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    if can_mod(uid, cid) or is_owner(cid, uid):
        return bot.reply_to(m, "❌ нельзя мутить администрацию")

    try:
        bot.restrict_chat_member(
            cid,
            uid,
            can_send_messages=False
        )

        bot.reply_to(m, f"🔇 пользователь замучен на {parts[1]}")

        threading.Thread(
            target=unmute,
            args=(cid, uid, sec)
        ).start()

    except Exception as e:
        bot.reply_to(m, f"ERROR: {e}")


# ----------------- РАЗМУТ -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("размут"))
def unmute_cmd(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    try:
        bot.restrict_chat_member(
            cid,
            uid,
            can_send_messages=True
        )

        bot.reply_to(m, "🔊 пользователь размучен")

    except Exception as e:
        bot.reply_to(m, f"ERROR: {e}")


# ----------------- БАН -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("бан"))
def ban(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    parts = m.text.split()

    if len(parts) < 2:
        return bot.reply_to(m, "пример: бан 1d")

    sec = parse_time(parts[1])

    if not sec:
        return bot.reply_to(m, "❌ ошибка времени")

    sec = min_ban(sec)

    uid = m.reply_to_message.from_user.id
    cid = m.chat.id

    if can_mod(uid, cid) or is_owner(cid, uid):
        return bot.reply_to(m, "❌ нельзя банить администрацию")

    try:
        bot.kick_chat_member(cid, uid)

        bot.reply_to(m, f"🚫 пользователь забанен на {parts[1]}")

        threading.Thread(
            target=unban,
            args=(cid, uid, sec)
        ).start()

    except Exception as e:
        bot.reply_to(m, f"ERROR: {e}")


# ----------------- ВАРН -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("варн"))
def warn(m):

    if not can_mod(m.from_user.id, m.chat.id):
        return bot.reply_to(m, "❌ нет прав")

    if not m.reply_to_message:
        return bot.reply_to(m, "⚠️ ответь на пользователя")

    uid = m.reply_to_message.from_user.id

    warns[uid] = warns.get(uid, 0) + 1

    bot.reply_to(
        m,
        f"⚠️ предупреждение {warns[uid]}/3"
    )


# ----------------- ШАНС -----------------
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("шанс"))
def chance(m):

    chance_value = random.randint(0, 100)

    bot.reply_to(
        m,
        f"🎲 вероятность: {chance_value}%"
    )


# ----------------- STAT -----------------
@bot.message_handler(commands=["stat"])
def stat(m):

    text = "📊 СТАТИСТИКА:\n\n"

    for uid, name in users.items():

        lvl = roles.get(uid, 1)

        text += f"{name} — уровень {lvl}\n"

    bot.reply_to(m, text)


# ----------------- START -----------------
@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "⚜️ Nativegly online")


# ----------------- START BOT -----------------
bot.infinity_polling(skip_pending=True)
