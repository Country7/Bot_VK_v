from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent
import Bot_vk
from generate_ticket import generate_ticket
from settings import *
from Bot_vk import Bot


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {
            'message': {
                'date': 1622989505, 'from_id': 655754131, 'id': 36, 'out': 0, 'peer_id': 655754131,
                'text': 'привет бот 24', 'conversation_message_id': 35, 'fwd_messages': [], 'important': False,
                'random_id': 0, 'attachments': [], 'is_hidden': False},
            'client_info': {
                'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link', 'callback',
                                   'intent_subscribe', 'intent_unsubscribe'],
                'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}},
        'group_id': 204731514, 'event_id': '167b50a7335aa941fd4d1c0730263fee3742c91f'}

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('Bot_vk.vk_api.VkApi'):
            with patch('Bot_vk.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()
                #
                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count
        # assert True

    INPUTS = [
        'что по чем',
        'Привет',
        'А когда?',
        'Где будет конференция?',
        'Зарегистрируй меня',
        'Вениамин',
        'мой адрес email@email',
        'email@email.ru',
    ]
    EXPECTED_OUTPUTS = [
        DEFAULT_ANSWER,
        INTENTS[0]['answer'],
        INTENTS[2]['answer'],
        INTENTS[3]['answer'],
        SCENARIOS['registration']['steps']['step1']['text'],
        SCENARIOS['registration']['steps']['step2']['text'],
        SCENARIOS['registration']['steps']['step2']['failure_text'],
        SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='email@email.ru'),
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('Bot_vk.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    # OLD
    # def test_on_event(self):
    #     event = VkBotMessageEvent(raw=self.RAW_EVENT)
    #     send_mock = Mock()
    #     with patch('EchoBot_VK.vk_api.VkApi'):
    #         with patch('EchoBot_VK.VkBotLongPoll'):
    #             bot = Bot('', '')
    #             bot.api.messages.send = send_mock
    #
    #             bot.on_event(event)
    #
    #     send_mock.assert_called_once_with(
    #             message='Эхо-бот: ' + self.RAW_EVENT['object']['message']['text'],
    #             random_id=ANY,
    #             peer_id=self.RAW_EVENT['object']['message']['peer_id'],
    #         )

    def test_image_generation(self):
        dice_mock = Mock(return_value='0')
        with patch('generate_ticket.dice', dice_mock):
            ticket_file = generate_ticket('HisName', 'hisemail@mail.ru')
        with open("files/ticket_example.png", 'rb') as file_ticket_example:
            expected_file = file_ticket_example.read()

        assert ticket_file.read() == expected_file

