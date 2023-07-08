from instagrapi import Client

from instagrapi.exceptions import LoginRequired

from send_file import Telegram
import time, os, datetime, pickle, logging
from cachetools import LRUCache
from webp2jpg import ConvertWebp



CACHE_FILE = "cache.pkl"

class InstaBackup(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        # self.cl = Client()
        # self.cl.delay_range = [2,5]
        
        # self.cl.login(username=self.username, password=self.password)
        
        self.cache = self.load_cache()
        # self.stories = self.get_stories()
    
        self.downloaded = {}
        self.token = "TOKEN"
        self.chat_id = "CHAT_ID"
        
        # self.actual_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # SE CREA EL OBJETO TELEGRAM PARA ENVIAR LOS MENSAJES
        self.bot = Telegram(token=self.token, chat_id=self.chat_id)
       
        self.logger = logging.getLogger(__name__)
       
        self.login_user(self.username, self.password)
    
    def login_user(self, username, password):
        
        self.cl = Client()
        
        #self.cl.set_proxy("PROXY") COMMENT THIS LINE IF YOU DON'T USE PROXY
        self.cl.delay_range = [2,5]
        
        try:
            session = self.cl.load_settings("session.json")
            
        except FileNotFoundError:
            pass
        
        
        login_via_session = False
        login_via_pw = False
        
        try:
            if session:
                try:
                    self.cl.set_settings(session)
                    self.cl.login(username, password)
                    # CHECK IF SESSION IS VALID
                    try: 
                        self.cl.account_info()
                        print("Login via session successful")
                    except LoginRequired:
                        
                        self.logger.info("Session is invalid, need to login via username and password")
                        
                        old_session = self.cl.get_settings()
                        
                        self.cl.set_settings({})
                        self.cl.set_uuids(old_session['uuids'])
                        self.cl.login(username, password)
                        
                    login_via_session = True
                
                except Exception as e:
                    self.logger.info("Couldn't login user using session information: %s" % e)
                    
        except Exception as e:
            self.logger.info("Couldn't load session information: %s" % e)
                    
        if not login_via_session:
            try:
                self.logger.info("Attempting to login via username and password. username: %s" % username)

                if self.cl.login(username, password):
                    self.cl.dump_settings("session.json")
                    print("Login via username and password successful")
                    login_via_pw = True
            except Exception as e:
                self.logger.info("Couldn't login user using username and password: %s" % e)
                
        if not login_via_session and not login_via_pw:
            
            raise Exception("Couldn't login user using session or username and password")
                
                
                
                
        
        
        
        #CHECK IF SESSION EXISTS
        
    
    
    
    def load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
        return LRUCache(maxsize=100)
                
                
    def save_cache(self):
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(self.cache, f)
            
            
    # def load_session(self):
    #     if os.path.exists("session.pkl"):
    #         with open("session.pkl", "rb") as f:
    #             print("Loading credentials from cache")
    #             return pickle.load(f)
    #     cl = Client()
    #     cl.login(username=self.username, password=self.password)
        
    #     self.save_session(cl)
    #     return cl
    
    # def save_session(self, cl):
    #     with open("session.pkl", "wb") as f:
    #         pickle.dump(cl, f)
    
    def get_stories(self, usuarios_backup) -> dict:
        stories = {}
        """
        Obtiene las historias de los usuarios y devuelve un diccionario con los pares usuario-clave.
        """
        
        def get_pk(user) -> tuple:
            """
            Obtiene las claves de las historias de un usuario dado y su media_type las devuelve como una tupla.
            """
            list_pk = []
            id_user = self.cl.user_id_from_username(user)
            user_stories = self.cl.user_stories(id_user)
            for story in user_stories:
                pk_media_type  = (story.pk, story.media_type, story.taken_at)
                list_pk.append(pk_media_type)
            return list_pk
        
        for user in usuarios_backup:
            stories[user] = get_pk(user)
        
        return stories
        
    
    # def get_stories_cache(self):
    #     if 'stories' not in self.cache:
    #         self.cache['stories'] = self.get_stories()
    #         print("Stories loaded")
        
    #     else: 
    #         print("Stories loaded from cache")
    #     return self.cache['stories']
     
    
    
    
    def download_stories(self, users):
        
        
        
        stories = self.get_stories(users)
        
        # Se comprueba si existe la historia en el diccionario de descargados
        def existe(user, story):
            if user in self.downloaded:
                if story in self.downloaded[user]:
                    return True
            else:
                self.downloaded[user] = []
                return False
            return False
        # Se itera sobre el diccionario par clave-valor de historias Ej. {'usuario': [(pk, media_type, taken_at), (pk, media_type, taken_at)]}
        for usuario_backup, stories in stories.items():
            for story, media_type, taken_at in stories:
                def convert_time(time):
                    time_uploud = time - datetime.timedelta(hours=6)
                    return time_uploud.strftime("%H:%M %p")
                
                if not existe(usuario_backup,story):
                    print(f"Nueva historia de {usuario_backup} 📚🎉")
                    self.cl.story_download(story, filename="story_{}".format(story), folder=".")
                    self.downloaded[usuario_backup].append(story)
                    if media_type == 2:
                        # se envia la historia a telegram
                        self.send_stories(story, media_type,message="{} - Nueva historia de {} 🎉".format(convert_time(taken_at), usuario_backup))
                        self.delete_stories(story, media_type)
                        
                        
                    elif media_type == 1:
                        # try:
                        if os.path.exists("story_{}.jpg".format(story)):
                            self.send_stories(story, media_type, message="{} - Nueva historia de {} 🎉".format(convert_time(taken_at), usuario_backup))
                        
                        elif os.path.exists("story_{}.webp".format(story)):
                            ConvertWebp("story_{}.webp".format(story)).convert()
                            self.send_stories(story, media_type, message="{} - Nueva historia de {} 🎉".format(convert_time(taken_at), usuario_backup))
                            # time.sleep(1)
                            # self.delete_stories(story, media_type)
                        # except FileNotFoundError as e:
                        #     if e.filename == "story_{}.jpg".format(story):
                        #         self.send_stories(story, media_type, message="Nueva historia de {} 📚🎉".format(usuario_backup))
                        #         continue
                                # time.sleep(1)
                                # self.delete_stories(story, media_type)
                            
        # for story, media_type in stories.items():
        #     if not existe(story):
        #         print(f"Nueva historia de {usuario_backup} 📚🎉")
        #         self.cl.story_download(story, filename="story_{}".format(story), folder=".")
        #         print("Downloaded story_{}".format(story))
        #         # self.downloaded.append("story_{}".format(story))
        #         if media_type == 2:
        #             self.send_stories(story, media_type, message="Nueva historia de {} 📚🎉".format(usuario_backup)})
        #             self.delete_stories(story, media_type)
        #             # self.send_message("Nueva historia de soesitxx")
                    
                    
        #         elif media_type == 1:
        #             ConvertWebp("story_{}.webp".format(story)).convert()
        #             self.send_stories(story, media_type)
        #             self.delete_stories(story, media_type)
        #     else:
        #         continue
        self.save_cache()
        
        # return self.downloaded
    
    def get_media(self, file):
        media = os.path.join(os.getcwd(), file)
        return open(media, 'rb')


    def send_stories(self, story, media_type, message):
        # token = "6372904069:AAEwfyXb1kp6hA3o1rU-2Htzqnud9eYDvYs"
        # client_id = "755575697"
        media_type_code = media_type
        if media_type_code == 2:
            parse_data = self.get_media("story_{}.mp4".format(story))
        elif media_type_code == 1:
            if os.path.isfile("story_{}.jpg".format(story)):
                parse_data = self.get_media("story_{}.jpg".format(story))
            elif os.path.isfile("story_{}.webp".format(story)):
                parse_data = self.get_media("story_{}.webp".format(story))
        self.bot.send_media(parse_data, media_type=media_type_code, caption=message)
        
        
    # def send_message(self, message):
    #     self.bot.send_message(self.token, self.chat_id, message)
        
    def delete_stories(self, story, media_type):
        if media_type == 2:
            os.remove("story_{}.mp4".format(story))
        elif media_type == 1:
            os.remove("story_{}.webp".format(story))
            os.remove("story_{}.jpg".format(story))
        print("Deleted story_{}".format(story))
    
            
    
        
        
# def get_stories(cl, username):
#     id_user = cl.user_id_from_username(username)
#     stories = cl.user_stories(id_user)
    
#     stories_dict = {}
#     for story in stories:
#         stories_dict[story.pk] = story.media_type
#     return stories_dict




def main():
    insta = InstaBackup("USER", "PASSWORD")
    while True:
        users = ["USER1", "USER2"]
        insta.download_stories(users)
        actual_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("{} - A la escucha de nuevas historias...".format(actual_time))
        time.sleep(3600)
    
if __name__ == "__main__":
    main()