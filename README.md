# 🇬🇧 English Word Bot — полностью бесплатный

Telegram-бот который каждый день присылает английские слова с транскрипцией и переводом.

**💰 Стоимость: 0 рублей навсегда.**

## ✨ Возможности

- 🎯 Выбор уровня: A1, A2, B1, B2, C1, C2
- 📖 180 слов в базе (30 на каждый уровень)
- 🌅 Ежедневная рассылка слов в 9:00
- ✅ Кнопки «Знаю это слово» / «Новое для меня»
- 📚 Личная библиотека слов
- 📊 Статистика прогресса

---

## 🚀 Деплой на Render.com

### Шаг 1 — Создай бота в Telegram

1. Найди @BotFather в Telegram
2. Напиши /newbot
3. Придумай название и username (заканчивается на bot)
4. Сохрани токен вида: 7234567890:AAFxxxxxxxxxxxxxxxxxxxxxxx

### Шаг 2 — Загрузи на GitHub

1. github.com → New repository → назови english-word-bot → Public
2. "uploading an existing file" → загрузи все 4 файла
3. Commit changes

### Шаг 3 — Задеплой на Render

1. render.com → войди через GitHub
2. New + → Blueprint → выбери репозиторий english-word-bot
3. Apply → нажми на созданный сервис
4. Environment → Add Environment Variable:
   - Key: TELEGRAM_TOKEN
   - Value: твой токен от BotFather
5. Save Changes → Logs → увидишь "Bot started!"

### Шаг 4 — Проверь

Найди бота в Telegram → /start → выбери уровень → получи слово 🎉

---

## Команды

- /start — начать
- /word — получить слово
- /library — библиотека
- /stats — статистика
- /level — изменить уровень
- /help — справка
