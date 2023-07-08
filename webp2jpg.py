
from PIL import Image

import os

class ConvertWebp(object):
    def __init__(self, file_name):
        self.file_name = f"{file_name}"
        self.convert()
        
    def convert(self):
        path = os.getcwd()
        file_path = os.path.join(path, self.file_name)
        
        with Image.open(file_path) as im:
            
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.save("{}.jpg".format(self.file_name.split(".")[0]), "jpeg")
            
# if __name__ == "__main__":
#     ConvertWebp("story_3140021016046649269")
        