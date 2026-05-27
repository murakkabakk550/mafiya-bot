import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random

TOKEN = "8936796412:AAHCDw3AM0gllNFBVBuq5FZ9OG-FBghXQ9g"
bot = telebot.TeleBot(TOKEN)

ROLLAR = {
    "Mafiya sardori":          {"taraf": "mafiya", "rang": "😈"},
    "Mafiya":                  {"taraf": "mafiya", "rang": "🔫"},
    "Komissiyar":              {"taraf": "tinch",  "rang": "🔍"},
    "Komissiyar yordamchisi":  {"taraf": "tinch",  "rang": "🪖"},
    "Shifokor":                {"taraf": "tinch",  "rang": "💊"},
    "Jurnalist":               {"taraf": "tinch",  "rang": "📰"},
    "Sehrgar":                 {"taraf": "tinch",  "rang": "🧙"},
    "Arvoh":                   {"taraf": "tinch",  "rang": "👻"},
    "Qaysar":                  {"taraf": "tinch",  "rang": "💪"},
    "Olmas":                   {"taraf": "tinch",  "rang": "💎"},
    "Hamelion":                {"taraf": "tinch",  "rang": "🦎"},
    "Shohi":                   {"taraf": "tinch",  "rang": "👑"},
    "Bomber":                  {"taraf": "tinch",  "rang": "💣"},
    "Qorbola":                 {"taraf": "tinch",  "rang": "❄️"},
    "Gadoyi":                  {"taraf": "tinch",  "rang": "🎒"},
    "Qotil":                   {"taraf": "yakka",  "rang": "🗡️"},
    "Tinch aholi":             {"taraf": "tinch",  "rang": "👤"},
}

ROL_TAVSIF = {
    "Mafiya sardori": "Tunda bir odamni o'ldirasan. Mafiyalar seni biladi.",
    "Mafiya": "Sardor bilan birga ishlaysan.",
    "Komissiyar": "Tunda 1 kishini tekshirasan (mafiyami yoki yo'q).",
    "Komissiyar yordamchisi": "Boshlig'ing o'lsa, komissiyar bo'lasan.",
    "Shifokor": "Tunda 1 kishini himoyalaysan (o'zingni ham).",
    "Jurnalist": "Tunda 1 kishining rolini bilib olasan.",
    "Sehrgar": "2 marta rol almashtirish + hammaning rolini ko'rish.",
    "Arvoh": "O'ldirilsang ovoz bergan birini o'zing bilan ola.",
    "Qaysar": "Birinchi ovozda chiqmaysan, ikkinchida chiqasan.",
    "Olmas": "Bir marta osib o'ldirishdan saqlanasan.",
    "Hamelion": "Mafiya/qotil o'ldirsa, o'rninga boshqa odam o'ladi.",
    "Shohi": "Ovozingiz 2 kishiga teng hisoblanadi.",
    "Bomber": "Tunda 3 kishini kuzatuv ostiga ol. O'lsang ular portlaydi.",
    "Qorbola": "Tunda 5 kishini muzlatasan — mafiya o'ldira olmaydi.",
    "Gadoyi": "Har kecha 1 uyga borasan. O'sha kishi o'lsa, mafiyani bilasan.",
    "Qotil": "Hammani o'ldiring — yolg'iz g'olib siz.",
    "Tinch aholi": "Kunduz ovoz berib mafiyani toping.",
}

games = {}

class Oyinchi:
    def __init__(self, user_id, ism):
        self.user_id = user_id
        self.ism = ism
        self.rol = None
        self.tirik = True
        self.himoyalangan = False
        self.muzlatilgan = False
        self.qaysar_chiqdi = False
        self.olmas_ishlatilgan = False
        self.bomber_kuzatuvdagilar = []

class GameState:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.oyinchilar = []
        self.boshlandi = False
        self.kun = 1
        self.faza = "yigish"
        self.admin_id = None
        self.tun_harakatlari = {}
        self.ovozlar = {}
        self.qorbola_tanlangan = []

    def oyinchi(self, user_id):
        for o in self.oyinchilar:
            if o.user_id == user_id:
                return o
        return None

    def tirik_oyinchilar(self):
        return [o for o in self.oyinchilar if o.tirik]

    def mafiyalar(self):
        return [o for o in self.tirik_oyinchilar()
                if o.rol in ("Mafiya", "Mafiya sardori")]

    def qotil(self):
        q = [o for o in self.tirik_oyinchilar() if o.rol == "Qotil"]
        return q[0] if q else None

    def golish_sharti(self):
        tiriklar = self.tirik_oyinchilar()
        maflar = self.mafiyalar()
        tinchlar = [o for o in tiriklar
                    if ROLLAR.get(o.rol, {}).get("taraf") == "tinch"]
        qotil = self.qotil()
        if len(maflar) == 0 and qotil is None:
            return "tinch"
        if len(maflar) >= len(tinchlar):
            return "mafiya"
        if qotil and len([o for o in tiriklar if o != qotil]) <= 1:
            return "qotil"
        return None

def rol_taqsimlash(n):
    rollar = ["Mafiya sardori"]
    for _ in range(max(0, n // 7 - 1)):
        rollar.append("Mafiya")
    maxsus = ["Komissiyar", "Komissiyar yordamchisi", "Shifokor",
              "Jurnalist", "Sehrgar", "Arvoh", "Qaysar", "Olmas",
              "Hamelion", "Shohi", "Bomber", "Qorbola", "Gadoyi", "Qotil"]
    qolgan = n - len(rollar)
    qosh = min(len(maxsus), max(0, qolgan - 1))
    rollar.extend(random.sample(maxsus, qosh))
    while len(rollar) < n:
        rollar.append("Tinch aholi")
    random.shuffle(rollar)
    return rollar

def tirik_royxat(g):
    tiriklar = g.tirik_oyinchilar()
    olganlar = [o for o in g.oyinchilar if not o.tirik]
    text = "👥 *Tirik o'yinchilar:*\n"
    for i, o in enumerate(tiriklar, 1):
        text += f"  {i}. {o.ism}\n"
    if olganlar:
        text += "\n💀 *O'lganlar:*\n"
        for o in olganlar:
            rang = ROLLAR.get(o.rol, {}).get("rang", "👤")
            text += f"  ✗ {o.ism} — {rang} {o.rol}\n"
    return text

def guruhga(chat_id, text, markup=None):
    bot.send_message(chat_id, text, parse_mode="Markdown",
                     reply_markup=markup)

def shaxsiy(user_id, text, markup=None):
    try:
        bot.send_message(user_id, text, parse_mode="Markdown",
                         reply_markup=markup)
        return True
    except:
        return False

def tugmalar(candidates, prefix, chat_id):
    kb = InlineKeyboardMarkup()
    for c in candidates:
        kb.add(InlineKeyboardButton(
            c.ism,
            callback_data=f"{prefix}|{chat_id}|{c.user_id}"
        ))
    return kb

# ======================== KOMANDALAR ========================

@bot.message_handler(commands=["start", "oyun"])
def cmd_oyun(msg):
    if msg.chat.type == "private":
        bot.reply_to(msg, "Salom! Guruhga qo'shing va /oyun bosing.")
        return
    chat_id = msg.chat.id
    if chat_id in games and games[chat_id].boshlandi:
        bot.reply_to(msg, "⚠️ O'yin allaqachon boshlangan!")
        return
    g = GameState(chat_id)
    g.admin_id = msg.from_user.id
    games[chat_id] = g
    bot.reply_to(msg,
        "🎮 *MAFIYA O'YINI YARATILDI!*\n\n"
        "Qo'shilish: /qoshil\n"
        "Kamida 4 kishi kerak.\n\n"
        f"👑 Admin: {msg.from_user.first_name}",
        parse_mode="Markdown")

@bot.message_handler(commands=["qoshil"])
def cmd_qoshil(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        bot.reply_to(msg, "Avval /oyun yozing!")
        return
    g = games[chat_id]
    if g.boshlandi:
        bot.reply_to(msg, "O'yin boshlangan!")
        return
    user = msg.from_user
    if g.oyinchi(user.id):
        bot.reply_to(msg, f"{user.first_name} allaqachon bor!")
        return
    g.oyinchilar.append(Oyinchi(user.id, user.first_name))
    bot.reply_to(msg,
        f"✅ {user.first_name} qo'shildi! Jami: {len(g.oyinchilar)} kishi")

@bot.message_handler(commands=["royhatt"])
def cmd_royhat(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        return
    g = games[chat_id]
    text = f"👥 Ro'yxat ({len(g.oyinchilar)} kishi):\n"
    for i, o in enumerate(g.oyinchilar, 1):
        text += f"  {i}. {o.ism}\n"
    bot.reply_to(msg, text)

@bot.message_handler(commands=["boshlash"])
def cmd_boshlash(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        bot.reply_to(msg, "Avval /oyun yozing!")
        return
    g = games[chat_id]
    if msg.from_user.id != g.admin_id:
        bot.reply_to(msg, "Faqat admin boshlashi mumkin!")
        return
    if len(g.oyinchilar) < 4:
        bot.reply_to(msg, "Kamida 4 kishi kerak!")
        return
    if g.boshlandi:
        bot.reply_to(msg, "Allaqachon boshlangan!")
        return

    g.boshlandi = True
    rollar = rol_taqsimlash(len(g.oyinchilar))
    for i, o in enumerate(g.oyinchilar):
        o.rol = rollar[i]

    guruhga(chat_id,
        "🎭 *Rollar taqsimlandi!*\n\n"
        "Har bir o'yinchi shaxsiy xabarini ko'rsin.\n"
        "Agar kelmasa — botga /start yozing!\n\n"
        "Admin /tun yozguncha muhokama qiling.")

    mafiyalar = g.mafiyalar()
    for o in g.oyinchilar:
        rang = ROLLAR.get(o.rol, {}).get("rang", "👤")
        tavsif = ROL_TAVSIF.get(o.rol, "")
        text = (f"🎭 *Sizning rolingiz:*\n\n"
                f"{rang} *{o.rol.upper()}*\n\n_{tavsif}_")
        if o.rol in ("Mafiya", "Mafiya sardori") and len(mafiyalar) > 1:
            boshq = [m.ism for m in mafiyalar if m.user_id != o.user_id]
            text += f"\n\n👥 Sheriklaring: {', '.join(boshq)}"
        ok = shaxsiy(o.user_id, text)
        if not ok:
            guruhga(chat_id, f"⚠️ {o.ism} — botga /start yuboring!")

@bot.message_handler(commands=["tun"])
def cmd_tun(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        return
    g = games[chat_id]
    if msg.from_user.id != g.admin_id:
        bot.reply_to(msg, "Faqat admin!")
        return

    g.faza = "tun"
    g.tun_harakatlari = {}
    g.qorbola_tanlangan = []

    for o in g.tirik_oyinchilar():
        o.himoyalangan = False
        o.muzlatilgan = False
        o.bomber_kuzatuvdagilar = []

    guruhga(chat_id,
        f"🌙 *{g.kun}-kun tuni!*\n\nMaxsus rollar shaxsiy xabarga qarang.")

    tiriklar = g.tirik_oyinchilar()

    # Qorbola
    qb = next((o for o in tiriklar if o.rol == "Qorbola"), None)
    if qb:
        candidates = [o for o in tiriklar if o != qb]
        shaxsiy(qb.user_id,
            "❄️ *Qor Bola* — 5 kishini muzlat (birma-bir tanlang):",
            tugmalar(candidates, "qorbola", chat_id))

    # Shifokor
    shif = next((o for o in tiriklar if o.rol == "Shifokor"), None)
    if shif:
        shaxsiy(shif.user_id, "💊 *Shifokor* — Kimni himoyalaysiz?",
                tugmalar(tiriklar, "shifokor", chat_id))

    # Mafiya sardori
    sardor = next((o for o in tiriklar if o.rol == "Mafiya sardori"), None)
    if sardor:
        candidates = [o for o in tiriklar if o not in g.mafiyalar()]
        shaxsiy(sardor.user_id, "😈 *Mafiya Sardori* — Kimni o'ldirasiz?",
                tugmalar(candidates, "mafiya", chat_id))

    # Komissiyar
    kom = next((o for o in tiriklar if o.rol == "Komissiyar"), None)
    if kom:
        candidates = [o for o in tiriklar if o != kom]
        shaxsiy(kom.user_id, "🔍 *Komissiyar* — Kimni tekshirасiz?",
                tugmalar(candidates, "komissiyar", chat_id))

    # Jurnalist
    jur = next((o for o in tiriklar if o.rol == "Jurnalist"), None)
    if jur:
        candidates = [o for o in tiriklar if o != jur]
        shaxsiy(jur.user_id, "📰 *Jurnalist* — Kimning rolini bilasiz?",
                tugmalar(candidates, "jurnalist", chat_id))

    # Bomber
    bomb = next((o for o in tiriklar if o.rol == "Bomber"), None)
    if bomb:
        candidates = [o for o in tiriklar if o != bomb]
        shaxsiy(bomb.user_id,
            "💣 *Bomber* — 3 kishini kuzatuv ostiga ol (birma-bir):",
            tugmalar(candidates, "bomber", chat_id))

    # Gadoyi
    gad = next((o for o in tiriklar if o.rol == "Gadoyi"), None)
    if gad:
        candidates = [o for o in tiriklar if o != gad]
        shaxsiy(gad.user_id, "🎒 *Gadoyi* — Qaysi uyga borасiz?",
                tugmalar(candidates, "gadoyi", chat_id))

    # Qotil
    qot = g.qotil()
    if qot:
        candidates = [o for o in tiriklar if o != qot]
        shaxsiy(qot.user_id, "🗡️ *Qotil* — Kimni o'ldirasiz?",
                tugmalar(candidates, "qotil", chat_id))

@bot.message_handler(commands=["tontugat"])
def cmd_tontugat(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        return
    g = games[chat_id]
    if msg.from_user.id != g.admin_id:
        bot.reply_to(msg, "Faqat admin!")
        return

    xabarlar = []

    # Mafiya harakati
    if "mafiya" in g.tun_harakatlari:
        nishon = g.oyinchi(g.tun_harakatlari["mafiya"])
        if nishon and nishon.tirik:
            if nishon.muzlatilgan:
                xabarlar.append(f"❄️ {nishon.ism} muzlatilgan edi — omon qoldi!")
            elif nishon.himoyalangan:
                xabarlar.append(f"💊 {nishon.ism} shifokor tomonidan saqlanib qoldi!")
            elif nishon.rol == "Hamelion":
                boshqalar = [o for o in g.tirik_oyinchilar() if o != nishon]
                if boshqalar:
                    alm = random.choice(boshqalar)
                    alm.tirik = False
                    xabarlar.append(f"🦎 Hamelion: {nishon.ism} o'rniga {alm.ism} o'ldi!")
            elif nishon.rol == "Olmas" and not nishon.olmas_ishlatilgan:
                nishon.olmas_ishlatilgan = True
                xabarlar.append(f"💎 {nishon.ism} (Olmas) — omon qoldi!")
            else:
                nishon.tirik = False
                xabarlar.append(f"💀 {nishon.ism} tunda o'ldirildi.")
                if nishon.rol == "Mafiya sardori":
                    qolgan = [m for m in g.mafiyalar() if m.tirik]
                    if qolgan:
                        qolgan[0].rol = "Mafiya sardori"
                        xabarlar.append(f"😈 Yangi sardor: {qolgan[0].ism}")
                if nishon.rol == "Komissiyar":
                    yord = next((o for o in g.tirik_oyinchilar()
                                 if o.rol == "Komissiyar yordamchisi"), None)
                    if yord:
                        yord.rol = "Komissiyar"
                        xabarlar.append(f"🔍 Yangi komissiyar: {yord.ism}")
                if nishon.bomber_kuzatuvdagilar:
                    xabarlar.append("💥 PORTLASH!")
                    for k in nishon.bomber_kuzatuvdagilar:
                        if k.tirik:
                            k.tirik = False
                            xabarlar.append(f"  💥 {k.ism} portlashdan halok!")

    # Qotil harakati
    if "qotil" in g.tun_harakatlari:
        nishon = g.oyinchi(g.tun_harakatlari["qotil"])
        if nishon and nishon.tirik and not nishon.himoyalangan and not nishon.muzlatilgan:
            nishon.tirik = False
            xabarlar.append(f"🗡️ {nishon.ism} qotil tomonidan o'ldirildi.")

    # Gadoyi natijasi
    if "gadoyi" in g.tun_harakatlari:
        gad = next((o for o in g.oyinchilar if o.rol == "Gadoyi"), None)
        nishon = g.oyinchi(g.tun_harakatlari["gadoyi"])
        if gad and gad.tirik and nishon and not nishon.tirik:
            maf_nishon = g.tun_harakatlari.get("mafiya")
            if maf_nishon == nishon.user_id:
                maf_ismlar = ", ".join([m.ism for m in g.mafiyalar()])
                shaxsiy(gad.user_id,
                    f"🎒 {nishon.ism} o'ldirildi!\nMafiya: {maf_ismlar}")

    text = "☀️ *Tong xabarlari:*\n\n"
    text += "\n".join(xabarlar) if xabarlar else "Tunda hech narsa bo'lmadi."
    text += "\n\n" + tirik_royxat(g)

    goldi = g.golish_sharti()
    if goldi:
        yakunlash(g, goldi)
        return

    text += "\n\nMuhokama qiling! Ovoz: /ovoz"
    g.faza = "kun"
    g.tun_harakatlari = {}
    guruhga(chat_id, text)

@bot.message_handler(commands=["ovoz"])
def cmd_ovoz(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        return
    g = games[chat_id]
    if msg.from_user.id != g.admin_id:
        bot.reply_to(msg, "Faqat admin!")
        return
    g.ovozlar = {}
    tiriklar = g.tirik_oyinchilar()
    guruhga(chat_id,
        "🗳️ *OVOZ BERISH!*\n\nKimni osib o'ldirish kerak?\n(Har kishi 1 marta)",
        tugmalar(tiriklar, "ovoz", chat_id))

@bot.message_handler(commands=["holat"])
def cmd_holat(msg):
    chat_id = msg.chat.id
    if chat_id not in games:
        bot.reply_to(msg, "O'yin yo'q. /oyun bilan boshlang.")
        return
    g = games[chat_id]
    text = f"📊 *{g.kun}-kun | Faza: {g.faza}*\n\n" + tirik_royxat(g)
    bot.reply_to(msg, text, parse_mode="Markdown")

@bot.message_handler(commands=["yordam"])
def cmd_yordam(msg):
    bot.reply_to(msg,
        "🎮 *KOMANDALAR:*\n\n"
        "/oyun — Yangi o'yin\n"
        "/qoshil — Qo'shilish\n"
        "/royhatt — Ro'yxat\n"
        "/boshlash — Boshlash (admin)\n"
        "/tun — Tunni boshlash (admin)\n"
        "/tontugat — Tunni yakunlash (admin)\n"
        "/ovoz — Ovoz berish (admin)\n"
        "/holat — O'yin holati",
        parse_mode="Markdown")

# ======================== TUGMALAR ========================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    parts = call.data.split("|")
    if len(parts) < 3:
        return
    amal, chat_id, nishon_id = parts[0], int(parts[1]), int(parts[2])
    user_id = call.from_user.id

    if chat_id not in games:
        return
    g = games[chat_id]
    nishon = g.oyinchi(nishon_id)
    if not nishon:
        return

    if amal == "shifokor":
        nishon.himoyalangan = True
        g.tun_harakatlari["shifokor"] = nishon_id
        bot.edit_message_text(f"💊 {nishon.ism} himoyalandi! ✅",
                              call.message.chat.id, call.message.message_id)

    elif amal == "mafiya":
        g.tun_harakatlari["mafiya"] = nishon_id
        bot.edit_message_text(f"😈 Nishon: {nishon.ism} ✅",
                              call.message.chat.id, call.message.message_id)

    elif amal == "komissiyar":
        g.tun_harakatlari["komissiyar"] = nishon_id
        taraf = ROLLAR.get(nishon.rol, {}).get("taraf", "tinch")
        natija = "🔴 MAFIYA!" if taraf == "mafiya" else "🟢 Tinch aholi"
        shaxsiy(user_id, f"🔍 *{nishon.ism}* — {natija}")
        bot.edit_message_text(f"🔍 Tekshirildi ✅",
                              call.message.chat.id, call.message.message_id)

    elif amal == "jurnalist":
        g.tun_harakatlari["jurnalist"] = nishon_id
        rang = ROLLAR.get(nishon.rol, {}).get("rang", "👤")
        shaxsiy(user_id, f"📰 *{nishon.ism}* — {rang} {nishon.rol}")
        bot.edit_message_text(f"📰 Bilib oldingiz ✅",
                              call.message.chat.id, call.message.message_id)

    elif amal == "qotil":
        g.tun_harakatlari["qotil"] = nishon_id
        bot.edit_message_text(f"🗡️ Nishon: {nishon.ism} ✅",
                              call.message.chat.id, call.message.message_id)

    elif amal == "gadoyi":
        g.tun_harakatlari["gadoyi"] = nishon_id
        bot.edit_message_text(f"🎒 {nishon.ism} uyiga bordingiz ✅",
                              call.message.chat.id, call.message.message_id)

    elif amal == "qorbola":
        if "qorbola" not in g.tun_harakatlari:
            g.tun_harakatlari["qorbola"] = []
        lst = g.tun_harakatlari["qorbola"]
        if len(lst) < 5 and nishon_id not in lst:
            lst.append(nishon_id)
            nishon.muzlatilgan = True
            bot.answer_callback_query(call.id, f"❄️ {nishon.ism} muzlatildi! ({len(lst)}/5)")
            if len(lst) < 5:
                tiriklar = g.tirik_oyinchilar()
                qb = g.oyinchi(user_id)
                candidates = [o for o in tiriklar if o != qb and o.user_id not in lst]
                if candidates:
                    try:
                        bot.edit_message_reply_markup(
                            call.message.chat.id, call.message.message_id,
                            reply_markup=tugmalar(candidates, "qorbola", chat_id))
                    except:
                        pass
            else:
                bot.edit_message_text(f"❄️ 5 kishi muzlatildi ✅",
                                      call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "Allaqachon tanlangan!")
        return

    elif amal == "bomber":
        if "bomber" not in g.tun_harakatlari:
            g.tun_harakatlari["bomber"] = []
        lst = g.tun_harakatlari["bomber"]
        bomb = next((o for o in g.tirik_oyinchilar() if o.rol == "Bomber"), None)
        if bomb and len(lst) < 3 and nishon_id not in lst:
            lst.append(nishon_id)
            if bomb.bomber_kuzatuvdagilar is None:
                bomb.bomber_kuzatuvdagilar = []
            bomb.bomber_kuzatuvdagilar.append(nishon)
            bot.answer_callback_query(call.id, f"💣 {nishon.ism} kuzatuvda! ({len(lst)}/3)")
            if len(lst) < 3:
                tiriklar = g.tirik_oyinchilar()
                candidates = [o for o in tiriklar if o != bomb and o.user_id not in lst]
                if candidates:
                    try:
                        bot.edit_message_reply_markup(
                            call.message.chat.id, call.message.message_id,
                            reply_markup=tugmalar(candidates, "bomber", chat_id))
                    except:
                        pass
            else:
                bot.edit_message_text("💣 3 kishi kuzatuvda ✅",
                                      call.message.chat.id, call.message.message_id)
        return

    elif amal == "ovoz":
        if user_id in g.ovozlar:
            bot.answer_callback_query(call.id, "Allaqachon ovoz berdingiz!")
            return
        beruvchi = g.oyinchi(user_id)
        if not beruvchi or not beruvchi.tirik:
            bot.answer_callback_query(call.id, "Siz o'yinda emassiz!")
            return
        ovoz_soni = 2 if beruvchi.rol == "Shohi" else 1
        g.ovozlar[user_id] = {"nishon": nishon_id, "soni": ovoz_soni}
        bot.answer_callback_query(call.id, f"✅ {nishon.ism} ga ovoz berdingiz!")
        guruhga(g.chat_id,
            f"✅ {beruvchi.ism} ovoz berdi. ({len(g.ovozlar)}/{len(g.tirik_oyinchilar())})")
        if len(g.ovozlar) >= len(g.tirik_oyinchilar()):
            ovoz_yakunla(g)
        return

    bot.answer_callback_query(call.id, "✅")

def ovoz_yakunla(g):
    natija = {}
    for v in g.ovozlar.values():
        nid = v["nishon"]
        natija[nid] = natija.get(nid, 0) + v["soni"]

    text = "📊 *Ovoz natijalari:*\n"
    for nid, son in sorted(natija.items(), key=lambda x: x[1], reverse=True):
        o = g.oyinchi(nid)
        if o:
            text += f"  {o.ism}: {son} ovoz\n"

    if not natija:
        guruhga(g.chat_id, "Hech kim ovoz bermadi.")
        return

    eng_kop = max(natija.values())
    liderar = [nid for nid, son in natija.items() if son == eng_kop]

    if len(liderar) == 1:
        nishon = g.oyinchi(liderar[0])
        xabar = osib_oldirish(g, nishon)
        text += f"\n{xabar}"
    else:
        ismlar = ", ".join([g.oyinchi(n).ism for n in liderar if g.oyinchi(n)])
        text += f"\n⚖️ Barobar: {ismlar} — Hech kim o'lmadi!"

    guruhga(g.chat_id, text)

    goldi = g.golish_sharti()
    if goldi:
        yakunlash(g, goldi)
        return

    g.kun += 1
    g.faza = "tun_kutish"
    guruhga(g.chat_id, f"🌙 Admin /tun yozsin ({g.kun}-kun tuni)!")

def osib_oldirish(g, nishon):
    if nishon.rol == "Qaysar" and not nishon.qaysar_chiqdi:
        nishon.qaysar_chiqdi = True
        return f"💪 {nishon.ism} (Qaysar) — bu safar chiqmadi!"
    if nishon.rol == "Olmas" and not nishon.olmas_ishlatilgan:
        nishon.olmas_ishlatilgan = True
        return f"💎 {nishon.ism} (Olmas) — omon qoldi!"
    nishon.tirik = False
    rang = ROLLAR.get(nishon.rol, {}).get("rang", "👤")
    xabar = f"⚰️ {nishon.ism} o'ldi! Roli: {rang} {nishon.rol}"
    if nishon.bomber_kuzatuvdagilar:
        xabar += "\n💥 PORTLASH!"
        for k in nishon.bomber_kuzatuvdagilar:
            if k.tirik:
                k.tirik = False
                xabar += f"\n  💥 {k.ism} portlashdan halok!"
    return xabar

def yakunlash(g, goluvchi):
    if goluvchi == "tinch":
        text = "🎉 *TINCH AHOLI G'ALABA QOZONDI!*"
    elif goluvchi == "mafiya":
        text = "😈 *MAFIYA G'ALABA QOZONDI!*"
    else:
        text = "🗡️ *QOTIL G'ALABA QOZONDI!*"
    text += "\n\n📋 *Barcha rollar:*\n"
    for o in g.oyinchilar:
        holat = "✅" if o.tirik else "💀"
        rang = ROLLAR.get(o.rol, {}).get("rang", "👤")
        text += f"  {holat} {o.ism} — {rang} {o.rol}\n"
    text += "\nYangi o'yin: /oyun"
    guruhga(g.chat_id, text)
    if g.chat_id in games:
        del games[g.chat_id]

print("🤖 Mafiya bot ishga tushdi!")
bot.infinity_polling()
