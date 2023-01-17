# -*- coding: utf-8 -*-

import logging
import random

import requests
import vk_api
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import handlers
from models import UserState, Registration

try:
    from settings import *
except ImportError:
    exit('DO Copy settings.py.default to settings.py and set GROUP_ID, TOKEN')

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log', mode='a', encoding='utf8', delay=False)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.INFO)


class Bot:
    """
    Bot для vk.com
    Use python 3.9
    Поддерживает ответы на вопросы про дату, место проведения и сценарий регистрации
    """
    def __init__(self, group_id, token):
        """
        :param group_id: group_id из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            log.debug('Получено событие от сервера')
            try:
                self.on_event(event)
            except Exception:
                log.exception('ошибка в обработке события')

    @db_session
    def on_event(self, event):
        """
        Отправляет сообщение назад, если сообщение текстовое
        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug('мы пока не умеем обрабатывать событие такого типа %s', event.type)
            log.debug(event)
            return

        user_id = event.object.message['peer_id']
        text = event.object.message['text']

        state = UserState.get(user_id=str(user_id))

        # если UserState по user_id не пустой
        if state is not None:
            # continue scenario
            self.continue_scenario(text=text, state=state, user_id=user_id)
        else:
            # search intent
            for intent in INTENTS:
                if any(token in text.lower() for token in intent['tokens']):
                    # run intent
                    log.debug(f'User gets intent: {intent["name"]}')
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(user_id, intent['scenario'], text)
                    break
            else:
                # token not found
                self.send_text(DEFAULT_ANSWER, user_id)



    def send_text(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
        )

    def send_image(self, image, user_id):
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(upload_url, files={'photo': ("image.png", image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)

        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(
            attachment=attachment,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
        )

    def send_step(self, step, user_id, text, context):
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)
        if 'image' in step:
            handle_image = getattr(handlers, step['image'])
            image = handle_image(text, context)
            self.send_image(image, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        scenario = SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        self.send_step(step, user_id, text, context={})
        UserState(user_id=str(user_id),
                  scenario_name=scenario_name,
                  step_name=first_step,
                  context={})
        log.info(f'Старт сценария, запись в базу user_id={str(user_id)}')

    def continue_scenario(self, text, state, user_id):
        steps = SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]

        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            self.send_step(next_step, user_id, text, state.context)

            if next_step['next_step']:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                log.info('Registered: {name}, {email}'.format(**state.context))
                Registration(name=state.context['name'], email=state.context['email'])
                # self.user_states.pop(user_id)
                state.delete()
        else:
            # retry current step
            self.send_text(step['failure_text'].format(**state.context), user_id)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(GROUP_ID, TOKEN)
    log.info('Ключ на старт!')
    bot.run()