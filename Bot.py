"""
Класс для содания простых телеграмм ботов

Для создания своего бота необходимо наследовать класс Bot, к кострукторе вызвать базовый конструктор
Bot(url, token, update_frequency=1) где:
    url - URL телеграмма
    token - токен Вашего бота
    update_frequency - частота обновления бота (по умолчанию = 1)

Для добавления новой команды, необзодимо содать в классе метод с сигнатурой:
on_<название_команды>_command(command, data) -> (files, data, request_type)
    command - сообщение которое отправил пользователь, разбитое по пробелу, первый элемент -
        название команды

    data - словарь с опасание ответа пользователю; содердит такие поля: 'chat_id'(номер чата куда мы
        собираемся отправить ответ, только для чтения), 'text'(если request_type == '/sendMessage',
        то данное поле является сообщением которе увивит пользователь и не должно быть пустым!;
        поддерживает HTML разметку; по умолчанию равно пустой строке), 'caption'(если request_type
        == '/sendPhoto', то данное поле должно содержать описание картинки)

    files - словарь с файлами для отправки пользователю, обычно он None (что и следут возращеть из
        метода), на данный момент нужен только для отправки фото и возваращется из метода
        send_photo() (про  который чуть ниже)

    request_type - тип вашего ответа в зависимоти от его содежимого; на данный момент поддерживается
        два виде: '/sendMessage' - при отправки текстового сообщения и '/sendPhoto' - при отправки
        фото

Существует несколько всторенных команд, которые можно реализовать в своем классе:
default_command(command, data) -> (files, data, request_type) - вызывется если ни одна комманда не
    подходит под запрос пользователя, комманда по умолчанию

on_message_received(command_str, data) -> (files, data, request_type) - вызывается когда
    пользователь отправил сообщение без команды; command_str - сообщение пользователя (не разбитое
    по пробелу!)

on_photo_received(update, data) -> (files, data, request_type) - вызывается когда пользователь
    отправил фотографию; update - массив который хранит всю информацию про сообщение (например:
    update['message']['caption'] - описание картинки), update можно передать в функцию get_photo()
    для получения фото

Реализация ни одного из данных методов в Вашем классе не является обязательной. При отсутствии
подходящего метода, сообщение от пользователя будет проигнорировано и не получит никакой ответ.

Хорошим тоном считается реализация команд /start и /help.

методы:
run() - запуск бота
send_photo(img) -> (files, request_type) - отправляет фото img пользователю
get_photo(update) -> ndarray - получает изображение из update

"""

import requests
from urllib.request import urlopen
from skimage.io import *
from io import BytesIO
import time


class Bot:
    def __init__(self, url, token, update_frequency=1):
        self.URL = url
        self.TOKEN = token
        self.offset = 0

        # время обновления в секундах
        self.update_frequency = update_frequency

    def get_updates(self):
        """
        метод который получет новые сообщения для бота, опрашивая сервер телеграмма
        """
        data = {'offset': self.offset, 'limit': 0, 'timeout': 0}
        return self.send_request('/getUpdates', data)

    def execute_update(self, update):
        """
        метод выполняет комманды которые ему приходят от пользователей
        """
        self.update_offset(update)
        if not ('text' or 'photo' in update['message']):
            return

        files = None
        data = {
            'chat_id': str(update['message']['chat']['id']),
            'text': "",
            'parse_mode': 'HTML'
        }
        request_type = ''

        if 'text' in update['message']:

            if update['message']['text'].strip()[0] == '/':
                command = update['message']['text'].strip().split(" ")
                method_name = "on_"+command[0][1:]+"_command"
                if hasattr(self, method_name):
                    method_to_call = getattr(self, method_name)
                    files, data, request_type = method_to_call(command, data)
                elif hasattr(self, "default_command"):
                    files, data, request_type = self.default_command(command, data)
            elif hasattr(self, "on_message_received"):
                files, data, request_type =\
                    self.on_message_received(update['message']['text'].strip(), data)
            else:
                return
        if 'photo' in update['message']:
            if hasattr(self, "on_photo_received"):
                files, data, request_type = self.on_photo_received(update, data)
            else:
                return

        request = self.send_request(request_type, data, files=files)
        if request is not None and not request.status_code == 200:
            print("answer is not sent")

    def send_request(self, command, data, files=None):
        try:
            if files is None:
                return requests.post(self.URL + self.TOKEN + command, data=data)
            else:
                return requests.post(self.URL + self.TOKEN + command, data=data,
                                     files=files)
        except Exception as ex:
            print(ex)
            return None

    def send_photo(self, img):
        str_io = BytesIO()
        imsave(str_io, img, plugin='pil', format_str='png')
        str_io.seek(0)
        files = {
            'photo': str_io
        }
        request_type = '/sendPhoto'
        return files, request_type

    def get_photo(self, update):
        # получаем номер фотки с самым большим размром
        file_id = update['message']['photo'][-1]['file_id']
        response = self.send_request('/getFile', data={'file_id': file_id})
        if response is None:
            return None
        photo_path = response.json()['result']['file_path']
        # request = requests.get("https://api.telegram.org/file/bot" + self.TOKEN + "/" +
        #                        photo_path, verify=False)
        request = urlopen("https://api.telegram.org/file/bot" + self.TOKEN + "/" + photo_path)
        if request is None:
            return None
        try:
            img = imread(request)
            return img
        except:
            return None

    def update_offset(self, update):
        """
        метод который обновляет id поселднего обработанного запроса
        """
        self.offset = update['update_id'] + 1

    def run(self):
        print("Bot is started")
        try:
            while True:
                time.sleep(self.update_frequency)
                request = self.get_updates()
                print("update...")
                if request is None:
                    continue
                # print(request.json())
                for update in request.json()['result']:
                    self.execute_update(update)

        except KeyboardInterrupt:
            print("\nBot will come back!")
