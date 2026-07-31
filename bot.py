import os, logging
from dotenv import load_dotenv
import telebot

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
if not TOKEN or not ADMIN_ID:
    raise RuntimeError("BOT_TOKEN va ADMIN_ID ni .env faylida kiriting.")

bot = telebot.TeleBot(TOKEN, parse_mode=None)
links = {}  # admin chatidagi message_id -> user_id

def save(mid, uid):
    links[mid] = uid

def get_uid(m):
    r = m.reply_to_message
    return links.get(r.message_id) if r else None

def user_info(u):
    name = ' '.join(filter(None, [u.first_name, u.last_name])) or 'Nomaʼlum'
    username = f'@{u.username}' if u.username else 'mavjud emas'
    return name, username

def desc(m):
    if m.caption:
        return m.caption
    return {
        "photo":"📷 Rasm", "video":"🎥 Video", "audio":"🎵 Audio",
        "voice":"🎤 Ovozli xabar", "document":"📎 Fayl",
        "animation":"🎞 GIF", "sticker":"🙂 Sticker",
        "video_note":"⭕ Video xabar", "contact":"👤 Kontakt",
        "location":"📍 Lokatsiya"
    }.get(m.content_type, f"📩 {m.content_type}")

@bot.message_handler(commands=["start","help"])
def start(m):
    bot.send_message(m.chat.id, "Assalomu alaykum!\n\nXabaringizni yozing. U administratorga yetkaziladi.")

@bot.message_handler(
    func=lambda m: m.chat.id != ADMIN_ID,
    content_types=["text","photo","video","audio","voice","document","animation","sticker","video_note","contact","location"]
)
def user_message(m):
    u = m.from_user
    name, username = user_info(u)
    if m.content_type == "text":
        info = bot.send_message(ADMIN_ID, f"👤 Ism: {name}\n🔗 User name: {username}\n🆔 ID: {u.id}\n💬 Xabar: {m.text}")
        save(info.message_id, u.id)
    else:
        info = bot.send_message(ADMIN_ID, f"👤 Ism: {name}\n🔗 User name: {username}\n🆔 ID: {u.id}\n💬 Xabar: {desc(m)}")
        save(info.message_id, u.id)
        copied = bot.copy_message(ADMIN_ID, m.chat.id, m.message_id, reply_to_message_id=info.message_id)
        save(copied.message_id, u.id)

@bot.message_handler(
    func=lambda m: m.chat.id == ADMIN_ID,
    content_types=["text","photo","video","audio","voice","document","animation","sticker","video_note","contact","location"]
)
def admin_message(m):
    if m.content_type == "text" and m.text.startswith("/"):
        return
    uid = get_uid(m)
    if not uid:
        bot.send_message(ADMIN_ID, "⚠️ Foydalanuvchiga javob berish uchun uning xabariga Reply qiling.")
        return
    try:
        bot.copy_message(uid, ADMIN_ID, m.message_id)
    except Exception:
        logging.exception("Reply yuborishda xato")
        bot.send_message(ADMIN_ID, "❌ Xabarni foydalanuvchiga yuborib bo‘lmadi.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🤖 Bot ishga tushdi...")
    bot.infinity_polling(skip_pending=True)
