import telebot
import yt_dlp
import os
import tempfile

TOKEN = "8668457678:AAGq2WdTUj3knAny4xHVB_wZEf7U_JwdL-M"
KANAL = "@botcreator550"
KANAL_LINK = "https://t.me/botcreator550"

bot = telebot.TeleBot(TOKEN)

def obuna_tekshir(user_id):
    try:
        member = bot.get_chat_member(KANAL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def obuna_tugmasi():
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Kanalga obuna bo'lish", url=KANAL_LINK))
    kb.add(InlineKeyboardButton("✅ Obuna bo'ldim", callback_data="tekshir"))
    return kb

def havola_tekshir(text):
    domains = ["youtube.com", "youtu.be", "instagram.com", "tiktok.com",
               "twitter.com", "x.com", "facebook.com", "vk.com"]
    return any(d in text.lower() for d in domains)

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    user_id = msg.from_user.id
    if not obuna_tekshir(user_id):
        bot.send_message(msg.chat.id,
            "👋 Salom! Botdan foydalanish uchun kanalga obuna bo'ling!",
            reply_markup=obuna_tugmasi())
        return

    bot.send_message(msg.chat.id,
        "👋 *Salom!*\n\n"
        "Men video va rasm yuklab oluvchi botman!\n\n"
        "📥 *Qo'llab-quvvatlanadigan saytlar:*\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok\n"
        "• Twitter/X\n"
        "• Facebook\n"
        "• VK\n\n"
        "Havola yuboring — yuklab beraman! 🚀",
        parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    user_id = msg.from_user.id

    if not obuna_tekshir(user_id):
        bot.send_message(msg.chat.id,
            "⚠️ Botdan foydalanish uchun kanalga obuna bo'ling!",
            reply_markup=obuna_tugmasi())
        return

    text = msg.text.strip() if msg.text else ""

    if not havola_tekshir(text):
        bot.reply_to(msg, "🔗 Iltimos, to'g'ri havola yuboring!\n\nYouTube, Instagram, TikTok va boshqa saytlar qo'llab-quvvatlanadi.")
        return

    yuklanmoqda = bot.reply_to(msg, "⏳ Yuklanmoqda... Iltimos kuting!")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                "format": "best[filesize<50M]/best",
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                title = info.get("title", "Video")

            fayllar = os.listdir(tmpdir)
            if not fayllar:
                bot.edit_message_text("❌ Video yuklab bo'lmadi.",
                                      msg.chat.id, yuklanmoqda.message_id)
                return

            fayl_yoli = os.path.join(tmpdir, fayllar[0])
            fayl_hajmi = os.path.getsize(fayl_yoli)

            # 50MB dan katta bo'lsa
            if fayl_hajmi > 50 * 1024 * 1024:
                bot.edit_message_text(
                    "⚠️ Fayl hajmi 50MB dan katta. Telegram cheklovi tufayli yuborib bo'lmaydi.",
                    msg.chat.id, yuklanmoqda.message_id)
                return

            ext = fayllar[0].split(".")[-1].lower()

            bot.edit_message_text("📤 Yuborilmoqda...",
                                  msg.chat.id, yuklanmoqda.message_id)

            with open(fayl_yoli, "rb") as f:
                if ext in ["jpg", "jpeg", "png", "webp"]:
                    bot.send_photo(msg.chat.id, f, caption=f"📸 {title}")
                else:
                    bot.send_video(msg.chat.id, f, caption=f"🎬 {title}",
                                   supports_streaming=True)

            bot.delete_message(msg.chat.id, yuklanmoqda.message_id)

    except yt_dlp.utils.DownloadError as e:
        bot.edit_message_text(
            "❌ Bu havoladan yuklab bo'lmadi.\n\nSabab: Maxfiy yoki mavjud emas.",
            msg.chat.id, yuklanmoqda.message_id)
    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
            msg.chat.id, yuklanmoqda.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "tekshir")
def tekshir_callback(call):
    user_id = call.from_user.id
    if obuna_tekshir(user_id):
        bot.edit_message_text(
            "✅ Obuna tasdiqlandi! Endi havola yuboring.",
            call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id,
            "❌ Hali obuna bo'lmadingiz!", show_alert=True)

print("🤖 Yuklovchi bot ishga tushdi!")
bot.infinity_polling()
