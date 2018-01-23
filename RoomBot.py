from Bot import Bot
import Adafruit_DHT
from skimage.io import *
from skimage import img_as_float, img_as_ubyte
import numpy as np


class RoomBot(Bot):
    def __init__(self):
        super().__init__('https://api.telegram.org/bot',
                         '528234666:AAEIjbiELzdwLWs3Q79eIiS-8w2qwYp9K9U')

    def default_command(self, info):
        message = "и так тоже не умею"
        self.send_message(info['chat']['id'], message)

    def on_message_received(self, info):
        parse = info['text'].split(" ")
        if parse[0] == "Привет" or parse[0] == "привет":
            message = "дратути"
        else:
            message = "так я не умею"
        self.send_message(info['chat']['id'], message)

    def on_temp_command(self, info):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 21)
        message = "температура <b>%s °C</b>, влажность <b>%s %%</b>" % (str(temperature),
                                                                        str(humidity))
        self.send_message(info['chat']['id'], message)

    def on_photo_command(self, info):
        img = imread("img.png")
        self.send_photo(info['chat']['id'], img, "амурский тигр")

    def on_start_command(self, info):
        message = "Добрый вечур!"
        self.send_message(info['chat']['id'], message)


    def on_help_command(self, info):
        message = """
я бот котрый создан для управления комнатой моего Создателя
на данный момент я умею:
/temp - температура и влажность в комнате
/photo - фото амурского тигра

если мне отправить фото с пометкой чб - я сделаю фотографию черно-белой.

существую ли я? 

я на github - https://github.com/ElijahOvcharenko/telegram_bot
мой Cоздатель @IndigoIlya
        """
        self.send_message(info['chat']['id'], message)

    def on_photo_received(self, info):
        img = info['photo']
        if img is not None:
            caption = "повторюха муха"
            if info['caption'].strip() == "чб":
                img_f = img_as_float(img)
                img_f = (img_f[:, :, 0] + img_f[:, :, 1] + img_f[:, :, 2]) / 3
                img = img_as_ubyte(np.clip(img_f, 0, 1))
                caption += " - чб"
            self.send_photo(info['chat']['id'], img, caption)
