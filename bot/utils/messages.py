"""
Barcha xabar matnlari — O'zbek va Rus tillarida
"""

MESSAGES = {
    "uz": {
        "start": (
            "🎬 <b>AI Video Bot</b> ga xush kelibsiz!\n\n"
            "Siz matn yozing — biz <b>8 soniyalik professional video</b> yasaymiz.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>SIZGA SOVG'A: 1 ta BEPUL video!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Qanday ishlaydi?\n"
            "1️⃣ /video yozing yoki tugmani bosing\n"
            "2️⃣ Videongiz haqida yozing (o'zbek yoki ingliz)\n"
            "3️⃣ 30-60 soniyada tayyor video qo'lingizda!\n\n"
            "📊 Narxlar: 3 video = 15,000 so'm dan\n\n"
            "👇 Boshlaylik!"
        ),
        "start_existing": (
            "🎬 <b>AI Video Bot</b>\n\n"
            "Xush kelibsiz! Quyidagi tugmalardan birini tanlang 👇"
        ),
        "select_model": (
            "🎬 <b>Qanday video kerak?</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>Tez va arzon</b>\n"
            "   Sifat: ⭐⭐⭐⭐\n"
            "   Narx: {fast_price:,} so'm/video\n"
            "   Vaqt: ~30 soniya\n\n"
            "🏆 <b>Premium sifat</b>\n"
            "   Sifat: ⭐⭐⭐⭐⭐\n"
            "   Narx: {premium_price:,} so'm/video\n"
            "   Vaqt: ~60 soniya\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "enter_prompt": (
            "✍️ <b>Videongizni tasvirlab bering:</b>\n\n"
            "Misol promtlar:\n"
            '- "Tog\'lar orasida quyosh botayotgan manzara, epik musiqa"\n'
            '- "Futuristik shahar, neon chiroqlar, yomg\'ir, kecha"\n'
            '- "Dengiz bo\'yi, to\'lqinlar, palma daraxti, sokin"\n\n'
            "💡 <b>Maslahat:</b> Qancha batafsil yozsangiz, shuncha yaxshi!\n\n"
            "⌨️ Yozing:"
        ),
        "confirm_video": (
            "🎬 <b>Video yaratish</b>\n\n"
            "📝 Prompt: {prompt}\n"
            "⚡ Model: {model_name}\n"
            "💰 Narx: {cost:,} so'm\n"
            "💳 Balansingiz: {balance:,} so'm → {new_balance:,} so'm\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Davom etasizmi?"
        ),
        "generation_started": (
            "⏳ <b>Video yaratilmoqda...</b>\n\n"
            "🎬 Taxminiy vaqt: {time} soniya\n"
            "Iltimos kuting..."
        ),
        "generation_progress": "⏳ Video yaratilmoqda...\n\n🎬 [{bar}] {percent}%\n\nTaxminiy vaqt: ~{remaining} soniya\nIltimos kuting...",
        "generation_done": (
            "✅ <b>Videongiz tayyor!</b>\n\n"
            "📝 Prompt: \"{prompt}\"\n"
            "⏱ Yaratish vaqti: {duration} soniya\n"
            "💰 Yechildi: {cost:,} so'm\n"
            "💳 Qoldiq balans: {balance:,} so'm\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👇 Video quyida:"
        ),
        "generation_failed": (
            "❌ <b>Xato yuz berdi!</b>\n"
            "💰 {cost:,} so'm qaytarildi\n\n"
            "Qaytadan urinib ko'ring 🔄"
        ),
        "balance_info": (
            "💳 <b>HISOBINGIZ</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💰 Joriy balans:  {balance:,} so'm\n"
            "🎬 Jami videolar: {total_videos} ta\n"
            "💸 Jami sarflagan: {total_spent:,} so'm\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📅 Ro'yxatdan: {created}\n"
            "🏆 Status: {status}"
        ),
        "balance_low": (
            "❌ <b>Balans yetarli emas!</b>\n"
            "💰 Kerak: {needed:,} so'm\n"
            "💳 Sizda: {balance:,} so'm\n\n"
            "Balansni to'ldiring 👇"
        ),
        "topup_menu": (
            "💰 <b>Balans to'ldirish</b>\n\n"
            "💳 Joriy balans: {balance:,} so'm\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 <b>PAKETLAR:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "select_payment": (
            "💳 <b>To'lov usulini tanlang:</b>\n\n"
            "📦 {package_name} — {price:,} so'm ({videos} video)"
        ),
        "payment_link": (
            "🔗 <b>To'lov havolasi:</b>\n"
            "{link}\n\n"
            "⏰ Havola 30 daqiqa davomida faol\n\n"
            "To'lov amalga oshgandan so'ng balans\n"
            "avtomatik ravishda to'ldiriladi ✅"
        ),
        "payment_confirmed": (
            "✅ <b>To'lov qabul qilindi!</b>\n"
            "💰 +{amount:,} so'm\n"
            "💳 Yangi balans: {balance:,} so'm\n\n"
            "🎬 /video — video yaratishni boshlang!"
        ),
        "referral_info": (
            "🔗 <b>DO'ST TAKLIF QILING!</b>\n\n"
            "Har bir do'st taklif qilsangiz:\n"
            "  ✅ Siz: +1 bepul video ({bonus:,} so'm qiymat)\n"
            "  ✅ Do'stingiz: +1 bepul video\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 <b>Sizning havolangiz:</b>\n"
            "<code>t.me/{bot_username}?start=REF_{ref_code}</code>\n\n"
            "📊 <b>Statistika:</b>\n"
            "👥 Taklif qilganlar: {total_referred} kishi\n"
            "🎬 Bonus videolar: {bonuses} ta\n"
            "💰 Tejagan: {saved:,} so'm\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "referral_bonus": (
            "🎁 <b>Bonus!</b>\n"
            "{name} sizning havolangiz orqali qo'shildi!\n"
            "💰 +{bonus:,} so'm (1 bepul video)"
        ),
        "history_header": "📋 <b>SIZNING VIDEOLARINGIZ</b>\n\n━━━━━━━━━━━━━━━━━━━━",
        "history_item": (
            "\n{num}️⃣ {date}\n"
            '   📝 "{prompt}"\n'
            "   {model} | {status} | {cost:,} so'm"
        ),
        "history_empty": "📋 Sizda hali videolar yo'q.\n\n🎬 /video — birinchi videongizni yarating!",
        "help": (
            "❓ <b>YORDAM</b>\n\n"
            "🎬 <b>Video yaratish:</b>\n"
            "/video — AI video generatsiya qilish\n\n"
            "💰 <b>To'lov:</b>\n"
            "/topup — Balans to'ldirish\n"
            "/balance — Balansni ko'rish\n\n"
            "📋 <b>Boshqa:</b>\n"
            "/history — Video tarixingiz\n"
            "/referral — Do'st taklif qilish\n"
            "/settings — Sozlamalar\n"
            "/help — Shu yordam\n\n"
            "📞 <b>Muammo bo'lsa:</b> @admin_username"
        ),
        "settings": (
            "⚙️ <b>SOZLAMALAR</b>\n\n"
            "🌐 Til: {lang}\n"
        ),
        "nsfw_blocked": "🚫 Bu turdagi kontent taqiqlangan. Iltimos, boshqa prompt kiriting.",
        "rate_limited": "⏳ Iltimos, biroz kuting. Juda ko'p so'rov yubordingiz.",
        "user_blocked": "🚫 Sizning hisobingiz bloklangan. Admin bilan bog'laning.",
        "error_generic": "❌ Xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.",
        "admin_only": "🚫 Bu buyruq faqat adminlar uchun.",
        "admin_panel": (
            "👑 <b>ADMIN PANEL</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>Bugungi statistika:</b>\n"
            "👥 Jami userlar: {total_users}\n"
            "🆕 Bugun yangilar: {new_today}\n"
            "🎬 Bugun videolar: {videos_today}\n"
            "💰 Bugun daromad: {revenue_today:,} so'm\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "broadcast_ask": "📢 <b>Broadcast xabar yozing:</b>\n\nBarcha foydalanuvchilarga yuboriladi.",
        "broadcast_confirm": "📢 Bu xabarni {count} foydalanuvchiga yuborasizmi?\n\n{text}",
        "broadcast_done": "✅ Xabar {sent}/{total} foydalanuvchiga yuborildi.",
    },
    "ru": {
        "start": (
            "🎬 Добро пожаловать в <b>AI Video Bot</b>!\n\n"
            "Вы пишете текст — мы создаём <b>8-секундное профессиональное видео</b>.\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 <b>ПОДАРОК: 1 БЕСПЛАТНОЕ видео!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Как это работает?\n"
            "1️⃣ Напишите /video или нажмите кнопку\n"
            "2️⃣ Опишите своё видео\n"
            "3️⃣ Через 30-60 секунд видео готово!\n\n"
            "📊 Цены: 3 видео от 15,000 сум\n\n"
            "👇 Начнём!"
        ),
        "start_existing": (
            "🎬 <b>AI Video Bot</b>\n\n"
            "Добро пожаловать! Выберите действие 👇"
        ),
        "select_model": (
            "🎬 <b>Какое видео нужно?</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>Быстрое и доступное</b>\n"
            "   Качество: ⭐⭐⭐⭐\n"
            "   Цена: {fast_price:,} сум/видео\n"
            "   Время: ~30 секунд\n\n"
            "🏆 <b>Премиум качество</b>\n"
            "   Качество: ⭐⭐⭐⭐⭐\n"
            "   Цена: {premium_price:,} сум/видео\n"
            "   Время: ~60 секунд\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "enter_prompt": (
            "✍️ <b>Опишите ваше видео:</b>\n\n"
            "Примеры:\n"
            '- "Закат в горах, эпическая музыка"\n'
            '- "Футуристический город, неоновые огни, дождь, ночь"\n\n'
            "💡 <b>Совет:</b> Чем подробнее — тем лучше!\n\n"
            "⌨️ Пишите:"
        ),
        "confirm_video": (
            "🎬 <b>Создать видео</b>\n\n"
            "📝 Промпт: {prompt}\n"
            "⚡ Модель: {model_name}\n"
            "💰 Цена: {cost:,} сум\n"
            "💳 Баланс: {balance:,} сум → {new_balance:,} сум\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Продолжить?"
        ),
        "generation_started": (
            "⏳ <b>Видео создаётся...</b>\n\n"
            "🎬 Примерное время: {time} секунд\n"
            "Пожалуйста, подождите..."
        ),
        "generation_progress": "⏳ Видео создаётся...\n\n🎬 [{bar}] {percent}%\n\nПримерное время: ~{remaining} сек\nПожалуйста, подождите...",
        "generation_done": (
            "✅ <b>Ваше видео готово!</b>\n\n"
            "📝 Промпт: \"{prompt}\"\n"
            "⏱ Время создания: {duration} сек\n"
            "💰 Списано: {cost:,} сум\n"
            "💳 Остаток: {balance:,} сум\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👇 Видео ниже:"
        ),
        "generation_failed": (
            "❌ <b>Произошла ошибка!</b>\n"
            "💰 {cost:,} сум возвращено\n\n"
            "Попробуйте снова 🔄"
        ),
        "balance_info": (
            "💳 <b>ВАШ СЧЁТ</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💰 Баланс: {balance:,} сум\n"
            "🎬 Всего видео: {total_videos}\n"
            "💸 Всего потрачено: {total_spent:,} сум\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "balance_low": (
            "❌ <b>Недостаточно средств!</b>\n"
            "💰 Нужно: {needed:,} сум\n"
            "💳 У вас: {balance:,} сум\n\n"
            "Пополните баланс 👇"
        ),
        "topup_menu": (
            "💰 <b>Пополнение баланса</b>\n\n"
            "💳 Текущий баланс: {balance:,} сум\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📦 <b>ПАКЕТЫ:</b>\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "select_payment": (
            "💳 <b>Выберите способ оплаты:</b>\n\n"
            "📦 {package_name} — {price:,} сум ({videos} видео)"
        ),
        "payment_link": (
            "🔗 <b>Ссылка на оплату:</b>\n"
            "{link}\n\n"
            "⏰ Ссылка действительна 30 минут\n\n"
            "После оплаты баланс\n"
            "пополнится автоматически ✅"
        ),
        "payment_confirmed": (
            "✅ <b>Оплата принята!</b>\n"
            "💰 +{amount:,} сум\n"
            "💳 Новый баланс: {balance:,} сум\n\n"
            "🎬 /video — начните создавать видео!"
        ),
        "referral_info": (
            "🔗 <b>ПРИГЛАСИТЕ ДРУГА!</b>\n\n"
            "За каждого друга:\n"
            "  ✅ Вам: +1 бесплатное видео ({bonus:,} сум)\n"
            "  ✅ Другу: +1 бесплатное видео\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 <b>Ваша ссылка:</b>\n"
            "<code>t.me/{bot_username}?start=REF_{ref_code}</code>\n\n"
            "📊 <b>Статистика:</b>\n"
            "👥 Приглашённых: {total_referred}\n"
            "🎬 Бонусных видео: {bonuses}\n"
            "💰 Сэкономлено: {saved:,} сум\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "referral_bonus": (
            "🎁 <b>Бонус!</b>\n"
            "{name} присоединился по вашей ссылке!\n"
            "💰 +{bonus:,} сум (1 бесплатное видео)"
        ),
        "history_header": "📋 <b>ВАШИ ВИДЕО</b>\n\n━━━━━━━━━━━━━━━━━━━━",
        "history_item": (
            "\n{num}️⃣ {date}\n"
            '   📝 "{prompt}"\n'
            "   {model} | {status} | {cost:,} сум"
        ),
        "history_empty": "📋 У вас пока нет видео.\n\n🎬 /video — создайте первое!",
        "help": (
            "❓ <b>ПОМОЩЬ</b>\n\n"
            "🎬 <b>Создание видео:</b>\n"
            "/video — Создать AI видео\n\n"
            "💰 <b>Оплата:</b>\n"
            "/topup — Пополнить баланс\n"
            "/balance — Проверить баланс\n\n"
            "📋 <b>Другое:</b>\n"
            "/history — История видео\n"
            "/referral — Пригласить друга\n"
            "/settings — Настройки\n"
            "/help — Эта справка\n\n"
            "📞 <b>Проблемы?</b> @admin_username"
        ),
        "settings": "⚙️ <b>НАСТРОЙКИ</b>\n\n🌐 Язык: {lang}\n",
        "nsfw_blocked": "🚫 Такой контент запрещён. Введите другой промпт.",
        "rate_limited": "⏳ Подождите немного. Слишком много запросов.",
        "user_blocked": "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору.",
        "error_generic": "❌ Произошла ошибка. Попробуйте снова.",
        "admin_only": "🚫 Эта команда только для админов.",
        "admin_panel": (
            "👑 <b>АДМИН ПАНЕЛЬ</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "📊 <b>Сегодня:</b>\n"
            "👥 Всего: {total_users}\n"
            "🆕 Новых: {new_today}\n"
            "🎬 Видео: {videos_today}\n"
            "💰 Доход: {revenue_today:,} сум\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        "broadcast_ask": "📢 <b>Напишите сообщение:</b>\n\nОтправится всем пользователям.",
        "broadcast_confirm": "📢 Отправить {count} пользователям?\n\n{text}",
        "broadcast_done": "✅ Отправлено {sent}/{total} пользователям.",
    },
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
