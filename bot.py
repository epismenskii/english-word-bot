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

# ─── Единый словарь из всех файлов ───────────────────────────────────────────
WORDS = {
    "A1": WORDS_A1,
    "A2": WORDS_A2,
    "B1": WORDS_B1,
    "B2": WORDS_B2,
    "C1": WORDS_C1,
    "C2": WORDS_C2,
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
        db[user_id] = {"level": None, "known_words": [], "new_words": [], "seen_words": [], "active": True}
        save_db(db)
    return db[user_id]

def update_user(user_id: str, data: dict):
    db = load_db()
    if user_id not in db:
        db[user_id] = {}
    db[user_id].update(data)
    save_db(db)

def get_random_word(level: str, seen: list) -> dict:
    available = [w for w in WORDS.get(level, []) if w["word"] not in seen]
    if not available:
        available = WORDS.get(level, [])
    return random.choice(available)

# ─── UI ───────────────────────────────────────────────────────────────────────
LEVEL_INFO = {
    "A1": ("🟢", "Начинающий",    "Базовые слова — числа, цвета, животные"),
    "A2": ("🟢", "Элементарный",  "Повседневные темы — еда, путешествия, семья"),
    "B1": ("🟡", "Средний",       "Общение на большинство тем"),
    "B2": ("🟡", "Выше среднего", "Сложные темы, абстрактные понятия"),
    "C1": ("🔴", "Продвинутый",   "Академический язык, нюансы"),
    "C2": ("🔴", "Мастерство",    "Редкие слова, идиомы, тонкости"),
}

def level_keyboard():
    rows = []
    levels = list(LEVEL_INFO.items())
    for i in range(0, len(levels), 2):
        row = []
        for lvl, (emoji, label, _) in levels[i:i+2]:
            row.append(InlineKeyboardButton(f"{emoji} {lvl} · {label}", callback_data=f"level_{lvl}"))
        rows.append(row)
    return InlineKeyboardMarkup(rows)

def word_keyboard(word: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Знаю это слово", callback_data=f"known_{word}"),
            InlineKeyboardButton("📚 Новое для меня", callback_data=f"new_{word}"),
        ],
        [InlineKeyboardButton("🔄 Другое слово", callback_data="get_word")]
    ])

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

# ─── Handlers ─────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Привет, *{user.first_name}*!\n\n"
        f"Я буду каждый день присылать тебе новые английские слова "
        f"с транскрипцией и переводом 🇬🇧\n\n"
        f"Выбери свой уровень английского:",
        parse_mode="Markdown", reply_markup=level_keyboard()
    )

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user(user_id)
    if not user_data.get("level"):
        await update.message.reply_text("⚠️ Сначала выбери уровень:", reply_markup=level_keyboard())
        return
    level = user_data["level"]
    seen = user_data.get("seen_words", [])
    word_data = get_random_word(level, seen)
    seen.append(word_data["word"])
    update_user(user_id, {"seen_words": seen[-200:]})
    await update.message.reply_text(
        format_word(word_data, level), parse_mode="Markdown",
        reply_markup=word_keyboard(word_data["word"])
    )

async def library_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user(user_id)
    known = user_data.get("known_words", [])
    new_words = user_data.get("new_words", [])
    if not known and not new_words:
        await update.message.reply_text("📚 Библиотека пуста.\n\nПолучи слово командой /word и добавь его!")
        return
    text = "📚 *Твоя библиотека*\n\n"
    if known:
        text += f"✅ *Знаю — {len(known)} сл.:*\n"
        text += "  " + ",  ".join(f"`{w}`" for w in known[-15:])
        if len(known) > 15: text += f"\n  _...и ещё {len(known)-15}_"
        text += "\n\n"
    if new_words:
        text += f"📖 *Изучаю — {len(new_words)} сл.:*\n"
        text += "  " + ",  ".join(f"`{w}`" for w in new_words[-15:])
        if len(new_words) > 15: text += f"\n  _...и ещё {len(new_words)-15}_"
    await update.message.reply_text(text, parse_mode="Markdown")

async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 Выбери новый уровень:", reply_markup=level_keyboard())

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = get_user(user_id)
    level = user_data.get("level", "не выбран")
    emoji = LEVEL_INFO.get(level, ("📚",))[0] if level != "не выбран" else "📚"
    total = len(WORDS.get(level, [])) if level != "не выбран" else 0
    await update.message.reply_text(
        f"📊 *Твоя статистика*\n\n"
        f"🎯 Уровень: {emoji} *{level}*\n"
        f"📖 Слов в базе: *{total}*\n"
        f"👀 Показано: *{len(user_data.get('seen_words', []))}*\n"
        f"✅ Знаю: *{len(user_data.get('known_words', []))}*\n"
        f"📚 Изучаю: *{len(user_data.get('new_words', []))}*",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Команды бота:*\n\n"
        "/start — начать\n"
        "/word — получить слово\n"
        "/library — моя библиотека\n"
        "/stats — статистика\n"
        "/level — изменить уровень\n"
        "/help — справка\n\n"
        "💡 Каждый день в 9:00 я буду присылать тебе новое слово!",
        parse_mode="Markdown"
    )

# ─── Callbacks ────────────────────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if data.startswith("level_"):
        level = data.split("_", 1)[1]
        update_user(user_id, {"level": level, "seen_words": []})
        emoji, label, desc = LEVEL_INFO[level]
        await query.edit_message_text(
            f"{emoji} Отлично! Уровень *{level} — {label}* выбран.\n"
            f"_{desc}_\n\n"
            f"В базе *{len(WORDS[level])} слов* для этого уровня.\n\nПолучи первое слово:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📖 Получить первое слово!", callback_data="get_word")]
            ])
        )

    elif data == "get_word":
        user_data = get_user(user_id)
        level = user_data.get("level", "B1")
        seen = user_data.get("seen_words", [])
        word_data = get_random_word(level, seen)
        seen.append(word_data["word"])
        update_user(user_id, {"seen_words": seen[-200:]})
        await query.edit_message_text(
            format_word(word_data, level), parse_mode="Markdown",
            reply_markup=word_keyboard(word_data["word"])
        )

    elif data.startswith("known_"):
        word = data.split("_", 1)[1]
        user_data = get_user(user_id)
        known = user_data.get("known_words", [])
        new_words = user_data.get("new_words", [])
        if word not in known: known.append(word)
        if word in new_words: new_words.remove(word)
        update_user(user_id, {"known_words": known, "new_words": new_words})
        await query.edit_message_text(
            query.message.text + f"\n\n✅ *«{word}»* добавлено в «Знаю»!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Ещё слово", callback_data="get_word")],
                [InlineKeyboardButton("📚 Библиотека", callback_data="show_library")]
            ])
        )

    elif data.startswith("new_"):
        word = data.split("_", 1)[1]
        user_data = get_user(user_id)
        new_words = user_data.get("new_words", [])
        if word not in new_words: new_words.append(word)
        update_user(user_id, {"new_words": new_words})
        await query.edit_message_text(
            query.message.text + f"\n\n📚 *«{word}»* добавлено в «Изучаю»!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Ещё слово", callback_data="get_word")],
                [InlineKeyboardButton("📚 Библиотека", callback_data="show_library")]
            ])
        )

    elif data == "show_library":
        user_data = get_user(user_id)
        known = user_data.get("known_words", [])
        new_words = user_data.get("new_words", [])
        text = "📚 *Твоя библиотека*\n\n"
        if known:
            text += f"✅ *Знаю ({len(known)}):* " + ", ".join(f"`{w}`" for w in known[-8:])
            if len(known) > 8: text += "..."
            text += "\n\n"
        if new_words:
            text += f"📖 *Изучаю ({len(new_words)}):* " + ", ".join(f"`{w}`" for w in new_words[-8:])
            if len(new_words) > 8: text += "..."
        if not known and not new_words:
            text = "📚 Библиотека пуста!"
        await query.edit_message_text(
            text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Получить слово", callback_data="get_word")]
            ])
        )

# ─── Daily job ────────────────────────────────────────────────────────────────
async def send_daily_words(context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    logger.info(f"Daily words → {len(db)} users")
    for user_id, user_data in db.items():
        if not user_data.get("active", True): continue
        level = user_data.get("level")
        if not level: continue
        try:
            seen = user_data.get("seen_words", [])
            word_data = get_random_word(level, seen)
            seen.append(word_data["word"])
            update_user(user_id, {"seen_words": seen[-200:]})
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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("word", word_command))
    app.add_handler(CommandHandler("library", library_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("level", level_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_daily(send_daily_words, time=time(hour=9, minute=0))
    logger.info("Bot started!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()