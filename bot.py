import os
import json
import random
import logging
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ─── Word Database ────────────────────────────────────────────────────────────
WORDS = {
    "A1": [
        {"word": "cat", "transcription": "/kæt/", "translation": "кот, кошка", "part_of_speech": "noun", "example": "I have a cat.", "example_ru": "У меня есть кошка."},
        {"word": "dog", "transcription": "/dɒɡ/", "translation": "собака", "part_of_speech": "noun", "example": "The dog is big.", "example_ru": "Собака большая."},
        {"word": "house", "transcription": "/haʊs/", "translation": "дом", "part_of_speech": "noun", "example": "This is my house.", "example_ru": "Это мой дом."},
        {"word": "water", "transcription": "/ˈwɔːtər/", "translation": "вода", "part_of_speech": "noun", "example": "I drink water every day.", "example_ru": "Я пью воду каждый день."},
        {"word": "food", "transcription": "/fuːd/", "translation": "еда", "part_of_speech": "noun", "example": "The food is good.", "example_ru": "Еда хорошая."},
        {"word": "book", "transcription": "/bʊk/", "translation": "книга", "part_of_speech": "noun", "example": "I read a book.", "example_ru": "Я читаю книгу."},
        {"word": "car", "transcription": "/kɑːr/", "translation": "машина, автомобиль", "part_of_speech": "noun", "example": "He has a red car.", "example_ru": "У него красная машина."},
        {"word": "day", "transcription": "/deɪ/", "translation": "день", "part_of_speech": "noun", "example": "Today is a good day.", "example_ru": "Сегодня хороший день."},
        {"word": "eat", "transcription": "/iːt/", "translation": "есть, кушать", "part_of_speech": "verb", "example": "I eat breakfast every morning.", "example_ru": "Я завтракаю каждое утро."},
        {"word": "go", "transcription": "/ɡoʊ/", "translation": "идти, ехать", "part_of_speech": "verb", "example": "I go to school.", "example_ru": "Я иду в школу."},
        {"word": "big", "transcription": "/bɪɡ/", "translation": "большой", "part_of_speech": "adjective", "example": "That is a big dog.", "example_ru": "Это большая собака."},
        {"word": "small", "transcription": "/smɔːl/", "translation": "маленький", "part_of_speech": "adjective", "example": "She has a small bag.", "example_ru": "У неё маленькая сумка."},
        {"word": "happy", "transcription": "/ˈhæpi/", "translation": "счастливый", "part_of_speech": "adjective", "example": "I am happy today.", "example_ru": "Я сегодня счастлив."},
        {"word": "good", "transcription": "/ɡʊd/", "translation": "хороший", "part_of_speech": "adjective", "example": "This is good food.", "example_ru": "Это хорошая еда."},
        {"word": "friend", "transcription": "/frend/", "translation": "друг, подруга", "part_of_speech": "noun", "example": "She is my best friend.", "example_ru": "Она моя лучшая подруга."},
        {"word": "work", "transcription": "/wɜːrk/", "translation": "работа; работать", "part_of_speech": "noun/verb", "example": "I go to work by bus.", "example_ru": "Я еду на работу на автобусе."},
        {"word": "school", "transcription": "/skuːl/", "translation": "школа", "part_of_speech": "noun", "example": "My school is near home.", "example_ru": "Моя школа рядом с домом."},
        {"word": "time", "transcription": "/taɪm/", "translation": "время", "part_of_speech": "noun", "example": "What time is it?", "example_ru": "Который час?"},
        {"word": "money", "transcription": "/ˈmʌni/", "translation": "деньги", "part_of_speech": "noun", "example": "I need money.", "example_ru": "Мне нужны деньги."},
        {"word": "like", "transcription": "/laɪk/", "translation": "нравиться, любить", "part_of_speech": "verb", "example": "I like pizza.", "example_ru": "Мне нравится пицца."},
        {"word": "run", "transcription": "/rʌn/", "translation": "бежать, бегать", "part_of_speech": "verb", "example": "I run every morning.", "example_ru": "Я бегаю каждое утро."},
        {"word": "sun", "transcription": "/sʌn/", "translation": "солнце", "part_of_speech": "noun", "example": "The sun is bright today.", "example_ru": "Сегодня яркое солнце."},
        {"word": "tree", "transcription": "/triː/", "translation": "дерево", "part_of_speech": "noun", "example": "There is a big tree in the garden.", "example_ru": "В саду есть большое дерево."},
        {"word": "new", "transcription": "/njuː/", "translation": "новый", "part_of_speech": "adjective", "example": "I have a new phone.", "example_ru": "У меня новый телефон."},
        {"word": "old", "transcription": "/oʊld/", "translation": "старый", "part_of_speech": "adjective", "example": "This is an old house.", "example_ru": "Это старый дом."},
        {"word": "man", "transcription": "/mæn/", "translation": "мужчина, человек", "part_of_speech": "noun", "example": "The man is tall.", "example_ru": "Мужчина высокий."},
        {"word": "woman", "transcription": "/ˈwʊmən/", "translation": "женщина", "part_of_speech": "noun", "example": "The woman is kind.", "example_ru": "Женщина добрая."},
        {"word": "see", "transcription": "/siː/", "translation": "видеть", "part_of_speech": "verb", "example": "I can see the mountains.", "example_ru": "Я вижу горы."},
        {"word": "say", "transcription": "/seɪ/", "translation": "говорить, сказать", "part_of_speech": "verb", "example": "What did you say?", "example_ru": "Что ты сказал?"},
        {"word": "year", "transcription": "/jɪər/", "translation": "год", "part_of_speech": "noun", "example": "I am ten years old.", "example_ru": "Мне десять лет."},
    ],
    "A2": [
        {"word": "travel", "transcription": "/ˈtrævəl/", "translation": "путешествовать; путешествие", "part_of_speech": "verb/noun", "example": "I love to travel.", "example_ru": "Я люблю путешествовать."},
        {"word": "weather", "transcription": "/ˈweðər/", "translation": "погода", "part_of_speech": "noun", "example": "The weather is cold today.", "example_ru": "Сегодня холодная погода."},
        {"word": "hospital", "transcription": "/ˈhɒspɪtl/", "translation": "больница, госпиталь", "part_of_speech": "noun", "example": "She works at the hospital.", "example_ru": "Она работает в больнице."},
        {"word": "angry", "transcription": "/ˈæŋɡri/", "translation": "злой, сердитый", "part_of_speech": "adjective", "example": "He was angry about the mistake.", "example_ru": "Он злился из-за ошибки."},
        {"word": "careful", "transcription": "/ˈkeərfəl/", "translation": "осторожный, внимательный", "part_of_speech": "adjective", "example": "Be careful on the road.", "example_ru": "Будь осторожен на дороге."},
        {"word": "explain", "transcription": "/ɪkˈspleɪn/", "translation": "объяснять", "part_of_speech": "verb", "example": "Can you explain this word?", "example_ru": "Ты можешь объяснить это слово?"},
        {"word": "choose", "transcription": "/tʃuːz/", "translation": "выбирать", "part_of_speech": "verb", "example": "Choose your favourite colour.", "example_ru": "Выбери свой любимый цвет."},
        {"word": "dream", "transcription": "/driːm/", "translation": "мечта; мечтать", "part_of_speech": "noun/verb", "example": "I dream of visiting Paris.", "example_ru": "Я мечтаю посетить Париж."},
        {"word": "quiet", "transcription": "/ˈkwaɪət/", "translation": "тихий, спокойный", "part_of_speech": "adjective", "example": "The library is very quiet.", "example_ru": "В библиотеке очень тихо."},
        {"word": "busy", "transcription": "/ˈbɪzi/", "translation": "занятой", "part_of_speech": "adjective", "example": "I am busy at work today.", "example_ru": "Я сегодня занят на работе."},
        {"word": "forget", "transcription": "/fərˈɡet/", "translation": "забывать", "part_of_speech": "verb", "example": "Don't forget your keys!", "example_ru": "Не забудь свои ключи!"},
        {"word": "remember", "transcription": "/rɪˈmembər/", "translation": "помнить, вспоминать", "part_of_speech": "verb", "example": "I remember her name.", "example_ru": "Я помню её имя."},
        {"word": "enjoy", "transcription": "/ɪnˈdʒɔɪ/", "translation": "наслаждаться, получать удовольствие", "part_of_speech": "verb", "example": "I enjoy reading books.", "example_ru": "Я люблю читать книги."},
        {"word": "safe", "transcription": "/seɪf/", "translation": "безопасный", "part_of_speech": "adjective", "example": "This area is safe at night.", "example_ru": "Этот район безопасен ночью."},
        {"word": "strange", "transcription": "/streɪndʒ/", "translation": "странный, незнакомый", "part_of_speech": "adjective", "example": "That is a strange noise.", "example_ru": "Это странный звук."},
        {"word": "wait", "transcription": "/weɪt/", "translation": "ждать, подождать", "part_of_speech": "verb", "example": "Please wait a moment.", "example_ru": "Пожалуйста, подожди минуту."},
        {"word": "meet", "transcription": "/miːt/", "translation": "встречать, знакомиться", "part_of_speech": "verb", "example": "Nice to meet you!", "example_ru": "Приятно познакомиться!"},
        {"word": "difficult", "transcription": "/ˈdɪfɪkəlt/", "translation": "трудный, сложный", "part_of_speech": "adjective", "example": "This exam is very difficult.", "example_ru": "Этот экзамен очень трудный."},
        {"word": "early", "transcription": "/ˈɜːrli/", "translation": "ранний; рано", "part_of_speech": "adjective/adverb", "example": "She wakes up early.", "example_ru": "Она рано просыпается."},
        {"word": "practice", "transcription": "/ˈpræktɪs/", "translation": "практика; практиковать", "part_of_speech": "noun/verb", "example": "Practice makes perfect.", "example_ru": "Практика ведёт к совершенству."},
        {"word": "hope", "transcription": "/hoʊp/", "translation": "надеяться; надежда", "part_of_speech": "verb/noun", "example": "I hope you feel better soon.", "example_ru": "Я надеюсь, ты скоро поправишься."},
        {"word": "surprise", "transcription": "/sərˈpraɪz/", "translation": "сюрприз; удивлять", "part_of_speech": "noun/verb", "example": "What a nice surprise!", "example_ru": "Какой приятный сюрприз!"},
        {"word": "ticket", "transcription": "/ˈtɪkɪt/", "translation": "билет", "part_of_speech": "noun", "example": "I bought two tickets for the train.", "example_ru": "Я купил два билета на поезд."},
        {"word": "message", "transcription": "/ˈmesɪdʒ/", "translation": "сообщение", "part_of_speech": "noun", "example": "Did you get my message?", "example_ru": "Ты получил моё сообщение?"},
        {"word": "question", "transcription": "/ˈkwestʃən/", "translation": "вопрос", "part_of_speech": "noun", "example": "Do you have any questions?", "example_ru": "У тебя есть вопросы?"},
        {"word": "answer", "transcription": "/ˈɑːnsər/", "translation": "ответ; отвечать", "part_of_speech": "noun/verb", "example": "What is the answer?", "example_ru": "Какой ответ?"},
        {"word": "bring", "transcription": "/brɪŋ/", "translation": "приносить, привозить", "part_of_speech": "verb", "example": "Please bring me some water.", "example_ru": "Пожалуйста, принеси мне воды."},
        {"word": "market", "transcription": "/ˈmɑːrkɪt/", "translation": "рынок, магазин", "part_of_speech": "noun", "example": "We buy vegetables at the market.", "example_ru": "Мы покупаем овощи на рынке."},
        {"word": "clean", "transcription": "/kliːn/", "translation": "чистый; убирать", "part_of_speech": "adjective/verb", "example": "Keep your room clean.", "example_ru": "Держи комнату в чистоте."},
        {"word": "late", "transcription": "/leɪt/", "translation": "поздний; опаздывать", "part_of_speech": "adjective/verb", "example": "Don't be late for school.", "example_ru": "Не опаздывай в школу."},
    ],
    "B1": [
        {"word": "achieve", "transcription": "/əˈtʃiːv/", "translation": "достигать, добиваться", "part_of_speech": "verb", "example": "She worked hard to achieve her goals.", "example_ru": "Она усердно работала, чтобы достичь своих целей."},
        {"word": "influence", "transcription": "/ˈɪnfluəns/", "translation": "влиять; влияние", "part_of_speech": "verb/noun", "example": "Music can influence our mood.", "example_ru": "Музыка может влиять на настроение."},
        {"word": "opportunity", "transcription": "/ˌɒpəˈtjuːnɪti/", "translation": "возможность", "part_of_speech": "noun", "example": "This is a great opportunity.", "example_ru": "Это отличная возможность."},
        {"word": "significant", "transcription": "/sɪɡˈnɪfɪkənt/", "translation": "значительный, важный", "part_of_speech": "adjective", "example": "There has been a significant improvement.", "example_ru": "Наблюдалось значительное улучшение."},
        {"word": "consider", "transcription": "/kənˈsɪdər/", "translation": "рассматривать, считать", "part_of_speech": "verb", "example": "Please consider my offer.", "example_ru": "Пожалуйста, рассмотри моё предложение."},
        {"word": "suggest", "transcription": "/səˈdʒest/", "translation": "предлагать, предполагать", "part_of_speech": "verb", "example": "I suggest we leave early.", "example_ru": "Я предлагаю уйти пораньше."},
        {"word": "improve", "transcription": "/ɪmˈpruːv/", "translation": "улучшать(ся)", "part_of_speech": "verb", "example": "You need to improve your writing.", "example_ru": "Тебе нужно улучшить письмо."},
        {"word": "require", "transcription": "/rɪˈkwaɪər/", "translation": "требовать, нуждаться", "part_of_speech": "verb", "example": "This job requires experience.", "example_ru": "Эта работа требует опыта."},
        {"word": "experience", "transcription": "/ɪkˈspɪəriəns/", "translation": "опыт; переживать", "part_of_speech": "noun/verb", "example": "I have experience in teaching.", "example_ru": "У меня есть опыт преподавания."},
        {"word": "purpose", "transcription": "/ˈpɜːrpəs/", "translation": "цель, намерение", "part_of_speech": "noun", "example": "What is the purpose of this meeting?", "example_ru": "Какова цель этой встречи?"},
        {"word": "aware", "transcription": "/əˈweər/", "translation": "осведомлённый, знающий", "part_of_speech": "adjective", "example": "Are you aware of the risks?", "example_ru": "Ты осведомлён о рисках?"},
        {"word": "effort", "transcription": "/ˈefərt/", "translation": "усилие, старание", "part_of_speech": "noun", "example": "It takes a lot of effort.", "example_ru": "Это требует больших усилий."},
        {"word": "despite", "transcription": "/dɪˈspaɪt/", "translation": "несмотря на", "part_of_speech": "preposition", "example": "Despite the rain, we went out.", "example_ru": "Несмотря на дождь, мы вышли."},
        {"word": "benefit", "transcription": "/ˈbenɪfɪt/", "translation": "польза, выгода; получать пользу", "part_of_speech": "noun/verb", "example": "Exercise has many health benefits.", "example_ru": "Упражнения имеют много преимуществ для здоровья."},
        {"word": "develop", "transcription": "/dɪˈveləp/", "translation": "развивать(ся)", "part_of_speech": "verb", "example": "She developed a new skill.", "example_ru": "Она развила новый навык."},
        {"word": "available", "transcription": "/əˈveɪləbl/", "translation": "доступный, имеющийся", "part_of_speech": "adjective", "example": "Is this product available online?", "example_ru": "Этот товар доступен онлайн?"},
        {"word": "provide", "transcription": "/prəˈvaɪd/", "translation": "обеспечивать, предоставлять", "part_of_speech": "verb", "example": "We provide free support.", "example_ru": "Мы предоставляем бесплатную поддержку."},
        {"word": "challenge", "transcription": "/ˈtʃælɪndʒ/", "translation": "вызов, трудность; бросать вызов", "part_of_speech": "noun/verb", "example": "Learning a language is a challenge.", "example_ru": "Изучение языка — это вызов."},
        {"word": "solution", "transcription": "/səˈluːʃən/", "translation": "решение, выход", "part_of_speech": "noun", "example": "We need to find a solution.", "example_ru": "Нам нужно найти решение."},
        {"word": "environment", "transcription": "/ɪnˈvaɪrənmənt/", "translation": "окружающая среда, обстановка", "part_of_speech": "noun", "example": "We must protect the environment.", "example_ru": "Мы должны защищать окружающую среду."},
        {"word": "manage", "transcription": "/ˈmænɪdʒ/", "translation": "управлять, справляться", "part_of_speech": "verb", "example": "Can you manage the project?", "example_ru": "Ты можешь управлять проектом?"},
        {"word": "support", "transcription": "/səˈpɔːrt/", "translation": "поддержка; поддерживать", "part_of_speech": "noun/verb", "example": "Thank you for your support.", "example_ru": "Спасибо за вашу поддержку."},
        {"word": "behaviour", "transcription": "/bɪˈheɪvjər/", "translation": "поведение", "part_of_speech": "noun", "example": "His behaviour was very strange.", "example_ru": "Его поведение было очень странным."},
        {"word": "affect", "transcription": "/əˈfekt/", "translation": "влиять на, затрагивать", "part_of_speech": "verb", "example": "Stress can affect your health.", "example_ru": "Стресс может влиять на здоровье."},
        {"word": "recently", "transcription": "/ˈriːsntli/", "translation": "недавно, в последнее время", "part_of_speech": "adverb", "example": "I recently moved to a new city.", "example_ru": "Я недавно переехал в новый город."},
        {"word": "reduce", "transcription": "/rɪˈdjuːs/", "translation": "сокращать, уменьшать", "part_of_speech": "verb", "example": "We need to reduce costs.", "example_ru": "Нам нужно сократить расходы."},
        {"word": "mention", "transcription": "/ˈmenʃən/", "translation": "упоминать; упоминание", "part_of_speech": "verb/noun", "example": "He didn't mention the problem.", "example_ru": "Он не упомянул проблему."},
        {"word": "involve", "transcription": "/ɪnˈvɒlv/", "translation": "включать, вовлекать", "part_of_speech": "verb", "example": "The project involves a lot of work.", "example_ru": "Проект предполагает много работы."},
        {"word": "therefore", "transcription": "/ˈðeərfɔːr/", "translation": "поэтому, следовательно", "part_of_speech": "adverb", "example": "I was tired, therefore I slept early.", "example_ru": "Я устал, поэтому лёг спать рано."},
        {"word": "according", "transcription": "/əˈkɔːrdɪŋ/", "translation": "согласно, в соответствии", "part_of_speech": "preposition", "example": "According to the report, sales increased.", "example_ru": "Согласно отчёту, продажи выросли."},
    ],
    "B2": [
        {"word": "pragmatic", "transcription": "/præɡˈmætɪk/", "translation": "прагматичный, практичный", "part_of_speech": "adjective", "example": "She took a pragmatic approach to the problem.", "example_ru": "Она подошла к проблеме прагматично."},
        {"word": "resilient", "transcription": "/rɪˈzɪliənt/", "translation": "стойкий, устойчивый", "part_of_speech": "adjective", "example": "Children are very resilient.", "example_ru": "Дети очень стойкие."},
        {"word": "ambiguous", "transcription": "/æmˈbɪɡjuəs/", "translation": "неоднозначный, двусмысленный", "part_of_speech": "adjective", "example": "His answer was ambiguous.", "example_ru": "Его ответ был неоднозначным."},
        {"word": "perceive", "transcription": "/pərˈsiːv/", "translation": "воспринимать, осознавать", "part_of_speech": "verb", "example": "How do you perceive the situation?", "example_ru": "Как ты воспринимаешь ситуацию?"},
        {"word": "substantial", "transcription": "/səbˈstænʃəl/", "translation": "существенный, значительный", "part_of_speech": "adjective", "example": "There was a substantial increase in sales.", "example_ru": "Наблюдался существенный рост продаж."},
        {"word": "contemplate", "transcription": "/ˈkɒntəmpleɪt/", "translation": "размышлять, рассматривать", "part_of_speech": "verb", "example": "She contemplated her next move.", "example_ru": "Она обдумывала свой следующий шаг."},
        {"word": "advocate", "transcription": "/ˈædvəkeɪt/", "translation": "выступать за; защитник", "part_of_speech": "verb/noun", "example": "He advocates for human rights.", "example_ru": "Он выступает за права человека."},
        {"word": "reluctant", "transcription": "/rɪˈlʌktənt/", "translation": "неохотный, не желающий", "part_of_speech": "adjective", "example": "She was reluctant to share her opinion.", "example_ru": "Она неохотно делилась своим мнением."},
        {"word": "collaborate", "transcription": "/kəˈlæbəreɪt/", "translation": "сотрудничать", "part_of_speech": "verb", "example": "We collaborated on the project.", "example_ru": "Мы сотрудничали над проектом."},
        {"word": "inevitable", "transcription": "/ɪnˈevɪtəbl/", "translation": "неизбежный", "part_of_speech": "adjective", "example": "Change is inevitable.", "example_ru": "Перемены неизбежны."},
        {"word": "phenomenon", "transcription": "/fɪˈnɒmɪnən/", "translation": "явление, феномен", "part_of_speech": "noun", "example": "This is a fascinating phenomenon.", "example_ru": "Это увлекательное явление."},
        {"word": "whereas", "transcription": "/ˌweərˈæz/", "translation": "тогда как, в то время как", "part_of_speech": "conjunction", "example": "She likes tea, whereas he prefers coffee.", "example_ru": "Она любит чай, тогда как он предпочитает кофе."},
        {"word": "consequence", "transcription": "/ˈkɒnsɪkwəns/", "translation": "последствие, результат", "part_of_speech": "noun", "example": "Think about the consequences.", "example_ru": "Подумай о последствиях."},
        {"word": "versatile", "transcription": "/ˈvɜːrsətaɪl/", "translation": "многосторонний, универсальный", "part_of_speech": "adjective", "example": "She is a versatile musician.", "example_ru": "Она разносторонний музыкант."},
        {"word": "perspective", "transcription": "/pərˈspektɪv/", "translation": "точка зрения, перспектива", "part_of_speech": "noun", "example": "Try to see it from my perspective.", "example_ru": "Попробуй взглянуть на это с моей точки зрения."},
        {"word": "acknowledge", "transcription": "/əkˈnɒlɪdʒ/", "translation": "признавать, подтверждать", "part_of_speech": "verb", "example": "He acknowledged his mistake.", "example_ru": "Он признал свою ошибку."},
        {"word": "coherent", "transcription": "/koʊˈhɪərənt/", "translation": "связный, последовательный", "part_of_speech": "adjective", "example": "Please give a coherent explanation.", "example_ru": "Пожалуйста, дайте связное объяснение."},
        {"word": "fluctuate", "transcription": "/ˈflʌktʃueɪt/", "translation": "колебаться, меняться", "part_of_speech": "verb", "example": "Prices fluctuate throughout the year.", "example_ru": "Цены колеблются в течение года."},
        {"word": "persist", "transcription": "/pərˈsɪst/", "translation": "настаивать, продолжаться", "part_of_speech": "verb", "example": "If symptoms persist, see a doctor.", "example_ru": "Если симптомы сохраняются, обратитесь к врачу."},
        {"word": "emphasis", "transcription": "/ˈemfəsɪs/", "translation": "акцент, ударение", "part_of_speech": "noun", "example": "The emphasis is on quality.", "example_ru": "Акцент делается на качестве."},
        {"word": "elaborate", "transcription": "/ɪˈlæbərɪt/", "translation": "детальный; разрабатывать подробнее", "part_of_speech": "adjective/verb", "example": "Could you elaborate on that point?", "example_ru": "Не могли бы вы подробнее рассказать об этом?"},
        {"word": "tangible", "transcription": "/ˈtændʒɪbl/", "translation": "ощутимый, реальный", "part_of_speech": "adjective", "example": "We need tangible results.", "example_ru": "Нам нужны ощутимые результаты."},
        {"word": "generate", "transcription": "/ˈdʒenəreɪt/", "translation": "генерировать, создавать", "part_of_speech": "verb", "example": "The project generated a lot of interest.", "example_ru": "Проект вызвал большой интерес."},
        {"word": "implication", "transcription": "/ˌɪmplɪˈkeɪʃən/", "translation": "подтекст, следствие", "part_of_speech": "noun", "example": "What are the implications of this decision?", "example_ru": "Каковы последствия этого решения?"},
        {"word": "hierarchy", "transcription": "/ˈhaɪərɑːrki/", "translation": "иерархия", "part_of_speech": "noun", "example": "There is a strict hierarchy in this company.", "example_ru": "В этой компании строгая иерархия."},
        {"word": "contradict", "transcription": "/ˌkɒntrəˈdɪkt/", "translation": "противоречить", "part_of_speech": "verb", "example": "These two statements contradict each other.", "example_ru": "Эти два утверждения противоречат друг другу."},
        {"word": "preliminary", "transcription": "/prɪˈlɪmɪnəri/", "translation": "предварительный", "part_of_speech": "adjective", "example": "Here are the preliminary results.", "example_ru": "Вот предварительные результаты."},
        {"word": "constitute", "transcription": "/ˈkɒnstɪtjuːt/", "translation": "составлять, образовывать", "part_of_speech": "verb", "example": "Women constitute 40% of the workforce.", "example_ru": "Женщины составляют 40% рабочей силы."},
        {"word": "hypothesis", "transcription": "/haɪˈpɒθɪsɪs/", "translation": "гипотеза, предположение", "part_of_speech": "noun", "example": "We need to test this hypothesis.", "example_ru": "Нам нужно проверить эту гипотезу."},
        {"word": "endeavour", "transcription": "/ɪnˈdevər/", "translation": "стремиться; усилие, попытка", "part_of_speech": "verb/noun", "example": "He endeavoured to finish on time.", "example_ru": "Он стремился закончить вовремя."},
    ],
    "C1": [
        {"word": "perspicacious", "transcription": "/ˌpɜːrspɪˈkeɪʃəs/", "translation": "проницательный, дальновидный", "part_of_speech": "adjective", "example": "A perspicacious observer noticed the flaw.", "example_ru": "Проницательный наблюдатель заметил недостаток."},
        {"word": "ephemeral", "transcription": "/ɪˈfemərəl/", "translation": "мимолётный, кратковременный", "part_of_speech": "adjective", "example": "Fame can be ephemeral.", "example_ru": "Слава может быть мимолётной."},
        {"word": "ubiquitous", "transcription": "/juːˈbɪkwɪtəs/", "translation": "вездесущий, повсеместный", "part_of_speech": "adjective", "example": "Smartphones have become ubiquitous.", "example_ru": "Смартфоны стали повсеместными."},
        {"word": "convoluted", "transcription": "/ˈkɒnvəluːtɪd/", "translation": "запутанный, сложный", "part_of_speech": "adjective", "example": "The instructions were unnecessarily convoluted.", "example_ru": "Инструкции были излишне запутанными."},
        {"word": "lucid", "transcription": "/ˈluːsɪd/", "translation": "ясный, понятный; в ясном уме", "part_of_speech": "adjective", "example": "She gave a lucid explanation.", "example_ru": "Она дала ясное объяснение."},
        {"word": "meticulous", "transcription": "/mɪˈtɪkjələs/", "translation": "тщательный, скрупулёзный", "part_of_speech": "adjective", "example": "He is meticulous about detail.", "example_ru": "Он скрупулёзен в деталях."},
        {"word": "ambivalent", "transcription": "/æmˈbɪvələnt/", "translation": "двойственный, амбивалентный", "part_of_speech": "adjective", "example": "I feel ambivalent about moving abroad.", "example_ru": "Я испытываю двойственные чувства насчёт переезда."},
        {"word": "mitigate", "transcription": "/ˈmɪtɪɡeɪt/", "translation": "смягчать, уменьшать", "part_of_speech": "verb", "example": "We must mitigate the risks.", "example_ru": "Мы должны смягчить риски."},
        {"word": "tenacious", "transcription": "/tɪˈneɪʃəs/", "translation": "упорный, настойчивый", "part_of_speech": "adjective", "example": "She was tenacious in pursuing her goals.", "example_ru": "Она настойчиво добивалась своих целей."},
        {"word": "superfluous", "transcription": "/suːˈpɜːrfluəs/", "translation": "излишний, лишний", "part_of_speech": "adjective", "example": "Remove any superfluous words from the text.", "example_ru": "Удалите лишние слова из текста."},
        {"word": "disparate", "transcription": "/ˈdɪspərɪt/", "translation": "несхожий, разнородный", "part_of_speech": "adjective", "example": "The team brought together disparate skills.", "example_ru": "Команда объединила разнородные навыки."},
        {"word": "nuance", "transcription": "/ˈnjuːɑːns/", "translation": "нюанс, тонкость", "part_of_speech": "noun", "example": "The translation lost many nuances.", "example_ru": "При переводе были утеряны многие нюансы."},
        {"word": "futile", "transcription": "/ˈfjuːtaɪl/", "translation": "тщетный, бесполезный", "part_of_speech": "adjective", "example": "It was futile to resist.", "example_ru": "Сопротивляться было бессмысленно."},
        {"word": "dichotomy", "transcription": "/daɪˈkɒtəmi/", "translation": "дихотомия, противопоставление", "part_of_speech": "noun", "example": "There is a false dichotomy between work and life.", "example_ru": "Между работой и жизнью существует ложное противопоставление."},
        {"word": "articulate", "transcription": "/ɑːrˈtɪkjuleɪt/", "translation": "чётко выражать; красноречивый", "part_of_speech": "verb/adjective", "example": "She articulated her concerns clearly.", "example_ru": "Она чётко выразила свои опасения."},
        {"word": "alleviate", "transcription": "/əˈliːvieɪt/", "translation": "облегчать, смягчать", "part_of_speech": "verb", "example": "Medicine can alleviate the pain.", "example_ru": "Лекарство может облегчить боль."},
        {"word": "plausible", "transcription": "/ˈplɔːzɪbl/", "translation": "правдоподобный, убедительный", "part_of_speech": "adjective", "example": "That sounds like a plausible explanation.", "example_ru": "Это звучит как правдоподобное объяснение."},
        {"word": "rhetoric", "transcription": "/ˈretərɪk/", "translation": "риторика; красноречие", "part_of_speech": "noun", "example": "His speech was full of empty rhetoric.", "example_ru": "Его речь была полна пустой риторики."},
        {"word": "irrevocable", "transcription": "/ɪˈrevəkəbl/", "translation": "безвозвратный, окончательный", "part_of_speech": "adjective", "example": "The decision is irrevocable.", "example_ru": "Решение окончательное."},
        {"word": "corroborate", "transcription": "/kəˈrɒbəreɪt/", "translation": "подтверждать, подкреплять", "part_of_speech": "verb", "example": "The evidence corroborates his story.", "example_ru": "Доказательства подтверждают его историю."},
        {"word": "ostensible", "transcription": "/ɒˈstensɪbl/", "translation": "мнимый, показной", "part_of_speech": "adjective", "example": "The ostensible reason was budget cuts.", "example_ru": "Мнимой причиной были сокращения бюджета."},
        {"word": "sycophant", "transcription": "/ˈsɪkəfænt/", "translation": "льстец, подхалим", "part_of_speech": "noun", "example": "The boss was surrounded by sycophants.", "example_ru": "Начальника окружали подхалимы."},
        {"word": "propagate", "transcription": "/ˈprɒpəɡeɪt/", "translation": "распространять(ся), пропагандировать", "part_of_speech": "verb", "example": "Ideas can propagate quickly online.", "example_ru": "Идеи могут быстро распространяться в сети."},
        {"word": "exemplify", "transcription": "/ɪɡˈzemplɪfaɪ/", "translation": "служить примером, иллюстрировать", "part_of_speech": "verb", "example": "Her work exemplifies dedication.", "example_ru": "Её работа является примером преданности."},
        {"word": "polarise", "transcription": "/ˈpoʊləraɪz/", "translation": "поляризовать, разделять", "part_of_speech": "verb", "example": "The issue polarised public opinion.", "example_ru": "Этот вопрос поляризовал общественное мнение."},
        {"word": "coerce", "transcription": "/koʊˈɜːrs/", "translation": "принуждать, заставлять", "part_of_speech": "verb", "example": "He was coerced into signing the document.", "example_ru": "Его принудили подписать документ."},
        {"word": "inadvertent", "transcription": "/ˌɪnədˈvɜːrtənt/", "translation": "ненамеренный, случайный", "part_of_speech": "adjective", "example": "It was an inadvertent mistake.", "example_ru": "Это была непреднамеренная ошибка."},
        {"word": "paradox", "transcription": "/ˈpærədɒks/", "translation": "парадокс", "part_of_speech": "noun", "example": "It is a paradox that the more we know, the less certain we feel.", "example_ru": "Парадокс в том, что чем больше знаешь, тем меньше уверенности."},
        {"word": "scrutinise", "transcription": "/ˈskruːtɪnaɪz/", "translation": "тщательно изучать, рассматривать", "part_of_speech": "verb", "example": "The documents were scrutinised carefully.", "example_ru": "Документы были тщательно изучены."},
        {"word": "precipitate", "transcription": "/prɪˈsɪpɪteɪt/", "translation": "ускорять, провоцировать; поспешный", "part_of_speech": "verb/adjective", "example": "The crisis was precipitated by poor planning.", "example_ru": "Кризис был спровоцирован плохим планированием."},
    ],
    "C2": [
        {"word": "mellifluous", "transcription": "/məˈlɪfluəs/", "translation": "сладкозвучный, мелодичный", "part_of_speech": "adjective", "example": "Her mellifluous voice captivated the audience.", "example_ru": "Её мелодичный голос покорил аудиторию."},
        {"word": "ineffable", "transcription": "/ɪˈnefəbl/", "translation": "невыразимый, неописуемый", "part_of_speech": "adjective", "example": "The view from the summit was ineffable.", "example_ru": "Вид с вершины был невыразимым."},
        {"word": "loquacious", "transcription": "/loʊˈkweɪʃəs/", "translation": "болтливый, разговорчивый", "part_of_speech": "adjective", "example": "My loquacious neighbour talks for hours.", "example_ru": "Мой болтливый сосед говорит часами."},
        {"word": "petrichor", "transcription": "/ˈpetrɪkɔːr/", "translation": "запах дождя на земле", "part_of_speech": "noun", "example": "After the storm, the petrichor was intoxicating.", "example_ru": "После бури запах дождя был восхитительным."},
        {"word": "apricity", "transcription": "/æˈprɪsɪti/", "translation": "тепло зимнего солнца", "part_of_speech": "noun", "example": "She enjoyed the apricity on a cold January day.", "example_ru": "Она наслаждалась теплом зимнего солнца в январе."},
        {"word": "crepuscular", "transcription": "/krɪˈpʌskjələr/", "translation": "сумеречный, относящийся к сумеркам", "part_of_speech": "adjective", "example": "Bats are crepuscular creatures.", "example_ru": "Летучие мыши — сумеречные существа."},
        {"word": "numinous", "transcription": "/ˈnjuːmɪnəs/", "translation": "священный, таинственный, возвышенный", "part_of_speech": "adjective", "example": "The ancient cathedral had a numinous quality.", "example_ru": "Древний собор обладал возвышенной атмосферой."},
        {"word": "ennui", "transcription": "/ɒnˈwiː/", "translation": "скука, томление (из французского)", "part_of_speech": "noun", "example": "A sense of ennui crept over him.", "example_ru": "Его охватило чувство томительной скуки."},
        {"word": "hiraeth", "transcription": "/ˈhɪraɪθ/", "translation": "тоска по родине или прошлому (валлийск.)", "part_of_speech": "noun", "example": "Living abroad, she felt hiraeth for her village.", "example_ru": "Живя за рубежом, она тосковала по своей деревне."},
        {"word": "verisimilitude", "transcription": "/ˌverɪsɪˈmɪlɪtjuːd/", "translation": "правдоподобие, достоверность", "part_of_speech": "noun", "example": "The novel had great verisimilitude.", "example_ru": "Роман обладал большой правдоподобностью."},
        {"word": "palimpsest", "transcription": "/ˈpælɪmpsest/", "translation": "палимпсест (рукопись поверх старой)", "part_of_speech": "noun", "example": "The city is a palimpsest of its history.", "example_ru": "Город — это палимпсест своей истории."},
        {"word": "sonder", "transcription": "/ˈsɒndər/", "translation": "осознание полноты жизни каждого встречного", "part_of_speech": "noun", "example": "Walking through the crowd, he felt a deep sonder.", "example_ru": "Идя сквозь толпу, он ощутил жизнь каждого вокруг."},
        {"word": "liminal", "transcription": "/ˈlɪmɪnəl/", "translation": "пороговый, переходный", "part_of_speech": "adjective", "example": "Graduation is a liminal moment in life.", "example_ru": "Окончание учёбы — переходный момент в жизни."},
        {"word": "sempiternal", "transcription": "/ˌsempɪˈtɜːrnəl/", "translation": "вечный, бесконечный", "part_of_speech": "adjective", "example": "They spoke of sempiternal love.", "example_ru": "Они говорили о вечной любви."},
        {"word": "nugatory", "transcription": "/ˈnjuːɡətəri/", "translation": "ничтожный, несущественный", "part_of_speech": "adjective", "example": "His objections were nugatory.", "example_ru": "Его возражения были несущественными."},
        {"word": "defenestration", "transcription": "/dɪˌfenɪˈstreɪʃən/", "translation": "выбрасывание из окна", "part_of_speech": "noun", "example": "The defenestration of Prague was a historical event.", "example_ru": "Дефенестрация Праги была историческим событием."},
        {"word": "persiflage", "transcription": "/ˈpɜːrsɪflɑːʒ/", "translation": "лёгкая насмешка, болтовня", "part_of_speech": "noun", "example": "His persiflage masked a sharp mind.", "example_ru": "За его лёгкой болтовнёй скрывался острый ум."},
        {"word": "velleity", "transcription": "/vɪˈliːɪti/", "translation": "слабое желание без намерения действовать", "part_of_speech": "noun", "example": "His wish to learn piano was only velleity.", "example_ru": "Его желание научиться играть было лишь слабым порывом."},
        {"word": "apophenia", "transcription": "/ˌæpəˈfiːniə/", "translation": "поиск закономерностей в случайных вещах", "part_of_speech": "noun", "example": "Seeing patterns in noise is a form of apophenia.", "example_ru": "Видеть закономерности в случайном — это апофения."},
        {"word": "sylvan", "transcription": "/ˈsɪlvən/", "translation": "лесной, относящийся к лесу", "part_of_speech": "adjective", "example": "They walked through a sylvan landscape.", "example_ru": "Они шли через лесистый пейзаж."},
        {"word": "sesquipedalian", "transcription": "/ˌseskwɪpɪˈdeɪliən/", "translation": "любящий длинные слова; многосложный", "part_of_speech": "adjective", "example": "His sesquipedalian speech confused everyone.", "example_ru": "Его речь из длинных слов смутила всех."},
        {"word": "absquatulate", "transcription": "/æbˈskwɒtʃəleɪt/", "translation": "тайно сбежать, улизнуть (устар.)", "part_of_speech": "verb", "example": "The thief absquatulated before police arrived.", "example_ru": "Вор улизнул до прихода полиции."},
        {"word": "xenodochial", "transcription": "/ˌzenədɒˈkaɪəl/", "translation": "гостеприимный к чужестранцам", "part_of_speech": "adjective", "example": "The xenodochial host welcomed all travellers.", "example_ru": "Гостеприимный хозяин встречал всех путников."},
        {"word": "accismus", "transcription": "/ækˈsɪzməs/", "translation": "притворный отказ от желаемого", "part_of_speech": "noun", "example": "Her refusal was mere accismus.", "example_ru": "Её отказ был лишь притворным."},
        {"word": "perspicuity", "transcription": "/ˌpɜːrspɪˈkjuːɪti/", "translation": "ясность, понятность изложения", "part_of_speech": "noun", "example": "The perspicuity of his writing was admired.", "example_ru": "Ясность его письма вызывала восхищение."},
        {"word": "solipsism", "transcription": "/ˈsɒlɪpsɪzəm/", "translation": "убеждение что реальна только собственная личность", "part_of_speech": "noun", "example": "His worldview bordered on solipsism.", "example_ru": "Его мировоззрение граничило с солипсизмом."},
        {"word": "tmesis", "transcription": "/ˈtiːmɪsɪs/", "translation": "тмесис — вставка слова внутрь другого", "part_of_speech": "noun", "example": "'Abso-bloody-lutely' is an example of tmesis.", "example_ru": "'Abso-bloody-lutely' — пример тмесиса."},
        {"word": "vellichor", "transcription": "/ˈvelɪkɔːr/", "translation": "ностальгия по старым книгам (неологизм)", "part_of_speech": "noun", "example": "She felt vellichor browsing the antique bookshop.", "example_ru": "Она ощутила ностальгию по книгам в антикварном магазине."},
        {"word": "eigenvalue", "transcription": "/ˈaɪɡənvæljuː/", "translation": "собственное значение (математика)", "part_of_speech": "noun", "example": "The eigenvalue of the matrix was calculated.", "example_ru": "Собственное значение матрицы было вычислено."},
        {"word": "callipygian", "transcription": "/ˌkælɪˈpɪdʒiən/", "translation": "с красиво сложённой фигурой (из греч.)", "part_of_speech": "adjective", "example": "The statue was described as callipygian.", "example_ru": "Статуя была описана с использованием греческого термина."},
    ],
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
    update_user(user_id, {"seen_words": seen[-100:]})
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
    await update.message.reply_text(
        f"📊 *Твоя статистика*\n\n"
        f"🎯 Уровень: {emoji} *{level}*\n"
        f"👀 Показано слов: *{len(user_data.get('seen_words', []))}*\n"
        f"✅ Знаю: *{len(user_data.get('known_words', []))}*\n"
        f"📖 Изучаю: *{len(user_data.get('new_words', []))}*",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Команды бота:*\n\n"
        "/start — начать\n"
        "/word — получить слово\n"
        "/library — моя библиотека\n"
        "/stats — моя статистика\n"
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
        update_user(user_id, {"seen_words": seen[-100:]})
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
            update_user(user_id, {"seen_words": seen[-100:]})
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
