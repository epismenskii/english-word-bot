import os
import json
import random
import logging
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

# ─── Импорт слов из отдельных файлов ─────────────────────────────────────────
from words_a1 import WORDS_A1
from words_a2 import WORDS_A2
from words_b1 import WORDS_B1
from words_b2 import WORDS_B2
from words_c1 import WORDS_C1
from words_c2 import WORDS_C2

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

WORDS = {
    "A1": WORDS_A1,
    "A2": WORDS_A2,
    "B1": WORDS_B1,
    "B2": WORDS_B2,
    "C1": WORDS_C1,
    "C2": WORDS_C2,
}

LEVEL_INFO = {
    "A1": ("🟢", "Начинающий",    "Базовые слова — числа, цвета, животные"),
    "A2": ("🟢", "Элементарный",  "Повседневные темы — еда, путешествия, семья"),
    "B1": ("🟡", "Средний",       "Общение на большинство тем"),
    "B2": ("🟡", "Выше среднего", "Сложные темы, абстрактные понятия"),
    "C1": ("🔴", "Продвинутый",   "Академический язык, нюансы"),
    "C2": ("🔴", "Мастерство",    "Редкие слова, идиомы, тонкости"),
}

# ─── Database ─────────────────────────────────────────────────────────────────
DB_FILE = "users.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_user(user_id: str):
    db = load_db()
    if user_id not in db:
        db[user_id] = {
            "level": None,
            "known_words": [],
            "new_words": [],
            "seen_words": [],
            "active": True,
            "repeat_mode": None,  # None | "all" | "new"
        }
        save_db(db)
    return db[user_id]

def update_user(user_id: str, data: dict):
    db = load_db()
    if user_id not in db:
        db[user_id] = {}
    db[user_id].update(data)
    save_db(db)

# ─── Word helpers ─────────────────────────────────────────────────────────────
def get_word_translation(word_key: str, level: str) -> str:
    """Возвращает перевод слова по ключу."""
    for w in WORDS.get(level, []):
        if w["word"] == word_key:
            return w["translation"]
    return ""

def get_random_word(level: str, seen: list, pool: list = None) -> dict | None:
    """
    Возвращает случайное слово.
    pool — если задан, выбирает только из этого списка слов (режим повторения).
    """
    source = pool if pool is not None else WORDS.get(level, [])
    available = [w for w in source if w["word"] not in seen]
    if not available:
        return None  # все слова показаны
    return random.choice(available)

# ─── Keyboards ────────────────────────────────────────────────────────────────
def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Получить слово", callback_data="get_word")],
        [InlineKeyboardButton("📚 Моя библиотека", callback_data="show_library")],
        [InlineKeyboardButton("🎯 Сменить уровень", callback_data="change_level")],
        [InlineKeyboardButton("📊 Статистика",      callback_data="show_stats")],
    ])

def level_keyboard():
    rows = []
    levels = list(LEVEL_INFO.items())
    for i in range(0, len(levels), 2):
        row = []
        for lvl, (emoji, label, _) in levels[i:i+2]:
            row.append(InlineKeyboardButton(f"{emoji} {lvl} · {label}", callback_data=f"level_{lvl}"))
        rows.append(row)
    rows.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

def word_keyboard(word: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Знаю это слово",  callback_data=f"known_{word}"),
            InlineKeyboardButton("📚 Новое для меня",  callback_data=f"new_{word}"),
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ])

def finished_keyboard(repeat_new_count: int):
    """Клавиатура по окончании всех слов уровня."""
    rows = [
        [InlineKeyboardButton("🔄 Повторить все слова уровня", callback_data="repeat_all")],
    ]
    if repeat_new_count > 0:
        rows.append([InlineKeyboardButton(
            f"📖 Повторить «Новые для меня» ({repeat_new_count} сл.)",
            callback_data="repeat_new"
        )])
    rows.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

# ─── Formatting ───────────────────────────────────────────────────────────────
def format_word(data: dict, level: str) -> str:
    emoji, label, _ = LEVEL_INFO.get(level, ("📖", level, ""))
    return (
        f"📖 *{data['word'].upper()}*\n"
        f"🔤 `{data['transcription']}`\n"
        f"🇷🇺 *{data['translation']}*  —  _{data['part_of_speech']}_\n\n"
        f"💬 _{data['example']}_\n"
        f"    {data['example_ru']}\n\n"
        f"🏷 {emoji} {label} ({level})"
    )

def format_library(user_data: dict, level: str) -> str:
    known    = user_data.get("known_words", [])
    new_words = user_data.get("new_words", [])

    def word_lines(words):
        lines = []
        for w in words:
            tr = get_word_translation(w, level)
            if tr:
                lines.append(f"• {w} — {tr}")
            else:
                lines.append(f"• {w}")
        return "\n".join(lines)

    text = "📚 *Твоя библиотека*\n\n"

    if known:
        text += f"✅ *Знаю ({len(known)} сл.):*\n"
        display = known[-30:]
        text += word_lines(display)
        if len(known) > 30:
            text += f"\n_...и ещё {len(known) - 30}_"
        text += "\n\n"

    if new_words:
        text += f"📖 *Новые для меня ({len(new_words)} сл.):*\n"
        display = new_words[-30:]
        text += word_lines(display)
        if len(new_words) > 30:
            text += f"\n_...и ещё {len(new_words) - 30}_"

    if not known and not new_words:
        text += "_Библиотека пуста. Получи первое слово!_"

    return text

def format_finished(user_data: dict, level: str) -> str:
    total   = len(WORDS.get(level, []))
    known   = len(user_data.get("known_words", []))
    new_cnt = len(user_data.get("new_words", []))
    emoji, label, _ = LEVEL_INFO.get(level, ("📖", level, ""))
    return (
        f"🎉 *Поздравляем!*\n\n"
        f"Ты просмотрел все слова уровня {emoji} *{level} — {label}*!\n\n"
        f"📊 *Твои результаты:*\n"
        f"✅ Знаю: *{known}* из *{total}*\n"
        f"📖 Новые для меня: *{new_cnt}*\n\n"
        f"Что делаем дальше?"
    )

# ─── Handlers ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, *{user.first_name}*!\n\n"
        f"Я помогу тебе учить английские слова каждый день 🇬🇧\n\n"
        f"Выбери свой уровень:",
        parse_mode="Markdown",
        reply_markup=level_keyboard()
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 *Главное меню*",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user(user_id)
    if not user_data.get("level"):
        await update.message.reply_text("⚠️ Сначала выбери уровень:", reply_markup=level_keyboard())
        return
    await _send_next_word(update.message.reply_text, user_id, user_data)

async def library_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user(user_id)
    level = user_data.get("level", "A1")
    text = format_library(user_data, level)
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await _send_stats(update.message.reply_text, user_id)

async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 Выбери уровень:", reply_markup=level_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Команды бота:*\n\n"
        "/start — начать\n"
        "/menu — главное меню\n"
        "/word — получить слово\n"
        "/library — моя библиотека\n"
        "/stats — статистика\n"
        "/level — изменить уровень\n"
        "/help — справка\n\n"
        "💡 Каждый день в 9:00 я пришлю тебе новое слово!",
        parse_mode="Markdown"
    )

# ─── Core word sending ────────────────────────────────────────────────────────
async def _send_next_word(reply_fn, user_id: str, user_data: dict):
    level       = user_data["level"]
    seen        = user_data.get("seen_words", [])
    repeat_mode = user_data.get("repeat_mode")

    # Определяем пул слов в зависимости от режима
    if repeat_mode == "new":
        new_word_keys = user_data.get("new_words", [])
        pool = [w for w in WORDS.get(level, []) if w["word"] in new_word_keys]
    elif repeat_mode == "all":
        pool = None  # все слова уровня
    else:
        pool = None

    word_data = get_random_word(level, seen, pool)

    if word_data is None:
        # Все слова просмотрены
        update_user(user_id, {"seen_words": [], "repeat_mode": None})
        user_data = get_user(user_id)
        new_cnt = len(user_data.get("new_words", []))
        text = format_finished(user_data, level)
        await reply_fn(text, parse_mode="Markdown", reply_markup=finished_keyboard(new_cnt))
        return

    seen.append(word_data["word"])
    update_user(user_id, {"seen_words": seen[-300:]})
    await reply_fn(
        format_word(word_data, level),
        parse_mode="Markdown",
        reply_markup=word_keyboard(word_data["word"])
    )

async def _send_stats(reply_fn, user_id: str):
    user_data = get_user(user_id)
    level = user_data.get("level", "не выбран")
    emoji = LEVEL_INFO.get(level, ("📚",))[0] if level != "не выбран" else "📚"
    total = len(WORDS.get(level, [])) if level != "не выбран" else 0
    await reply_fn(
        f"📊 *Твоя статистика*\n\n"
        f"🎯 Уровень: {emoji} *{level}*\n"
        f"📖 Слов в базе: *{total}*\n"
        f"👀 Показано: *{len(user_data.get('seen_words', []))}*\n"
        f"✅ Знаю: *{len(user_data.get('known_words', []))}*\n"
        f"📚 Новые для меня: *{len(user_data.get('new_words', []))}*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ])
    )

# ─── Callbacks ────────────────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data    = query.data

    # Главное меню
    if data == "main_menu":
        await query.edit_message_text(
            "🏠 *Главное меню*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # Выбор уровня
    elif data == "change_level":
        await query.edit_message_text("🎯 Выбери уровень:", reply_markup=level_keyboard())

    elif data.startswith("level_"):
        level = data.split("_", 1)[1]
        update_user(user_id, {"level": level, "seen_words": [], "repeat_mode": None})
        emoji, label, desc = LEVEL_INFO[level]
        await query.edit_message_text(
            f"{emoji} Уровень *{level} — {label}* выбран!\n"
            f"_{desc}_\n\n"
            f"В базе *{len(WORDS[level])} слов*.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Получить первое слово!", callback_data="get_word")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
            ])
        )

    # Получить слово
    elif data == "get_word":
        user_data = get_user(user_id)
        if not user_data.get("level"):
            await query.edit_message_text("⚠️ Сначала выбери уровень:", reply_markup=level_keyboard())
            return
        await _send_next_word(query.edit_message_text, user_id, user_data)

    # ✅ Знаю это слово
    elif data.startswith("known_"):
        word = data.split("_", 1)[1]
        user_data = get_user(user_id)
        known     = user_data.get("known_words", [])
        new_words = user_data.get("new_words", [])

        if word not in known:
            known.append(word)
        if word in new_words:
            new_words.remove(word)  # переносим из "новых" в "знаю"

        update_user(user_id, {"known_words": known, "new_words": new_words})

        # Сразу показываем следующее слово
        user_data = get_user(user_id)
        await _send_next_word(query.edit_message_text, user_id, user_data)

    # 📚 Новое для меня
    elif data.startswith("new_"):
        word = data.split("_", 1)[1]
        user_data = get_user(user_id)
        new_words = user_data.get("new_words", [])

        if word not in new_words:
            new_words.append(word)

        update_user(user_id, {"new_words": new_words})

        # Сразу показываем следующее слово
        user_data = get_user(user_id)
        await _send_next_word(query.edit_message_text, user_id, user_data)

    # Библиотека
    elif data == "show_library":
        user_data = get_user(user_id)
        level = user_data.get("level", "A1")
        text = format_library(user_data, level)
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ])
        )

    # Статистика
    elif data == "show_stats":
        await _send_stats(query.edit_message_text, user_id)

    # Режимы повторения
    elif data == "repeat_all":
        update_user(user_id, {"seen_words": [], "repeat_mode": "all"})
        user_data = get_user(user_id)
        await _send_next_word(query.edit_message_text, user_id, user_data)

    elif data == "repeat_new":
        update_user(user_id, {"seen_words": [], "repeat_mode": "new"})
        user_data = get_user(user_id)
        await _send_next_word(query.edit_message_text, user_id, user_data)

# ─── Daily job ────────────────────────────────────────────────────────────────
async def send_daily_words(context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    logger.info(f"Daily words → {len(db)} users")
    for user_id, user_data in db.items():
        if not user_data.get("active", True):
            continue
        level = user_data.get("level")
        if not level:
            continue
        try:
            seen = user_data.get("seen_words", [])
            word_data = get_random_word(level, seen)
            if word_data is None:
                continue
            seen.append(word_data["word"])
            update_user(user_id, {"seen_words": seen[-300:]})
            await context.bot.send_message(
                chat_id=int(user_id),
                text="🌅 *Слово дня!*\n\n" + format_word(word_data, level),
                parse_mode="Markdown",
                reply_markup=word_keyboard(word_data["word"])
            )
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("menu",    menu_command))
    app.add_handler(CommandHandler("word",    word_command))
    app.add_handler(CommandHandler("library", library_command))
    app.add_handler(CommandHandler("stats",   stats_command))
    app.add_handler(CommandHandler("level",   level_command))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_daily(send_daily_words, time=time(hour=9, minute=0))

    logger.info("Bot started!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()