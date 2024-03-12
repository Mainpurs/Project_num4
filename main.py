import sqlite3
import logging
from SQLite import add_user, update_row_value, delete_user, user_in, get_data_for_user
import requests
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from create import prepare_database

TOKEN = "6907816424:AAFtptMbHmk8FH4w39qBW7Zy1533IKPiPEM"
bot = telebot.TeleBot(TOKEN)
db_file = 'sqliteData.db'


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

MAX_TASK_TOKENS = 150
system_content_maths = 'Ты учитель по математике на русском языке'
system_content_art = 'Ты учитель по изобразительному исскуству на русском языке'
assistant_content_beginner = 'Вот ответ на ваш вопрос(кратко): '
assistant_content_advanced = 'Вот ответ на ваш вопрос(развернуто):'
user_content = ''
answer = ''
subject = ''
lvl = ''


def menu_keyboard(text_1, text_2):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    # добавляем кнопочки с вариантами ответа
    answer_1 = KeyboardButton(text=text_1)
    answer_2 = KeyboardButton(text=text_2)
    keyboard.add(answer_1, answer_2)
    # возвращаем готовую клавиатуру с кнопочками
    return keyboard


# -------------------------------------------------Основной_код---------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    prepare_database()
    user_name = message.from_user.first_name
    user_id = message.chat.id

    delete_user(db_file, tg_id=user_id)
    add_user(db_file, tg_id=user_id, status=1, admin=0, user_prompt='0', subject='0', lvl=0, ANSWER='0')

    msg = bot.send_message(user_id,
                           f"Привет, {user_name}! Я бот-помощник для решения задач по разным предметам!",
                           reply_markup=menu_keyboard("/help_with_maths", "/help_with_art"))

    bot.register_next_step_handler(msg, choose_subject)


# ------------------------------------------------------------------
def choose_subject(message):
    user_id = message.chat.id  # Получаем идентификатор пользователя

    if message.text == '/help_with_maths':
        subject = 'maths'
        update_row_value(db_file, tg_id=user_id, column_name='subject', new_value='maths')
        print(subject)

    elif message.text == '/help_with_art':
        subject = 'art'
        update_row_value(db_file, tg_id=user_id, column_name='subject', new_value='art')
        print(subject)
    else:
        start(message)
        return

    # Предлагаем пользователю выбрать уровень сложности
    msg = bot.send_message(user_id, "Выбери свой уровень знаний:\n"
                                    "beginner - начинающий\n"
                                    "advanced - продвинутый",
                           reply_markup=menu_keyboard('beginner', 'advanced'))
    bot.register_next_step_handler(msg, choose_lvl)  # Регистрируем функцию-обработчик для выбора уровня


# ------------------------------------------------------------------
def choose_lvl(message):
    user_id = message.from_user.id  # Извлекаем идентификатор пользователя
    lvl = message.text

    if lvl == 'beginner':
        update_row_value(db_file, tg_id=user_id, column_name='lvl', new_value=1)
        print(lvl)
    elif lvl == 'advanced':
        update_row_value(db_file, tg_id=user_id, column_name='lvl', new_value=2)
        print(lvl)
    else:
        bot.send_message(user_id, 'Ошибка выбора слжности.')
        logging.error('Ошибка выбора слжности.')
        choose_subject(message)
        return

    msg = bot.send_message(user_id, 'Теперь напишите вопрос или задачу')
    bot.register_next_step_handler(msg, get_answer_from_gpt)


# --------------------------------------------------!!ДЖЫПИТИ!!---------------------------------------------------------
def get_answer_from_gpt(message):
    user_id = message.chat.id

    user_content = message.text
    answer = ''
    if len(message.text) > MAX_TASK_TOKENS:  # Выполняем проверку на размер задачи
        user_content = ""
        answer = ""

        bot.send_message(user_id, "Текст задачи слишком длинный. Пожалуйста, попробуй его укоротить.")
        logging.info(f"TELEGRAM BOT: Input: {message.text}\nOutput: Текст задачи слишком длинный")
        get_answer_from_gpt(message)
        return

    update_row_value(db_file, tg_id=user_id, column_name='user_prompt', new_value=user_content)
    update_row_value(db_file, tg_id=user_id, column_name='status', new_value=2)

    bot.send_message(user_id, 'Думаю...')

    # --------------------------------------------------------------------
    result = get_data_for_user(db_file, tg_id=user_id)
    user_content = result['user_prompt']
    subject = result['subject']
    lvl = result['lvl']
    print(user_content)
    print(subject)
    print(lvl)

    if subject == 'maths':
        system_content = system_content_maths
    else:
        system_content = system_content_art

    if lvl == 1:
        assistant_content = assistant_content_beginner
    else:
        assistant_content = assistant_content_advanced

    # ------------------------------------------------------------
    resp = requests.post(
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content},
                {"role": "system", "content": system_content},
            ],
            "temperature": 1,
            "max_tokens": 1124
        }
    )

    if resp.status_code == 200 and 'choices' in resp.json():
        answer = resp.json()['choices'][0]['message']['content']
        if answer == "":
            bot.send_message(user_id, "Введите /continue чтобы продолжить!",
                             reply_markup=menu_keyboard("/help_with_maths", "/help_with_art"))
        else:
            bot.send_message(user_id, f'{answer}')
            bot.send_message(user_id, "Введите /continue чтобы продолжить!",
                             reply_markup=menu_keyboard("/help_with_maths", "/help_with_art"))
    else:
        logging.error(f'Не удалось получить ответ от нейросети.\nЗапрос:\n{user_content}')
        bot.send_message(user_id, 'Не удалось получить ответ от нейросети')

    update_row_value(db_file, tg_id=user_id, column_name='ANSWER', new_value=answer)
    print(result)

    return answer


# ===================================================Fgpt===============================================================
@bot.message_handler(commands=['continue'])
def Fcontinue(message):
    user_id = message.chat.id


    result = get_data_for_user(db_file, tg_id=user_id)
    user_content = result['user_prompt']
    subject = result['subject']
    lvl = result['lvl']
    answer = result['ANSWER']
    status = result['status']
    print(user_content)
    print(lvl)
    print(subject)
    print(answer)
    print(status)

    if status != 2:  # проверка на 1-й запрос
        return

    if subject == 'maths':
        system_content = system_content_maths
    else:
        system_content = system_content_art

    if lvl == 1:
        assistant_content = assistant_content_beginner
    else:
        assistant_content = assistant_content_advanced

    bot.send_message(user_id, 'Думаю...')
    # --------------------------------------------------------

    assistant_content += answer
    print(assistant_content)

    # --------------------------------------------------------

    resp = requests.post(
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content},
                {"role": "system", "content": system_content},
            ],
            "temperature": 1,
            "max_tokens": 1124
        }
    )

    if resp.status_code == 200 and 'choices' in resp.json():
        answer = resp.json()['choices'][0]['message']['content']
        if answer == "":
            bot.send_message(user_id, "Введите /continue чтобы продолжить!",
                             reply_markup=menu_keyboard("/help_with_maths", "/help_with_art"))
        else:
            bot.send_message(user_id, f'{answer}')
            bot.send_message(user_id, "Введите /continue чтобы продолжить!",
                             reply_markup=menu_keyboard("/help_with_maths", "/help_with_art"))
    else:
        logging.error(f'Не удалось получить ответ от нейросети.\nЗапрос:\n{user_content}')
        bot.send_message(user_id, 'Не удалось получить ответ от нейросети')

    answer += answer
    print(answer)
    update_row_value(db_file, tg_id=user_id, column_name='ANSWER', new_value=answer)
    print(result)

    return answer


bot.infinity_polling()
