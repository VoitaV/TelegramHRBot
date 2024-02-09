# zadachi.py

import time
import threading
from telebot import types  # Импортируем типы для кнопок

# Функция для запуска тестирования
def test_razrab_start(bot, message, user_data):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['score'] = 0
    user_data[user_id]['start_time'] = time.time()
    user_data[user_id]['test_started'] = True
    user_data[user_id]['current_question_index'] = 0
    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # keyboard.add(types.KeyboardButton("Да! Я весь внимание!"))
    # msg = bot.send_message(message.chat.id, "Время уже пошло! Ты точно сосредоточен?", reply_markup=keyboard)
    send_question(bot, message, user_data)
    # Запускаем таймер для завершения теста через 3 минуты
    timer = threading.Timer(180, finish_test_timeout, args=[bot, message, user_data])
    timer.start()
    user_data[user_id]['timer'] = timer

def send_question(bot, message, user_data):
    user_id = message.from_user.id
    current_question_index = user_data[user_id]['current_question_index']
    if current_question_index < len(questions):
        question = questions[current_question_index]
        # Создаем клавиатуру с вариантами ответов
        keyboard = create_answer_keyboard(question['answers'])
        bot.send_message(message.chat.id, f"{question['text']}", reply_markup=keyboard)
        bot.register_next_step_handler(message, lambda m: handle_answer(bot, m, user_data))
    else:
        finish_test(bot, message, user_data)

def handle_answer(bot, message, user_data):
    user_id = message.from_user.id
    if 'test_started' in user_data.get(user_id, {}):
        current_question_index = user_data[user_id].get('current_question_index', 0)
        if current_question_index < len(questions):
            question = questions[current_question_index]
            user_answer = message.text.strip()
            if user_answer.lower() == question['correct_answer'].lower():
                user_data[user_id]['score'] += 1
            user_data[user_id][f'question{current_question_index + 1}_answer'] = user_answer
            user_data[user_id]['current_question_index'] += 1
            send_question(bot, message, user_data)

def finish_test(bot, message, user_data):
    user_id = message.from_user.id
    if 'test_started' in user_data.get(user_id, {}):
        end_time = time.time()
        start_time = user_data[user_id]['start_time']
        duration = end_time - start_time
        user_data[user_id]['end_time'] = end_time
        bot.send_message(message.chat.id, f"Тестирование завершено! Ваш результат: {user_data[user_id]['score']} из {len(questions)}")
        bot.send_message(message.chat.id, f"Время прохождения теста: {duration:.2f} секунд.")
        user_data[user_id]['timer'].cancel()
        from main import save_to_excel
        save_to_excel(message, user_data)


def finish_test_timeout(bot, message, user_data):
    user_id = message.from_user.id
    if 'test_started' in user_data.get(user_id, {}):
        bot.send_message(message.chat.id, "Время вышло! Тестирование автоматически завершено.")
        finish_test(bot, message, user_data)

# Создание клавиатуры с вариантами ответов
def create_answer_keyboard(answers):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for answer in answers:
        keyboard.add(types.KeyboardButton(answer))
    return keyboard

# Список вопросов для теста
questions = [
    {
        'text': 'Вопрос 1: Сколько будет 2 + 2?',
        'answers': ['3', '4', '5', '6'],
        'correct_answer': '4'
    },
    {
        'text': 'Вопрос 2: Какой год был високосным: 2000, 2010, 2012, 2020?',
        'answers': ['2000', '2010', '2012', '2020'],
        'correct_answer': '2012'
    },
    {
        'text': 'Вопрос 3: Что из перечисленного является фруктом: апельсин, помидор, картофель, огурец?',
        'answers': ['Апельсин', 'Помидор', 'Картофель', 'Огурец'],
        'correct_answer': 'Апельсин'
    }
]
