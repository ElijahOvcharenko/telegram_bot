from Bot import Bot
import Adafruit_DHT
from skimage.io import *
from skimage import img_as_float, img_as_ubyte
import numpy as np


class RoomBot(Bot):
    def __init__(self):
        super().__init__('https://api.telegram.org/bot',
                         '528234666:AAEIjbiELzdwLWs3Q79eIiS-8w2qwYp9K9U')

    def default_command(self, command, data):
        data['text'] = "и так тоже не умею"
        return None, data, '/sendMessage'

    def on_message_received(self, command_str, data):
        parse = command_str.split(" ")
        if parse[0] == "Привет" or command_str[0] == "привет":
            data['text'] += "дратути"
        else:
            data['text'] += "так я не умею"
        return None, data, '/sendMessage'

    def on_temp_command(self, command, data):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 21)
        data['text'] += "температура <b>%s °C</b>, влажность <b>%s %%</b>" % \
                        (str(temperature), str(humidity))
        return None, data, '/sendMessage'

    def on_photo_command(self, command, data):
        img = imread("img.png")
        files, request_type = self.send_photo(img)
        return files, data, request_type

    def on_start_command(self, command, data):
        data['text'] += "Добрый вечур!"
        return None, data, '/sendMessage'

    def on_photo_received(self, update, data):
        img = self.get_photo(update)
        if img is not None:
            data['caption'] = "повторюха муха"
            if 'caption' in update['message']:
                if update['message']['caption'].strip() == "чб":
                    img_f = img_as_float(img)
                    img_f = (img_f[:, :, 0] + img_f[:, :, 1] + img_f[:, :, 2]) / 3
                    img = img_as_ubyte(np.clip(img_f, 0, 1))
                    data['caption'] += " - чб"

            files, request_type = self.send_photo(img)
            return files, data, request_type
