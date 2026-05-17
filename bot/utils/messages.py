"""
Barcha xabar matnlari — O'zbek tili (tanga iqtisodiyoti asosida)
"""

MESSAGES = {
    "uz": {
        "start": (
            "🎬 <b>AI Videochi</b> ga xush kelibsiz!\n\n"
            "Matn yozing — biz professional video yasaymiz!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>SIZGA SOVG'A!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🪙 <b>50 tanga</b> berildi!\n"
            "▶️ Bitta tekin video yasang!\n\n"
            "Qanday ishlaydi?\n"
            "1️⃣ <b>\"🎬 Video yaratish\"</b> tugmasini bosing\n"
            "2️⃣ Videongizni tasvirlab yozing\n"
            "3️⃣ 30-60 soniyada tayyor! 🚀\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "main_menu": (
            "🎬 <b>AI Videochi</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🪙 Tangalar: <b>{tangas} ta</b>\n"
            "🎬 Jami videolar: <b>{total_videos} ta</b>\n"
            "🔥 Streak: <b>{streak} kun</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "enter_prompt": (
            "🎬 <b>Video yaratish</b>\n\n"
            "✍️ Videongizni tasvirlab bering:\n\n"
            "<b>Misollar:</b>\n"
            "• <i>\"Tog'lar orasida quyosh botayotgan manzara\"</i>\n"
            "• <i>\"Futuristik shahar, neon chiroqlar, yomg'ir\"</i>\n"
            "• <i>\"Dengiz bo'yi, to'lqinlar, palma daraxti\"</i>\n\n"
            "💡 Batafsil yozsangiz — yaxshiroq natija!\n\n"
            "🪙 Narx: <b>30 tanga</b> | Sizda: <b>{balance} tanga</b>"
        ),
        "confirm_video": (
            "🎬 <b>Video yaratilsinmi?</b>\n\n"
            "📝 <i>\"{prompt}\"</i>\n"
            "🪙 <b>30 tanga</b> yechildi: <b>{balance} → {new_balance} tanga</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "generation_started": (
            "⏳ <b>Video yaratilmoqda...</b>\n\n"
            "⏱ Taxminan {time} soniya qoldi"
        ),
        "generation_progress": (
            "⏳ <b>Video yaratilmoqda...</b>\n\n"
            "[{bar}] {percent}%\n\n"
            "⏱ Taxminan <b>{remaining} soniya</b> qoldi"
        ),
        "generation_done": (
            "✅ <b>Video tayyor!</b>\n\n"
            "📝 <i>\"{prompt}\"</i>\n"
            "⏱ Yaratish vaqti: <b>{duration} soniya</b>\n"
            "🪙 Qoldiq: <b>{balance} tanga</b>\n\n"
            "👇"
        ),
        "balance_low": (
            "🪙 <b>Tanga yetarli emas!</b>\n\n"
            "Kerak: <b>30 tanga</b>\n"
            "Sizda: <b>{balance} tanga</b>\n"
            "Yetishmaydi: <b>{needed} tanga</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "topup_menu": (
            "🪙 <b>Tanga olish</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🪙 Joriy tangalar: <b>{balance} ta</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📦 <b>PAKETLAR:</b>"
        ),
        "topup_details": (
            "📦 <b>{package_name} — {tangas} tanga</b>\n\n"
            "To'lov usulini tanlang:"
        ),
        "stars_payment": (
            "⭐ <b>Telegram Stars orqali to'lov</b>\n\n"
            "{tangas} tanga uchun: <b>{stars} ⭐</b>\n\n"
            "👇 To'lash uchun bosing:"
        ),
        "manual_payment": (
            "💳 <b>Karta orqali to'lov</b>\n\n"
            "{tangas} tanga uchun: <b>{som:,} so'm</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Quyidagi karta raqamiga o'tkazing:\n"
            "<code>{card_number}</code> (Humo)\n"
            "Ega: <b>{card_owner}</b>\n\n"
            "📸 O'tkazmadan keyin chekni (rasmini) yuboring\n"
            "⏰ 5-30 daqiqa ichida tangalar beriladi\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "referral_info": (
            "👥 <b>DO'ST TAKLIF QILING!</b>\n\n"
            "Har bir do'st uchun:\n"
            "✅ Siz: <b>+20 🪙 tanga</b>\n"
            "✅ Do'stingiz: <b>+20 🪙 tanga (qo'shimcha)</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 Sizning havolangiz:\n"
            "<code>t.me/{bot_username}?start=REF_{ref_code}</code>\n\n"
            "📊 <b>Statistika:</b>\n"
            "👥 Taklif qilganlar: <b>{total_referred} kishi</b>\n"
            "🪙 Bonus tangalar: <b>{bonuses} ta</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "balance_info": (
            "🪙 <b>TANGALARINGIZ</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🪙 Joriy tangalar: <b>{balance} ta</b>\n"
            "🎬 Jami videolar: <b>{total_videos} ta</b>\n"
            "🔥 Streak: <b>{streak} kun</b>\n"
            "📅 Ro'yxatdan: <b>{created}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "premium_info": (
            "🏆 <b>PREMIUM OBUNA</b>\n\n"
            "Premium bilan nimalar bo'ladi?\n"
            "✅ Har kuni +5 tanga sovg'a\n"
            "✅ Videolar 2x tezroq\n"
            "✅ Watermark yo'q\n"
            "✅ Priority navbat\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 Oylik: <b>500 🪙 tanga</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "nsfw_blocked": "🚫 Bu turdagi kontent taqiqlangan. Iltimos, boshqa prompt kiriting.",
        "user_blocked": "🚫 Sizning hisobingiz bloklangan. Admin bilan bog'laning.",
        "admin_only": "🚫 Bu buyruq faqat adminlar uchun.",
    },
    "ru": {
        "start": (
            "🎬 Добро пожаловать в <b>AI Videochi</b>!\n\n"
            "Вы пишете текст — мы создаём профессиональное видео!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>ПОДАРОК!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🪙 Вам начислено <b>50 монет</b>!\n"
            "▶️ Создайте одно бесплатное видео!\n\n"
            "Как это работает?\n"
            "1️⃣ Нажмите <b>\"🎬 Создать видео\"</b>\n"
            "2️⃣ Опишите ваше видео\n"
            "3️⃣ Готово за 30-60 секунд! 🚀\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "main_menu": (
            "🎬 <b>AI Videochi</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🪙 Монеты: <b>{tangas} шт</b>\n"
            "🎬 Всего видео: <b>{total_videos} шт</b>\n"
            "🔥 Серия: <b>{streak} дней</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "enter_prompt": (
            "🎬 <b>Создание видео</b>\n\n"
            "✍️ Опишите ваше видео:\n\n"
            "🪙 Цена: <b>30 монет</b> | У вас: <b>{balance} монет</b>"
        ),
        "confirm_video": (
            "🎬 <b>Создать видео?</b>\n\n"
            "📝 <i>\"{prompt}\"</i>\n"
            "🪙 Будет списано <b>30 монет</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "generation_started": (
            "⏳ <b>Видео создаётся...</b>\n\n"
            "⏱ Осталось примерно {time} секунд"
        ),
        "generation_progress": (
            "⏳ <b>Видео создаётся...</b>\n\n"
            "⏱ Осталось примерно <b>{remaining} секунд</b>"
        ),
        "generation_done": (
            "✅ <b>Видео готово!</b>\n\n"
            "🪙 Остаток: <b>{balance} монет</b>\n\n"
            "👇"
        ),
        "balance_low": (
            "🪙 <b>Недостаточно монет!</b>\n\n"
            "Нужно: <b>30 монет</b>\n"
            "У вас: <b>{balance} монет</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "topup_menu": (
            "🪙 <b>Покупка монет</b>\n\n"
            "🪙 Текущий баланс: <b>{balance} шт</b>\n\n"
            "📦 <b>ПАКЕТЫ:</b>"
        ),
        "topup_details": (
            "📦 <b>{package_name} — {tangas} монет</b>\n\n"
            "Выберите способ оплаты:"
        ),
        "stars_payment": (
            "⭐ <b>Оплата через Telegram Stars</b>\n\n"
            "За {tangas} монет: <b>{stars} ⭐</b>"
        ),
        "manual_payment": (
            "💳 <b>Оплата на карту</b>\n\n"
            "За {tangas} монет: <b>{som:,} сум</b>\n\n"
            "Переведите на карту:\n"
            "<code>{card_number}</code>\n"
            "Владелец: <b>{card_owner}</b>\n\n"
            "📸 Отправьте фото чека после перевода."
        ),
        "referral_info": (
            "👥 <b>ПРИГЛАСИТЬ ДРУГА!</b>\n\n"
            "За каждого друга:\n"
            "✅ Вы: <b>+20 🪙 монет</b>\n"
            "✅ Друг: <b>+20 🪙 монет</b>"
        ),
        "balance_info": (
            "🪙 <b>ВАШИ МОНЕТЫ</b>\n\n"
            "🪙 Монеты: <b>{balance} шт</b>\n"
            "🔥 Серия: <b>{streak} дней</b>"
        ),
        "premium_info": (
            "🏆 <b>PREMIUM ПОДПИСКА</b>\n\n"
            "Преимущества:\n"
            "✅ +5 монет ежедневно\n"
            "✅ Создание в 2 раза быстрее\n"
            "✅ Без водяного знака\n\n"
            "📦 Месяц: <b>500 🪙 монет</b>"
        ),
        "nsfw_blocked": "🚫 Такой контент запрещён. Введите другой промпт.",
        "user_blocked": "🚫 Ваш аккаунт заблокирован.",
        "admin_only": "🚫 Команда только для админов.",
    }
}


# NSFW filter words
NSFW_WORDS = [
    "porn", "nude", "naked", "sex", "xxx", "nsfw", "erotic",
    "hentai", "18+", "adult", "pornography",
]


def get_msg(lang: str, key: str) -> str:
    """Get message by language and key"""
    msgs = MESSAGES.get(lang, MESSAGES["uz"])
    return msgs.get(key, MESSAGES["uz"].get(key, ""))
