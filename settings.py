# -*- coding: utf-8 -*-

GROUP_ID = 204731514
TOKEN = ""

INTENTS = [
    {
        "name": "Приветствие",
        "tokens": ("привет", "здравствуй", "хай", "здарова", "добрый"),
        "scenario": None,
        "answer": "Привет, я Бот. Хочу рассказать когда и где пройдет конференция, "
                  "а также зарегистрировать Вас. Просто спросите."
    },
    {
        "name": "Досвидания",
        "tokens": ("пока", "свидан", "давай", "счастлив"),
        "scenario": None,
        "answer": "Пока. Заходите еще!"
    },
    {
        "name": "Дата проведения",
        "tokens": ("когда", "сколько", "дата", "дату"),
        "scenario": None,
        "answer": "Конференция проводится 15-го июля, регистрация начнется в 10 утра"
    },
    {
        "name": "Место проведения",
        "tokens": ("где", "место", "локация", "адрес", "метро"),
        "scenario": None,
        "answer": "Конференция пройдет в павильоне 18Г в Экспоцентре"
    },
    {
        "name": "Регистрация",
        "tokens": ("регист", "добав"),
        "scenario": "registration",
        "answer": None
    },
]

SCENARIOS = {
    "registration": {
        "first_step": "step1",
        "steps": {
            "step1": {
                "text": "Чтобы зарегистрироваться, введите Ваше имя. Оно будет отображено на бейдже.",
                "failure_text": "Имя должно состоять из 3 - 30 букв и дефиса. Попробуйте еще раз.",
                "handler": "handle_name",
                "next_step": "step2"
            },
            "step2": {
                "text": "Введите e-mail, мы отправим на него все данные.",
                "failure_text": "Во введенном адресе ошибка. Попробуйте еще раз.",
                "handler": "handle_email",
                "next_step": "step3"
            },
            "step3": {
                "text": "Спасибо за регистрацию, {name}! Ваш билет ниже. Копию мы отправили на {email} билет, "
                        "распечатайте его.",
                "image": "handle_generate_ticket",
                "failure_text": None,
                "handler": None,
                "next_step": None
            }
        }
    }
}

DEFAULT_ANSWER = "Не знаю как на это ответить. " \
                 "Могу сказать когда и где пройдет конференция, а также зарегистрировать Вас. Просто спросите."


DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    password='qaz',
    host='localhost',
    database='bot_vk'
)