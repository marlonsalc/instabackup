 
import requests

import os

class Telegram(object):
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id


    def send_media(self, media, media_type: int, caption=None):
        params = {"chat_id": self.chat_id, "caption": caption}

        if media_type == 2:
            files = {"video": media}
            telegram_api = "https://api.telegram.org/bot{}/sendVideo".format(self.token)
        elif media_type == 1:
            files = {"photo": media}
            telegram_api = "https://api.telegram.org/bot{}/sendPhoto".format(self.token)
        response = requests.post(telegram_api, params=params, files=files)
        return response.json()

    def send_message(self, message):
        params = {"chat_id": self.chat_id, "text": message}
        telegram_message_api = "https://api.telegram.org/bot{}/sendMessage".format(self.token)
        response = requests.post(telegram_message_api, params=params)
        return response.json()

    # def send_message(self, message):
    #     params = {"chat_id": self.chat_id, "text": message}
    #     response = requests.post(self.telegram_message_api, params=params)
    #     return response.json()

# def send_file(file_name=""):
#     path = os.getcwd()
#     video = os.path.join(path, file_name)
#     return open(video, 'rb')



# if __name__ == "__main__":

# #     # video = send_file()

#     bot = Telegram(token="TOKEN", chat_id="CHAT_ID")
#     bot.send_media(media=send_file(file_name="FILE"), media_type=2, caption="Nueva historia de {} 📚🎉")

