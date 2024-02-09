# zadachi_analit.py

import time
import threading
from telebot import types  # Импортируем типы для кнопок
import openpyxl
# Функция для запуска тестирования
def test_analit_start(bot, message, user_data):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['score'] = 0
    user_data[user_id]['start_time'] = time.time()
    user_data[user_id]['test_started'] = True
    user_data[user_id]['current_question_index'] = 0
    
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
        if question['type'] == 'текст':
            keyboard = create_answer_keyboard(question['answers'])
            bot.send_message(message.chat.id, f"{question['content']}", reply_markup=keyboard)
        elif question['type'] == 'картинка':
            with open(question['content'], 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            keyboard = create_answer_keyboard(question['answers'])
            bot.send_message(message.chat.id, "Выберите ответ:", reply_markup=keyboard)
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
            if str(user_answer).lower() == str(question['correct_answer']).lower():
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
def load_questions_from_excel(filename):
    questions = []
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        question_number = row[0]
        question_type = row[1]  # Тип вопроса: "текст" или "картинка"
        question_content = row[2]  # Содержание вопроса (текстовый вопрос или путь к файлу с картинкой)
        answers = row[3:7]  # Ответы находятся в столбцах с 4 по 7 (включительно)
        correct_answer = row[7]  # Правильный ответ находится в восьмом столбце
        questions.append({
            'number': question_number,
            'type': question_type,
            'content': question_content,
            'answers': answers,
            'correct_answer': correct_answer
        })
    return questions

# Теперь вместо жестко прописанных вопросов используем функцию load_questions_from_excel
questions = load_questions_from_excel('analit_zadachi_list.xlsx')
